# MVP Test Checklist

Use this after cloning the repo locally.

## Local files

- [ ] `.env.example` copied to `.env`
- [ ] Discord webhook added only to `.env`, not committed
- [ ] LM Studio server started
- [ ] OBS Browser Source added: `http://127.0.0.1:8787/overlay`

## Demo mode

Run:

```powershell
py -m src.bridge --demo
```

Test commands:

```text
!ask are you alive
!mood angry
!ask why are you angry
!lore
!roast yourself
!reset
```

Expected result:

- [ ] Overlay loads in browser/OBS
- [ ] Terminal accepts commands
- [ ] Overlay updates after a command
- [ ] Discord receives logs if webhook is set
- [ ] Cooldowns prevent rapid repeated messages
- [ ] Long prompts are blocked
- [ ] Link-style prompts are blocked
- [ ] Email/phone/postcode style prompts are blocked

## Tikfinity mode

Run:

```powershell
py -m src.bridge
```

Expected result:

- [ ] Bridge connects to Tikfinity WebSocket
- [ ] Non-command chat is ignored
- [ ] `!ask` messages are queued
- [ ] Public username is cleaned before display
- [ ] Private raw username is only sent to Discord logs
- [ ] Overlay shows the filtered reply

## LM Studio check

Current repo status:

- [ ] `src/lmstudio_client.py` still needs final local API implementation
- [ ] Confirm exact LM Studio model name
- [ ] Confirm local endpoint with a manual request
- [ ] Replace placeholder client
- [ ] Test with a very small model first

## OBS/TTS check

- [ ] `OVERLAY_TTS_ENABLED=false` works silently
- [ ] `OVERLAY_TTS_ENABLED=true` speaks only AI replies
- [ ] Raw usernames are not spoken if sanitised/replaced
- [ ] Raw TikTok chat is never spoken directly

## Stream safety check

- [ ] Username sanitiser replaces obviously risky names
- [ ] Message filter blocks obvious bait
- [ ] AI output filter catches unsafe generated replies
- [ ] Discord logs blocked attempts
- [ ] Queue limit prevents spam overload
- [ ] Per-user cooldown works
- [ ] Global cooldown works
