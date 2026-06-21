# Tikfinity LM Studio AI Stream Bot

A local TikTok LIVE experiment using Tikfinity, LM Studio, OBS, and Discord webhooks.

The aim is to let TikTok chat interact with a small local LLM character while keeping the stream manageable through username sanitisation, message filtering, output filtering, cooldowns, queue limits, a local pause file, and Discord logging.

## What this is

This project is a first-pass MVP for a 24/7 style TikTok livestream where chat can talk to a local potato AI character.

Stream flow:

```text
TikTok LIVE chat
  -> Tikfinity Desktop WebSocket
  -> Python bridge
  -> username sanitiser
  -> message filter and queue
  -> LM Studio local API
  -> output filter
  -> OBS browser overlay / optional browser TTS
  -> Discord webhook logs
```

## Current MVP features

- Tikfinity WebSocket listener
- `!ask`, `!roast`, `!lore`, `!mood`, `!reset`, `!help`, and `!status` command parsing
- Separate username sanitising layer
- Message and AI-output filtering hooks
- Per-user cooldowns
- Prompt queue limits
- Local pause file support using `config/PAUSE_STREAM.txt`
- Working LM Studio client using the local OpenAI-compatible API
- `py -m src.doctor` setup report for first-run troubleshooting
- `--test-lmstudio` health check for local model testing
- `--test-overlay` mode for testing OBS without Tikfinity or LM Studio
- `--demo --fake-llm` mode for testing the bridge without LM Studio
- `--debug-tikfinity` mode for printing raw Tikfinity payloads before enabling the bot
- Local OBS browser overlay using Server-Sent Events
- Optional browser text-to-speech in the overlay
- Discord webhook logging for accepted, blocked, error, and status events
- Basic pytest coverage for filters, command parsing, Tikfinity extraction, and LM Studio response parsing
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

6. Run the setup doctor:

```powershell
.\.venv\Scripts\python.exe -m src.doctor
```

7. Test the OBS overlay:

```powershell
.\scripts\start-overlay-test.ps1
```

Add this as an OBS Browser Source:

```text
http://127.0.0.1:8787/overlay
```

8. Test the bridge without LM Studio:

```powershell
.\scripts\start-fake-demo.ps1
```

9. Test LM Studio:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --test-lmstudio
```

10. Run a local demo using LM Studio:

```powershell
.\scripts\start-lmstudio-demo.ps1
```

11. Once the demo works, debug Tikfinity's payload shape:

```powershell
.\scripts\start-tikfinity-debug.ps1
```

12. When the payload parses correctly, run the full bridge:

```powershell
.\scripts\start-live-bridge.ps1
```

For the full setup flow, see [`docs/setup-and-test.md`](docs/setup-and-test.md).

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

## Recommended small models

Start with something in the 350M to 1.5B range. The bot is meant to be quick and funny, not academically clever.

Good first targets:

- 350M to 700M model for very weak PCs
- 1B to 1.5B model for better replies
- 2B to 3B only if OBS and Tikfinity still run smoothly

## Safety design

The intended rule is soft chaos with hard account-protection limits.

The system should allow normal stream banter, silly commands, mood changes, and fictional AI character jokes, while filtering platform-risk content, private personal data, spam walls, and obvious stream-bait attempts.

## Username handling

The project keeps two names internally:

```text
raw_username  = real TikTok username, used only for cooldowns and private Discord logs
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

# Overlay only, no Tikfinity, no LM Studio
.\scripts\start-overlay-test.ps1

# Local demo with built-in fake replies
.\scripts\start-fake-demo.ps1

# Check LM Studio and print visible model IDs
.\.venv\Scripts\python.exe -m src.bridge --test-lmstudio

# Local demo with LM Studio
.\scripts\start-lmstudio-demo.ps1

# Print raw Tikfinity payloads and parsed chat results
.\scripts\start-tikfinity-debug.ps1

# Full Tikfinity -> LM Studio -> OBS run
.\scripts\start-live-bridge.ps1

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
doctor -> overlay test -> fake bridge demo -> LM Studio test -> LM Studio demo -> Tikfinity debug -> full run
```

The next important task is local hardware testing on the actual stream PC: LM Studio model speed, OBS load, Tikfinity payload shape, TTS behaviour, and filter strictness.

After that, the next upgrades are gifts, likes, mood changes, stream events, better filters, and a nicer retro overlay.
