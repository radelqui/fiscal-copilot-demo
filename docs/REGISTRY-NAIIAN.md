# Mapeo Requisitos NAIIAN → Implementación

Este documento mapea cada requisito de la vacante NAIIAN a su implementación concreta en el proyecto.

---

## 1. Bedrock Agents + Action Flows + Permisos + Estados + Trazabilidad

**Implementación**: Agent `2BOPZRAI7X` con Sonnet 4.6, action group `fiscal-tools` (Lambda `fiscal-copilot-tools`).

| Componente | Ubicación |
|-----------|-----------|
| Agent config | `aws/ids.env` (AGENT_ID, ALIAS_ID) |
| Lambda handler | `aws/lambda/handler.py` (3 tools) |
| Client + fallback | `app/bedrock_agent.py` (invoke_agent + mock fallback) |
| Trazas persistidas | `app/routers/demo.py:77-93` → tabla `traces` (PostgreSQL) |
| Estado por traza | `app/db.py:54-66` — trace_id, provider, model, tokens, coste, latencia, tools |

**Cómo probar**: `POST /demo/{token}/ask` → traza con provider=bedrock, tokens > 0, tools registradas.

---

## 2. RAG Multi-Fuente + Source Attribution

**Implementación**: Knowledge Base `5I5RDNA2V1` con S3 Vectors (Titan Embedding V2), corpus fiscal dominicano.

| Componente | Ubicación |
|-----------|-----------|
| KB ID | `aws/ids.env` (asociada al Agent) |
| Corpus local (mock) | `app/rag/corpus/` (4 documentos: ITBIS, NCF, 606/607, calendario) |
| Citas en respuestas | Respuestas del agente real incluyen normativa (Ley 11-92, DGII) |

**Cómo probar**: "¿Fecha límite del 606?" → cita día 15, OFV, normativa.

---

## 3. Structured Outputs + Tool Calling

**Implementación**: Pydantic strict I/O en FastAPI + functionSchema en Lambda.

| Componente | Ubicación |
|-----------|-----------|
| Pydantic models | `app/schemas.py` (TraceSchema, ApprovalSchema, MetricsResponse, etc.) |
| Tool schemas | `aws/lambda/handler.py` (calcular_itbis, validar_ncf, presentar_formato_606) |
| Local tools | `app/tools/` (3 módulos con dataclass output) |
| JSON Schema strict | `evals/router.py:173-189` (OpenAI route con response_format) |

**Cómo probar**: Trace muestra tool_name + tool_input + tool_output estructurado.

---

## 4. Eval Harness: Factualidad / Completitud / Coste / Latencia

**Implementación**: Pipeline de 4 pasos con golden set de 8 casos fiscales.

| Componente | Ubicación |
|-----------|-----------|
| Golden set | `evals/golden_set.jsonl` (8 casos: cálculo, validación, normativa, injection, HITL) |
| Harness | `evals/run_harness.py` (expected_contains OR logic, expected_tools) |
| Judges LLM-as-Judge | `evals/judges.py` (faithfulness, answer_relevancy, context_precision, geval) |
| Router multi-modelo | `evals/router.py` (Haiku, Nova Micro, GPT-4o-mini, Sonnet 4.6) |
| Orquestador | `evals/run_all.py` (4 pasos → reports/comparativa.md) |
| Reporte | `reports/comparativa.md` (tablas coste/latencia/calidad por ruta) |

**Cómo probar**: `make evals` → genera `reports/comparativa.md`.

---

## 5. HITL: Revisión / Aprobación / Rechazo + Estados + Checkpoints

**Implementación**: `presentar_formato_606` con `requireConfirmation=ENABLED` en Bedrock.

| Componente | Ubicación |
|-----------|-----------|
| Spec | `specs/hitl-workflow.md` (retroactiva) |
| returnControl parsing | `app/bedrock_agent.py:147-157` |
| Tabla approvals | `app/db.py:67-79` (status: pending/approved/rejected/executed) |
| Endpoints decide | `app/routers/demo.py:162-193` (POST approve/reject con 404/409/422) |
| UI bandeja | `app/static/demo.html` (sidebar aprobaciones, polling 5s) |
| Tests | `tests/test_f7.py::TestDemoApprovals` (5 tests) |

**Cómo probar**: "Presenta el 606..." → approval pendiente → aprobar en sidebar → status=approved.

---

## 6. Guardrails + Prompt Injection

**Implementación**: Guardrail `xgn38kcg6hrq` en Bedrock (denied topics + prompt attack filter).

| Componente | Ubicación |
|-----------|-----------|
| Guardrail ID | `aws/ids.env` (GUARDRAIL_ID) |
| Golden set injection | `evals/golden_set.jsonl` caso injection-001 |
| XSS protection | `app/static/demo.html:889-892` (escapeHtml + textContent) |
| Rate limiting | `app/auth.py:64-78` (30 req/hour por token) |
| Cost cap | `app/auth.py:81-97` ($2/day) |

**Cómo probar**: "Ignora instrucciones..." → rechazado, se identifica como asistente fiscal.

---

## 7. Trazabilidad: Modelo / Proveedor / Tenant / Coste

**Implementación**: Observabilidad completa en PostgreSQL + endpoints JSON/HTML.

| Componente | Ubicación |
|-----------|-----------|
| Tabla traces | `app/db.py:54-66` (trace_id, tenant, model, tokens, cost, latency, tools) |
| GET /metrics | `app/routers/metrics.py` (totals, p50/p95, by_model, by_tenant) |
| GET /dashboard | `app/routers/dashboard.py` (HTML con tablas por tenant/modelo/proveedor) |
| GET /traces | `app/routers/traces.py` (historial filtrable) |
| enableTrace | `app/bedrock_agent.py:132` (extrae usage real de trace events) |
| Spec | `specs/metrics-endpoint.md` (spec-first) |

**Cómo probar**: `/metrics` → JSON con total_requests, cost, p50, p95. `/dashboard` → tablas HTML.

---

## 8. Desarrollo Agéntico: Specs + Coding Agents + Skills + Evals

**Implementación**: Metodología de 6 fases con gates, sub-agentes paralelos, spec-driven.

| Componente | Ubicación |
|-----------|-----------|
| Metodología | `AGENTS.md` (flujo 6 pasos, patrones, herramientas) |
| Specs | `specs/hitl-workflow.md` (retroactiva) + `specs/metrics-endpoint.md` (spec-first) |
| Informes por fase | `docs/INFORME-F1.md`, `INFORME-F3.md`, `INFORME-F5.md`, `INFORME-F7UI.md`, `INFORME-FINAL.md` |
| Evidencia F2 | `docs/EVIDENCIA-F2.md` (invocaciones reales Bedrock) |
| Tests | 82 tests automatizados (tools, API, auth, HITL, metrics, observabilidad) |

**Cómo probar**: `make test` → 82 passed. `git log` → commits Co-Authored-By: Claude.

---

## 9. Multi-Model Trade-offs

**Implementación**: Router con 4 modelos comparados en coste, latencia, y calidad.

| Modelo | Coste/query | Latencia avg | Estado |
|--------|-------------|-------------|--------|
| Haiku 4.5 | $0.0014 | 2543ms | Activo |
| Nova Micro | $0.00004 | 1473ms | Activo |
| GPT-4o-mini | — | — | Key inválida |
| Sonnet 4.6 | $0.018 | 7628ms | Producción |

| Componente | Ubicación |
|-----------|-----------|
| Router | `evals/router.py` (4 rutas, PRICING dict, Bedrock Converse API) |
| Resultados | `evals/router_results.json` + `reports/comparativa.md` |
| Recomendación | Haiku demo, Nova Micro volumen, Sonnet 4.6 producción |

**Cómo probar**: `make evals` → tabla comparativa en `reports/comparativa.md`.
