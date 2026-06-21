from src.bridge import ChatCommand, build_fake_reply, extract_comment_payload, parse_command
from src.filters import SafetyConfig, filter_ai_output, filter_chat_text, sanitise_username


def test_parse_ask_command() -> None:
    assert parse_command("!ask are you awake", "!") == ("ask", "are you awake")


def test_parse_short_ask_alias() -> None:
    assert parse_command("!q are you awake", "!") == ("ask", "are you awake")


def test_parse_lore_command_gets_default_prompt() -> None:
    command = parse_command("!lore", "!")

    assert command is not None
    assert command[0] == "lore"
    assert command[1]


def test_parse_help_aliases() -> None:
    assert parse_command("!help", "!") == ("help", "Show the available stream commands.")
    assert parse_command("!commands", "!") == ("help", "Show the available stream commands.")


def test_parse_status_aliases() -> None:
    assert parse_command("!status", "!") == ("status", "Show the bridge status.")
    assert parse_command("!queue", "!") == ("status", "Show the bridge status.")


def test_filter_blocks_links() -> None:
    config = SafetyConfig((), {}, (), {})
    result = filter_chat_text("look at https://example.test", config, max_chars=200)

    assert not result.allowed
    assert result.reason == "link blocked"


def test_filter_truncates_ai_output() -> None:
    config = SafetyConfig((), {}, (), {})
    result = filter_ai_output("one two three four five", config, max_chars=10)

    assert result.allowed
    assert result.text.endswith("...")
    assert len(result.text) <= 10


def test_username_keeps_safe_name() -> None:
    config = SafetyConfig((), {}, (), {})
    result = sanitise_username("retro_gamer_uk", config)

    assert result.text == "retro_gamer_uk"


def test_username_replaces_configured_risky_name() -> None:
    config = SafetyConfig((), {}, ("replace_me",), {})
    result = sanitise_username("replace_me_user", config)

    assert result.text.startswith("Viewer ")


def test_extract_comment_payload_from_flat_shape() -> None:
    payload = {"event": "chat", "uniqueId": "viewer_one", "comment": "!ask hello"}

    assert extract_comment_payload(payload) == ("viewer_one", "!ask hello")


def test_extract_comment_payload_from_nested_shape() -> None:
    payload = {
        "event": "message",
        "data": {
            "user": {"nickname": "Viewer Two"},
            "commentText": "!lore",
        },
    }

    assert extract_comment_payload(payload) == ("Viewer Two", "!lore")


def test_extract_comment_payload_ignores_non_chat_events() -> None:
    payload = {"event": "gift", "data": {"user": {"nickname": "viewer"}, "content": "rose"}}

    assert extract_comment_payload(payload) is None


def test_fake_reply_returns_stream_text() -> None:
    command = ChatCommand("raw", "Viewer 1", "ask", "hello")
    reply = build_fake_reply(command, "normal")

    assert isinstance(reply, str)
    assert reply
