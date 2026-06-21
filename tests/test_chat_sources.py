from src.chat_sources import extract_kick_webhook_message, extract_tikfinity_message, extract_youtube_message


def test_extract_tikfinity_message_basic_payload():
    payload = {
        "event": "chat",
        "data": {
            "user": {"uniqueId": "retro_user"},
            "comment": "!ask are you alive",
        },
    }

    result = extract_tikfinity_message(payload)

    assert result is not None
    assert result.platform == "tiktok"
    assert result.raw_username == "retro_user"
    assert result.message == "!ask are you alive"


def test_extract_tikfinity_ignores_gift_like_events():
    payload = {
        "event": "gift",
        "data": {
            "user": {"uniqueId": "retro_user"},
            "comment": "!ask ignored",
        },
    }

    assert extract_tikfinity_message(payload) is None


def test_extract_youtube_text_message():
    item = {
        "snippet": {
            "type": "textMessageEvent",
            "displayMessage": "!ask hello from youtube",
        },
        "authorDetails": {
            "displayName": "YouTube Viewer",
            "channelId": "UC123",
        },
    }

    result = extract_youtube_message(item)

    assert result is not None
    assert result.platform == "youtube"
    assert result.raw_username == "YouTube Viewer"
    assert result.message == "!ask hello from youtube"


def test_extract_youtube_ignores_non_text_message():
    item = {
        "snippet": {
            "type": "newSponsorEvent",
            "displayMessage": "new member",
        },
        "authorDetails": {"displayName": "Member"},
    }

    assert extract_youtube_message(item) is None


def test_extract_kick_webhook_message_removes_emote_tokens():
    payload = {
        "message_id": "msg1",
        "sender": {
            "username": "kick_viewer",
            "channel_slug": "kick_viewer",
        },
        "content": "!ask hello [emote:123:WAVE]",
    }
    headers = {"Kick-Event-Type": "chat.message.sent"}

    result = extract_kick_webhook_message(payload, headers)

    assert result is not None
    assert result.platform == "kick"
    assert result.raw_username == "kick_viewer"
    assert result.message == "!ask hello"


def test_extract_kick_webhook_ignores_other_events():
    payload = {
        "sender": {"username": "kick_viewer"},
        "content": "!ask ignored",
    }
    headers = {"Kick-Event-Type": "channel.followed"}

    assert extract_kick_webhook_message(payload, headers) is None
