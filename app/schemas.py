from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TenantSchema(BaseModel):
    id: str
    name: str


class TraceSchema(BaseModel):
    trace_id: str
    tenant_id: str
    query: str
    response: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    tools_used: list[dict[str, Any]]
    created_at: datetime


class TraceListResponse(BaseModel):
    traces: list[TraceSchema]
    total: int
    filters: dict[str, str | None]


class ApprovalSchema(BaseModel):
    id: int
    trace_id: str | None
    tenant_id: str
    action: str
    payload: dict[str, Any]
    status: str
    decided_by: str | None
    decided_at: datetime | None
    created_at: datetime


class ApprovalDecision(BaseModel):
    decision: str = Field(..., pattern="^(approved|rejected)$")
    decided_by: str = Field(default="demo-user")


class ApprovalListResponse(BaseModel):
    approvals: list[ApprovalSchema]
    total: int


class FacturaSchema(BaseModel):
    id: int
    ncf: str
    rnc: str
    razon_social: str
    monto: float
    itbis: float
    periodo: str
    tipo_ncf: str
    estado: str
    tenant_id: str


class DashboardCostRow(BaseModel):
    group_key: str
    total_cost_usd: float
    total_traces: int
    avg_latency_ms: float
    total_input_tokens: int
    total_output_tokens: int


class HealthResponse(BaseModel):
    status: str
    version: str
    mock_mode: bool
    db_connected: bool
    db_tables: int


class MetricsModelBreakdown(BaseModel):
    model: str
    requests: int
    cost_usd: float
    avg_latency_ms: float


class MetricsTenantBreakdown(BaseModel):
    tenant_id: str
    requests: int
    cost_usd: float


class MetricsResponse(BaseModel):
    total_requests: int
    total_cost_usd: float
    avg_latency_ms: float
    latency_p50_ms: float
    latency_p95_ms: float
    by_model: list[MetricsModelBreakdown]
    by_tenant: list[MetricsTenantBreakdown]
    generated_at: datetime
