# Local Testing Checklist

Use this checklist before trying to run the stream for real.

## 1. Clone and install

```powershell
git clone https://github.com/n4thyan/tikfinity-lmstudio-ai-stream-bot.git
cd tikfinity-lmstudio-ai-stream-bot
copy .env.example .env
py -m pip install -r requirements.txt
```

## 2. Start LM Studio

1. Open LM Studio.
2. Download or load a small model.
3. Open the Developer tab.
4. Start the local server.
5. Confirm the port matches `.env`.

Default expected base URL:

```env
LMSTUDIO_BASE_URL=http://127.0.0.1:1234/v1
```

## 3. Find the model ID

Run:

```powershell
py -m src.bridge --test-lmstudio
```

If the configured model name is wrong, copy one of the listed model IDs into `.env`:

```env
LMSTUDIO_MODEL=your-model-id-here
```

Then run the test again.

## 4. Test the OBS overlay without Tikfinity

Run:

```powershell
py -m src.bridge --demo
```

Open this URL in your browser:

```text
http://127.0.0.1:8787/overlay
```

Type demo commands in the terminal:

```text
!ask are you alive
!mood dramatic
!lore
!roast the situation
!reset
```

Expected result:

- the browser overlay updates
- the AI replies in character
- long or risky prompts are blocked
- replies are shortened to the configured limit

## 5. Add OBS

In OBS:

1. Add Browser Source.
2. Set URL to `http://127.0.0.1:8787/overlay`.
3. Use a transparent background.
4. Keep the bridge running while OBS is open.

## 6. Add Discord logging

Create a Discord webhook in a private channel, then add it to `.env`:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-here
```

Run demo mode again and confirm the channel logs accepted prompts, blocked prompts, replies, errors, and status messages.

Never commit your real `.env` file.

## 7. Connect Tikfinity

1. Open Tikfinity Desktop.
2. Connect it to the TikTok LIVE session.
3. Check the TikTok LIVE API / WebSocket page for the local WebSocket URL.
4. Put that URL in `.env`:

```env
TIKFINITY_WS_URL=ws://127.0.0.1:21213/
```

Then run:

```powershell
py -m src.bridge
```

Expected result:

- regular chat is ignored unless it starts with the command prefix
- `!ask` messages are queued
- public usernames are cleaned before the model sees them
- accepted and blocked prompts are logged to Discord
- approved AI replies appear on the OBS overlay

## 8. TTS test

Browser TTS is off by default.

To enable it:

```env
OVERLAY_TTS_ENABLED=true
```

Test carefully before going live. TTS should only speak filtered AI replies, not raw TikTok chat.

## 9. First stream safety pass

Before leaving the stream running for long periods:

- keep Discord alerts enabled
- keep prompt length short
- keep reply length short
- use a small queue limit
- test cooldowns with repeated messages
- keep the TikTok account moderation tools ready
- watch the first real run manually before trusting it

## 10. Known next improvements

- better Tikfinity payload detection once real payload examples are captured
- gift and like events changing AI mood
- optional manual pause switch
- improved retro overlay theme
- persistent local log file
- more detailed filter categories
