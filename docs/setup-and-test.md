# Setup and test checklist

Use this checklist before trying a real TikTok LIVE run.

## 1. Clone and install

```powershell
git clone https://github.com/n4thyan/tikfinity-lmstudio-ai-stream-bot.git
cd tikfinity-lmstudio-ai-stream-bot
copy .env.example .env
py -m pip install -r requirements-dev.txt
```

## 2. Test the OBS overlay without LM Studio

This checks the browser source first, with no Tikfinity and no model involved.

```powershell
py -m src.bridge --test-overlay
```

Add this to OBS as a Browser Source:

```text
http://127.0.0.1:8787/overlay
```

Expected result:

- OBS shows the PotatoBrain overlay.
- A new local test message appears every few seconds.
- If `OVERLAY_TTS_ENABLED=true`, the browser source should speak the sample replies.

## 3. Test the bridge without LM Studio

This checks command parsing, filters, cooldowns, queueing, Discord logging, and the OBS overlay.

```powershell
py -m src.bridge --demo --fake-llm
```

Try:

```text
!ask are you alive
!lore
!mood dramatic
!ask what happened to your computer
!reset
```

Expected result:

- OBS updates after each accepted command.
- Replies appear even though LM Studio is not running.
- Discord receives logs if `DISCORD_WEBHOOK_URL` is set.

## 4. Start LM Studio

In LM Studio:

1. Download a small model first.
2. Load it.
3. Open the Developer tab.
4. Start the local server.
5. Keep the default base URL unless you intentionally changed it.

Default `.env` value:

```env
LMSTUDIO_BASE_URL=http://127.0.0.1:1234/v1
```

## 5. Find the exact model ID

```powershell
py -m src.bridge --test-lmstudio
```

If the configured model ID is wrong, the command prints the model IDs LM Studio can see. Copy the exact ID into `.env`:

```env
LMSTUDIO_MODEL=replace-with-the-listed-model-id
```

Run the check again until it prints a test reply.

## 6. Test the full local demo with LM Studio

```powershell
py -m src.bridge --demo
```

Try:

```text
!ask say hello to TikTok chat
!roast your own tiny CPU
!lore
!mood scared
!ask why are you scared
```

Expected result:

- The local model replies through the overlay.
- Output is short enough for the stream.
- Replies are logged to Discord if enabled.

## 7. Check Tikfinity payloads before enabling the bot

Open Tikfinity and connect it to your TikTok LIVE session. Then run:

```powershell
py -m src.bridge --debug-tikfinity
```

Send a normal chat message in TikTok LIVE.

Expected result:

- The console prints the raw Tikfinity payload.
- The console prints the parsed username and message.

If parsed chat says `no chat message detected`, save the raw payload and update `extract_comment_payload()` in `src/bridge.py` to match the shape Tikfinity is sending.

## 8. Run with Tikfinity

```powershell
py -m src.bridge
```

Expected result:

- The bridge connects to Tikfinity.
- Only supported commands are processed.
- The overlay updates when viewers use commands.
- Discord receives accepted, blocked, reply, and error logs depending on `.env` settings.

## 9. Basic stream safety checks

Before leaving it running for a long session:

- Keep raw chat out of OBS and TTS.
- Keep usernames sanitised before public display.
- Keep TTS off until text-only mode behaves properly.
- Use a short reply length at first.
- Watch CPU, RAM, and OBS dropped frames.
- Check Discord logs from your phone.
- Keep the stream account open on your phone for emergency moderation.

## 10. Recommended first-run settings

For the first real test, use conservative values:

```env
OVERLAY_TTS_ENABLED=false
USER_COOLDOWN_SECONDS=30
GLOBAL_COOLDOWN_SECONDS=3
QUEUE_LIMIT=5
MAX_PROMPT_CHARS=160
MAX_REPLY_CHARS=220
```

Once the text-only stream behaves properly, enable TTS and test again.
