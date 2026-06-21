# PotatoBrain Live AI Stream Bot

A local AI livestream bot that connects live chat commands to a small LM Studio model and displays the replies in OBS through a terminal-style browser overlay.

The project is built for practical stream automation: chat input, filtering, cooldowns, local LLM replies, OBS display output, optional browser text-to-speech, Discord webhook logging and an emergency pause control.

## Project status

**Portfolio v1: working local release**

Validated setup path:

```text
Windows PC
  -> LM Studio local server
  -> Python bridge
  -> message filtering and command handling
  -> local LLM reply
  -> OBS browser overlay
  -> browser TTS
  -> Discord webhook logging
```

TikTok/Tikfinity path:

```text
TikTok LIVE chat
  -> Tikfinity local Event API / WebSocket
  -> Python bridge
  -> PotatoBrain reply pipeline
```

Confirmed locally:

- LM Studio local model connection
- OBS browser overlay
- browser text-to-speech
- Discord webhook logging
- local fake demo mode
- local LM Studio demo mode
- emergency pause/resume control
- Tikfinity WebSocket connection path
- automated compile and pytest checks

Longer live-stream testing still depends on the streaming PC being powerful enough to run TikTok LIVE Studio, OBS, LM Studio, Tikfinity and the bridge together. This is a working local project, not a claim of fully unattended production moderation.

## What it does

PotatoBrain is a lightweight livestream character bot. Viewers send supported commands, the bridge sanitises usernames, filters the message, applies cooldowns, sends accepted prompts to a local LM Studio model, filters the output, then shows the final reply on stream.

The project is intentionally built around local AI rather than a hosted paid API. It can run without per-request API costs, but performance depends on the local machine and model size.

## Stream flow

```text
TikTok / YouTube / Kick chat
  -> platform adapter
  -> Python bridge
  -> username sanitiser
  -> message filter and queue
  -> LM Studio local OpenAI-compatible API
  -> output filter
  -> OBS browser overlay
  -> optional browser TTS
  -> Discord webhook logs
```

Local showcase mode is also supported:

```text
manual PowerShell prompt
  -> Python bridge
  -> LM Studio local API
  -> OBS terminal overlay and TTS
```

This makes it possible to test the project, record clips or demonstrate the workflow without going live.

## Supported chat sources

| Platform | Adapter name | Status | Notes |
|---|---|---|---|
| TikTok LIVE | `tiktok` | Primary target | Uses Tikfinity's local WebSocket/Event API. |
| YouTube Live | `youtube` | Implemented | Polls YouTube Live chat through the official API. Requires a YouTube API key and live chat ID or video ID. |
| Kick | `kick-webhook` | Implemented | Runs a local webhook receiver for Kick-style event payloads. Real use needs a tunnel or reverse proxy. |

Set the active platform in `.env`:

```env
CHAT_PLATFORM=tiktok
```

Allowed values:

```text
tiktok
youtube
kick-webhook
```

## Main features

- Multi-platform chat adapter layer
- Tikfinity WebSocket listener for TikTok LIVE
- YouTube Live chat polling adapter
- Kick webhook receiver adapter
- `!ask`, `!roast`, `!lore`, `!mood`, `!reset`, `!help` and `!status` commands
- Separate username sanitisation layer
- Input filtering and AI output filtering hooks
- Per-user cooldowns across platforms
- Queue limit to stop the model being overwhelmed
- Local emergency pause file using `config/PAUSE_STREAM.txt`
- LM Studio client using the local OpenAI-compatible API
- Terminal/CMD-style OBS browser overlay using Server-Sent Events
- Optional browser text-to-speech in the overlay
- Discord webhook logging for accepted prompts, blocked prompts, replies, status and errors
- `py -m src.doctor` setup report for first-run troubleshooting
- Local fake demo mode without LM Studio
- Local LM Studio demo mode without a live platform
- Platform debug modes for Tikfinity, YouTube and Kick
- Windows setup and run helper scripts
- `.env.example` config so secrets are not committed
- Basic pytest coverage for filters, command parsing, platform extraction and LM Studio response parsing
- GitHub Actions workflow for compile and test checks

## Why this is a portfolio project

This project demonstrates practical AI-assisted engineering rather than a simple chatbot wrapper. It combines local AI, livestream tooling, event-driven message handling, frontend overlay work, platform adapters, basic safety controls and operational tooling.

It shows:

- Local LLM integration through LM Studio
- OpenAI-compatible API usage without depending on a hosted API
- Async Python service design
- OBS browser overlay development
- WebSocket and webhook-based chat ingestion
- Event queue and cooldown handling
- Input and output filtering
- Discord webhook observability
- Windows-first setup scripting
- Real-world testing under hardware limits

## What this is not

This is not a moderation replacement. Raw chat, raw usernames and raw model output should not be treated as safe for public display without filtering and review.

It is also not a high-end AI agent. It is intentionally designed around small local models and a simple stream character. The goal is a practical, lightweight interaction loop that can be tested on a modest Windows setup.

This project is not affiliated with TikTok, YouTube, Kick, Tikfinity, LM Studio or OBS. It is an independent local integration project using user-configured tools and APIs.

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

12. Debug your chosen platform when needed:

```powershell
# TikTok / Tikfinity
.\scripts\start-tikfinity-debug.ps1

# YouTube Live
.\scripts\start-youtube-debug.ps1

# Kick webhook receiver
.\scripts\start-kick-webhook-debug.ps1
```

13. Run the full bridge:

```powershell
# Uses CHAT_PLATFORM from .env
.\scripts\start-live-bridge.ps1

# Or force a platform for this run
.\scripts\start-tiktok-live.ps1
.\scripts\start-youtube-live.ps1
.\scripts\start-kick-webhook-live.ps1
```

For the full setup flow, see [`docs/setup-and-test.md`](docs/setup-and-test.md).

## TikTok / Tikfinity setup

Use this `.env` configuration:

```env
CHAT_PLATFORM=tiktok
TIKFINITY_WS_URL=ws://127.0.0.1:21213/
```

Recommended live order:

```text
1. Start LM Studio local server and load the model.
2. Open OBS and check the overlay source.
3. Open TikTok LIVE Studio and prepare the scene.
4. Go live from TikTok LIVE Studio.
5. Open Tikfinity and connect it to the active TikTok LIVE.
6. Start the bridge with scripts/start-live-bridge.ps1.
```

Tikfinity is used because it provides a practical local way to capture TikTok LIVE events without writing a full TikTok chat client from scratch.

## Safety and control design

The intended rule is soft chaos with hard account-protection limits.

The project keeps two names internally:

```text
raw_username  = real platform username, used only for cooldowns and private Discord logs
safe_username = cleaned public name, used for LM Studio, OBS and TTS
```

Safety controls include:

- username sanitisation before public display
- prompt filtering before the model sees chat text
- output filtering before OBS/TTS
- cooldowns and queue limits
- local pause/resume scripts
- private Discord logs for troubleshooting and review

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
!mood angry
!mood dramatic
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

## Known limitations

- Live performance depends heavily on the local PC.
- TikTok LIVE Studio, OBS, Tikfinity, LM Studio and the bridge can be heavy together on weak hardware.
- Small local models can give strange or low-quality replies.
- Longer supervised livestream testing is still recommended before using it for many hours.
- TikTok integration depends on Tikfinity being connected to the active live session.
- YouTube and Kick support are implemented as adapters, but the main tested path is TikTok/Tikfinity.

## Portfolio summary

PotatoBrain Live AI Stream Bot is a local AI livestream automation project. It connects chat events to a small LM Studio model, pushes replies to an OBS browser overlay, optionally speaks them with browser TTS and logs activity to Discord. It demonstrates local LLM integration, async Python, event-driven stream tooling, safety controls, setup scripting, documentation and real-world testing under hardware constraints.

For a website-ready project write-up, see [`docs/portfolio-case-study.md`](docs/portfolio-case-study.md).
