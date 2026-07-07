import json
import os
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn
from app.mock_agent import mock_invoke_agent

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
    use_mock = os.environ.get("USE_MOCK_AGENT", "0") == "1"

    if use_mock:
        start = time.monotonic()
        result = mock_invoke_agent(request.query)
        latency = (time.monotonic() - start) * 1000

        trace_id = str(uuid.uuid4())
        input_tokens = len(request.query.split()) * 2
        output_tokens = len(result["response"].split()) * 2

        response = AskResponse(
            trace_id=trace_id,
            response=result["response"],
            provider="mock",
            model="local-tools",
            tools_used=result.get("tools_used", []),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=0.0,
            latency_ms=round(latency, 2),
        )

        try:
            async with get_conn() as conn:
                # Ensure tenant exists
                await conn.execute(
                    "INSERT INTO tenants (id, name) VALUES (%s, %s) "
                    "ON CONFLICT (id) DO NOTHING",
                    [request.tenant_id, request.tenant_id],
                )
                # Persist trace
                await conn.execute(
                    "INSERT INTO traces (trace_id, tenant_id, query, response, provider, "
                    "model, input_tokens, output_tokens, cost_usd, latency_ms, tools_used) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    [
                        trace_id, request.tenant_id, request.query,
                        result["response"], "mock", "local-tools",
                        input_tokens, output_tokens, 0.0, round(latency, 2),
                        json.dumps(result.get("tools_used", [])),
                    ],
                )

                # If the tool was generar_reporte_arquitectura, create an approval
                tools_used = result.get("tools_used", [])
                for tool in tools_used:
                    if tool.get("tool_name") == "generar_reporte_arquitectura":
                        await conn.execute(
                            "INSERT INTO approvals (trace_id, tenant_id, action, payload, status) "
                            "VALUES (%s, %s, %s, %s, 'pending')",
                            [
                                trace_id, request.tenant_id,
                                "generar_reporte_arquitectura",
                                json.dumps(tool.get("tool_input", {})),
                            ],
                        )

                await conn.commit()
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to persist trace")

        return response

    raise HTTPException(
        status_code=503,
        detail="Bedrock agent not configured. Set USE_MOCK_AGENT=1 for local mode.",
    )
