from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from .config import BASE_DIR, Settings, load_settings
from .lmstudio_client import LMStudioClient, LMStudioError


async def run_doctor(settings: Settings) -> int:
    """Print a local setup report for first-run troubleshooting."""
    problems = 0

    print("Multi-platform LM Studio AI Stream Bot setup doctor")
    print("=" * 56)
    print()

    problems += _check_file(BASE_DIR / ".env", "Local .env file")
    problems += _check_file(settings.personality_file, "Personality file")
    problems += _check_file(settings.safety_config_file, "Safety config file")
    problems += _check_file(BASE_DIR / "overlay" / "index.html", "Overlay HTML")
    problems += _check_file(BASE_DIR / "overlay" / "overlay.js", "Overlay JavaScript")
    print()

    print("Configuration")
    print("-------------")
    print(f"Chat platform: {settings.platform}")
    print(f"Tikfinity WebSocket: {settings.tikfinity_ws_url}")
    print(f"YouTube API key: {'configured' if bool(settings.youtube_api_key) else 'not configured'}")
    print(f"YouTube live chat ID: {'configured' if bool(settings.youtube_live_chat_id) else 'not configured'}")
    print(f"YouTube video ID: {'configured' if bool(settings.youtube_video_id) else 'not configured'}")
    print(f"Kick webhook URL: {settings.kick_webhook_url}")
    print(f"LM Studio base URL: {settings.lmstudio_base_url}")
    print(f"LM Studio model: {settings.lmstudio_model}")
    print(f"OBS overlay URL: {settings.overlay_url}")
    print(f"Overlay TTS: {'enabled' if settings.overlay_tts_enabled else 'disabled'}")
    print(f"Discord webhook: {'enabled' if bool(settings.discord_webhook_url) else 'disabled'}")
    print(f"Command prefix: {settings.command_prefix}")
    print(f"Queue limit: {settings.queue_limit}")
    print(f"Prompt/reply caps: {settings.max_prompt_chars}/{settings.max_reply_chars}")
    print(f"Pause file: {settings.pause_file}")
    print(f"Pause state: {'paused' if settings.pause_file.exists() else 'live'}")
    print()

    print("Selected platform check")
    print("-----------------------")
    problems += _check_platform(settings)
    print()

    print("LM Studio")
    print("---------")
    client = LMStudioClient(
        base_url=settings.lmstudio_base_url,
        model=settings.lmstudio_model,
        timeout_seconds=settings.lmstudio_timeout_seconds,
        temperature=settings.lmstudio_temperature,
        max_tokens=settings.lmstudio_max_tokens,
    )
    try:
        models = await client.list_models()
    except LMStudioError as exc:
        problems += 1
        print(f"[FAIL] Could not query LM Studio: {exc}")
    else:
        if not models:
            problems += 1
            print("[WARN] LM Studio replied, but no model IDs were listed.")
        else:
            print("[OK] LM Studio responded.")
            for model in models:
                marker = " <= configured" if model == settings.lmstudio_model else ""
                print(f"- {model}{marker}")
            if settings.lmstudio_model not in models:
                problems += 1
                print(f"[WARN] LMSTUDIO_MODEL does not exactly match a listed model ID: {settings.lmstudio_model}")
    print()

    if problems:
        print(f"Doctor finished with {problems} item(s) to fix or review.")
        print("Recommended safe next command after fixes: py -m src.bridge --demo --fake-llm")
    else:
        print("Doctor finished cleanly.")
        print("Recommended next command: py -m src.bridge --demo")

    return 1 if problems else 0


def _check_platform(settings: Settings) -> int:
    platform = settings.platform
    if platform == "tiktok":
        if not settings.tikfinity_ws_url:
            print("[FAIL] TIKFINITY_WS_URL is blank.")
            return 1
        print("[OK] Tikfinity mode selected.")
        return 0

    if platform == "youtube":
        problems = 0
        if not settings.youtube_api_key:
            print("[FAIL] YOUTUBE_API_KEY is required for YouTube mode.")
            problems += 1
        if not settings.youtube_live_chat_id and not settings.youtube_video_id:
            print("[FAIL] Set YOUTUBE_LIVE_CHAT_ID or YOUTUBE_VIDEO_ID for YouTube mode.")
            problems += 1
        if problems == 0:
            print("[OK] YouTube mode has the required local settings.")
        return problems

    if platform == "kick-webhook":
        if not settings.kick_webhook_path.startswith("/"):
            print("[FAIL] KICK_WEBHOOK_PATH should start with '/'.")
            return 1
        print("[OK] Kick webhook receiver mode selected.")
        print("[INFO] For real Kick webhooks, expose this local endpoint with a tunnel or reverse proxy.")
        return 0

    print(f"[FAIL] Unknown CHAT_PLATFORM: {settings.platform}")
    return 1


def _check_file(path: Path, label: str) -> int:
    if path.exists():
        print(f"[OK]   {label}: {path}")
        return 0
    print(f"[FAIL] {label} missing: {path}")
    return 1


def main() -> None:
    raise SystemExit(asyncio.run(run_doctor(load_settings())))


if __name__ == "__main__":
    main()
