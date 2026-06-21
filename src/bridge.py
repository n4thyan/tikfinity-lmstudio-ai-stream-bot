from __future__ import annotations

import argparse
import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass
from typing import Any

from .chat_sources import (
    ChatMessage,
    KickWebhookChatSource,
    TikfinityChatSource,
    YouTubeLiveChatSource,
    extract_kick_webhook_message,
    extract_tikfinity_message,
    extract_youtube_message,
)
from .config import Settings, load_personality, load_settings
from .discord_webhook import DiscordLogger
from .filters import SafetyConfig, filter_ai_output, filter_chat_text, sanitise_username
from .lmstudio_client import LMStudioClient
from .overlay_server import OverlayBroadcaster, start_overlay_server


LOGGER = logging.getLogger(__name__)
PAUSE_NOTICE_SECONDS = 15
SUPPORTED_PLATFORMS = {"tiktok", "youtube", "kick-webhook"}


@dataclass(frozen=True)
class ChatCommand:
    raw_username: str
    safe_username: str
    command: str
    prompt: str
    platform: str = "demo"


class StreamBridge:
    def __init__(self, settings: Settings, *, use_fake_llm: bool = False) -> None:
        self.settings = settings
        self.use_fake_llm = use_fake_llm
        self.personality = load_personality(settings)
        self.safety = SafetyConfig.load(settings.safety_config_file)
        self.discord = DiscordLogger(settings.discord_webhook_url)
        self.llm = LMStudioClient(
            base_url=settings.lmstudio_base_url,
            model=settings.lmstudio_model,
            timeout_seconds=settings.lmstudio_timeout_seconds,
            temperature=settings.lmstudio_temperature,
            max_tokens=settings.lmstudio_max_tokens,
        )
        self.overlay = OverlayBroadcaster()
        self.queue: asyncio.Queue[ChatCommand] = asyncio.Queue(maxsize=settings.queue_limit)
        self.last_user_seen: dict[str, float] = {}
        self.last_global_seen = 0.0
        self.last_pause_notice = 0.0
        self.mood = "normal"

    async def start(self) -> None:
        await start_overlay_server(
            self.settings.overlay_host,
            self.settings.overlay_port,
            self.overlay,
            self.settings.overlay_tts_enabled,
        )
        await self.overlay.publish(
            {
                "type": "status",
                "text": "Overlay connected. Waiting for chat.",
                "tts": False,
                "ttsEnabled": self.settings.overlay_tts_enabled,
            }
        )
        await self.discord.status(f"Bridge started for {self.settings.platform}. Overlay: {self.settings.overlay_url}")
        asyncio.create_task(self._worker())

    async def test_lmstudio(self) -> None:
        """Check LM Studio connectivity without starting a chat platform or OBS."""
        print(f"Checking LM Studio at {self.settings.lmstudio_base_url}")
        models = await self.llm.list_models()
        if models:
            print("Models visible from LM Studio:")
            for model in models:
                marker = " <= configured" if model == self.settings.lmstudio_model else ""
                print(f"- {model}{marker}")
            if self.settings.lmstudio_model not in models:
                print(f"Warning: LMSTUDIO_MODEL is set to '{self.settings.lmstudio_model}', but that exact ID was not listed.")
        else:
            print("LM Studio responded, but no model IDs were listed.")

        reply = await self.llm.chat(
            self.personality,
            "Public viewer name: local_test\nCurrent mood: normal\nCommand: ask\nViewer message: Say hello to the stream in one short sentence.",
        )
        filtered = filter_ai_output(reply, self.safety, self.settings.max_reply_chars)
        if not filtered.allowed:
            print(f"LM Studio replied, but the local output filter blocked it: {filtered.reason}")
            return
        print("Test reply:")
        print(filtered.text)

    async def test_youtube(self) -> None:
        """Check YouTube API/chat discovery without starting the main bridge."""
        print("Checking YouTube chat settings.")
        source = YouTubeLiveChatSource(
            api_key=self.settings.youtube_api_key,
            live_chat_id=self.settings.youtube_live_chat_id,
            video_id=self.settings.youtube_video_id,
            poll_floor_seconds=self.settings.youtube_poll_floor_seconds,
        )
        chat_id = await source.resolve_live_chat_id()
        if chat_id:
            print(f"YouTube live chat ID ready: {chat_id}")
        else:
            print("No active YouTube live chat ID found. Check YOUTUBE_LIVE_CHAT_ID or YOUTUBE_VIDEO_ID.")

    async def test_overlay(self) -> None:
        """Run only the OBS browser overlay and publish fake events for setup testing."""
        await start_overlay_server(
            self.settings.overlay_host,
            self.settings.overlay_port,
            self.overlay,
            self.settings.overlay_tts_enabled,
        )
        print(f"OBS overlay: {self.settings.overlay_url}")
        print("Overlay test mode is running. Add the URL above as an OBS Browser Source.")
        print("Press Ctrl+C to stop.")
        count = 1
        while True:
            await self.overlay.publish(
                {
                    "type": "reply",
                    "username": f"Viewer {count}",
                    "prompt": "local overlay test",
                    "reply": f"Overlay test message {count}. If you can see this in OBS, the browser source is working.",
                    "mood": self.mood,
                    "tts": True,
                    "ttsEnabled": self.settings.overlay_tts_enabled,
                }
            )
            count += 1
            await asyncio.sleep(5)

    async def run_demo(self) -> None:
        await self.start()
        print(f"OBS overlay: {self.settings.overlay_url}")
        mode = "fake local replies" if self.use_fake_llm else "LM Studio replies"
        print(f"Demo mode using {mode}.")
        print("Type messages like: !ask are you alive")
        print("Other useful commands: !help, !status, !lore, !mood confused")
        while True:
            line = await asyncio.to_thread(input, "> ")
            await self.process_chat_message("demo_user", line, platform="demo")

    async def run_platform(self, platform: str | None = None) -> None:
        selected = (platform or self.settings.platform).strip().lower()
        if selected not in SUPPORTED_PLATFORMS:
            raise RuntimeError(f"Unsupported CHAT_PLATFORM '{selected}'. Use one of: {', '.join(sorted(SUPPORTED_PLATFORMS))}.")

        await self.start()
        while True:
            try:
                source = self._build_source(selected)
                await self.discord.status(f"Connected to {selected} chat source.")
                async for message in source.messages():
                    await self.process_platform_message(message)
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("%s chat source problem: %s", selected, exc)
                await self.discord.error(f"{selected} chat source problem: {exc}")
                await asyncio.sleep(5)

    async def run_tikfinity(self) -> None:
        await self.run_platform("tiktok")

    async def run_youtube(self) -> None:
        await self.run_platform("youtube")

    async def run_kick_webhook(self) -> None:
        await self.run_platform("kick-webhook")

    def _build_source(self, platform: str):
        if platform == "tiktok":
            return TikfinityChatSource(self.settings.tikfinity_ws_url)
        if platform == "youtube":
            return YouTubeLiveChatSource(
                api_key=self.settings.youtube_api_key,
                live_chat_id=self.settings.youtube_live_chat_id,
                video_id=self.settings.youtube_video_id,
                poll_floor_seconds=self.settings.youtube_poll_floor_seconds,
            )
        if platform == "kick-webhook":
            return KickWebhookChatSource(
                host=self.settings.kick_webhook_host,
                port=self.settings.kick_webhook_port,
                path=self.settings.kick_webhook_path,
            )
        raise RuntimeError(f"Unsupported platform: {platform}")

    async def debug_tikfinity(self) -> None:
        """Print raw Tikfinity payloads and the parsed chat result without generating replies."""
        source = TikfinityChatSource(self.settings.tikfinity_ws_url)
        print(f"Connecting to Tikfinity WebSocket: {self.settings.tikfinity_ws_url}")
        print("Debug mode only prints payloads. It does not call LM Studio or update OBS.")
        async for message in source.messages():
            print(f"Parsed TikTok chat: @{message.raw_username}: {message.message}")

    async def debug_youtube(self) -> None:
        """Print parsed YouTube chat without generating replies."""
        source = YouTubeLiveChatSource(
            api_key=self.settings.youtube_api_key,
            live_chat_id=self.settings.youtube_live_chat_id,
            video_id=self.settings.youtube_video_id,
            poll_floor_seconds=self.settings.youtube_poll_floor_seconds,
        )
        print("Debug mode only prints YouTube chat. It does not call LM Studio or update OBS.")
        async for message in source.messages():
            print(f"Parsed YouTube chat: @{message.raw_username}: {message.message}")

    async def debug_kick_webhook(self) -> None:
        """Run the Kick webhook receiver and print parsed chat without generating replies."""
        source = KickWebhookChatSource(
            host=self.settings.kick_webhook_host,
            port=self.settings.kick_webhook_port,
            path=self.settings.kick_webhook_path,
        )
        print(f"Kick webhook receiver: {self.settings.kick_webhook_url}")
        print("Debug mode only prints Kick webhook chat. It does not call LM Studio or update OBS.")
        async for message in source.messages():
            print(f"Parsed Kick chat: @{message.raw_username}: {message.message}")

    async def process_tikfinity_payload(self, raw_payload: str | bytes) -> None:
        text_payload = raw_payload.decode("utf-8", errors="replace") if isinstance(raw_payload, bytes) else raw_payload
        try:
            payload = json.loads(text_payload)
        except json.JSONDecodeError:
            LOGGER.debug("Ignored non-JSON Tikfinity payload: %r", text_payload)
            return

        extracted = extract_tikfinity_message(payload)
        if extracted is None:
            return
        await self.process_platform_message(extracted)

    async def process_platform_message(self, message: ChatMessage) -> None:
        await self.process_chat_message(message.raw_username, message.message, platform=message.platform)

    async def process_chat_message(self, raw_username: str, message: str, *, platform: str = "demo") -> None:
        parsed = parse_command(message, self.settings.command_prefix)
        if parsed is None:
            return

        command, prompt = parsed
        safe_user = sanitise_username(raw_username, self.safety)

        if self._is_paused() and command not in {"help", "status"}:
            await self._publish_pause_notice()
            return

        chat_filter = filter_chat_text(prompt, self.safety, self.settings.max_prompt_chars)
        if not chat_filter.allowed:
            if self.settings.discord_log_blocked:
                await self.discord.blocked(f"[{platform}] {raw_username}", chat_filter.reason, message)
            return

        now = time.monotonic()
        user_key = f"{platform}:{raw_username}"
        if now - self.last_global_seen < self.settings.global_cooldown_seconds:
            return
        if now - self.last_user_seen.get(user_key, 0.0) < self.settings.user_cooldown_seconds:
            return

        self.last_global_seen = now
        self.last_user_seen[user_key] = now

        if command == "help":
            await self._publish_help(safe_user.text)
            return
        if command == "status":
            await self._publish_status(safe_user.text)
            return
        if command == "mood":
            await self._set_mood(safe_user.text, chat_filter.text)
            return
        if command == "reset":
            self.mood = "normal"
            await self.overlay.publish({"type": "status", "text": "Mood reset to normal.", "tts": False})
            return

        item = ChatCommand(raw_username, safe_user.text, command, chat_filter.text, platform)
        try:
            self.queue.put_nowait(item)
        except asyncio.QueueFull:
            if self.settings.discord_log_blocked:
                await self.discord.blocked(f"[{platform}] {raw_username}", "queue full", message)
            return
        if self.settings.discord_log_accepted:
            await self.discord.accepted(f"[{platform}] {raw_username}", safe_user.text, chat_filter.text)

    async def _publish_help(self, safe_username: str) -> None:
        text = "Commands: !ask <message>, !roast <topic>, !lore, !mood normal/angry/scared/sad/happy/confused/dramatic, !status, !reset."
        await self._publish_local_reply(safe_username, "!help", text, speak=False)

    async def _publish_status(self, safe_username: str) -> None:
        mode = "fake local replies" if self.use_fake_llm else "LM Studio"
        pause_state = "paused" if self._is_paused() else "live"
        text = f"Status: {pause_state}. Platform: {self.settings.platform}. Mood: {self.mood}. Queue: {self.queue.qsize()}/{self.settings.queue_limit}. Brain: {mode}."
        await self._publish_local_reply(safe_username, "!status", text, speak=False)

    async def _publish_local_reply(self, safe_username: str, prompt: str, reply_text: str, *, speak: bool) -> None:
        await self.overlay.publish(
            {
                "type": "reply",
                "username": safe_username,
                "prompt": prompt,
                "reply": reply_text,
                "mood": self.mood,
                "tts": speak,
                "ttsEnabled": self.settings.overlay_tts_enabled,
            }
        )
        if self.settings.discord_log_replies:
            await self.discord.reply(safe_username, prompt, reply_text)

    async def _publish_pause_notice(self) -> None:
        now = time.monotonic()
        if now - self.last_pause_notice < PAUSE_NOTICE_SECONDS:
            return
        self.last_pause_notice = now
        await self.overlay.publish({"type": "status", "text": "Bridge paused by local pause file.", "tts": False})

    def _is_paused(self) -> bool:
        return self.settings.pause_file.exists()

    async def _set_mood(self, safe_username: str, requested_mood: str) -> None:
        allowed_moods = {"normal", "angry", "scared", "sad", "happy", "confused", "dramatic"}
        mood = requested_mood.lower().strip().split()[0] if requested_mood.strip() else "normal"
        if mood not in allowed_moods:
            mood = "confused"
        self.mood = mood
        await self.overlay.publish(
            {
                "type": "status",
                "text": f"{safe_username} changed PotatoBrain's mood to {self.mood}.",
                "tts": False,
            }
        )

    async def _worker(self) -> None:
        while True:
            command = await self.queue.get()
            try:
                reply = await self._generate_reply(command)
                filtered_reply = filter_ai_output(reply, self.safety, self.settings.max_reply_chars)
                if not filtered_reply.allowed:
                    filtered_reply_text = "That reply was blocked by the local output filter."
                else:
                    filtered_reply_text = filtered_reply.text

                await self._publish_reply(command, filtered_reply_text)
                if self.settings.discord_log_replies:
                    await self.discord.reply(f"[{command.platform}] {command.safe_username}", command.prompt, filtered_reply_text)
            except Exception as exc:  # noqa: BLE001
                LOGGER.exception("Reply generation failed")
                await self.discord.error(f"Reply generation failed: {exc}")
                await self._publish_reply(command, "Local reply generation failed. Try again soon.")
            finally:
                self.queue.task_done()

    async def _publish_reply(self, command: ChatCommand, reply_text: str) -> None:
        await self.overlay.publish(
            {
                "type": "reply",
                "username": command.safe_username,
                "prompt": command.prompt,
                "reply": reply_text,
                "mood": self.mood,
                "platform": command.platform,
                "tts": True,
                "ttsEnabled": self.settings.overlay_tts_enabled,
            }
        )

    async def _generate_reply(self, command: ChatCommand) -> str:
        if self.use_fake_llm:
            return build_fake_reply(command, self.mood)

        command_hint = {
            "ask": "Answer the viewer's exact comment directly as PotatoBrain.",
            "roast": "Give a mild fictional roast of PotatoBrain, the stream, or the situation. Do not attack the real viewer seriously.",
            "lore": "Invent one short piece of harmless lore about PotatoBrain.",
        }.get(command.command, "Reply in character as PotatoBrain.")

        viewer_message = (
            "LIVE COMMENT EVENT\n"
            "Role boundary: you are PotatoBrain. The viewer below is a separate person. You are not the viewer and you are not chat.\n"
            "Reply only as PotatoBrain. Do not ask what the message is unless it is impossible to understand.\n"
            f"Platform: {command.platform}\n"
            f"Viewer display name: {command.safe_username}\n"
            f"Current mood: {self.mood}\n"
            f"Command: {command.command}\n"
            f"Task: {command_hint}\n"
            f"Viewer comment: {command.prompt}\n"
            "PotatoBrain reply:"
        )
        return await self.llm.chat(self.personality, viewer_message)


def build_fake_reply(command: ChatCommand, mood: str) -> str:
    """Small deterministic-ish reply generator for overlay and filter testing without LM Studio."""
    templates = [
        "I heard that, {user}. My potato circuits are pretending to understand.",
        "Current mood is {mood}. That means my answer is probably held together with tape.",
        "Command received from {platform}: {cmd}. The tiny brain cell has been notified.",
        "{user}, I would answer properly but Windows just made a mysterious USB noise.",
    ]
    template = random.choice(templates)
    return template.format(user=command.safe_username, mood=mood, cmd=command.command, platform=command.platform)


def parse_command(message: str, prefix: str) -> tuple[str, str] | None:
    text = message.strip()
    if not text.startswith(prefix):
        return None
    body = text[len(prefix) :].strip()
    if not body:
        return None
    command, _, rest = body.partition(" ")
    command = command.lower().strip()
    rest = rest.strip()

    aliases = {
        "ask": "ask",
        "q": "ask",
        "roast": "roast",
        "lore": "lore",
        "mood": "mood",
        "reset": "reset",
        "help": "help",
        "commands": "help",
        "status": "status",
        "queue": "status",
    }
    if command not in aliases:
        return None
    normalised = aliases[command]
    if normalised in {"ask", "roast"} and not rest:
        return None
    if normalised == "lore" and not rest:
        rest = "Tell the stream one tiny piece of your backstory."
    if normalised == "help" and not rest:
        rest = "Show the available stream commands."
    if normalised == "status" and not rest:
        rest = "Show the bridge status."
    if normalised == "reset" and not rest:
        rest = "Reset the stream mood."
    return normalised, rest


def extract_comment_payload(payload: dict[str, Any]) -> tuple[str, str] | None:
    """Backward-compatible Tikfinity extractor used by earlier tests."""
    message = extract_tikfinity_message(payload)
    if message is None:
        return None
    return message.raw_username, message.message


def extract_kick_payload(payload: dict[str, Any]) -> tuple[str, str] | None:
    """Small helper for tests and local Kick webhook payload inspection."""
    message = extract_kick_webhook_message(payload)
    if message is None:
        return None
    return message.raw_username, message.message


def extract_youtube_payload(item: dict[str, Any]) -> tuple[str, str] | None:
    """Small helper for tests and local YouTube payload inspection."""
    message = extract_youtube_message(item)
    if message is None:
        return None
    return message.raw_username, message.message


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


async def async_main() -> None:
    parser = argparse.ArgumentParser(description="Multi-platform chat to LM Studio stream bridge")
    parser.add_argument("--platform", choices=sorted(SUPPORTED_PLATFORMS), help="Override CHAT_PLATFORM for this run")
    parser.add_argument("--demo", action="store_true", help="Run without a live platform and read commands from stdin")
    parser.add_argument("--fake-llm", action="store_true", help="Use built-in fake replies instead of LM Studio")
    parser.add_argument("--test-lmstudio", action="store_true", help="Check the local LM Studio server and print one reply")
    parser.add_argument("--test-youtube", action="store_true", help="Check YouTube API settings and live chat ID discovery")
    parser.add_argument("--test-overlay", action="store_true", help="Run only the OBS overlay with sample messages")
    parser.add_argument("--debug-tikfinity", action="store_true", help="Print parsed Tikfinity chat without using LM Studio")
    parser.add_argument("--debug-youtube", action="store_true", help="Print parsed YouTube chat without using LM Studio")
    parser.add_argument("--debug-kick-webhook", action="store_true", help="Run Kick webhook receiver and print parsed chat without using LM Studio")
    args = parser.parse_args()

    settings = load_settings()
    configure_logging(settings.log_level)
    bridge = StreamBridge(settings, use_fake_llm=args.fake_llm)

    if args.test_lmstudio:
        await bridge.test_lmstudio()
    elif args.test_youtube:
        await bridge.test_youtube()
    elif args.test_overlay:
        await bridge.test_overlay()
    elif args.debug_tikfinity:
        await bridge.debug_tikfinity()
    elif args.debug_youtube:
        await bridge.debug_youtube()
    elif args.debug_kick_webhook:
        await bridge.debug_kick_webhook()
    elif args.demo:
        await bridge.run_demo()
    else:
        await bridge.run_platform(args.platform)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
