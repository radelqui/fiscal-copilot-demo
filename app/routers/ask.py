import os
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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
        return AskResponse(
            trace_id=str(uuid.uuid4()),
            response=result["response"],
            provider="mock",
            model="local-tools",
            tools_used=result.get("tools_used", []),
            input_tokens=len(request.query.split()) * 2,
            output_tokens=len(result["response"].split()) * 2,
            cost_usd=0.0,
            latency_ms=round(latency, 2),
        )

    raise HTTPException(
        status_code=503,
        detail="Bedrock agent not configured. Set USE_MOCK_AGENT=1 for local mode.",
    )
