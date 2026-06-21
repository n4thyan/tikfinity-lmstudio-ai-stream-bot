# Roadmap

## Local setup phase

- Confirm Python setup on the stream PC.
- Confirm OBS overlay works.
- Confirm LM Studio model speed.
- Confirm text-only replies before enabling TTS.
- Confirm Tikfinity payload parsing.
- Confirm YouTube live chat ID discovery.
- Confirm Kick webhook payload parsing locally.

## Platform hardening phase

- Add richer event handling for gifts, follows, likes, memberships, and subscriptions.
- Add platform-specific cooldown overrides.
- Add optional per-platform command prefixes.
- Add better Discord alert summaries.
- Add replay-safe logging for debugging bad payloads.

## Kick production phase

- Add Kick webhook signature verification.
- Add HTTPS/tunnel setup docs.
- Add public endpoint rate limiting.
- Add a simple local allow/deny mode for webhook event types.

## Overlay phase

- Improve the retro visual design.
- Add platform badge display.
- Add mood animations.
- Add queue/status panels.
- Add a TTS mute toggle on the overlay.
