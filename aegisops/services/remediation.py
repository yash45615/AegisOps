from datetime import UTC, datetime
from typing import Any

ALLOWED_ACTIONS = {
    "clear_dns_cache_simulated",
    "restart_service_simulated",
    "retry_probe_simulated",
}


def simulate_remediation(
    action: str,
    target: str,
) -> dict[str, Any]:
    """Record a proposed remediation without changing the host."""
    if action not in ALLOWED_ACTIONS:
        raise ValueError("Unsupported remediation action")

    return {
        "action": action,
        "target": target,
        "status": "simulated",
        "system_modified": False,
        "message": "Simulation completed; no system changes were made.",
        "created_at": datetime.now(UTC).isoformat(),
    }
