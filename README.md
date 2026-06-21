# PotatoBrain Live AI Stream Bot

A working local livestream AI bot that lets TikTok, YouTube, or Kick chat send commands to a small LM Studio model and display the replies in OBS with a terminal-style overlay, optional browser text-to-speech, Discord logging, filtering, cooldowns, and emergency pause control.

This is the first completed portfolio project in this repo. It was built as a practical stream automation project, not just a code demo.

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

The local LM Studio, OBS overlay, TTS, Discord logging, pause/resume control, and Tikfinity WebSocket connection path have been tested. Longer unattended livestream testing still depends on the streaming PC being powerful enough to run TikTok LIVE Studio, OBS, LM Studio, Tikfinity, and the bridge at the same time.

## What it does

PotatoBrain is a small livestream character bot designed for chaotic but controlled chat interaction. Viewers can send commands, the bridge sanitises and filters input, a local LLM generates a short reply, and the result appears on stream through an OBS browser overlay.

The project is intentionally built around local AI rather than a hosted API. This means it can run without paying per request, but performance depends heavily on the machine and model size.

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

This is useful for testing, recording clips, tuning the character, or showing the project without needing to go live.

## Supported chat sources

| Platform | Adapter name | Status | Notes |
|---|---|---|---|
| TikTok LIVE | `tiktok` | Primary target | Uses Tikfinity's local WebSocket/Event API. |
| YouTube Live | `youtube` | Implemented | Polls YouTube Live chat through the official API. Requires a YouTube API key and live chat ID or video ID. |
| Kick | `kick-webhook` | Implemented | Runs a local webhook receiver for Kick chat event payloads. For real use, expose it with a tunnel or reverse proxy. |

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
- `!ask`, `!roast`, `!lore`, `!mood`, `!reset`, `!help`, and `!status` command parsing
- Separate username sanitisation layer
- Message filtering and AI output filtering hooks
- Per-user cooldowns across platforms
- Queue limit to stop the model being overwhelmed
- Local emergency pause file using `config/PAUSE_STREAM.txt`
- Working LM Studio client using the local OpenAI-compatible API
- Terminal/CMD-style OBS browser overlay using Server-Sent Events
- Optional browser text-to-speech in the overlay
- Discord webhook logging for accepted prompts, blocked prompts, replies, status, and errors
- `py -m src.doctor` setup report for first-run troubleshooting
- Local fake demo mode without LM Studio
- Local LM Studio demo mode without a live platform
- Platform debug modes for Tikfinity, YouTube, and Kick
- Windows setup and run helper scripts
- `.env.example` config so secrets are not committed
- Basic pytest coverage for filters, command parsing, platform extraction, and LM Studio response parsing
- GitHub Actions workflow for compile and test checks

## Why this is a portfolio project

This project demonstrates practical AI-assisted engineering rather than a simple chatbot wrapper. It combines local AI, livestream tooling, event-driven message handling, frontend overlay work, platform adapters, basic safety controls, and operational tooling.

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
- Real-world debugging under hardware limits

## What this is not

This is not a moderation replacement and it should not be treated as fully unattended production software. The stream character is designed to be chaotic, but raw chat and raw usernames should never go straight to OBS or TTS.

This is also not a high-end AI agent. It is intentionally designed to work with small local models, so the personality is part of the appeal: quick, odd, funny, and sometimes genuinely potato-brained.

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

For live use, keep a second PowerShell window open with the pause command ready.

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

Recommended small models:

- 350M to 700M for very weak PCs
- 1B to 1.5B for better replies while staying lightweight
- 2B to 3B only if OBS, Tikfinity, and the streaming software still run smoothly

## Personality prompt

The stream character prompt lives in:

```text
config/bot_personality.example.txt
```

Edit this file to change PotatoBrain's style. Keeping the prompt in the project is better than relying on LM Studio global settings because it stays versioned with the stream setup.

## Discord logging

Discord webhook logging is optional, but useful for checking prompts, blocked messages, model replies, and errors from another screen or phone.

Setup guide:

```text
docs/discord-webhook.md
```

The webhook URL should only be placed in your local `.env` file. Never commit it to GitHub.

## Safety design

The intended rule is soft chaos with hard account-protection limits.

The system should allow normal stream banter, silly commands, mood changes, and fictional AI character jokes, while filtering platform-risk content, private personal data, spam walls, and obvious stream-bait attempts.

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
- TikTok LIVE Studio, OBS, Tikfinity, LM Studio, and the bridge can be heavy together on weak hardware.
- Small local models can give strange or low-quality replies, which is part of the PotatoBrain character but not ideal for serious assistant use.
- Longer unattended testing is still recommended before leaving the stream running for many hours.
- TikTok integration depends on Tikfinity being connected to the active live session.

## Portfolio summary

This project is a complete first portfolio build showing a real AI-assisted workflow: idea, implementation, local testing, integration with external tools, safety controls, documentation, and release polish.

For a website-ready project write-up, see [`docs/portfolio-case-study.md`](docs/portfolio-case-study.md).
