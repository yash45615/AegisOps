
from sqlalchemy.orm import Session

from aegisops.models import ProbeRecord


def save_probe_result(
    db: Session,
    probe_type: str,
    target: str,
    result: dict,
) -> ProbeRecord:
    """Persist a network probe result in SQLite."""
    record = ProbeRecord(
        probe_type=probe_type,
        target=target,
        success=result["success"],
        latency_ms=result["latency_ms"],
        status_code=result.get("status_code"),
        error=result.get("error"),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record
