# Observabilidad y Evaluaciones — Cómo Se Mide Este Demo

## Persistencia de Trazas

Cada invocación al agente se persiste en PostgreSQL (puerto 5544, base de datos `fiscal_copilot`).  
La tabla `traces` almacena:

| Campo | Tipo | Descripción |
|---|---|---|
| `trace_id` | UUID | Identificador único de la invocación |
| `tenant_id` | VARCHAR | Sesión o usuario (para multi-tenancy) |
| `model` | VARCHAR | Modelo usado (ej: `claude-sonnet-4-6`) |
| `provider` | VARCHAR | Proveedor (`bedrock`, `mock`) |
| `tokens_in` | INTEGER | Tokens de entrada extraídos del trace |
| `tokens_out` | INTEGER | Tokens de salida extraídos del trace |
| `cost_usd` | NUMERIC | Coste calculado en el momento |
| `latency_ms` | INTEGER | Tiempo total de respuesta en milisegundos |
| `tools_used` | JSONB | Array de herramientas invocadas en la sesión |

## Endpoints de Métricas

| Endpoint | Formato | Contenido |
|---|---|---|
| `GET /metrics` | JSON | Totales, promedios, percentiles por modelo |
| `GET /dashboard` | HTML | Dashboard visual con Chart.js |

Los percentiles se calculan con `PERCENTILE_CONT(0.5) WITHIN GROUP` (mediana) y `PERCENTILE_CONT(0.95)` (p95) directamente en PostgreSQL. No hay dependencia de herramientas de observabilidad externas.

## Harness de Evaluaciones

Las evaluaciones automatizadas viven en `evals/` y se ejecutan con `make evals`.

- **Golden set**: `evals/golden_set.jsonl` — 23 casos de prueba con pregunta, respuesta esperada y contexto de referencia
- **Jueces implementados**:
  - `faithfulness` — mide si la respuesta es fiel al contexto recuperado
  - `answer_relevancy` — mide si la respuesta es relevante a la pregunta
  - `context_precision` — mide si el contexto recuperado era el correcto
  - `geval` — evaluación libre con LLM como juez (G-Eval framework)

## Router Comparison

Una parte del harness compara tres modelos en términos de calidad vs. coste para tareas de clasificación/routing:

| Modelo | Caso de uso esperado |
|---|---|
| Claude Haiku | Clasificación simple, bajo coste |
| Amazon Nova Micro | Alternativa económica AWS-nativa |
| Claude Sonnet 4.6 | Razonamiento complejo, respuesta final |

Los resultados del comparison se guardan en `evals/results/` como JSON con scores por juez y por modelo.

## Coste Total Acumulado

El endpoint `GET /metrics` incluye `total_cost_usd` calculado como suma de todos los registros en `traces`. El presupuesto máximo del proyecto es $15 sobre $100 en créditos AWS.  
Cada respuesta de `POST /chat` incluye el campo `cost_usd` de esa invocación para visibilidad inmediata.
