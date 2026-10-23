
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from aegisops.models import IncidentRecord


def create_incident_if_needed(
    db: Session,
    probe_type: str,
    target: str,
    error: str | None,
) -> IncidentRecord | None:
    """Create an incident for a failed probe unless one is already open."""
    title = f"{probe_type.upper()} probe failed: {target}"

    existing = (
        db.query(IncidentRecord)
        .filter(
            IncidentRecord.title == title,
            IncidentRecord.status == "open",
        )
        .first()
    )

    if existing:
        return existing

    incident = IncidentRecord(
        title=title,
        description=error or "The network probe failed.",
        severity="high",
        status="open",
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


def list_incidents(
    db: Session,
    limit: int = 20,
) -> list[IncidentRecord]:
    """Return the most recently created incidents first."""
    return (
        db.query(IncidentRecord)
        .order_by(IncidentRecord.created_at.desc())
        .limit(limit)
        .all()
    )


def resolve_incident(
    db: Session,
    incident_id: int,
) -> IncidentRecord | None:
    """Resolve an open incident. Return None if it does not exist."""
    incident = (
        db.query(IncidentRecord)
        .filter(IncidentRecord.id == incident_id)
        .first()
    )

    if incident is None:
        return None

    if incident.status == "open":
        incident.status = "resolved"
        incident.resolved_at = datetime.now(UTC)
        db.commit()
        db.refresh(incident)

    return incident
