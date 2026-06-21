# PotatoBrain Live AI Stream Bot: Portfolio Case Study

## One-line summary

A working local AI livestream bot that lets live chat interact with a small LM Studio model, displays replies in OBS, speaks them with browser TTS and logs activity to Discord.

## Project type

AI-assisted livestream interaction project.

## Problem

I wanted to build a real stream tool where viewers could interact with a local AI character during a live show instead of relying on a hosted chatbot API. The goal was to make something practical, funny and technically useful: a small AI character that could run locally, appear on stream, react to commands, and be controlled safely enough for public livestream testing.

The main challenge was not only generating AI replies. The project also needed to handle live chat input, command parsing, user cooldowns, message filtering, display output, TTS, logging and a quick emergency pause option.

## Solution

I built a Python bridge that connects livestream chat events to a local LM Studio model. The bridge receives chat events from a platform adapter, sanitises usernames, filters messages, applies cooldowns, sends accepted prompts to the local model, filters the output, and pushes the final reply to an OBS browser overlay.

The stream character is called PotatoBrain. It is intentionally small, chaotic and lightweight enough to run on a modest Windows PC.

## Core flow

```text
TikTok / YouTube / Kick chat
  -> platform adapter
  -> Python bridge
  -> username sanitiser
  -> message filter and queue
  -> LM Studio local OpenAI-compatible API
  -> output filter
  -> OBS terminal overlay
  -> optional browser TTS
  -> Discord webhook logs
```

## What I built

- Local LM Studio integration using the OpenAI-compatible API
- Python bridge for command parsing and stream message handling
- TikTok/Tikfinity WebSocket support
- YouTube Live chat polling support
- Kick webhook receiver support
- OBS browser overlay with terminal/CMD-style visual design
- Optional browser text-to-speech
- Discord webhook logging for accepted prompts, blocked prompts, replies, status and errors
- Input and output filtering hooks
- Username sanitisation so raw usernames are not sent straight to OBS/TTS
- Per-user cooldowns and queue limits
- Emergency pause/resume scripts
- Windows setup scripts
- Local showcase/demo mode for recording or testing without going live
- Setup doctor command for troubleshooting
- Basic automated tests and GitHub Actions checks

## Tech stack

- Python
- AsyncIO
- aiohttp
- WebSockets
- LM Studio local server
- OpenAI-compatible local API format
- OBS Browser Source
- HTML, CSS and JavaScript overlay
- Browser SpeechSynthesis TTS
- Discord webhooks
- PowerShell helper scripts
- GitHub Actions

## Commands supported

```text
!ask <message>
!roast <topic>
!lore
!mood normal
!mood confused
!mood angry
!mood dramatic
!help
!status
!reset
```

## Testing and validation

The project has been tested through staged setup checks:

```text
doctor -> overlay test -> fake bridge demo -> LM Studio test -> LM Studio demo -> platform connection -> full bridge
```

Confirmed working locally:

- `.env` setup
- LM Studio model connection
- OBS browser overlay
- terminal-style stream display
- browser TTS
- Discord webhook logging
- local manual demo mode
- emergency pause/resume control
- Tikfinity WebSocket/Event API connection path

## Real-world constraint

The project is designed to run locally, which is a strength and a limitation. Running OBS, TikTok LIVE Studio, Tikfinity, LM Studio and the bridge on the same weak PC can be heavy. The software path works, but longer livestream sessions need a stronger machine or a cleaner split between streaming and AI processing.

This is useful portfolio evidence because it shows the difference between code that works in isolation and a tool that must work in a real streaming environment.

## Safety and control design

The project is not a moderation replacement. It is designed around controlled chaos:

- Chat can make the bot funny and unpredictable.
- Raw usernames are sanitised before public display.
- Raw prompts are filtered before reaching the model.
- Model replies are filtered before OBS/TTS.
- Cooldowns and queue limits stop spam from overwhelming the model.
- A local pause file can stop replies quickly without killing the whole stream.
- Discord logging provides a private audit trail.

## What I learned

- How to connect a local LLM to a real-time stream workflow
- How to design a small async Python service around multiple inputs and outputs
- How to use OBS Browser Sources as a live UI layer
- How to handle practical failure points like lag, TTS routing, stream mirroring and model delay
- How to separate demo mode, debug mode and live mode
- How to document a project so another person can understand the setup path
- How to use AI assistance productively while still testing and checking the actual system myself

## Portfolio description

PotatoBrain is a local AI livestream bot built around LM Studio, OBS and live chat platform adapters. It lets stream viewers send commands to a small local AI character, shows the reply in a terminal-style OBS overlay, optionally speaks it through browser TTS and logs activity to Discord. The project includes filtering, username sanitisation, cooldowns, queue limits, setup scripts, debug modes and an emergency pause system. It demonstrates practical AI-assisted development, local LLM integration, async Python, streaming tool integration and real-world testing under hardware constraints.

## Current status

Portfolio v1 is complete and released as a working local project. Further improvements could include stronger stream testing, more event types, better model tuning, more advanced safety rules and a polished public demo video.
