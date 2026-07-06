from fastapi import APIRouter

from app.db import get_conn
from app.schemas import TraceSchema, TraceListResponse

router = APIRouter(prefix="/traces", tags=["traces"])


@router.get("", response_model=TraceListResponse)
async def list_traces(
    tenant_id: str | None = None,
    model: str | None = None,
    limit: int = 50,
):
    async with get_conn() as conn:
        conditions = []
        params: list = []
        if tenant_id:
            conditions.append("tenant_id = %s")
            params.append(tenant_id)
        if model:
            conditions.append("model = %s")
            params.append(model)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(min(limit, 200))

        query = (
            f"SELECT trace_id, tenant_id, query, response, provider, model, "
            f"input_tokens, output_tokens, cost_usd, latency_ms, tools_used, "
            f"created_at FROM traces {where} ORDER BY created_at DESC LIMIT %s"
        )
        rows = await conn.execute(query, params)
        results = await rows.fetchall()

        count_query = f"SELECT COUNT(*) FROM traces {where}"
        count_row = await conn.execute(count_query, params[:-1] if params[:-1] else None)
        total = (await count_row.fetchone())[0]

        traces = [
            TraceSchema(
                trace_id=r[0], tenant_id=r[1], query=r[2], response=r[3],
                provider=r[4], model=r[5], input_tokens=r[6], output_tokens=r[7],
                cost_usd=float(r[8]), latency_ms=float(r[9]),
                tools_used=r[10] if isinstance(r[10], list) else [],
                created_at=r[11],
            )
            for r in results
        ]
        return TraceListResponse(
            traces=traces, total=total,
            filters={"tenant_id": tenant_id, "model": model},
        )
