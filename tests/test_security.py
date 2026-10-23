
from fastapi import HTTPException

from aegisops.security import require_api_key


def test_missing_api_key_is_rejected():
    try:
        require_api_key(None)
        raise AssertionError("Expected authentication to fail")
    except HTTPException as exc:
        assert exc.status_code == 401


def test_incorrect_api_key_is_rejected():
    try:
        require_api_key("definitely-the-wrong-key")
        raise AssertionError("Expected authentication to fail")
    except HTTPException as exc:
        assert exc.status_code == 401


def test_correct_api_key_is_accepted(monkeypatch):
    monkeypatch.setattr(
        "aegisops.security.settings.aegisops_api_key",
        "test-only-secret-key",
    )

    assert require_api_key("test-only-secret-key") is None
