from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import aiohttp


LOGGER = logging.getLogger(__name__)


def _escape_mentions(text: str) -> str:
    return text.replace("@", "@\u200b")


def _trim(text: str, limit: int = 1800) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


@dataclass
class DiscordLogger:
    webhook_url: str = ""

    @property
    def enabled(self) -> bool:
        return bool(self.webhook_url.strip())

    async def send(self, title: str, body: str, level: str = "info") -> None:
        if not self.enabled:
            return

        content = f"**{title}**\n{_trim(_escape_mentions(body))}"
        payload: dict[str, Any] = {
            "username": "Tikfinity LM Studio Bot",
            "content": content,
            "allowed_mentions": {"parse": []},
        }

        try:
            timeout = aiohttp.ClientTimeout(total=12)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status >= 400:
                        LOGGER.warning("Discord webhook returned HTTP %s", response.status)
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Discord webhook failed: %s", exc)

    async def status(self, message: str) -> None:
        await self.send("Status", message)

    async def accepted(self, raw_username: str, safe_username: str, prompt: str) -> None:
        body = f"Raw user: {raw_username}\nPublic user: {safe_username}\nPrompt: {prompt}"
        await self.send("Accepted prompt", body)

    async def blocked(self, raw_username: str, reason: str, original_text: str) -> None:
        body = f"Raw user: {raw_username}\nReason: {reason}\nText: {original_text}"
        await self.send("Blocked prompt", body, level="warning")

    async def reply(self, safe_username: str, prompt: str, reply_text: str) -> None:
        body = f"Public user: {safe_username}\nPrompt: {prompt}\nReply: {reply_text}"
        await self.send("AI reply", body)

    async def error(self, message: str) -> None:
        await self.send("Error", message, level="error")
