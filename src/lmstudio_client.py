from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp


class LMStudioError(RuntimeError):
    """Raised when the local LM Studio server cannot return a usable reply."""


@dataclass(frozen=True)
class LMStudioClient:
    base_url: str
    model: str
    timeout_seconds: int = 45
    temperature: float = 0.8
    max_tokens: int = 120

    @property
    def chat_completions_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/chat/completions"

    @property
    def models_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/models"

    async def chat(self, instructions: str, viewer_message: str) -> str:
        """Generate one short in-character reply using LM Studio's local server."""
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": instructions},
                {"role": "user", "content": viewer_message},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        data = await self._post_json(self.chat_completions_url, payload)
        return _extract_reply(data)

    async def list_models(self) -> list[str]:
        """Return model IDs reported by the local LM Studio server."""
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.models_url) as response:
                    body = await response.text()
                    if response.status >= 400:
                        raise LMStudioError(f"LM Studio returned HTTP {response.status}: {body[:300]}")
                    data = await response.json(content_type=None)
        except aiohttp.ClientError as exc:
            raise LMStudioError(f"Could not connect to LM Studio at {self.base_url}: {exc}") from exc

        models = data.get("data") if isinstance(data, dict) else None
        if not isinstance(models, list):
            return []
        ids: list[str] = []
        for item in models:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                ids.append(item["id"])
        return ids

    async def _post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    body = await response.text()
                    if response.status >= 400:
                        raise LMStudioError(f"LM Studio returned HTTP {response.status}: {body[:300]}")
                    try:
                        data = await response.json(content_type=None)
                    except Exception as exc:  # noqa: BLE001
                        raise LMStudioError(f"LM Studio returned non-JSON data: {body[:300]}") from exc
        except aiohttp.ClientError as exc:
            raise LMStudioError(f"Could not connect to LM Studio at {self.base_url}: {exc}") from exc

        if not isinstance(data, dict):
            raise LMStudioError("LM Studio returned an unexpected response shape.")
        return data


def _extract_reply(data: dict[str, Any]) -> str:
    """Extract assistant text from an OpenAI-compatible chat response."""
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LMStudioError("LM Studio response did not include any choices.")

    first = choices[0]
    if not isinstance(first, dict):
        raise LMStudioError("LM Studio response choice had an unexpected shape.")

    message = first.get("message")
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()

    legacy_text = first.get("text")
    if isinstance(legacy_text, str) and legacy_text.strip():
        return legacy_text.strip()

    raise LMStudioError("LM Studio response did not include reply text.")
