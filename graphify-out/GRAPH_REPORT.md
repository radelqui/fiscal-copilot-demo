# Graph Report - fiscal-copilot  (2026-07-07)

## Corpus Check
- 76 files · ~44,983 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1021 nodes · 1384 edges · 81 communities (71 shown, 10 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `98419494`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]

## God Nodes (most connected - your core abstractions)
1. `═══════════════════════════════════════════════════════════════════` - 36 edges
2. `get_conn()` - 29 edges
3. `Evidencia` - 26 edges
4. `detectar_requisito()` - 23 edges
5. `ApprovalDecision` - 20 edges
6. `mock_invoke_agent()` - 17 edges
7. `invoke_agent()` - 16 edges
8. `_invoke_bedrock()` - 15 edges
9. `_estimate_cost()` - 15 edges
10. `TestDetectarRequisito` - 14 edges

## Surprising Connections (you probably didn't know these)
- `TestDetectarRequisito` --uses--> `ResultadoVerificacion`  [INFERRED]
  tests/test_tools.py → app/tools/donde_verificar.py
- `TestDondeVerificar` --uses--> `ResultadoVerificacion`  [INFERRED]
  tests/test_tools.py → app/tools/donde_verificar.py
- `TestExplicarComponente` --uses--> `ResultadoVerificacion`  [INFERRED]
  tests/test_tools.py → app/tools/donde_verificar.py
- `TestGenerarReporteArquitectura` --uses--> `ResultadoVerificacion`  [INFERRED]
  tests/test_tools.py → app/tools/donde_verificar.py
- `TestDetectarRequisito` --uses--> `ResultadoComponente`  [INFERRED]
  tests/test_tools.py → app/tools/explicar_componente.py

## Import Cycles
- 1-file cycle: `app/main.py -> app/main.py`
- 2-file cycle: `app/auth.py -> app/main.py -> app/auth.py`

## Communities (81 total, 10 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.29
Nodes (5): str, TestDondeVerificar, ResultadoComponente, generar_reporte_arquitectura(), ResultadoReporte

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (46): ═══════════════════════════════════════════════════════════════════, 0.1 La Ley del Estilo Fable (cómo trabajo yo; así trabajáis vosotros), 0-BIS. DÓNDE VIVE LA SOLUCIÓN (decisión de arquitectura, cerrada), 0. EL PROTOCOLO — CÓMO SE TRABAJA (heredado del PLAN-EJECUCION-MAESTRO, innegociable), ═══════════════════════════════════════════════════════════════════, ═══════════════════════════════════════════════════════════════════, ═══════════════════════════════════════════════════════════════════, ═══════════════════════════════════════════════════════════════════ (+38 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (11): ApprovalDecision, AskResponse, int, F3 integration tests — backend + PostgreSQL + observability.  Requires PostgreSQ, Demonstrates that Pydantic REJECTS malformed structured outputs., TestApprovals, TestAskWithPersistence, TestDashboard (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (26): 1.1 PostgreSQL 16 en Docker, 1.2 Esquema de base de datos (5 tablas), 1.3 Seed data, 1.4 Endpoints FastAPI, 1.5 Observabilidad, 1.6 HITL (Human-in-the-Loop), 1. Qué se hizo, 2.1 Tests: 57/57 passed (+18 more)

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (22): check_rate_limit(), create_demo_tokens_table(), ensure_demo_token(), generate_token(), main(), int, str, Demo token authentication, rate limiting, and cost cap.  Tokens are path-based: (+14 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (20): 1.1 Estructura del proyecto, 1.2 Corpus DGII (4 documentos, normativa real verificable), 1.3 Tools Python (deterministas, pure stdlib), 1.4 FastAPI skeleton (USE_MOCK_AGENT=1), 1.5 AWS CLI, 1. Qué se hizo, 2.1 Tests: 37/37 passed, 2.2 Smoke test servidor (+12 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (56): Reset all rate limit counters (for testing)., reset_rate_limits(), CaseResult, Client, available_routes(), _estimate_cost(), get_system_prompt(), _load_openai_key() (+48 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (16): Campos requeridos por registro, Campos requeridos por registro, Contexto General, Cruces de Información por la DGII, Errores comunes que generan inconsistencias, Formato 606 — Compras de Bienes y Servicios, Formato 607 — Ventas de Bienes y Servicios, Formato 608 — Comprobantes Anulados (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (39): 1. Bedrock Agents + Action Groups, 2. RAG con S3 Vectors (Knowledge Base), 3. Guardrails, 4. Structured Outputs (Pydantic), 5. Human-in-the-Loop (HITL), 6. Evaluaciones LLM (Ragas + DeepEval), 7. Observabilidad por tenant y coste, 8. Desarrollo agéntico (spec-driven + arquitecto/sub-agentes) (+31 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (4): Verify that the response matches the strict Pydantic model., Verify that the response matches the strict Pydantic model., TestAsk, TestHealth

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (13): Año Fiscal, Calendario Fiscal — República Dominicana, Impuesto a los Activos, Impuesto al Patrimonio Inmobiliario (IPI), Impuesto Sobre la Renta (ISR) — Personas Jurídicas, Impuesto Sobre la Renta — Personas Físicas, Obligaciones Anuales, Obligaciones Mensuales (+5 more)

### Community 11 - "Community 11"
Cohesion: 0.17
Nodes (11): Base Imponible, Bienes y Servicios Exentos, Compensación ITBIS Crédito vs. Débito, Cómo Calcular el ITBIS, Declaración y Pago, Definición y Marco Legal, ITBIS — Impuesto a la Transferencia de Bienes Industrializados y Servicios, Quién Paga y Quién Recauda (+3 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (11): O10. ESTADO FASE H A 2026-07-06 (cierre de día) + RELAJACIONES DE CARLOS, O1. REALIDAD CORREGIDA (verificada, no asumida), O2. ORDEN NUEVO: MVP-PRIMERO (sustituye la secuencia rígida F1→F8), O3. RIESGO #1 — MODEL ACCESS BEDROCK EN CUENTA FREE-TIER NUEVA, O4. DECISIÓN F4 PASO 1 — CERRADA POR EL SM (no esperar a Carlos), O5. RECORTES (menos teatro, misma cobertura de requisitos), O6. TOKEN DE INVITADO — PATH-BASED, O7. LO QUE SE HACE YA, SIN AWS (F1 ampliada — empezar HOY) (+3 more)

### Community 13 - "Community 13"
Cohesion: 0.18
Nodes (10): Anulación de NCF, Definición y Autoridad, Formato e-NCF (Electrónico — vigente), Formato Legado (B-series), Formatos: Legado vs. Electrónico, Importancia en Declaraciones, NCF — Números de Comprobantes Fiscales, Reglas de Validación (+2 more)

### Community 14 - "Community 14"
Cohesion: 0.20
Nodes (9): Comandos frecuentes, Fiscal Copilot — Demo Total (NAIIAN), Presupuesto, PROHIBIDO, Proyecto, Puertos, Región AWS, Reglas de oro (+1 more)

### Community 15 - "Community 15"
Cohesion: 0.20
Nodes (9): Calendario fiscal, Conocimiento base, Cuándo usar este skill, Formato NCF, Formatos 606/607, ITBIS, Retenciones comunes, Skill: Normativa Fiscal Dominicana (DGII) (+1 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (16): Agentes disponibles, AGENTS.md — Fiscal Copilot, Comandos, Convenciones de desarrollo agéntico, Evidencia de Desarrollo Agéntico, Fases de Desarrollo, Flujo de trabajo, Flujo por Fase (+8 more)

### Community 17 - "Community 17"
Cohesion: 0.50
Nodes (3): Antes de crear cualquier recurso:, Después de crear:, Reglas inquebrantables:

### Community 18 - "Community 18"
Cohesion: 0.50
Nodes (3): Estilo:, Reglas:, Stack:

### Community 19 - "Community 19"
Cohesion: 0.50
Nodes (3): Output de comparativa:, Reglas:, Responsabilidades:

### Community 20 - "Community 20"
Cohesion: 0.50
Nodes (3): Contexto (lo recibe del arquitecto):, Reglas:, Tu proceso:

### Community 21 - "Community 21"
Cohesion: 0.50
Nodes (3): Completado y verificado, Done Registry, Intentado pero fallido

### Community 24 - "Community 24"
Cohesion: 0.50
Nodes (3): Estado de sesion (pre-compact auto-save), NOTA, Session State

### Community 25 - "Community 25"
Cohesion: 0.33
Nodes (5): Completed, Date: 2026-07-07, ORDEN FINAL: FISCAL FUERA TOTAL → ¿Cómo Estoy Hecho?, Status: COMPLETE, Task

### Community 32 - "Community 32"
Cohesion: 0.06
Nodes (12): demo_token(), _get_valid_token(), str, F7-UI tests — demo token auth, rate limiting, cost cap, UI endpoints.  Requires, Fetch a valid demo token from the DB via health-triggering lifespan., Get a valid demo token (created by lifespan)., TestArchitecture, TestCostCap (+4 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (23): _estimate_cost(), float, int, Estimate cost for Claude Sonnet on Bedrock (per 1K tokens)., Estimate cost for Claude Sonnet on Bedrock (per 1K tokens)., Estimate cost for Claude Sonnet on Bedrock (per 1K tokens)., Estimate cost for Claude Sonnet on Bedrock (per 1K tokens)., Estimate cost for Claude Sonnet on Bedrock (per 1K tokens). (+15 more)

### Community 34 - "Community 34"
Cohesion: 0.18
Nodes (13): bool, float, int, str, calcular_itbis(), donde_verificar(), explicar_componente(), generar_reporte_arquitectura() (+5 more)

### Community 35 - "Community 35"
Cohesion: 0.12
Nodes (16): A. Backend en tmux (NO systemd), Archivos nuevos/modificados, B. Demo UI (HTML+JS vanilla), C. Token auth path-based, D. Bedrock Agent client con fallback, E. Demo router, Edge cases, Entregables (+8 more)

### Community 36 - "Community 36"
Cohesion: 0.09
Nodes (23): 401 sin token, A1: Batería de preguntas — 10/10 PASS, A2: Endpoints — 5/5 PASS, A3: HITL — 2/2 PASS, A4: Seguridad — 11/11 BLOCKED, 0 leaks, B1: Approvals por sesión, B3: Timeout 502, Cambios adicionales (+15 more)

### Community 37 - "Community 37"
Cohesion: 0.20
Nodes (9): Agent: 2BOPZRAI7X (modelo: eu.anthropic.claude-sonnet-4-6), Alias demo: TJRZR1FCDY (PREPARED), EVIDENCIA F2 — stack Bedrock (ejecutado por el SM, 2026-07-06), GATE F2 — invokes reales, GATE F2 REAL (post-habilitacion Sonnet) 2026-07-06T19:36:09Z, invoke test itbis 118000 incluido:, Lambda: arn:aws:lambda:eu-central-1:324908171132:function:fiscal-copilot-tools, Medio de presentación (+1 more)

### Community 38 - "Community 38"
Cohesion: 0.25
Nodes (7): Componentes nuevos, Evidencia — Mapeo Requisito-Vacante → Componente Correcto, Fecha: 2026-07-07, Formato de respuesta, Gate: 9/9 requisitos mapeados correctamente, Nota sobre guardrails (requisito 6), Verificación local

### Community 39 - "Community 39"
Cohesion: 0.15
Nodes (12): 1. Entregables, 2. Resultados del Pipeline, 3. Decisiones Técnicas, 4. Limitaciones Conocidas, 5. Recomendación, 6. Verificación, 7. Commits, Harness (backend mock :7020) (+4 more)

### Community 40 - "Community 40"
Cohesion: 0.22
Nodes (8): 1. Harness — Backend Mock (:7020), 2. Métricas de Calidad (LLM-as-Judge), 3. Comparativa de Rutas (Modelos), 4. Presupuesto, 5. Conclusiones y Trade-offs, Comparativa de Rutas — Fiscal Copilot Evals, Detalle por caso, Recomendación

### Community 41 - "Community 41"
Cohesion: 0.50
Nodes (3): bedrock-haiku, bedrock-nova-micro, openai-gpt4o-mini

### Community 44 - "Community 44"
Cohesion: 0.50
Nodes (8): Architecture, ¿Cómo Estoy Hecho? — Meta-Demo, Fiscal Copilot, Fiscal Copilot — Meta-Demo, License, NAIIAN Requirements Matrix, Project Structure, Quickstart

### Community 46 - "Community 46"
Cohesion: 0.10
Nodes (19): 1. Resumen Ejecutivo, 2. Entregables por Fase, 3. Arquitectura Final, 4.1 Bloque 1: FIX Observabilidad Real, 4.2 Bloque 2: README.md, 4.3 Bloque 3: DEMO-GUIDE.md, 4.4 Bloque 4: Specs, 4.5 Bloque 5: Higiene (+11 more)

### Community 47 - "Community 47"
Cohesion: 0.14
Nodes (13): Archivos a crear/modificar, By model, By tenant, Criterios de aceptación, Endpoint, Objetivo, Percentiles (p50, p95), Pydantic Models (+5 more)

### Community 48 - "Community 48"
Cohesion: 0.08
Nodes (29): 1. Meta-pregunta: Composición del agente, 2. Meta-pregunta: RAG, 2. Meta-pregunta: RAG multi-fuente, 3. Tool: Explicar componente, 3. Tool fiscal: ITBIS, 4. HITL vivo: Formato 606, 4. HITL vivo: Generar reporte, 5. Meta-pregunta: Observabilidad (+21 more)

### Community 49 - "Community 49"
Cohesion: 0.20
Nodes (9): Archivos involucrados, Configuración AWS, Endpoints, Flujo, GET /demo/{token}/approvals?status=pending, Objetivo, POST /demo/{token}/approvals/{id}/decide, Spec: HITL Workflow (Retroactive) (+1 more)

### Community 50 - "Community 50"
Cohesion: 0.28
Nodes (7): _insert_trace(), Tests for GET /metrics endpoint., Helper to insert a trace directly via the ask endpoint won't work for controlled, Verify that /metrics returns valid schema and zero values when traces table is e, test_metrics_empty_db(), test_metrics_percentiles(), test_metrics_with_data()

### Community 51 - "Community 51"
Cohesion: 0.18
Nodes (10): 1. Bedrock Agents + Action Flows + Permisos + Estados + Trazabilidad, 2. RAG Multi-Fuente + Source Attribution, 3. Structured Outputs + Tool Calling, 4. Eval Harness: Factualidad / Completitud / Coste / Latencia, 5. HITL: Revisión / Aprobación / Rechazo + Estados + Checkpoints, 6. Guardrails + Prompt Injection, 7. Trazabilidad: Modelo / Proveedor / Tenant / Coste, 8. Desarrollo Agéntico: Specs + Coding Agents + Skills + Evals (+2 more)

### Community 52 - "Community 52"
Cohesion: 0.08
Nodes (25): A1: Batería de Preguntas (10/10 PASS), A2: Endpoints y Botones (5/5 PASS), A3: HITL (Human-in-the-Loop) — PASS, A4: Ataques de Seguridad (11/11 BLOCKED, 0 leaks), B1: Approvals por Sesión, B3: Timeout / 502 Prevention, Conclusión, Configuración del Guardrail (+17 more)

### Community 53 - "Community 53"
Cohesion: 0.40
Nodes (4): Cómo usar /architecture, Cómo usar el Registry, Tabla de Verificación, Verificación en Vivo — Registry como Fuente de Verdad

### Community 54 - "Community 54"
Cohesion: 0.13
Nodes (14): APERTURA (30 seg, antes de tocar nada), CIERRE (20 seg), GUIÓN DE ENTREVISTA — "¿Cómo Estoy Hecho?", NOTA HONESTA (por si preguntan pegas), PASO 1 — El agente explica su propio Bedrock Agent, PASO 2 — Verificación en vivo (el momento diferenciador), PASO 3 — El RAG, PASO 4 — Tool calling + structured output (componente real) (+6 more)

### Community 55 - "Community 55"
Cohesion: 0.18
Nodes (22): answer_relevancy(), context_precision(), evaluate_all_metrics(), _extract_score(), faithfulness(), _geval_fallback(), geval_fiscal_correctness(), _judge_call() (+14 more)

### Community 58 - "Community 58"
Cohesion: 0.22
Nodes (8): Actualizar el Corpus, Almacenamiento: S3 Vectors (No OpenSearch), Atribución de Fuentes, Knowledge Base en AWS Bedrock, Modo Mock, Motor de Embeddings, Qué Contiene el Corpus, RAG y Knowledge Base — Recuperación Semántica en Este Demo

### Community 59 - "Community 59"
Cohesion: 0.18
Nodes (11): 1. pytest (69/69 PASS), 2. UI fiscal sweep (0 matches), 3. Live Bedrock agent gate (3/3 PASS), 4. KB ingestion, AWS changes, Date: 2026-07-07 ~04:40 UTC, Local changes, Verdict: PASS (+3 more)

### Community 60 - "Community 60"
Cohesion: 0.29
Nodes (6): Action Group: fiscal-tools, Bedrock Agent — Cómo Funciona el Núcleo de Este Demo, Identidad del Agente, Modo Mock (Desarrollo Local), Punto de Entrada, Trazabilidad y Extracción de Tokens

### Community 61 - "Community 61"
Cohesion: 0.29
Nodes (6): Flujo HITL Paso a Paso, Guardrails de Bedrock, HITL y Guardrails — Seguridad y Control Humano en Este Demo, Human-in-the-Loop (HITL), Por Qué HITL en Una Demo, Seguridad Multi-Capa

### Community 62 - "Community 62"
Cohesion: 0.29
Nodes (6): Coste Total Acumulado, Endpoints de Métricas, Harness de Evaluaciones, Observabilidad y Evaluaciones — Cómo Se Mide Este Demo, Persistencia de Trazas, Router Comparison

### Community 63 - "Community 63"
Cohesion: 0.22
Nodes (9): Adversarial verification (3 verifiers), API live (tmux window arq-demototal:api, port 7020), Archivos, Commit, Demo ask (200 with response + trace), Demo page (200, HTML with injected token), Tests (74/74 PASSED), Token auth (401 on invalid) (+1 more)

### Community 64 - "Community 64"
Cohesion: 0.38
Nodes (7): Commit: d5d9ccb, Fecha: 2026-07-07, Qué cambió, Resultado: PASS, Tarea: ORDEN-REGISTRY-V22, Verificación: click tooltips en diagrama Mermaid, Verificación: Registry v2.2 Update

### Community 65 - "Community 65"
Cohesion: 0.15
Nodes (13): Evidencia curl :5055, Evidencia curl :8502, Evidencia docker ps, Fecha: 2026-07-07 ~05:30 UTC, Infraestructura, Notebook creado, Qué se cambió, Resultado (+5 more)

### Community 68 - "Community 68"
Cohesion: 0.15
Nodes (22): check_daily_cost_cap(), Check if daily cost cap is exceeded. Raises HTTPException if so., ApprovalDecision, int, str, architecture_page(), demo_approvals(), demo_ask() (+14 more)

### Community 69 - "Community 69"
Cohesion: 0.30
Nodes (13): int, str, DashboardCostRow, FacturaSchema, MetricsModelBreakdown, MetricsResponse, MetricsTenantBreakdown, TenantSchema (+5 more)

### Community 70 - "Community 70"
Cohesion: 0.23
Nodes (13): Any, _detect_componente(), _detect_intent(), _extract_number(), _kb_response(), mock_invoke_agent(), Any, float (+5 more)

### Community 71 - "Community 71"
Cohesion: 0.20
Nodes (6): str, TestDetectarRequisito, detectar_requisito(), explicar_componente(), Detect if user text matches a vacancy requirement and return confirmation., ResultadoRequisito

### Community 72 - "Community 72"
Cohesion: 0.53
Nodes (8): ApprovalDecision, int, str, ApprovalListResponse, ApprovalSchema, ApprovalDecision, decide_approval(), list_approvals()

### Community 73 - "Community 73"
Cohesion: 0.24
Nodes (9): bool, Check if token exists and is not expired., validate_token(), str, _clean_name(), Presentation-layer sanitizer. AWS resources keep their real names     (fiscal-co, Read AWS resource states in real-time via boto3., Read AWS resource states in real-time via boto3. (+1 more)

### Community 75 - "Community 75"
Cohesion: 0.39
Nodes (6): get_conn(), str, HealthResponse, _build_table(), dashboard(), health()

### Community 76 - "Community 76"
Cohesion: 0.38
Nodes (6): str, ask(), AskRequest, _normalize_guardrail_query(), Rewrite guardrail-sensitive queries to avoid PROMPT_ATTACK false positive., ToolTrace

### Community 77 - "Community 77"
Cohesion: 0.14
Nodes (21): _guardrail_fallback(), invoke_agent(), _invoke_bedrock_sync(), _invoke_mock(), _normalize_query(), Any, str, Fallback: use local mock agent. (+13 more)

### Community 79 - "Community 79"
Cohesion: 0.15
Nodes (14): _invoke_bedrock(), is_bedrock_available(), load_agent_config(), bool, Bedrock Agent client with automatic fallback to mock.  Reads agent IDs from aws/, Real Bedrock Agent invocation., Real Bedrock Agent invocation., Real Bedrock Agent invocation. (+6 more)

### Community 80 - "Community 80"
Cohesion: 0.60
Nodes (3): str, donde_verificar(), ResultadoVerificacion

## Knowledge Gaps
- **442 isolated node(s):** `int`, `bool`, `bool`, `int`, `float` (+437 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `detectar_requisito()` connect `Community 71` to `Community 0`, `Community 70`, `Community 76`, `Community 77`, `Community 79`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `get_conn()` connect `Community 75` to `Community 32`, `Community 4`, `Community 68`, `Community 69`, `Community 72`, `Community 73`, `Community 76`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `reset_rate_limits()` connect `Community 6` to `Community 32`, `Community 4`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `ApprovalDecision` (e.g. with `ApprovalDecision` and `int`) actually correct?**
  _`ApprovalDecision` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `int`, `bool`, `Demo token authentication, rate limiting, and cost cap.  Tokens are path-based:` to the rest of the system?**
  _544 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.044444444444444446 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.09848484848484848 - nodes in this community are weakly interconnected._