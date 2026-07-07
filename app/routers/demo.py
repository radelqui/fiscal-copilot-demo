import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from app.auth import validate_token, check_rate_limit, check_daily_cost_cap
from app.bedrock_agent import invoke_agent
from app.db import get_conn
from app.schemas import ApprovalDecision

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demo", tags=["demo"])

_demo_html: str | None = None


def _load_demo_html() -> str:
    global _demo_html
    if _demo_html is None:
        path = Path(__file__).parent.parent / "static" / "demo.html"
        _demo_html = path.read_text(encoding="utf-8")
    return _demo_html


class DemoAskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    tenant_id: str = Field(default="demo-visitor")


async def _require_token(token: str):
    """Validate token or raise 401."""
    if not await validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired demo token")


@router.get("/{token}", response_class=HTMLResponse)
async def demo_page(token: str):
    """Serve the demo UI with injected token."""
    await _require_token(token)
    raw_html = _load_demo_html()
    inject = (
        f"<script>const DEMO_TOKEN={json.dumps(token)};"
        f"const API_BASE='/demo/'+DEMO_TOKEN;</script>\n"
    )
    page = raw_html.replace("<head>", "<head>\n" + inject, 1)
    return HTMLResponse(content=page)


@router.get("/{token}/architecture", response_class=HTMLResponse)
async def architecture_page(token: str):
    """Serve the architecture diagram page."""
    await _require_token(token)
    path = Path(__file__).parent.parent / "static" / "architecture.html"
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@router.post("/{token}/ask")
async def demo_ask(token: str, request: DemoAskRequest):
    """Chat endpoint with auth, rate limit, and cost cap."""
    await _require_token(token)
    check_rate_limit(token)
    await check_daily_cost_cap()

    result = await invoke_agent(
        query=request.query,
        tenant_id=request.tenant_id,
    )

    trace_id = str(uuid.uuid4())
    input_tokens = result.get("input_tokens", 0)
    output_tokens = result.get("output_tokens", 0)
    cost_usd = result.get("cost_usd", 0.0)
    latency_ms = result.get("latency_ms", 0.0)
    provider = result.get("provider", "mock")
    model = result.get("model", "local-tools")
    tools_used = result.get("tools_used", [])

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
                    result.get("response", ""), provider, model,
                    input_tokens, output_tokens, cost_usd, latency_ms,
                    json.dumps(tools_used),
                ],
            )

            if result.get("requires_confirmation"):
                await conn.execute(
                    "INSERT INTO approvals (trace_id, tenant_id, action, payload, status) "
                    "VALUES (%s, %s, %s, %s, 'pending')",
                    [
                        trace_id, request.tenant_id,
                        "presentar_formato_606",
                        json.dumps(result.get("confirmation_payload") or {}),
                    ],
                )

            await conn.commit()
    except Exception:
        logger.exception("Failed to persist demo trace")

    return JSONResponse(content={
        "response": result.get("response", ""),
        "trace": {
            "provider": provider,
            "model": model,
            "tokens_in": input_tokens,
            "tokens_out": output_tokens,
            "cost_usd": cost_usd,
            "latency_ms": latency_ms,
            "tools": tools_used,
        },
    })


@router.get("/{token}/approvals")
async def demo_approvals(token: str, status: str | None = None):
    """List approvals (optionally filtered by status)."""
    await _require_token(token)

    async with get_conn() as conn:
        if status:
            rows = await conn.execute(
                "SELECT id, action, payload, status, created_at "
                "FROM approvals WHERE status = %s ORDER BY created_at DESC",
                [status],
            )
        else:
            rows = await conn.execute(
                "SELECT id, action, payload, status, created_at "
                "FROM approvals ORDER BY created_at DESC"
            )
        results = await rows.fetchall()

    approvals = []
    for r in results:
        payload = r[2]
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except (json.JSONDecodeError, TypeError):
                payload = {}
        approvals.append({
            "id": r[0],
            "action": r[1],
            "payload": payload if isinstance(payload, dict) else {},
            "status": r[3],
            "created_at": r[4].isoformat() if r[4] else None,
        })

    return JSONResponse(content=approvals)


@router.post("/{token}/approvals/{approval_id}/decide")
async def demo_decide(token: str, approval_id: int, decision: ApprovalDecision):
    """Decide on an approval (approve/reject)."""
    await _require_token(token)

    async with get_conn() as conn:
        row = await conn.execute(
            "SELECT id, status FROM approvals WHERE id = %s", [approval_id]
        )
        existing = await row.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Approval not found")
        if existing[1] != "pending":
            raise HTTPException(
                status_code=409,
                detail=f"Approval already decided: {existing[1]}",
            )

        now = datetime.now(timezone.utc)
        await conn.execute(
            "UPDATE approvals SET status = %s, decided_by = %s, decided_at = %s "
            "WHERE id = %s",
            [decision.decision, decision.decided_by, now, approval_id],
        )
        await conn.commit()

    return JSONResponse(content={
        "ok": True,
        "id": approval_id,
        "decision": decision.decision,
    })
