# Setup Guide

This guide is for the first local MVP build.

## 1. Clone the repo

```powershell
git clone https://github.com/n4thyan/tikfinity-lmstudio-ai-stream-bot.git
cd tikfinity-lmstudio-ai-stream-bot
```

## 2. Create local config

```powershell
copy .env.example .env
notepad .env
```

Do not commit `.env`. It can contain your Discord webhook and local settings.

## 3. Install Python dependencies

```powershell
py -m pip install -r requirements.txt
```

## 4. Start LM Studio

1. Open LM Studio.
2. Download a small model.
3. Go to the Developer tab.
4. Start the local server.
5. Put the model name in `.env` as `LMSTUDIO_MODEL`.

Recommended first test: a model around 350M to 1.5B parameters.

## 5. Test the OBS overlay without TikTok

```powershell
py -m src.bridge --demo
```

Add this URL as an OBS Browser Source:

```text
http://127.0.0.1:8787/overlay
```

Then type a command in the terminal:

```text
!ask are you alive
```

## 6. Connect Tikfinity

1. Open Tikfinity Desktop.
2. Connect it to your TikTok LIVE account.
3. Open the TikTok LIVE API/WebSocket page in Tikfinity.
4. Copy the local WebSocket URL.
5. Put it in `.env` as `TIKFINITY_WS_URL`.

Then run:

```powershell
py -m src.bridge
```

## 7. Discord webhook logging

Create a Discord webhook in a private channel and set:

```text
DISCORD_WEBHOOK_URL=your_webhook_here
```

The bot will log accepted prompts, blocked prompts, generated replies, and connection errors depending on your `.env` settings.

## 8. TTS

The overlay has optional browser TTS.

Set this in `.env`:

```text
OVERLAY_TTS_ENABLED=true
```

Raw TikTok chat is not spoken. Only the filtered AI reply is sent to the overlay.

## 9. Current limitation

The repository currently includes the full bridge structure and a placeholder LM Studio client. The next development step is replacing `src/lmstudio_client.py` with the final HTTP client once local testing confirms the exact LM Studio endpoint and model name.
