# YouTube setup notes

The YouTube adapter uses the official YouTube API path:

```text
videos.list(part=liveStreamingDetails, id=<video_id>)
  -> activeLiveChatId
  -> liveChatMessages.list(part=snippet,authorDetails, liveChatId=<id>)
```

## Required `.env` values

```env
CHAT_PLATFORM=youtube
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_VIDEO_ID=your_live_video_id_here
```

Optional direct chat ID:

```env
YOUTUBE_LIVE_CHAT_ID=your_live_chat_id_here
```

If `YOUTUBE_LIVE_CHAT_ID` is set, the bridge uses that directly. If it is blank, the bridge tries to resolve it from `YOUTUBE_VIDEO_ID`.

## Test commands

Check API key and chat ID discovery:

```powershell
.\.venv\Scripts\python.exe -m src.bridge --test-youtube
```

Print parsed chat only:

```powershell
.\scripts\start-youtube-debug.ps1
```

Run live bridge with YouTube forced:

```powershell
.\scripts\start-youtube-live.ps1
```

## Notes

- The live video must currently have active chat.
- Keep an eye on API quota during long sessions.
- The adapter only processes normal text chat messages at the moment.
