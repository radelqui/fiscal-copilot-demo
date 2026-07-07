import json
import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.bedrock_agent import invoke_agent as bedrock_invoke_agent
from app.db import get_conn

router = APIRouter()


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    tenant_id: str = Field(default="demo-tenant")


class ToolTrace(BaseModel):
    tool_name: str
    tool_input: dict[str, Any]
    tool_output: dict[str, Any]


class AskResponse(BaseModel):
    trace_id: str
    response: str
    provider: str
    model: str
    tools_used: list[ToolTrace]
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    result = await bedrock_invoke_agent(request.query, tenant_id=request.tenant_id)

    trace_id = str(uuid.uuid4())

    response = AskResponse(
        trace_id=trace_id,
        response=result["response"],
        provider=result.get("provider", "bedrock"),
        model=result.get("model", "unknown"),
        tools_used=result.get("tools_used", []),
        input_tokens=result.get("input_tokens", 0),
        output_tokens=result.get("output_tokens", 0),
        cost_usd=result.get("cost_usd", 0.0),
        latency_ms=result.get("latency_ms", 0.0),
    )

    try:
        async with get_conn() as conn:
            await conn.execute(
                "INSERT INTO tenants (id, name) VALUES (%s, %s) "
                "ON CONFLICT (id) DO NOTHING",
                [request.tenant_id, request.tenant_id],
            )
            await conn.execute(
                "INSERT INTO traces (trace_id, tenant_id, query, response, provider, "
                "model, input_tokens, output_tokens, cost_usd, latency_ms, tools_used) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    trace_id, request.tenant_id, request.query,
                    result["response"], result.get("provider", "bedrock"),
                    result.get("model", "unknown"),
                    result.get("input_tokens", 0), result.get("output_tokens", 0),
                    result.get("cost_usd", 0.0), result.get("latency_ms", 0.0),
                    json.dumps(result.get("tools_used", [])),
                ],
            )

            # HITL: create approval if needed
            if result.get("requires_confirmation"):
                await conn.execute(
                    "INSERT INTO approvals (trace_id, tenant_id, action, payload, status) "
                    "VALUES (%s, %s, %s, %s, 'pending')",
                    [
                        trace_id, request.tenant_id,
                        "generar_reporte_arquitectura",
                        json.dumps(result.get("confirmation_payload", {})),
                    ],
                )

            await conn.commit()
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed to persist trace")

    return response
