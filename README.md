# Tikfinity LM Studio AI Stream Bot

A local TikTok LIVE experiment using Tikfinity, LM Studio, OBS, and Discord webhooks.

The aim is to let TikTok chat interact with a small local LLM character while keeping the stream manageable through username sanitisation, message filtering, output filtering, cooldowns, queue limits, and Discord logging.

## What this is

This project is a first-pass MVP for a 24/7 style TikTok livestream where chat can talk to a local potato AI character.

Planned stream flow:

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
- LM Studio OpenAI-compatible chat completions client
- Local OBS browser overlay using Server-Sent Events
- Optional browser text-to-speech in the overlay
- Discord webhook logging for accepted, blocked, error, and status events
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

7. Run a local demo without Tikfinity:

```powershell
py -m src.bridge --demo
```

8. Add this as an OBS Browser Source:

```text
http://127.0.0.1:8787/overlay
```

9. Once the demo works, set your Tikfinity WebSocket URL in `.env` and run:

```powershell
py -m src.bridge
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

## Repository status

This is an early MVP scaffold. The first goal is to get one loop working:

```text
Tikfinity message -> bridge -> LM Studio reply -> OBS overlay -> Discord log
```

After that, the next upgrades are gifts, likes, mood changes, stream events, better filters, and a nicer retro overlay.
