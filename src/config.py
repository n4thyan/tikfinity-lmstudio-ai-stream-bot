from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _path(name: str, default: str) -> Path:
    raw = os.getenv(name, default)
    path = Path(raw)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


@dataclass(frozen=True)
class Settings:
    tikfinity_ws_url: str
    lmstudio_base_url: str
    lmstudio_model: str
    lmstudio_timeout_seconds: int
    lmstudio_temperature: float
    lmstudio_max_tokens: int
    discord_webhook_url: str
    discord_log_accepted: bool
    discord_log_blocked: bool
    discord_log_replies: bool
    overlay_host: str
    overlay_port: int
    overlay_tts_enabled: bool
    command_prefix: str
    user_cooldown_seconds: int
    global_cooldown_seconds: int
    queue_limit: int
    max_prompt_chars: int
    max_reply_chars: int
    personality_file: Path
    safety_config_file: Path
    pause_file: Path
    log_level: str

    @property
    def overlay_url(self) -> str:
        return f"http://{self.overlay_host}:{self.overlay_port}/overlay"


def load_settings() -> Settings:
    load_dotenv(BASE_DIR / ".env")

    return Settings(
        tikfinity_ws_url=os.getenv("TIKFINITY_WS_URL", "ws://127.0.0.1:21213/"),
        lmstudio_base_url=os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/"),
        lmstudio_model=os.getenv("LMSTUDIO_MODEL", "local-model"),
        lmstudio_timeout_seconds=_int("LMSTUDIO_TIMEOUT_SECONDS", 45),
        lmstudio_temperature=_float("LMSTUDIO_TEMPERATURE", 0.8),
        lmstudio_max_tokens=_int("LMSTUDIO_MAX_TOKENS", 120),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL", ""),
        discord_log_accepted=_bool("DISCORD_LOG_ACCEPTED", True),
        discord_log_blocked=_bool("DISCORD_LOG_BLOCKED", True),
        discord_log_replies=_bool("DISCORD_LOG_REPLIES", True),
        overlay_host=os.getenv("OVERLAY_HOST", "127.0.0.1"),
        overlay_port=_int("OVERLAY_PORT", 8787),
        overlay_tts_enabled=_bool("OVERLAY_TTS_ENABLED", False),
        command_prefix=os.getenv("COMMAND_PREFIX", "!"),
        user_cooldown_seconds=_int("USER_COOLDOWN_SECONDS", 20),
        global_cooldown_seconds=_int("GLOBAL_COOLDOWN_SECONDS", 2),
        queue_limit=_int("QUEUE_LIMIT", 10),
        max_prompt_chars=_int("MAX_PROMPT_CHARS", 180),
        max_reply_chars=_int("MAX_REPLY_CHARS", 260),
        personality_file=_path("PERSONALITY_FILE", "config/bot_personality.example.txt"),
        safety_config_file=_path("SAFETY_CONFIG_FILE", "config/safety_words.example.json"),
        pause_file=_path("PAUSE_FILE", "config/PAUSE_STREAM.txt"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )


def load_personality(settings: Settings) -> str:
    try:
        return settings.personality_file.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "Keep replies short and suitable for a public livestream."
