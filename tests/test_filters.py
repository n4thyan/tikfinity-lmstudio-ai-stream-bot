from src.bridge import parse_command
from src.filters import SafetyConfig, filter_ai_output, filter_chat_text, sanitise_username


def test_parse_ask_command() -> None:
    assert parse_command("!ask are you awake", "!") == ("ask", "are you awake")


def test_parse_lore_command_gets_default_prompt() -> None:
    command = parse_command("!lore", "!")

    assert command is not None
    assert command[0] == "lore"
    assert command[1]


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
