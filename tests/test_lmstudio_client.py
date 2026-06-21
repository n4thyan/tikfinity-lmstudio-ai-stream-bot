import pytest

from src.lmstudio_client import LMStudioError, _extract_reply


def test_extract_reply_from_chat_completion_shape() -> None:
    data = {
        "choices": [
            {
                "message": {
                    "content": "Hello from PotatoBrain."
                }
            }
        ]
    }

    assert _extract_reply(data) == "Hello from PotatoBrain."


def test_extract_reply_from_legacy_text_shape() -> None:
    data = {
        "choices": [
            {
                "text": "Legacy reply text."
            }
        ]
    }

    assert _extract_reply(data) == "Legacy reply text."


def test_extract_reply_rejects_empty_choices() -> None:
    with pytest.raises(LMStudioError):
        _extract_reply({"choices": []})
