from datetime import datetime, timezone

from fastapi import APIRouter

from app.db import get_conn
from app.schemas import (
    MetricsResponse,
    MetricsModelBreakdown,
    MetricsTenantBreakdown,
)

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_model=MetricsResponse)
async def metrics():
    async with get_conn() as conn:
        totals = await conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(cost_usd), 0), "
            "COALESCE(AVG(latency_ms), 0) FROM traces"
        )
        total_row = await totals.fetchone()
        total_requests = total_row[0]
        total_cost = float(total_row[1])
        avg_latency = float(total_row[2])

        if total_requests > 0:
            pct = await conn.execute(
                "SELECT "
                "PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) AS p50, "
                "PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95 "
                "FROM traces"
            )
            pct_row = await pct.fetchone()
            p50 = float(pct_row[0])
            p95 = float(pct_row[1])
        else:
            p50 = 0.0
            p95 = 0.0

        by_model_rows = await conn.execute(
            "SELECT model, COUNT(*), SUM(cost_usd), AVG(latency_ms) "
            "FROM traces GROUP BY model ORDER BY SUM(cost_usd) DESC"
        )
        model_data = await by_model_rows.fetchall()

        by_tenant_rows = await conn.execute(
            "SELECT tenant_id, COUNT(*), SUM(cost_usd) "
            "FROM traces GROUP BY tenant_id ORDER BY SUM(cost_usd) DESC"
        )
        tenant_data = await by_tenant_rows.fetchall()

    return MetricsResponse(
        total_requests=total_requests,
        total_cost_usd=round(total_cost, 6),
        avg_latency_ms=round(avg_latency, 2),
        latency_p50_ms=round(p50, 2),
        latency_p95_ms=round(p95, 2),
        by_model=[
            MetricsModelBreakdown(
                model=r[0], requests=r[1],
                cost_usd=round(float(r[2]), 6),
                avg_latency_ms=round(float(r[3]), 2),
            )
            for r in model_data
        ],
        by_tenant=[
            MetricsTenantBreakdown(
                tenant_id=r[0], requests=r[1],
                cost_usd=round(float(r[2]), 6),
            )
            for r in tenant_data
        ],
        generated_at=datetime.now(timezone.utc),
    )
