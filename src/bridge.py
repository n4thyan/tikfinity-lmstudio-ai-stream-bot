from __future__ import annotations

import argparse
import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

import websockets

from .config import Settings, load_personality, load_settings
from .discord_webhook import DiscordLogger
from .filters import SafetyConfig, filter_ai_output, filter_chat_text, sanitise_username
from .lmstudio_client import LMStudioClient
from .overlay_server import OverlayBroadcaster, start_overlay_server


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChatCommand:
    raw_username: str
    safe_username: str
    command: str
    prompt: str


class StreamBridge:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.personality = load_personality(settings)
        self.safety = SafetyConfig.load(settings.safety_config_file)
        self.discord = DiscordLogger(settings.discord_webhook_url)
        self.llm = LMStudioClient(
            base_url=settings.lmstudio_base_url,
            model=settings.lmstudio_model,
        )
        self.overlay = OverlayBroadcaster()
        self.queue: asyncio.Queue[ChatCommand] = asyncio.Queue(maxsize=settings.queue_limit)
        self.last_user_seen: dict[str, float] = {}
        self.last_global_seen = 0.0
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
        await self.discord.status(f"Bridge started. Overlay: {self.settings.overlay_url}")
        asyncio.create_task(self._worker())

    async def run_demo(self) -> None:
        await self.start()
        print(f"OBS overlay: {self.settings.overlay_url}")
        print("Demo mode. Type messages like: !ask are you alive")
        while True:
            line = await asyncio.to_thread(input, "> ")
            await self.process_chat_message("demo_user", line)

    async def run_tikfinity(self) -> None:
        await self.start()
        while True:
            try:
                LOGGER.info("Connecting to Tikfinity WebSocket: %s", self.settings.tikfinity_ws_url)
                async with websockets.connect(self.settings.tikfinity_ws_url, ping_interval=20) as websocket:
                    await self.discord.status("Connected to Tikfinity WebSocket.")
                    async for raw_payload in websocket:
                        await self.process_tikfinity_payload(raw_payload)
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("Tikfinity connection problem: %s", exc)
                await self.discord.error(f"Tikfinity connection problem: {exc}")
                await asyncio.sleep(5)

    async def process_tikfinity_payload(self, raw_payload: str | bytes) -> None:
        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            LOGGER.debug("Ignored non-JSON Tikfinity payload: %r", raw_payload)
            return

        extracted = extract_comment_payload(payload)
        if extracted is None:
            return

        raw_username, message = extracted
        await self.process_chat_message(raw_username, message)

    async def process_chat_message(self, raw_username: str, message: str) -> None:
        parsed = parse_command(message, self.settings.command_prefix)
        if parsed is None:
            return

        command, prompt = parsed
        safe_user = sanitise_username(raw_username, self.safety)
        chat_filter = filter_chat_text(prompt, self.safety, self.settings.max_prompt_chars)

        if not chat_filter.allowed:
            if self.settings.discord_log_blocked:
                await self.discord.blocked(raw_username, chat_filter.reason, message)
            return

        now = time.monotonic()
        if now - self.last_global_seen < self.settings.global_cooldown_seconds:
            return
        if now - self.last_user_seen.get(raw_username, 0.0) < self.settings.user_cooldown_seconds:
            return

        self.last_global_seen = now
        self.last_user_seen[raw_username] = now

        if command == "mood":
            await self._set_mood(safe_user.text, chat_filter.text)
            return
        if command == "reset":
            self.mood = "normal"
            await self.overlay.publish({"type": "status", "text": "Mood reset to normal.", "tts": False})
            return

        item = ChatCommand(raw_username, safe_user.text, command, chat_filter.text)
        try:
            self.queue.put_nowait(item)
        except asyncio.QueueFull:
            if self.settings.discord_log_blocked:
                await self.discord.blocked(raw_username, "queue full", message)
            return

        if self.settings.discord_log_accepted:
            await self.discord.accepted(raw_username, safe_user.text, chat_filter.text)

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
                    filtered_reply_text = "That reply got eaten by the stream goblin."
                else:
                    filtered_reply_text = filtered_reply.text

                await self.overlay.publish(
                    {
                        "type": "reply",
                        "username": command.safe_username,
                        "prompt": command.prompt,
                        "reply": filtered_reply_text,
                        "mood": self.mood,
                        "tts": True,
                        "ttsEnabled": self.settings.overlay_tts_enabled,
                    }
                )

                if self.settings.discord_log_replies:
                    await self.discord.reply(command.safe_username, command.prompt, filtered_reply_text)
            except Exception as exc:  # noqa: BLE001
                LOGGER.exception("Reply generation failed")
                await self.discord.error(f"Reply generation failed: {exc}")
                await self.overlay.publish(
                    {
                        "type": "reply",
                        "username": command.safe_username,
                        "prompt": command.prompt,
                        "reply": "My tiny local brain crashed. Try again in a minute.",
                        "mood": self.mood,
                        "tts": True,
                        "ttsEnabled": self.settings.overlay_tts_enabled,
                    }
                )
            finally:
                self.queue.task_done()

    async def _generate_reply(self, command: ChatCommand) -> str:
        command_hint = {
            "ask": "Answer the viewer in character.",
            "roast": "Give a mild fictional roast of the AI or the situation, not the real person.",
            "lore": "Invent one short piece of harmless lore about the AI character.",
        }.get(command.command, "Reply in character.")

        viewer_message = (
            f"Public viewer name: {command.safe_username}\n"
            f"Current mood: {self.mood}\n"
            f"Command: {command.command}\n"
            f"Instruction: {command_hint}\n"
            f"Viewer message: {command.prompt}"
        )
        return await self.llm.chat(self.personality, viewer_message)


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
    }
    if command not in aliases:
        return None
    if aliases[command] in {"ask", "roast"} and not rest:
        return None
    if aliases[command] == "lore" and not rest:
        rest = "Tell the stream one tiny piece of your backstory."
    return aliases[command], rest


def extract_comment_payload(payload: dict[str, Any]) -> tuple[str, str] | None:
    roots = [payload]
    for key in ("data", "event", "payload"):
        value = payload.get(key)
        if isinstance(value, dict):
            roots.append(value)

    event_name = str(payload.get("event") or payload.get("type") or payload.get("eventName") or "").lower()
    if event_name and not any(word in event_name for word in ("chat", "comment", "message")):
        pass

    message_keys = ("comment", "commentText", "message", "text", "content")
    user_keys = ("uniqueId", "nickname", "username", "displayName", "userId")

    message = None
    username = None
    for root in roots:
        for key in message_keys:
            value = root.get(key)
            if isinstance(value, str) and value.strip():
                message = value
                break
        user_obj = root.get("user")
        if isinstance(user_obj, dict):
            for key in user_keys:
                value = user_obj.get(key)
                if isinstance(value, str) and value.strip():
                    username = value
                    break
        for key in user_keys:
            value = root.get(key)
            if isinstance(value, str) and value.strip():
                username = username or value
                break
        if message:
            break

    if not message:
        return None
    return username or "unknown_viewer", message


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


async def async_main() -> None:
    parser = argparse.ArgumentParser(description="Tikfinity to LM Studio stream bridge")
    parser.add_argument("--demo", action="store_true", help="Run without Tikfinity and read commands from stdin")
    args = parser.parse_args()

    settings = load_settings()
    configure_logging(settings.log_level)
    bridge = StreamBridge(settings)

    if args.demo:
        await bridge.run_demo()
    else:
        await bridge.run_tikfinity()


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
