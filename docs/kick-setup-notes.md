# Kick setup notes

Kick support currently uses a local webhook receiver.

## Required `.env` values

```env
CHAT_PLATFORM=kick-webhook
KICK_WEBHOOK_HOST=127.0.0.1
KICK_WEBHOOK_PORT=8790
KICK_WEBHOOK_PATH=/kick/webhook
```

## Test commands

Run the local receiver in debug mode:

```powershell
.\scripts\start-kick-webhook-debug.ps1
```

Local receiver URL:

```text
http://127.0.0.1:8790/kick/webhook
```

Run live bridge with Kick forced:

```powershell
.\scripts\start-kick-webhook-live.ps1
```

## Local sample payload

A sample payload is included at:

```text
docs/kick-webhook-sample.json
```

When the debug receiver is running, you can POST that JSON to the local endpoint from a REST client or PowerShell.

## Public webhook warning

Keep the receiver local-only until you add proper public webhook hardening:

- HTTPS
- public tunnel or reverse proxy
- event signature verification
- rate limiting
- Discord error logging
- local pause-file access

The current implementation is ready for local parsing tests, not public unattended deployment.
