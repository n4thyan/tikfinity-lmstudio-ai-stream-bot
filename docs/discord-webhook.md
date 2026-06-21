# Discord webhook logging

Discord logging is optional, but useful when the stream is running on a second monitor or left unattended for short periods.

The bridge can log:

- accepted prompts
- blocked prompts
- generated replies
- errors
- pause/status events

## 1. Create a Discord channel

Create a private channel in your Discord server, for example:

```text
#potatobrain-logs
```

Keep this channel private because it can contain raw usernames and blocked prompts.

## 2. Create the webhook

In Discord:

1. Right-click the channel.
2. Open **Edit Channel**.
3. Go to **Integrations**.
4. Choose **Webhooks**.
5. Create a new webhook.
6. Copy the webhook URL.

Do not commit the webhook URL to GitHub.

## 3. Add it to `.env`

Open the local `.env` file:

```powershell
notepad .env
```

Find:

```env
DISCORD_WEBHOOK_URL=
```

Paste the webhook URL after the equals sign:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your/private/url
```

Leave these enabled at first:

```env
DISCORD_LOG_ACCEPTED=true
DISCORD_LOG_BLOCKED=true
DISCORD_LOG_REPLIES=true
```

Save the file.

## 4. Run the doctor

```powershell
.\.venv\Scripts\python.exe -m src.doctor
```

It should show that Discord webhook logging is enabled.

## 5. Test with the local demo

```powershell
.\scripts\start-lmstudio-demo.ps1
```

Try:

```text
!ask are you logging this to Discord
```

Check the Discord channel for a log message.

## Notes

- Keep the webhook URL private.
- If the webhook is leaked, delete it in Discord and create a new one.
- Discord logging is not required for the bot to run.
- Logging blocked prompts is useful during testing, but you may turn it off later if the channel becomes noisy.
