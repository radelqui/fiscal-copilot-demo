# Spec: GET /metrics

**Status**: Spec written — implementation pending  
**Fecha**: 2026-07-06  
**Tipo**: Spec-first (escrita ANTES de implementar)

## Objetivo

Endpoint JSON con métricas agregadas de uso del sistema. Consumible por Grafana, Datadog, o alertas internas. No requiere autenticación (datos agregados, no PII).

## Endpoint

```
GET /metrics
Content-Type: application/json
```

## Response Schema

```json
{
  "total_requests": 42,
  "total_cost_usd": 0.1234,
  "avg_latency_ms": 1523.4,
  "latency_p50_ms": 1200.0,
  "latency_p95_ms": 3500.0,
  "by_model": [
    {
      "model": "eu.anthropic.claude-sonnet-4-6-20250514-v1:0",
      "requests": 30,
      "cost_usd": 0.09,
      "avg_latency_ms": 1800.0
    }
  ],
  "by_tenant": [
    {
      "tenant_id": "demo-visitor",
      "requests": 42,
      "cost_usd": 0.1234
    }
  ],
  "generated_at": "2026-07-06T21:00:00Z"
}
```

## Pydantic Models

```python
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
```

## SQL Queries

### Totals
```sql
SELECT COUNT(*), COALESCE(SUM(cost_usd), 0), COALESCE(AVG(latency_ms), 0)
FROM traces
```

### Percentiles (p50, p95)
```sql
SELECT
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) AS p50,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95
FROM traces
```

### By model
```sql
SELECT model, COUNT(*), SUM(cost_usd), AVG(latency_ms)
FROM traces GROUP BY model ORDER BY SUM(cost_usd) DESC
```

### By tenant
```sql
SELECT tenant_id, COUNT(*), SUM(cost_usd)
FROM traces GROUP BY tenant_id ORDER BY SUM(cost_usd) DESC
```

## Archivos a crear/modificar

- `app/routers/metrics.py` — nuevo router
- `app/schemas.py` — agregar MetricsResponse, MetricsModelBreakdown, MetricsTenantBreakdown
- `app/main.py` — include_router(metrics.router)
- `tests/test_metrics.py` — tests

## Tests requeridos

1. `test_metrics_empty_db` — con BD vacía, retorna total_requests=0, arrays vacíos
2. `test_metrics_with_data` — insertar N trazas, verificar totals y breakdowns
3. `test_metrics_percentiles` — verificar p50/p95 con datos conocidos
4. `test_metrics_response_schema` — verificar que respuesta valida contra Pydantic model

## Criterios de aceptación

- [ ] Endpoint retorna 200 con JSON válido
- [ ] Schema Pydantic valida la respuesta
- [ ] Percentiles calculados con PERCENTILE_CONT (no aproximación)
- [ ] Sin autenticación requerida
- [ ] 4 tests pasan
