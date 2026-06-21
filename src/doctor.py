from __future__ import annotations

from pathlib import Path

from .config import BASE_DIR, Settings
from .lmstudio_client import LMStudioClient, LMStudioError


async def run_doctor(settings: Settings) -> int:
    """Print a local setup report for first-run troubleshooting."""
    problems = 0

    print("Tikfinity LM Studio AI Stream Bot setup doctor")
    print("=" * 52)
    print()

    problems += _check_file(BASE_DIR / ".env", "Local .env file")
    problems += _check_file(settings.personality_file, "Personality file")
    problems += _check_file(settings.safety_config_file, "Safety config file")
    problems += _check_file(BASE_DIR / "overlay" / "index.html", "Overlay HTML")
    problems += _check_file(BASE_DIR / "overlay" / "overlay.js", "Overlay JavaScript")
    print()

    print("Configuration")
    print("-------------")
    print(f"Tikfinity WebSocket: {settings.tikfinity_ws_url}")
    print(f"LM Studio base URL: {settings.lmstudio_base_url}")
    print(f"LM Studio model: {settings.lmstudio_model}")
    print(f"OBS overlay URL: {settings.overlay_url}")
    print(f"Overlay TTS: {'enabled' if settings.overlay_tts_enabled else 'disabled'}")
    print(f"Discord webhook: {'enabled' if bool(settings.discord_webhook_url) else 'disabled'}")
    print(f"Command prefix: {settings.command_prefix}")
    print(f"Queue limit: {settings.queue_limit}")
    print(f"Prompt/reply caps: {settings.max_prompt_chars}/{settings.max_reply_chars}")
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
        print("Recommended next command after fixes: py -m src.bridge --demo --fake-llm")
    else:
        print("Doctor finished cleanly.")
        print("Recommended next command: py -m src.bridge --demo")

    return 1 if problems else 0


def _check_file(path: Path, label: str) -> int:
    if path.exists():
        print(f"[OK]   {label}: {path}")
        return 0
    print(f"[FAIL] {label} missing: {path}")
    return 1
