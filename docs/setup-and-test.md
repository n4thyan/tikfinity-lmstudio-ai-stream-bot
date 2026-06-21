# Setup and test checklist

Use this checklist before trying a real TikTok LIVE run.

## 1. Clone and install

```powershell
git clone https://github.com/n4thyan/tikfinity-lmstudio-ai-stream-bot.git
cd tikfinity-lmstudio-ai-stream-bot
.\scripts\windows-setup.ps1
```

Manual install, if you do not want to use the helper script:

```powershell
copy .env.example .env
py -m pip install -r requirements-dev.txt
```

## 2. Run the setup doctor

This checks required files, important `.env` values, the OBS overlay URL, Discord status, pause state, and LM Studio connectivity.

```powershell
.\.venv\Scripts\python.exe -m src.doctor
```

It is OK if LM Studio fails here before you have started the LM Studio server. Fix the easy file/config warnings first, then come back to LM Studio after step 5.

## 3. Test the OBS overlay without LM Studio

This checks the browser source first, with no Tikfinity and no model involved.

```powershell
.\scripts\start-overlay-test.ps1
```

Equivalent manual command:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --test-overlay
```

Add this to OBS as a Browser Source:

```text
http://127.0.0.1:8787/overlay
```

Expected result:

- OBS shows the PotatoBrain overlay.
- A new local test message appears every few seconds.
- If `OVERLAY_TTS_ENABLED=true`, the browser source should speak the sample replies.

## 4. Test the bridge without LM Studio

This checks command parsing, filters, cooldowns, queueing, Discord logging, and the OBS overlay.

```powershell
.\scripts\start-fake-demo.ps1
```

Equivalent manual command:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --demo --fake-llm
```

Try:

```text
!help
!status
!ask are you alive
!lore
!mood dramatic
!ask what happened to your computer
!reset
```

Expected result:

- OBS updates after each accepted command.
- Replies appear even though LM Studio is not running.
- `!help` and `!status` work without using the model.
- Discord receives logs if `DISCORD_WEBHOOK_URL` is set.

## 5. Start LM Studio

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

## 6. Find the exact model ID

```powershell
.\.venv\Scripts\python.exe -m src.bridge --test-lmstudio
```

If the configured model ID is wrong, the command prints the model IDs LM Studio can see. Copy the exact ID into `.env`:

```env
LMSTUDIO_MODEL=replace-with-the-listed-model-id
```

Run the check again until it prints a test reply.

You can also rerun the full doctor after this:

```powershell
.\.venv\Scripts\python.exe -m src.doctor
```

## 7. Test the full local demo with LM Studio

```powershell
.\scripts\start-lmstudio-demo.ps1
```

Equivalent manual command:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --demo
```

Try:

```text
!help
!status
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

## 8. Test the local pause file

The bridge can be paused by creating `config/PAUSE_STREAM.txt`. This is a local safety control for testing or stopping new chat replies without closing OBS.

Pause:

```powershell
.\scripts\pause-bridge.ps1
```

Resume:

```powershell
.\scripts\resume-bridge.ps1
```

Expected result:

- While paused, normal chat commands are ignored.
- `!help` and `!status` still work.
- `!status` reports `paused`.
- Removing the pause file lets replies resume.

## 9. Check Tikfinity payloads before enabling the bot

Open Tikfinity and connect it to your TikTok LIVE session. Then run:

```powershell
.\scripts\start-tikfinity-debug.ps1
```

Equivalent manual command:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --debug-tikfinity
```

Send a normal chat message in TikTok LIVE.

Expected result:

- The console prints the raw Tikfinity payload.
- The console prints the parsed username and message.

If parsed chat says `no chat message detected`, save the raw payload and update `extract_comment_payload()` in `src/bridge.py` to match the shape Tikfinity is sending.

## 10. Run with Tikfinity

```powershell
.\scripts\start-live-bridge.ps1
```

Equivalent manual command:

```powershell
.\.venv\Scripts\python.exe -m src.bridge
```

Expected result:

- The bridge connects to Tikfinity.
- Only supported commands are processed.
- The overlay updates when viewers use commands.
- Discord receives accepted, blocked, reply, and error logs depending on `.env` settings.

## 11. Basic stream safety checks

Before leaving it running for a long session:

- Keep raw chat out of OBS and TTS.
- Keep usernames sanitised before public display.
- Keep TTS off until text-only mode behaves properly.
- Use a short reply length at first.
- Watch CPU, RAM, and OBS dropped frames.
- Check Discord logs from your phone.
- Keep the stream account open on your phone for emergency moderation.

## 12. Recommended first-run settings

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
