
from typing import Any

from pydantic import BaseModel, Field


class RemediationRequest(BaseModel):
    action: str = Field(min_length=1, max_length=80)
    target: str = Field(min_length=1, max_length=253)

class SystemMetricsResponse(BaseModel):
    platform: str
    platform_release: str
    cpu_percent: float = Field(ge=0, le=100)
    cpu_count: int | None
    memory: dict[str, Any]
    disk: dict[str, Any]


class TcpProbeRequest(BaseModel):
    host: str = Field(min_length=1, max_length=253)
    port: int = Field(ge=1, le=65535)
    timeout: float = Field(default=2.0, ge=0.2, le=5.0)


class DnsProbeRequest(BaseModel):
    hostname: str = Field(min_length=1, max_length=253)


class HttpProbeRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)
    timeout: float = Field(default=5.0, ge=0.5, le=15.0)


class TlsProbeRequest(BaseModel):
    hostname: str = Field(min_length=1, max_length=253)
    port: int = Field(default=443, ge=1, le=65535)
    timeout: float = Field(default=5.0, ge=0.5, le=15.0)


from datetime import datetime


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime
    resolved_at: datetime | None
