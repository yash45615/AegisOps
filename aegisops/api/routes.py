
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from aegisops.database import get_db
from aegisops.models import ProbeRecord
from aegisops.schemas import (
    DnsProbeRequest,
    HttpProbeRequest,
    RemediationRequest,
    SystemMetricsResponse,
    TcpProbeRequest,
    TlsProbeRequest,
)
from aegisops.security import require_api_key
from aegisops.services.network_probes import dns_probe, tcp_probe
from aegisops.services.probe_history import save_probe_result
from aegisops.services.remediation import simulate_remediation
from aegisops.services.system_metrics import get_system_metrics
from aegisops.services.web_probes import http_probe, tls_probe

router = APIRouter(
    prefix="/api/v1",
    tags=["AegisOps API"],
    dependencies=[Depends(require_api_key)],
)

from fastapi import HTTPException

from aegisops.services.incident_manager import (
    list_incidents,
    resolve_incident,
)


@router.get("/status")
def get_status() -> dict[str, str]:
    return {
        "service": "AegisOps",
        "status": "operational",
        "api_version": "v1",
    }


@router.get(
    "/system/metrics",
    response_model=SystemMetricsResponse,
)
def system_metrics() -> dict:
    return get_system_metrics()


@router.post("/probes/tcp")
def run_tcp_probe(
    request: TcpProbeRequest,
    db: Annotated[Session, Depends(get_db)]

) -> dict:
    result = tcp_probe(
        host=request.host,
        port=request.port,
        timeout=request.timeout,
    )
    save_probe_result(
        db,
        "tcp",
        f"{request.host}:{request.port}",
        result,
    )
    
    return result


@router.post("/probes/dns")
def run_dns_probe(
    request: DnsProbeRequest,
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    result = dns_probe(hostname=request.hostname)
    save_probe_result(db, "dns", request.hostname, result)
    return result


@router.post("/probes/http")
def run_http_probe(
    request: HttpProbeRequest,
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    result = http_probe(
        url=request.url,
        timeout=request.timeout,
    )
    save_probe_result(db, "http", request.url, result)
    return result


@router.post("/probes/tls")
def run_tls_probe(
    request: TlsProbeRequest,
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    result = tls_probe(
        hostname=request.hostname,
        port=request.port,
        timeout=request.timeout,
    )
    save_probe_result(
        db,
        "tls",
        f"{request.hostname}:{request.port}",
        result,
    )
    return result


@router.get("/probes/history")
def get_probe_history(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=20, ge=1, le=100),
) -> list[dict]:

    records = (
        db.query(ProbeRecord)
        .order_by(ProbeRecord.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": record.id,
            "probe_type": record.probe_type,
            "target": record.target,
            "success": record.success,
            "latency_ms": record.latency_ms,
            "status_code": record.status_code,
            "error": record.error,
            "created_at": record.created_at,
        }
        for record in records
    ]


@router.get("/incidents")
def get_incidents(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=20, ge=1, le=100),
) -> list[dict]:
    incidents = list_incidents(db, limit)

    return [
        {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "status": incident.status,
            "created_at": incident.created_at,
            "resolved_at": incident.resolved_at,
        }
        for incident in incidents
    ]


@router.post("/incidents/{incident_id}/resolve")
def resolve_incident_endpoint(
    incident_id: int,
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    incident = resolve_incident(db, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return {
        "id": incident.id,
        "title": incident.title,
        "status": incident.status,
        "resolved_at": incident.resolved_at,
    }


@router.post("/remediation/simulate")
def run_simulated_remediation(
    request: RemediationRequest,
) -> dict:
    try:
        return simulate_remediation(
            action=request.action,
            target=request.target,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
