# INFORME FINAL — Fiscal Copilot (Consolidación)

**Fecha**: 2026-07-06  
**Fase**: Consolidación Final  
**Estado**: COMPLETADO — esperando auditoría final SM  
**Tag**: v1.0.0-demo

---

## 1. Resumen Ejecutivo

Fiscal Copilot es un agente fiscal dominicano construido sobre AWS Bedrock (eu-central-1) para la entrevista en NAIIAN. Demuestra: Bedrock Agents con Sonnet 4.6, Knowledge Base (S3 Vectors), Action Groups (Lambda), Guardrails, Human-in-the-Loop, observabilidad completa, evaluaciones LLM-as-Judge, y desarrollo spec-driven.

## 2. Entregables por Fase

| Fase | Entregable | Tests | Gate |
|------|-----------|-------|------|
| F1 Bootstrap | Tools, mock agent, corpus, tests | 57 | GRANTED |
| F2 Bedrock | Agent+KB+Lambda+Guardrail (SM) | — | GRANTED |
| F3 Backend | PostgreSQL, endpoints, HITL, dashboard | 65 | GRANTED |
| F5 Evals | Harness, router, judges, comparativa | 74 | GRANTED |
| F7-UI Demo | Token auth, Bedrock client, chat UI | 74 | GRANTED |
| Consolidación | Observabilidad, README, specs, métricas | 82 | PENDIENTE |

## 3. Arquitectura Final

```
AWS eu-central-1 (Frankfurt)
├── Bedrock Agent 2BOPZRAI7X (Sonnet 4.6)
│   ├── KB 5I5RDNA2V1 (S3 Vectors, corpus fiscal)
│   ├── Lambda fiscal-copilot-tools (3 tools)
│   └── Guardrail xgn38kcg6hrq (injection, off-topic)
│
Servidor 67 (Frankfurt, ~5ms latencia)
├── FastAPI :7020
│   ├── /demo/{token} — UI demo (chat + aprobaciones)
│   ├── /demo/{token}/ask — chat endpoint
│   ├── /health — health check
│   ├── /metrics — métricas JSON (p50, p95, por modelo)
│   ├── /dashboard — dashboard HTML observabilidad
│   └── /traces — historial de trazas
├── PostgreSQL :5544
│   ├── traces (tokens, coste, latencia, tools)
│   ├── approvals (HITL workflow)
│   ├── tenants
│   └── facturas
└── Evals Pipeline
    ├── Golden set (8 casos)
    ├── Router (4 modelos)
    ├── Judges (4 métricas)
    └── reports/comparativa.md
```

## 4. Fase Consolidación — Detalle

### 4.1 Bloque 1: FIX Observabilidad Real
- **Problema**: tokens_in/tokens_out llegaban a 0 en modo real
- **Causa**: `response.get("usage")` no existe en invoke_agent; usage viene de trace events
- **Fix**: Acumular `modelInvocationOutput.metadata.usage` de todos los trace events
- **Tests**: 4 nuevos (test_bedrock_observability.py), total 82

### 4.2 Bloque 2: README.md
- Matriz NAIIAN: 10 requisitos → implementación → ubicación → cómo probar
- Diagrama ASCII: Bedrock ↔ FastAPI ↔ PostgreSQL
- Quickstart en 5 pasos

### 4.3 Bloque 3: DEMO-GUIDE.md
- 8 pruebas copy-paste para el entrevistador
- Cubre: RAG, cálculo, NCF, injection, HITL, dashboard, métricas

### 4.4 Bloque 4: Specs
- `specs/hitl-workflow.md` — retroactiva (documenta lo implementado)
- `specs/metrics-endpoint.md` — spec-first (escrita ANTES de implementar)
- GET /metrics implementado según spec: totals, p50/p95, by_model, by_tenant

### 4.5 Bloque 5: Higiene
- `aws/ids.env` añadido a .gitignore
- `aws/ids.env.example` creado con formato
- Scan de secretos: 0 reales encontrados
- CLIProxy key en router_results.json redactada a sk-REDACTED

### 4.6 Bloque 6: Cierre
- AGENTS.md actualizado con metodología completa
- Verificación adversarial (3 lentes: seguridad, correctitud, completitud)
- f-string no-op corregido en bedrock_agent.py

## 5. Números Finales

| Métrica | Valor |
|---------|-------|
| Archivos fuente | 52 |
| Líneas Python | 3,757 |
| Tests | 82 (0 failures) |
| Endpoints | 7 |
| Tools | 3 (calcular_itbis, validar_ncf, presentar_formato_606) |
| Modelos evaluados | 4 (Haiku, Nova Micro, GPT-4o-mini, Sonnet 4.6) |
| Métricas judge | 4 (faithfulness, relevancy, context_precision, geval) |
| Coste evals | $0.018 |
| Coste presupuesto | $15 de $100 |

## 6. §4.1 — Feedback al SM

### Qué funcionó bien
1. **Fases con gate**: cada fase tiene métrica de éxito, tests, y auditoría SM
2. **Mock agent pattern**: desarrollo completo sin AWS, fallback automático
3. **LLM-as-Judge manual**: más control que ragas/deepeval, mejor para demo
4. **Sub-agentes paralelos**: Wave 1 con 5 agents, Wave 2 con 1, Wave 3 con 2

### Qué mejoraría
1. **F2 antes que F3**: el Bedrock stack debería haberse creado primero para tener trazas reales desde el principio
2. **OpenAI key**: tener key válida desde el inicio para comparativa completa
3. **Test fixtures**: la BD compartida entre tests causa acoplamiento (test_metrics_empty_db necesita DELETE previo)

### Riesgos conocidos
1. **faithfulness bajo (0.323)**: esperado con mock (no hay contexto RAG real). Con agente real + KB, mejorará
2. **Sonnet 4.6 coste**: ~$0.018/query — monitorear con dashboard/metrics
3. **PostgreSQL sin backup**: BD demo sin persistencia — aceptable para demo

---
*Generado por arquitecto Opus, fase Consolidación Final*
