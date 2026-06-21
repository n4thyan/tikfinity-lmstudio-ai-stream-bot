# Portfolio v1 Release Notes

## Release name

PotatoBrain Live AI Stream Bot: Portfolio v1

## Release status

Working local release.

## Confirmed working

- Windows setup helper creates the local environment.
- Setup doctor validates config files, selected platform, LM Studio, Discord logging, TTS setting, and pause state.
- LM Studio responds through the local OpenAI-compatible API.
- OBS browser overlay renders the terminal-style PotatoBrain interface.
- Browser TTS works through the stream setup.
- Discord webhook logging works for status, accepted prompts, and replies.
- Local LM Studio demo mode works from PowerShell.
- Pause and resume scripts work through `config/PAUSE_STREAM.txt`.
- Tikfinity WebSocket/Event API path was detected and the bridge attempted connection against `ws://127.0.0.1:21213/`.

## Main local run path

```text
LM Studio -> Python bridge -> filters -> OBS overlay -> TTS -> Discord logs
```

## Main live target path

```text
TikTok LIVE -> Tikfinity -> Python bridge -> LM Studio -> OBS overlay/TTS -> Discord logs
```

## Known hardware limitation

Running TikTok LIVE Studio, OBS, Tikfinity, LM Studio, and the Python bridge on the same weak PC can cause lag. The project is functional, but longer public streams will benefit from a stronger PC, lower stream settings, a smaller model, or splitting the stream and AI workload across machines.

## Portfolio framing

This project is ready to be shown as a practical AI-assisted build. It demonstrates local AI integration, livestream tooling, chat event handling, OBS overlay work, filtering, logging, operational scripts, and documentation.

## Recommended next improvements

- Add screenshots or a short demo clip to the README.
- Tune the PotatoBrain personality prompt after more real chat testing.
- Reduce reply token limits if the stream PC struggles.
- Add more TikTok event types beyond chat commands.
- Add a cleaner public dashboard for runtime status.
- Test a longer YouTube Live or TikTok session on stronger hardware.
