
import pytest

from aegisops.services.remediation import (
    ALLOWED_ACTIONS,
    simulate_remediation,
)


@pytest.mark.parametrize("action", sorted(ALLOWED_ACTIONS))
def test_allowed_actions_are_simulated(action):
    result = simulate_remediation(action, "example.com")

    assert result["action"] == action
    assert result["target"] == "example.com"
    assert result["status"] == "simulated"
    assert result["system_modified"] is False
    assert result["created_at"]


def test_unsupported_action_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unsupported remediation action",
    ):
        simulate_remediation("execute-arbitrary-command", "localhost")
