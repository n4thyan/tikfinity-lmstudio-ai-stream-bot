# TikTok setup notes

TikTok support currently goes through Tikfinity.

## Required `.env` values

```env
CHAT_PLATFORM=tiktok
TIKFINITY_WS_URL=ws://127.0.0.1:21213/
```

## Test commands

Print parsed Tikfinity chat only:

```powershell
.\scripts\start-tikfinity-debug.ps1
```

Run live bridge with TikTok forced:

```powershell
.\scripts\start-tiktok-live.ps1
```

## Notes

- Tikfinity must be open and connected to your TikTok LIVE session.
- The bridge does not process raw TikTok chat directly. It receives Tikfinity payloads, extracts chat messages, then runs the usual sanitising/filtering pipeline.
- Start with TTS disabled until text-only mode is stable.
