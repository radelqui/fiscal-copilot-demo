import html

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.db import get_conn

router = APIRouter(tags=["dashboard"])

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>¿Cómo Estoy Hecho? — Dashboard de Costes</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }}
        h1 {{ color: #38bdf8; margin-bottom: 0.5rem; }}
        .subtitle {{ color: #94a3b8; margin-bottom: 2rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; border: 1px solid #334155; }}
        .card h2 {{ color: #38bdf8; font-size: 1.1rem; margin-bottom: 1rem; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ text-align: left; padding: 0.5rem; color: #94a3b8; border-bottom: 1px solid #334155; font-size: 0.85rem; }}
        td {{ padding: 0.5rem; border-bottom: 1px solid #1e293b; font-size: 0.9rem; }}
        .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
        .cost {{ color: #4ade80; font-weight: 600; }}
        .total-row {{ background: #0f172a; font-weight: 600; }}
        .total-row .cost {{ color: #facc15; }}
        .empty {{ color: #64748b; text-align: center; padding: 2rem; }}
    </style>
</head>
<body>
    <h1>¿Cómo Estoy Hecho? — Dashboard de Costes</h1>
    <p class="subtitle">Observabilidad por tenant, modelo y proveedor</p>
    <div class="grid">
        <div class="card">
            <h2>Coste por Tenant</h2>
            {tenant_table}
        </div>
        <div class="card">
            <h2>Coste por Modelo</h2>
            {model_table}
        </div>
        <div class="card">
            <h2>Coste por Proveedor</h2>
            {provider_table}
        </div>
    </div>
</body>
</html>"""


def _build_table(rows: list, key_label: str) -> str:
    if not rows:
        return '<p class="empty">Sin datos aún</p>'
    header = (
        f"<table><thead><tr><th>{key_label}</th><th class='num'>Trazas</th>"
        f"<th class='num'>Tokens In</th><th class='num'>Tokens Out</th>"
        f"<th class='num'>Latencia Avg (ms)</th><th class='num'>Coste (USD)</th>"
        f"</tr></thead><tbody>"
    )
    body = ""
    total_cost = 0.0
    total_traces = 0
    for r in rows:
        key, traces, tokens_in, tokens_out, avg_lat, cost = r
        total_cost += float(cost)
        total_traces += traces
        body += (
            f"<tr><td>{html.escape(str(key))}</td><td class='num'>{traces}</td>"
            f"<td class='num'>{tokens_in:,}</td><td class='num'>{tokens_out:,}</td>"
            f"<td class='num'>{float(avg_lat):.1f}</td>"
            f"<td class='num cost'>${float(cost):.4f}</td></tr>"
        )
    body += (
        f"<tr class='total-row'><td>TOTAL</td><td class='num'>{total_traces}</td>"
        f"<td colspan='3'></td><td class='num cost'>${total_cost:.4f}</td></tr>"
    )
    return header + body + "</tbody></table>"


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    async with get_conn() as conn:
        by_tenant = await conn.execute(
            "SELECT tenant_id, COUNT(*), SUM(input_tokens), SUM(output_tokens), "
            "AVG(latency_ms), SUM(cost_usd) FROM traces GROUP BY tenant_id ORDER BY SUM(cost_usd) DESC"
        )
        tenant_rows = await by_tenant.fetchall()

        by_model = await conn.execute(
            "SELECT model, COUNT(*), SUM(input_tokens), SUM(output_tokens), "
            "AVG(latency_ms), SUM(cost_usd) FROM traces GROUP BY model ORDER BY SUM(cost_usd) DESC"
        )
        model_rows = await by_model.fetchall()

        by_provider = await conn.execute(
            "SELECT provider, COUNT(*), SUM(input_tokens), SUM(output_tokens), "
            "AVG(latency_ms), SUM(cost_usd) FROM traces GROUP BY provider ORDER BY SUM(cost_usd) DESC"
        )
        provider_rows = await by_provider.fetchall()

    html = DASHBOARD_HTML.format(
        tenant_table=_build_table(tenant_rows, "Tenant"),
        model_table=_build_table(model_rows, "Modelo"),
        provider_table=_build_table(provider_rows, "Proveedor"),
    )
    return HTMLResponse(content=html)
