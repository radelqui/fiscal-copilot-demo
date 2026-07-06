# AGENTS.md — Fiscal Copilot

## Metodología de Desarrollo Agéntico

Este proyecto fue construido usando desarrollo agéntico con Claude Code como arquitecto y sub-agentes especializados para implementación, verificación y documentación.

## Fases de Desarrollo

| Fase | Descripción | Gate | Tests |
|------|-------------|------|-------|
| F1 — Bootstrap | Estructura, tools, tests, corpus, mock agent | GRANTED | 57 |
| F2 — Bedrock Stack | Agent, KB, Lambda, Guardrail (SM-ejecutado) | GRANTED | — |
| F3 — Backend | PostgreSQL, endpoints, HITL, dashboard, seed | GRANTED | 65 |
| F5 — Evals | Harness, router, judges, comparativa | GRANTED | 74 |
| F7-UI — Demo | Token auth, Bedrock client, chat UI | GRANTED | 74 |
| Final — Consolidación | Observabilidad, README, specs, métricas, higiene | — | 82 |

## Flujo por Fase

```
1. MÉTRICA ÉXITO — definir SQL/curl que mide delta antes/después
2. INVESTIGAR — leer archivos completos, mapear arquitectura
3. BLUEPRINT — escribir plan persistente antes de tocar código
4. IMPLEMENTAR — sub-agentes paralelos, archivos distintos
5. VERIFICAR — ejecutar métrica, delta > 0 = SUCCESS
6. GATE — commit + tag + informe + esperar auditoría SM
```

## Patrones Utilizados

### Spec-Driven Development
- `specs/hitl-workflow.md` — spec retroactiva del HITL
- `specs/metrics-endpoint.md` — spec escrita ANTES de implementar GET /metrics

### LLM-as-Judge (en lugar de Ragas librería)
- ragas 0.4.3 tenía imports rotos → implementamos faithfulness, answer_relevancy, context_precision manualmente usando Bedrock Haiku como judge
- DeepEval GEval → Haiku fallback cuando OpenAI no disponible

### Mock Agent Pattern
- `USE_MOCK_AGENT=1` usa tools locales Python idénticas a Lambda
- Permite desarrollo y testing sin AWS
- Fallback automático si Bedrock no disponible

### Multi-Model Evaluation
- Router con 4 modelos: Haiku, Nova Micro, GPT-4o-mini, Sonnet 4.6
- Golden set de 8 casos fiscales dominicanos
- Comparativa coste/latencia/calidad documentada

## Herramientas del Agente

| Herramienta | Rol |
|-------------|-----|
| Claude Code (Opus) | Arquitecto — planifica, delega, verifica |
| Sub-agentes (Sonnet) | Implementadores — escriben código, tests |
| Boris hooks | Calidad — bloquean commits sin verificación |
| pytest | Validación — 82 tests automatizados |
| Bedrock Haiku | Judge — evalúa calidad de respuestas |

## Evidencia de Desarrollo Agéntico

- Cada fase tiene su INFORME (docs/INFORME-*.md) con evidencia
- Cada commit tiene `Co-Authored-By: Claude` 
- specs/ contiene spec-first y retroactiva
- evals/ contiene pipeline reproducible
- reports/ contiene resultado generado automáticamente
