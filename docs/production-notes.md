# Production notes

This project is currently designed for local staged testing first.

## Do not expose raw chat directly

Keep this rule throughout the project:

```text
raw platform chat -> adapter -> sanitiser/filter -> bridge -> overlay/TTS
```

Raw platform usernames and raw messages should not be sent straight to OBS or TTS.

## Kick webhook receiver

The Kick webhook receiver is useful for local/debug testing of `chat.message.sent` payloads.

Before exposing it publicly:

- Add Kick webhook signature verification.
- Put the receiver behind HTTPS.
- Use a tunnel or reverse proxy only after local parsing is confirmed.
- Keep the local pause file available.
- Keep Discord error logging enabled.

Until then, keep this default local-only setting:

```env
KICK_WEBHOOK_HOST=127.0.0.1
```

## YouTube API

The YouTube adapter requires a valid API key and either:

- `YOUTUBE_LIVE_CHAT_ID`, or
- `YOUTUBE_VIDEO_ID` for an active livestream so the bridge can discover the chat ID.

Watch quota usage during long tests.

## First public test

Use conservative values:

```env
OVERLAY_TTS_ENABLED=false
USER_COOLDOWN_SECONDS=30
GLOBAL_COOLDOWN_SECONDS=3
QUEUE_LIMIT=5
MAX_PROMPT_CHARS=160
MAX_REPLY_CHARS=220
```

Only enable TTS after text-only mode behaves properly.
