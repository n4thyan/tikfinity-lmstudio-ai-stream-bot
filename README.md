# Tikfinity LM Studio AI Stream Bot

A local TikTok LIVE experiment using Tikfinity, LM Studio, OBS, and Discord webhooks.

The aim is to let TikTok chat interact with a small local LLM character while keeping the stream manageable through username sanitisation, message filtering, output filtering, cooldowns, queue limits, and Discord logging.

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
- `!ask`, `!roast`, `!lore`, `!mood`, and `!reset` command parsing
- Separate username sanitising layer
- Message and AI-output filtering hooks
- Per-user cooldowns
- Prompt queue limits
- Working LM Studio client using the local OpenAI-compatible API
- `--test-lmstudio` health check for local model testing
- Local OBS browser overlay using Server-Sent Events
- Optional browser text-to-speech in the overlay
- Discord webhook logging for accepted, blocked, error, and status events
- Basic pytest coverage for filters, command parsing, and LM Studio response parsing
- GitHub Actions workflow for compile and test checks
- `.env.example` config so secrets are not committed

## What this is not

This is not a moderation replacement and it should not be treated as fully unattended production software yet. The stream can be chaotic, but raw chat and raw usernames should never go straight to OBS or TTS.

## Quick start

1. Install Python 3.11+.
2. Install LM Studio.
3. Download a small local model in LM Studio.
4. Start the LM Studio local server from the Developer tab.
5. Copy `.env.example` to `.env` and edit it.
6. Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

7. Test LM Studio first:

```powershell
py -m src.bridge --test-lmstudio
```

8. Run a local demo without Tikfinity:

```powershell
py -m src.bridge --demo
```

9. Add this as an OBS Browser Source:

```text
http://127.0.0.1:8787/overlay
```

10. Once the demo works, set your Tikfinity WebSocket URL in `.env` and run:

```powershell
py -m src.bridge
```

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
py -m src.bridge --test-lmstudio
```

## Recommended small models

Start with something in the 350M to 1.5B range. The bot is meant to be quick and funny, not academically clever.

Good first targets:

- 350M to 700M model for very weak PCs
- 1B to 1.5B model for better replies
- 2B to 3B only if OBS and Tikfinity still run smoothly

## Safety design

The intended rule is soft chaos with hard account-protection limits.

Allowed style:

- chat teasing the fictional AI
- silly commands
- angry moods
- nonsense prompts
- fictional robot shutdown jokes

Blocked style:

- protected-class hate
- explicit slur bait
- sexual explicit content
- doxxing or personal data
- real-world threats
- graphic harm bait
- spam walls
- obvious ban bait

## Username handling

The project keeps two names internally:

```text
raw_username  = real TikTok username, used only for cooldowns and private Discord logs
safe_username = cleaned public name, used for LM Studio, OBS, and TTS
```

Safe usernames can be read on stream. Risky usernames are cleaned or replaced with a generic viewer label.

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

This is an early MVP, but the basic loop is now wired:

```text
bridge -> LM Studio reply -> output filter -> OBS overlay -> Discord log
```

The next important task is local hardware testing on the actual stream PC: LM Studio model speed, OBS load, Tikfinity payload shape, TTS behaviour, and filter strictness.

After that, the next upgrades are gifts, likes, mood changes, stream events, better filters, and a nicer retro overlay.
