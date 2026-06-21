from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from aiohttp import web


LOGGER = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parents[1]
OVERLAY_DIR = BASE_DIR / "overlay"


class OverlayBroadcaster:
    def __init__(self) -> None:
        self._clients: set[asyncio.Queue[dict[str, Any]]] = set()

    def add_client(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=20)
        self._clients.add(queue)
        return queue

    def remove_client(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self._clients.discard(queue)

    async def publish(self, event: dict[str, Any]) -> None:
        stale: list[asyncio.Queue[dict[str, Any]]] = []
        for queue in self._clients:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                stale.append(queue)
        for queue in stale:
            self.remove_client(queue)


async def _serve_overlay(_: web.Request) -> web.FileResponse:
    return web.FileResponse(OVERLAY_DIR / "index.html")


async def _events(request: web.Request) -> web.StreamResponse:
    broadcaster: OverlayBroadcaster = request.app["broadcaster"]
    queue = broadcaster.add_client()

    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )
    await response.prepare(request)

    try:
        await response.write(b": connected\n\n")
        while True:
            event = await queue.get()
            payload = json.dumps(event, ensure_ascii=False)
            await response.write(f"data: {payload}\n\n".encode("utf-8"))
    except (asyncio.CancelledError, ConnectionResetError):
        raise
    except Exception as exc:  # noqa: BLE001
        LOGGER.debug("Overlay SSE client disconnected: %s", exc)
    finally:
        broadcaster.remove_client(queue)

    return response


def create_app(broadcaster: OverlayBroadcaster, tts_enabled: bool = False) -> web.Application:
    app = web.Application()
    app["broadcaster"] = broadcaster
    app["tts_enabled"] = tts_enabled
    app.router.add_get("/overlay", _serve_overlay)
    app.router.add_get("/events", _events)
    app.router.add_static("/static", OVERLAY_DIR, show_index=False)
    return app


async def start_overlay_server(host: str, port: int, broadcaster: OverlayBroadcaster, tts_enabled: bool) -> web.AppRunner:
    app = create_app(broadcaster, tts_enabled=tts_enabled)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    return runner
