from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import AsyncIterator, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode

import aiohttp
from aiohttp import web
import websockets

LOGGER = logging.getLogger(__name__)
_KICK_EMOTE_RE = re.compile(r"\[emote:\d+:[^\]]+\]")


@dataclass(frozen=True)
class ChatMessage:
    """Normalised chat message from any supported livestream platform."""

    platform: str
    raw_username: str
    message: str
    raw: dict[str, Any] = field(default_factory=dict)


def extract_tikfinity_message(payload: dict[str, Any]) -> ChatMessage | None:
    """Extract a chat username/message pair from common Tikfinity payload shapes."""
    roots = list(_iter_dicts(payload))
    event_name = _find_first_string(roots, ("event", "type", "eventName", "name"))
    if event_name:
        event_name_lower = event_name.lower()
        if any(word in event_name_lower for word in ("gift", "like", "follow", "share", "join", "subscribe")):
            return None

    message_keys = ("comment", "commentText", "message", "msg", "text", "content")
    user_keys = ("uniqueId", "nickname", "username", "displayName", "userId", "id")

    message = _find_first_string(roots, message_keys)
    username = _find_username(roots, user_keys)

    if not message:
        return None
    return ChatMessage("tiktok", username or "unknown_viewer", message, payload)


def extract_youtube_message(item: dict[str, Any]) -> ChatMessage | None:
    """Extract a normal chat message from a YouTube liveChatMessages item."""
    snippet = item.get("snippet") if isinstance(item, dict) else None
    author = item.get("authorDetails") if isinstance(item, dict) else None
    if not isinstance(snippet, dict) or not isinstance(author, dict):
        return None

    message_type = str(snippet.get("type", "")).strip()
    if message_type and message_type != "textMessageEvent":
        return None

    message = snippet.get("displayMessage")
    if not isinstance(message, str) or not message.strip():
        details = snippet.get("textMessageDetails")
        if isinstance(details, dict):
            message = details.get("messageText")
    if not isinstance(message, str) or not message.strip():
        return None

    username = author.get("displayName") or author.get("channelId") or "youtube_viewer"
    return ChatMessage("youtube", str(username), message.strip(), item)


def extract_kick_webhook_message(payload: dict[str, Any], headers: Mapping[str, str] | None = None) -> ChatMessage | None:
    """Extract a chat message from Kick's documented chat.message.sent webhook payload."""
    event_type = ""
    if headers:
        event_type = str(headers.get("Kick-Event-Type") or headers.get("kick-event-type") or "").strip().lower()
    if event_type and event_type != "chat.message.sent":
        return None

    sender = payload.get("sender") if isinstance(payload, dict) else None
    if not isinstance(sender, dict):
        return None
    username = sender.get("username") or sender.get("channel_slug") or "kick_viewer"
    content = payload.get("content")
    if not isinstance(content, str) or not content.strip():
        return None

    cleaned = _KICK_EMOTE_RE.sub("", content).strip()
    if not cleaned:
        return None
    return ChatMessage("kick", str(username), cleaned, payload)


class TikfinityChatSource:
    def __init__(self, websocket_url: str) -> None:
        self.websocket_url = websocket_url

    async def messages(self) -> AsyncIterator[ChatMessage]:
        while True:
            try:
                LOGGER.info("Connecting to Tikfinity WebSocket: %s", self.websocket_url)
                async with websockets.connect(self.websocket_url, ping_interval=20) as websocket:
                    async for raw_payload in websocket:
                        text_payload = raw_payload.decode("utf-8", errors="replace") if isinstance(raw_payload, bytes) else raw_payload
                        try:
                            payload = json.loads(text_payload)
                        except json.JSONDecodeError:
                            LOGGER.debug("Ignored non-JSON Tikfinity payload: %r", text_payload)
                            continue
                        message = extract_tikfinity_message(payload)
                        if message:
                            yield message
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("Tikfinity connection problem: %s", exc)
                await asyncio.sleep(5)


class YouTubeLiveChatSource:
    def __init__(
        self,
        *,
        api_key: str,
        live_chat_id: str = "",
        video_id: str = "",
        poll_floor_seconds: float = 2.0,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self.api_key = api_key
        self.live_chat_id = live_chat_id
        self.video_id = video_id
        self.poll_floor_seconds = poll_floor_seconds
        self._external_session = session

    async def messages(self) -> AsyncIterator[ChatMessage]:
        if not self.api_key:
            raise RuntimeError("YOUTUBE_API_KEY is required for the YouTube adapter.")

        async with self._session_context() as session:
            live_chat_id = self.live_chat_id or await self.resolve_live_chat_id(session)
            if not live_chat_id:
                raise RuntimeError("No YouTube live chat ID found. Set YOUTUBE_LIVE_CHAT_ID or YOUTUBE_VIDEO_ID for an active live stream.")

            page_token = ""
            while True:
                params = {
                    "part": "snippet,authorDetails",
                    "liveChatId": live_chat_id,
                    "maxResults": "200",
                    "key": self.api_key,
                }
                if page_token:
                    params["pageToken"] = page_token
                data = await self._get_json(session, "https://www.googleapis.com/youtube/v3/liveChat/messages", params)
                for item in data.get("items", []):
                    if isinstance(item, dict):
                        message = extract_youtube_message(item)
                        if message:
                            yield message
                page_token = str(data.get("nextPageToken") or "")
                wait_ms = data.get("pollingIntervalMillis", int(self.poll_floor_seconds * 1000))
                try:
                    wait_seconds = max(self.poll_floor_seconds, int(wait_ms) / 1000)
                except (TypeError, ValueError):
                    wait_seconds = self.poll_floor_seconds
                await asyncio.sleep(wait_seconds)

    async def resolve_live_chat_id(self, session: aiohttp.ClientSession | None = None) -> str:
        if self.live_chat_id:
            return self.live_chat_id
        if not self.video_id:
            return ""

        if session is not None:
            return await self._resolve_live_chat_id_with_session(session)
        async with self._session_context() as owned_session:
            return await self._resolve_live_chat_id_with_session(owned_session)

    async def _resolve_live_chat_id_with_session(self, session: aiohttp.ClientSession) -> str:
        params = {
            "part": "liveStreamingDetails",
            "id": self.video_id,
            "key": self.api_key,
        }
        data = await self._get_json(session, "https://www.googleapis.com/youtube/v3/videos", params)
        for item in data.get("items", []):
            details = item.get("liveStreamingDetails") if isinstance(item, dict) else None
            if isinstance(details, dict):
                active_chat_id = details.get("activeLiveChatId")
                if isinstance(active_chat_id, str) and active_chat_id.strip():
                    return active_chat_id.strip()
        return ""

    async def _get_json(self, session: aiohttp.ClientSession, url: str, params: dict[str, str]) -> dict[str, Any]:
        request_url = f"{url}?{urlencode(params)}"
        async with session.get(request_url) as response:
            text = await response.text()
            if response.status >= 400:
                raise RuntimeError(f"YouTube API error {response.status}: {text[:300]}")
            data = json.loads(text)
            if not isinstance(data, dict):
                raise RuntimeError("YouTube API returned an unexpected response shape.")
            return data

    def _session_context(self):
        if self._external_session is not None:
            return _BorrowedSession(self._external_session)
        return aiohttp.ClientSession()


class KickWebhookChatSource:
    def __init__(self, *, host: str, port: int, path: str) -> None:
        self.host = host
        self.port = port
        self.path = path if path.startswith("/") else f"/{path}"
        self.queue: asyncio.Queue[ChatMessage] = asyncio.Queue()

    async def messages(self) -> AsyncIterator[ChatMessage]:
        app = web.Application()
        app.router.add_get("/health", self._health)
        app.router.add_post(self.path, self._handle_webhook)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        LOGGER.info("Kick webhook receiver listening on http://%s:%s%s", self.host, self.port, self.path)
        try:
            while True:
                yield await self.queue.get()
        finally:
            await runner.cleanup()

    async def _health(self, request: web.Request) -> web.Response:
        return web.json_response({"ok": True, "source": "kick-webhook"})

    async def _handle_webhook(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
        except Exception:  # noqa: BLE001
            return web.json_response({"ok": False, "error": "invalid_json"}, status=400)
        if not isinstance(payload, dict):
            return web.json_response({"ok": False, "error": "invalid_payload"}, status=400)
        message = extract_kick_webhook_message(payload, request.headers)
        if message:
            await self.queue.put(message)
        return web.json_response({"ok": True})


class _BorrowedSession:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def __aenter__(self) -> aiohttp.ClientSession:
        return self.session

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


def _iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_dicts(child)


def _find_first_string(roots: Iterable[dict[str, Any]], keys: tuple[str, ...]) -> str | None:
    for root in roots:
        for key in keys:
            value = root.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _find_username(roots: Iterable[dict[str, Any]], user_keys: tuple[str, ...]) -> str | None:
    for root in roots:
        user_obj = root.get("user")
        if isinstance(user_obj, dict):
            for key in user_keys:
                value = user_obj.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        for key in user_keys:
            value = root.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None
