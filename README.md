# ¿Cómo Estoy Hecho? — Meta-Demo

**¿Cómo Estoy Hecho?** Un agente de IA que explica su propia arquitectura. Demo técnica para la vacante NAIIAN
que demuestra AWS Bedrock Agents end-to-end: el agente está especializado en explicar
cómo se construyó esta misma demo — desde los requisitos de la vacante hasta la
implementación final. Las tools fiscales (ITBIS, NCF, 606) se mantienen como artefacto
vivo que demuestra action groups y Human-in-the-Loop.

---

## NAIIAN Requirements Matrix

| Requisito NAIIAN | Implementación | Ubicación | Cómo se prueba |
|---|---|---|---|
| Bedrock Agents | Agent 2BOPZRAI7X con Sonnet 4.6, action groups, KB | AWS eu-central-1 | `POST /demo/{token}/ask` con query fiscal |
| Knowledge Base (RAG) | KB S3 Vectors (5I5RDNA2V1) con corpus fiscal dominicano | AWS eu-central-1 | "¿Fecha límite del 606?" → cita normativa |
| Action Groups | Lambda fiscal-copilot-tools: calcular_itbis, validar_ncf, presentar_formato_606 | `aws/lambda/` + AWS | Trace muestra tool llamada y resultado |
| Guardrails | Guardrail xgn38kcg6hrq: bloquea prompt injection, temas off-topic | AWS eu-central-1 | "Ignora instrucciones..." → rechazado |
| Human-in-the-Loop | presentar_formato_606 requiere confirmación (requireConfirmation=ENABLED) | `app/routers/demo.py` + AWS | 606 → approval pendiente → aprobar → ejecutar |
| Observabilidad | Traces en PostgreSQL: tokens, coste, latencia, tools por request | `app/routers/traces.py`, `/dashboard` | Dashboard muestra coste por tenant/modelo |
| Evals (LLM-as-Judge) | 4 métricas: faithfulness, relevancy, context_precision, geval | `evals/judges.py` | `make evals` → reports/comparativa.md |
| Multi-model routing | Haiku, Nova Micro, GPT-4o-mini, Sonnet 4.6 comparison | `evals/router.py` | Tabla coste/latencia/calidad por modelo |
| Spec-driven development | specs/metrics-endpoint.md escrito ANTES de implementar GET /metrics | `specs/` | Diff spec→código como evidencia |
| FastAPI + PostgreSQL | API async con pool, Pydantic strict I/O, auth por token | `app/` | 74 tests, `make test` |

---

## Architecture

```
┌─────────────────────────────────────┐
│         AWS eu-central-1            │
│  ┌──────────────────────────────┐   │
│  │  Bedrock Agent (Sonnet 4.6)  │   │
│  │  ┌─────────┐ ┌───────────┐  │   │
│  │  │ KB (S3  │ │ Lambda    │  │   │
│  │  │ Vectors)│ │ (tools)   │  │   │
│  │  └─────────┘ └───────────┘  │   │
│  │  ┌───────────────────────┐  │   │
│  │  │ Guardrail             │  │   │
│  │  └───────────────────────┘  │   │
│  └──────────────────────────────┘   │
└─────────────┬───────────────────────┘
              │ invoke_agent
              │
┌─────────────▼───────────────────────┐
│  Servidor 67 (eu-central, Frankfurt)│
│  ┌──────────────────────────────┐   │
│  │  FastAPI :7020               │   │
│  │  ├── /demo/{token}    (UI)   │   │
│  │  ├── /demo/{token}/ask       │   │
│  │  ├── /health                 │   │
│  │  ├── /metrics         (JSON) │   │
│  │  └── /dashboard       (HTML) │   │
│  └──────────────┬───────────────┘   │
│  ┌──────────────▼───────────────┐   │
│  │  PostgreSQL :5544            │   │
│  │  traces, approvals, tenants  │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Quickstart

```bash
# 1. Clonar y configurar
cp aws/ids.env.example aws/ids.env  # rellenar con IDs reales
source ~/.env-demototal              # AWS credentials

# 2. Base de datos
docker run -d --name fiscal-pg -p 5544:5432 \
  -e POSTGRES_USER=fiscal -e POSTGRES_PASSWORD=fiscal_demo_2026 \
  -e POSTGRES_DB=fiscal_copilot postgres:16

# 3. API
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make serve  # http://localhost:7020

# 4. Demo UI
# Abrir http://localhost:7020/demo/{token} (token en logs del servidor)

# 5. Tests y Evals
make test   # 74 tests
make evals  # pipeline completo → reports/comparativa.md
```

---

## Project Structure

```
fiscal-copilot/
├── app/                  # FastAPI application
│   ├── main.py
│   ├── routers/          # demo, traces, metrics, dashboard
│   └── models/           # Pydantic schemas
├── evals/                # LLM-as-Judge evaluation pipeline
│   ├── judges.py         # faithfulness, relevancy, context_precision, geval
│   ├── router.py         # multi-model comparison
│   └── run_all.py
├── specs/                # Spec-driven development artifacts
│   └── metrics-endpoint.md
├── aws/                  # Lambda code, IDs, deployment scripts
│   ├── lambda/           # fiscal-copilot-tools handler
│   └── ids.env.example
├── docs/                 # Architecture decisions, interview notes
├── tests/                # 74 pytest tests
├── reports/              # Eval outputs (generated)
├── Makefile
└── requirements.txt
```

---

## License

Private — demo for NAIIAN interview
