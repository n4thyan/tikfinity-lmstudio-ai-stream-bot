# Multi-Platform LM Studio AI Stream Bot

A local livestream chat experiment using LM Studio, OBS, Discord webhooks, and platform adapters for TikTok/Tikfinity, YouTube Live, and Kick webhooks.

The aim is to let livestream chat interact with a small local LLM character while keeping the stream manageable through username sanitisation, message filtering, output filtering, cooldowns, queue limits, a local pause file, and Discord logging.

## What this is

This project is a first-pass MVP for a 24/7 style livestream where chat can talk to a local potato AI character.

Stream flow:

```text
TikTok / YouTube / Kick chat
  -> platform adapter
  -> Python bridge
  -> username sanitiser
  -> message filter and queue
  -> LM Studio local API
  -> output filter
  -> OBS browser overlay / optional browser TTS
  -> Discord webhook logs
```

You can also run it in local showcase mode without any platform connected:

```text
manual demo prompts
  -> Python bridge
  -> LM Studio local API
  -> terminal-style OBS overlay
```

This is useful for testing, recording clips, tuning the character, or building the stream scene before connecting real chat.

## Supported chat sources

| Platform | Adapter name | Status | Notes |
|---|---|---|---|
| TikTok LIVE | `tiktok` | First target | Uses Tikfinity's local WebSocket. |
| YouTube Live | `youtube` | Added | Polls YouTube Live chat through the official API. Requires a YouTube API key and live chat ID or video ID. |
| Kick | `kick-webhook` | Added | Runs a local webhook receiver for Kick's documented chat event payload. For real use, expose it with a tunnel or reverse proxy. |

Set the platform in `.env`:

```env
CHAT_PLATFORM=tiktok
```

Allowed values:

```text
tiktok
youtube
kick-webhook
```

## Current MVP features

- Multi-platform chat source adapter layer
- Tikfinity WebSocket listener
- YouTube Live chat polling adapter
- Kick chat webhook receiver adapter
- `!ask`, `!roast`, `!lore`, `!mood`, `!reset`, `!help`, and `!status` command parsing
- Separate username sanitising layer
- Message and AI-output filtering hooks
- Per-user cooldowns across platforms
- Prompt queue limits
- Local pause file support using `config/PAUSE_STREAM.txt`
- Working LM Studio client using the local OpenAI-compatible API
- `py -m src.doctor` setup report for first-run troubleshooting
- `--test-lmstudio` health check for local model testing
- `--test-youtube` health check for YouTube live chat ID discovery
- `--test-overlay` mode for testing OBS without a chat platform or LM Studio
- `--demo --fake-llm` mode for testing the bridge without LM Studio
- Local showcase/demo mode with real LM Studio replies
- Platform debug modes for Tikfinity, YouTube, and Kick webhook payloads
- Local OBS terminal-style browser overlay using Server-Sent Events
- Optional browser text-to-speech in the overlay
- Discord webhook logging for accepted, blocked, error, and status events
- Basic pytest coverage for filters, command parsing, platform extraction, and LM Studio response parsing
- GitHub Actions workflow for compile and test checks
- Windows setup and run helper scripts
- `.env.example` config so secrets are not committed

## What this is not

This is not a moderation replacement and it should not be treated as fully unattended production software yet. The stream can be chaotic, but raw chat and raw usernames should never go straight to OBS or TTS.

## Quick start

1. Install Python 3.11+.
2. Install LM Studio.
3. Download a small local model in LM Studio.
4. Start the LM Studio local server from the Developer tab.
5. Clone the repo and enter the folder.

Windows helper:

```powershell
.\scripts\windows-setup.ps1
```

Manual install:

```powershell
copy .env.example .env
py -m pip install -r requirements.txt
```

6. Edit `.env` and choose a platform:

```env
CHAT_PLATFORM=tiktok
```

7. Run the setup doctor:

```powershell
.\.venv\Scripts\python.exe -m src.doctor
```

8. Test the OBS overlay:

```powershell
.\scripts\start-overlay-test.ps1
```

Add this as an OBS Browser Source:

```text
http://127.0.0.1:8787/overlay
```

9. Test the bridge without LM Studio:

```powershell
.\scripts\start-fake-demo.ps1
```

10. Test LM Studio:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --test-lmstudio
```

11. Run a local showcase/demo using LM Studio:

```powershell
.\scripts\start-lmstudio-demo.ps1
```

This lets you type prompts manually in PowerShell and see the real local model reply in OBS without Tikfinity, YouTube, or Kick connected.

12. Debug your chosen platform:

```powershell
# TikTok / Tikfinity
.\scripts\start-tikfinity-debug.ps1

# YouTube Live
.\scripts\start-youtube-debug.ps1

# Kick webhook receiver
.\scripts\start-kick-webhook-debug.ps1
```

13. When the debug output parses correctly, run the full bridge:

```powershell
# Uses CHAT_PLATFORM from .env
.\scripts\start-live-bridge.ps1

# Or force a platform for this run
.\scripts\start-tiktok-live.ps1
.\scripts\start-youtube-live.ps1
.\scripts\start-kick-webhook-live.ps1
```

For the full setup flow, see [`docs/setup-and-test.md`](docs/setup-and-test.md).

## Local showcase mode

For testing or clip recording without live chat, run:

```powershell
.\scripts\start-lmstudio-demo.ps1
```

Then type commands into PowerShell:

```text
!ask are you alive
!mood confused
!ask why are you trapped in this computer
!status
```

This mode is the safest place to tune:

- model choice
- personality prompt
- overlay size and placement
- response length
- filters
- Discord logging
- CPU/RAM load

## Platform config

### TikTok / Tikfinity

```env
CHAT_PLATFORM=tiktok
TIKFINITY_WS_URL=ws://127.0.0.1:21213/
```

Use Tikfinity first because it is still the quickest local route for TikTok LIVE chat.

### YouTube Live

```env
CHAT_PLATFORM=youtube
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_VIDEO_ID=your_live_video_id_here
# or set this directly if you already know it:
YOUTUBE_LIVE_CHAT_ID=
```

The bridge can resolve an active chat ID from `YOUTUBE_VIDEO_ID` by calling YouTube's `videos.list` endpoint with `part=liveStreamingDetails`, then polls `liveChatMessages.list`.

Useful checks:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --test-youtube
.\scripts\start-youtube-debug.ps1
```

### Kick webhook

```env
CHAT_PLATFORM=kick-webhook
KICK_WEBHOOK_HOST=127.0.0.1
KICK_WEBHOOK_PORT=8790
KICK_WEBHOOK_PATH=/kick/webhook
```

Local debug URL:

```text
http://127.0.0.1:8790/kick/webhook
```

For a real Kick app webhook, expose that endpoint with a tunnel or reverse proxy and point Kick's event subscription at the public URL. Keep it local-only until you are ready to handle public traffic.

## Local pause control

The bridge checks for this file:

```text
config/PAUSE_STREAM.txt
```

Create it to pause new chat replies:

```powershell
.\scripts\pause-bridge.ps1
```

Remove it to resume:

```powershell
.\scripts\resume-bridge.ps1
```

While paused, `!help` and `!status` still work so the overlay can show that the bridge is paused.

## LM Studio config

The default `.env.example` assumes LM Studio is running locally on port `1234`:

```env
LMSTUDIO_BASE_URL=http://127.0.0.1:1234/v1
LMSTUDIO_MODEL=local-model
LMSTUDIO_TIMEOUT_SECONDS=45
LMSTUDIO_TEMPERATURE=0.8
LMSTUDIO_MAX_TOKENS=120
```

Set `LMSTUDIO_MODEL` to the model ID shown by LM Studio. You can check visible model IDs with:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --test-lmstudio
```

## Personality prompt

The stream character prompt lives in:

```text
config/bot_personality.example.txt
```

Edit this file to change PotatoBrain's style. Keeping the prompt in the project is better than relying on LM Studio global settings because it stays versioned with the stream setup.

## Discord logging

Discord webhook logging is optional. It is useful for checking prompts, blocked messages, model replies, and errors from another screen or your phone.

Setup guide:

```text
docs/discord-webhook.md
```

The webhook URL should only be placed in your local `.env` file. Never commit it to GitHub.

## Recommended small models

Start with something in the 350M to 1.5B range. The bot is meant to be quick and funny, not academically clever.

Good first targets:

- 350M to 700M model for very weak PCs
- 1B to 1.5B model for better replies
- 2B to 3B only if OBS and the platform adapter still run smoothly

## Safety design

The intended rule is soft chaos with hard account-protection limits.

The system should allow normal stream banter, silly commands, mood changes, and fictional AI character jokes, while filtering platform-risk content, private personal data, spam walls, and obvious stream-bait attempts.

## Username handling

The project keeps two names internally:

```text
raw_username  = real platform username, used only for cooldowns and private Discord logs
safe_username = cleaned public name, used for LM Studio, OBS, and TTS
```

Safe usernames can be read on stream. Risky usernames are cleaned or replaced with a generic viewer label.

The browser TTS currently speaks the AI reply only, not the raw username or raw prompt.

## Useful chat commands

```text
!help
!status
!ask <message>
!roast <topic>
!lore
!mood normal
!mood confused
!reset
```

## Useful local commands

```powershell
# Setup helper on Windows
.\scripts\windows-setup.ps1

# Setup report
.\.venv\Scripts\python.exe -m src.doctor

# Overlay only, no platform, no LM Studio
.\scripts\start-overlay-test.ps1

# Local demo with built-in fake replies
.\scripts\start-fake-demo.ps1

# Check LM Studio and print visible model IDs
.\.venv\Scripts\python.exe -m src.bridge --test-lmstudio

# Local demo with LM Studio
.\scripts\start-lmstudio-demo.ps1

# Platform debug modes
.\scripts\start-tikfinity-debug.ps1
.\scripts\start-youtube-debug.ps1
.\scripts\start-kick-webhook-debug.ps1

# Full runs
.\scripts\start-live-bridge.ps1
.\scripts\start-tiktok-live.ps1
.\scripts\start-youtube-live.ps1
.\scripts\start-kick-webhook-live.ps1

# Pause / resume chat replies
.\scripts\pause-bridge.ps1
.\scripts\resume-bridge.ps1
```

## Development checks

Install dev dependencies:

```powershell
py -m pip install -r requirements-dev.txt
```

Compile source:

```powershell
py -m compileall src
```

Run tests:

```powershell
py -m pytest
```

GitHub Actions also runs these checks on pushes and pull requests.

## Repository status

This is still an early MVP, but the setup/test path is now split into safe stages:

```text
doctor -> overlay test -> fake bridge demo -> LM Studio test -> LM Studio demo -> platform debug -> full run
```

The main tested local path is now:

```text
LM Studio -> bridge -> filters -> terminal OBS overlay
```

The next important tasks are live-platform payload testing, Discord logging test, longer runtime testing, TTS behaviour, filter strictness, and stream event support.
