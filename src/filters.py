from __future__ import annotations

import hashlib
import json
import re
import string
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_USERNAME_CHARS = set(string.ascii_letters + string.digits + "_-. ")

PERSONAL_DATA_PATTERNS = [
    re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b", re.IGNORECASE),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"\b(?:\+?44\s?7\d{3}|07\d{3})\s?\d{3}\s?\d{3}\b"),
    re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b", re.IGNORECASE),
]

SPAM_PATTERN = re.compile(r"(.)\1{8,}", re.IGNORECASE)
LINK_PATTERN = re.compile(r"https?://|www\.", re.IGNORECASE)

LEET_TABLE = str.maketrans(
    {
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "@": "a",
        "$": "s",
        "!": "i",
    }
)


@dataclass(frozen=True)
class SafetyConfig:
    blocked_terms: tuple[str, ...]
    soft_replace_terms: dict[str, str]
    username_blocked_terms: tuple[str, ...]
    username_soft_replace_terms: dict[str, str]

    @classmethod
    def load(cls, path: Path) -> "SafetyConfig":
        if not path.exists():
            return cls((), {}, (), {})
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            blocked_terms=tuple(str(x).lower() for x in data.get("blocked_terms", [])),
            soft_replace_terms={str(k).lower(): str(v) for k, v in data.get("soft_replace_terms", {}).items()},
            username_blocked_terms=tuple(str(x).lower() for x in data.get("username_blocked_terms", [])),
            username_soft_replace_terms={
                str(k).lower(): str(v) for k, v in data.get("username_soft_replace_terms", {}).items()
            },
        )


@dataclass(frozen=True)
class FilterResult:
    allowed: bool
    text: str
    reason: str = "ok"


def _normalise_for_checking(text: str) -> str:
    lowered = text.lower().translate(LEET_TABLE)
    lowered = re.sub(r"[\W_]+", "", lowered)
    return lowered


def _stable_viewer_label(raw_username: str) -> str:
    digest = hashlib.sha1(raw_username.encode("utf-8", errors="ignore")).hexdigest()
    number = int(digest[:6], 16) % 999 + 1
    return f"Viewer {number}"


def _apply_soft_replacements(text: str, replacements: dict[str, str]) -> str:
    cleaned = text
    for term, replacement in replacements.items():
        cleaned = re.sub(re.escape(term), replacement, cleaned, flags=re.IGNORECASE)
    return cleaned


def filter_chat_text(text: str, config: SafetyConfig, max_chars: int) -> FilterResult:
    original = " ".join(text.strip().split())
    if not original:
        return FilterResult(False, "", "empty")
    if len(original) > max_chars:
        return FilterResult(False, "", "too long")
    if SPAM_PATTERN.search(original):
        return FilterResult(False, "", "spam-like repetition")
    if LINK_PATTERN.search(original):
        return FilterResult(False, "", "link blocked")
    for pattern in PERSONAL_DATA_PATTERNS:
        if pattern.search(original):
            return FilterResult(False, "", "possible personal data")

    checkable = _normalise_for_checking(original)
    for term in config.blocked_terms:
        if term and _normalise_for_checking(term) in checkable:
            return FilterResult(False, "", "blocked term")

    return FilterResult(True, _apply_soft_replacements(original, config.soft_replace_terms))


def filter_ai_output(text: str, config: SafetyConfig, max_chars: int) -> FilterResult:
    original = " ".join(text.strip().split())
    if not original:
        return FilterResult(False, "", "empty model reply")
    if len(original) > max_chars:
        original = original[: max_chars - 3].rstrip() + "..."

    for pattern in PERSONAL_DATA_PATTERNS:
        if pattern.search(original):
            return FilterResult(False, "", "reply contained possible personal data")

    checkable = _normalise_for_checking(original)
    for term in config.blocked_terms:
        if term and _normalise_for_checking(term) in checkable:
            return FilterResult(False, "", "reply contained blocked term")

    return FilterResult(True, _apply_soft_replacements(original, config.soft_replace_terms))


def sanitise_username(raw_username: str, config: SafetyConfig) -> FilterResult:
    raw = (raw_username or "").strip().lstrip("@").strip()
    if not raw:
        return FilterResult(True, _stable_viewer_label("unknown"), "fallback")

    compact = _normalise_for_checking(raw)
    for term in config.username_blocked_terms:
        if term and _normalise_for_checking(term) in compact:
            return FilterResult(True, _stable_viewer_label(raw), "username replaced")

    cleaned = "".join(char for char in raw if char in ALLOWED_USERNAME_CHARS).strip()
    cleaned = _apply_soft_replacements(cleaned, config.username_soft_replace_terms)
    cleaned = " ".join(cleaned.split())

    if not cleaned:
        return FilterResult(True, _stable_viewer_label(raw), "username replaced")
    if len(cleaned) > 24:
        cleaned = cleaned[:24].rstrip()

    return FilterResult(True, cleaned, "ok")
