# Setup and test checklist

Use this checklist before trying a real livestream run.

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

## 2. Pick a platform in `.env`

```env
CHAT_PLATFORM=tiktok
```

Supported values:

```text
tiktok
youtube
kick-webhook
```

Start with `tiktok` if you want the original Tikfinity flow. Use `youtube` once you have a YouTube Data API key and a live video/chat ID. Use `kick-webhook` when you are ready to test Kick's webhook event payload.

## 3. Run the setup doctor

This checks required files, important `.env` values, the OBS overlay URL, Discord status, pause state, selected platform settings, and LM Studio connectivity.

```powershell
.\.venv\Scripts\python.exe -m src.doctor
```

It is OK if LM Studio fails here before you have started the LM Studio server. Fix the easy file/config warnings first, then come back to LM Studio after step 6.

## 4. Test the OBS overlay without LM Studio

This checks the browser source first, with no platform and no model involved.

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

## 5. Test the bridge without LM Studio

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

## 6. Start LM Studio

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

## 7. Find the exact model ID

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

## 8. Test the full local demo with LM Studio

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
!ask say hello to chat
!roast your own tiny CPU
!lore
!mood scared
!ask why are you scared
```

Expected result:

- The local model replies through the overlay.
- Output is short enough for the stream.
- Replies are logged to Discord if enabled.

## 9. Test the local pause file

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

## 10. Debug the selected platform

### TikTok / Tikfinity

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

- The console prints the parsed username and message.

### YouTube Live

Set either `YOUTUBE_LIVE_CHAT_ID` directly, or set `YOUTUBE_VIDEO_ID` for an active live stream and let the bridge discover the chat ID.

```env
CHAT_PLATFORM=youtube
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_VIDEO_ID=your_live_video_id_here
```

Check discovery:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --test-youtube
```

Then run:

```powershell
.\scripts\start-youtube-debug.ps1
```

Expected result:

- The console prints parsed YouTube chat messages.
- The bridge follows YouTube's returned polling interval instead of hammering the API.

### Kick webhook

Set:

```env
CHAT_PLATFORM=kick-webhook
KICK_WEBHOOK_HOST=127.0.0.1
KICK_WEBHOOK_PORT=8790
KICK_WEBHOOK_PATH=/kick/webhook
```

Run:

```powershell
.\scripts\start-kick-webhook-debug.ps1
```

Local endpoint:

```text
http://127.0.0.1:8790/kick/webhook
```

Expected result:

- The receiver starts locally.
- When a Kick `chat.message.sent` webhook payload reaches that endpoint, the console prints the parsed username and message.

For real Kick webhook testing, expose the local endpoint with a tunnel or reverse proxy and point Kick's event subscription at the public URL.

## 11. Run the full bridge

Use the platform selected in `.env`:

```powershell
.\scripts\start-live-bridge.ps1
```

Or force a specific platform for that run:

```powershell
.\scripts\start-tiktok-live.ps1
.\scripts\start-youtube-live.ps1
.\scripts\start-kick-webhook-live.ps1
```

Equivalent manual command examples:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --platform tiktok
.\.venv\Scripts\python.exe -m src.bridge --platform youtube
.\.venv\Scripts\python.exe -m src.bridge --platform kick-webhook
```

Expected result:

- The bridge connects to the selected chat source.
- Only supported commands are processed.
- The overlay updates when viewers use commands.
- Discord receives accepted, blocked, reply, and error logs depending on `.env` settings.

## 12. Basic stream safety checks

Before leaving it running for a long session:

- Keep raw chat out of OBS and TTS.
- Keep usernames sanitised before public display.
- Keep TTS off until text-only mode behaves properly.
- Use a short reply length at first.
- Watch CPU, RAM, and OBS dropped frames.
- Check Discord logs from your phone.
- Keep the stream account open on your phone for emergency moderation.

## 13. Recommended first-run settings

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
