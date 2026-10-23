
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from aegisops.database import Base
from aegisops.services.incident_manager import (
    create_incident_if_needed,
    list_incidents,
    resolve_incident,
)


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    test_session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    session = test_session()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_failed_probe_creates_incident(db_session):
    incident = create_incident_if_needed(
        db_session,
        probe_type="tcp",
        target="127.0.0.1:1",
        error="Connection refused",
    )

    assert incident is not None
    assert incident.status == "open"
    assert incident.severity == "high"
    assert "Connection refused" in incident.description


def test_repeated_failure_reuses_open_incident(db_session):
    first = create_incident_if_needed(
        db_session, "dns", "invalid.invalid", "Lookup failed"
    )
    second = create_incident_if_needed(
        db_session, "dns", "invalid.invalid", "Lookup failed again"
    )

    assert first.id == second.id
    assert len(list_incidents(db_session)) == 1


def test_incident_can_be_resolved(db_session):
    incident = create_incident_if_needed(
        db_session, "http", "https://example.com", "Timeout"
    )

    resolved = resolve_incident(db_session, incident.id)

    assert resolved is not None
    assert resolved.status == "resolved"
    assert resolved.resolved_at is not None


def test_missing_incident_returns_none(db_session):
    assert resolve_incident(db_session, 99999) is None
