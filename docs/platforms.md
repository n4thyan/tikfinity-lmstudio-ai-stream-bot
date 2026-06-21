# Platform setup guide

The bridge now supports three chat sources through one shared pipeline:

```text
platform chat -> adapter -> filters -> LM Studio -> OBS overlay -> Discord logs
```

## 1. TikTok via Tikfinity

Use this first if you want the original target setup.

`.env`:

```env
CHAT_PLATFORM=tiktok
TIKFINITY_WS_URL=ws://127.0.0.1:21213/
```

Debug command:

```powershell
.\scripts\start-tikfinity-debug.ps1
```

Live command:

```powershell
.\scripts\start-tiktok-live.ps1
```

Notes:

- Tikfinity must be open on the same machine as the bridge.
- The bridge only reacts to supported commands such as `!ask`, `!lore`, and `!mood`.
- Raw Tikfinity payloads are not sent straight to OBS or TTS.

## 2. YouTube Live

Use this when you want YouTube Live chat to control the same AI character.

`.env`:

```env
CHAT_PLATFORM=youtube
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_VIDEO_ID=your_live_video_id_here
YOUTUBE_LIVE_CHAT_ID=
```

You can either:

- Set `YOUTUBE_VIDEO_ID` and let the bridge discover the active chat ID.
- Set `YOUTUBE_LIVE_CHAT_ID` directly if you already know it.

Check chat ID discovery:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --test-youtube
```

Debug command:

```powershell
.\scripts\start-youtube-debug.ps1
```

Live command:

```powershell
.\scripts\start-youtube-live.ps1
```

Notes:

- The YouTube adapter uses YouTube's official API.
- It reads normal text chat messages only.
- It follows the polling interval returned by YouTube instead of repeatedly hammering the API.
- You need a valid YouTube Data API key.

## 3. Kick webhook receiver

Use this when you want Kick chat to send events into the same AI pipeline.

`.env`:

```env
CHAT_PLATFORM=kick-webhook
KICK_WEBHOOK_HOST=127.0.0.1
KICK_WEBHOOK_PORT=8790
KICK_WEBHOOK_PATH=/kick/webhook
```

Debug command:

```powershell
.\scripts\start-kick-webhook-debug.ps1
```

Local receiver URL:

```text
http://127.0.0.1:8790/kick/webhook
```

Live command:

```powershell
.\scripts\start-kick-webhook-live.ps1
```

Notes:

- For local testing, keep it bound to `127.0.0.1`.
- For real Kick webhook delivery, expose the endpoint through a tunnel or reverse proxy.
- The adapter currently reads Kick's documented `chat.message.sent` payload shape.
- Do not expose this publicly until you are ready to handle public webhook traffic properly.

## Platform switching

To switch platforms, change `CHAT_PLATFORM` in `.env` and rerun:

```powershell
.\.venv\Scripts\python.exe -m src.doctor
```

Then use the matching debug script before starting the full bridge.

Recommended order:

```text
setup doctor -> overlay test -> fake demo -> LM Studio demo -> platform debug -> platform live
```
