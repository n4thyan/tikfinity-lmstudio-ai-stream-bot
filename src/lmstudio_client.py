from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LMStudioClient:
    base_url: str
    model: str

    async def chat(self, instructions: str, viewer_message: str) -> str:
        return "LM Studio client placeholder."
