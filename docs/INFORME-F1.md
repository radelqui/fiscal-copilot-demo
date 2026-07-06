# INFORME F1 — Bootstrap Arquitecto + Prototipo Fiscal Copilot

**Fecha**: 2026-07-06
**Arquitecto**: arquitecto-bedrock-srv67 (Claude Opus 4.6)
**Tag**: `f1-bootstrap-ok`

---

## 1. Qué se hizo

### 1.1 Estructura del proyecto
```
fiscal-copilot/
  CLAUDE.md              — reglas proyecto (eu-central-1, $15, puertos 7020/5544)
  AGENTS.md              — 5 agentes + convenciones anti-colisión
  Makefile               — targets: test, evals, demo, serve, lint
  .gitignore             — Python, env, IDE, cache
  .claude/agents/        — 5 subagentes (analizador, verificador-adversarial, aws-deployer, backend-dev, evals-engineer)
  .claude/skills/dgii-fiscal/SKILL.md — conocimiento fiscal dominicano
  app/
    tools/               — 3 tools Python puras (calcular_itbis, validar_ncf, presentar_formato_606)
    agent/system_prompt.py — SYSTEM_PROMPT del agente fiscal (8 reglas)
    rag/corpus/          — 4 documentos DGII (itbis, ncf, 606/607, calendario)
    main.py              — FastAPI app
    mock_agent.py        — simula invoke_agent con tools locales
    routers/             — /health, /ask
  tests/                 — test_tools.py (26 tests) + test_api.py (11 tests)
  evals/golden_set.jsonl — 8 casos (2 calc, 2 NCF, 1 606, 1 KB, 1 injection, 1 HITL)
  pyproject.toml         — deps base + [aws] + [evals] opcionales
  aws/ specs/ demo/ reports/ docs/ — directorios para fases futuras
```

### 1.2 Corpus DGII (4 documentos, normativa real verificable)
| Documento | Palabras | Contenido clave |
|-----------|----------|-----------------|
| itbis_basico.md | ~558 | ITBIS 18%, Ley 11-92, cálculo, exenciones, penalidades |
| ncf_tipos.md | ~645 | 11 tipos NCF, formato e-NCF (E+2+10), validación |
| formatos_606_607.md | ~737 | Formatos 606/607/608, campos, fecha límite día 15 |
| calendario_fiscal.md | ~702 | Obligaciones mensuales (días 3/10/15/20), anuales, IPI |

### 1.3 Tools Python (deterministas, pure stdlib)
| Tool | Input | Output | Tests |
|------|-------|--------|-------|
| calcular_itbis | monto: float, incluido: bool | monto_sin_itbis, itbis, monto_con_itbis | 7 |
| validar_ncf | ncf: str | valido, tipo_codigo, tipo_nombre, errores | 9 |
| presentar_formato_606 | periodo: str, registros: int | fecha_limite, estado, mensaje | 10 |

### 1.4 FastAPI skeleton (USE_MOCK_AGENT=1)
- `GET /health` → status, version, mock_mode
- `POST /ask` → trace_id, response, provider, model, tools_used, tokens, cost_usd, latency_ms
- Mock agent detecta intent (ITBIS/NCF/606/KB) y usa tools locales reales
- Pydantic estricto en toda I/O

### 1.5 AWS CLI
- Instalado sin sudo: `~/.local/bin/aws` v2.35.15
- NO configurado (esperando Phase H para las keys)

---

## 2. Evidencia

### 2.1 Tests: 37/37 passed
```
tests/test_api.py::TestHealth::test_health_ok PASSED
tests/test_api.py::TestHealth::test_health_version PASSED
tests/test_api.py::TestAsk::test_ask_itbis_calculation PASSED
tests/test_api.py::TestAsk::test_ask_itbis_included PASSED
tests/test_api.py::TestAsk::test_ask_validar_ncf PASSED
tests/test_api.py::TestAsk::test_ask_ncf_invalido PASSED
tests/test_api.py::TestAsk::test_ask_knowledge_base PASSED
tests/test_api.py::TestAsk::test_ask_empty_query PASSED
tests/test_api.py::TestAsk::test_ask_cost_zero_in_mock PASSED
tests/test_api.py::TestAsk::test_response_has_trace_id PASSED
tests/test_api.py::TestAsk::test_pydantic_strict_response PASSED
tests/test_tools.py: 26 tests PASSED
======================== 37 passed in 0.61s =========================
```

### 2.2 Smoke test servidor
```
$ curl http://127.0.0.1:7020/health
{"status":"ok","version":"0.1.0","mock_mode":true}

$ curl -X POST http://127.0.0.1:7020/ask -d '{"query":"¿Cuánto ITBIS pago por 118000 con ITBIS incluido?"}'
{
  "trace_id": "ab6c80fc-3741-4eed-a211-43d61d4da0f5",
  "response": "Para un monto de RD$118,000.00 con ITBIS incluido:\n- Monto sin ITBIS: RD$100,000.00\n- ITBIS (18%): RD$18,000.00\n- Total: RD$118,000.00",
  "provider": "mock",
  "model": "local-tools",
  "tools_used": [{"tool_name": "calcular_itbis", "tool_input": {"monto": 118000.0, "incluido": true}, "tool_output": {"monto_sin_itbis": 100000.0, "itbis": 18000.0, "monto_con_itbis": 118000.0}}],
  "cost_usd": 0.0,
  "latency_ms": 0.28
}
```

### 2.3 AWS CLI
```
$ ~/.local/bin/aws --version
aws-cli/2.35.15 Python/3.14.5 Linux/6.8.0-107-generic exe/x86_64.ubuntu.24
```

### 2.4 Golden set
```
8 cases loaded:
  calc-itbis-001: calculation (confirmation=False)
  calc-itbis-002: calculation (confirmation=False)
  ncf-valid-001: validation (confirmation=False)
  ncf-invalid-001: validation (confirmation=False)
  formato-606-001: format (confirmation=True)
  kb-fecha-606: knowledge (confirmation=False)
  injection-001: injection (confirmation=False)
  hitl-606-001: hitl (confirmation=True)
```

### 2.5 Git log
```
83c802a docs: F1 plan maestro + overrides + prompt + verificacion
3f7581d feat: F1 golden set — 8 casos evaluacion (incl injection + HITL)
e7bf6dc feat: F1 FastAPI skeleton con mock agent (USE_MOCK_AGENT=1)
1b49fa6 feat: F1 tools — 3 tools Python deterministas + tests + SYSTEM_PROMPT
c49ad8f feat: F1 corpus DGII — 4 documentos normativa fiscal dominicana
e390271 chore: F1 bootstrap — project structure, CLAUDE.md, agents, skill
Tag: f1-bootstrap-ok → 83c802a
```

---

## 3. Verificación adversarial

"Encuentra algo del entorno que falte para F2":

| Item | Estado | Detalle |
|------|--------|---------|
| AWS CLI instalado | PASS | v2.35.15 en ~/.local/bin/ |
| AWS CLI configurado | ESPERADO | Fase H entrega las keys |
| Tools pure Python (portables a Lambda) | PASS | Solo stdlib (re, dataclasses) |
| Corpus en markdown (portable a S3) | PASS | 4 docs en app/rag/corpus/ |
| SYSTEM_PROMPT porteable a Bedrock | PASS | app/agent/system_prompt.py |
| pyproject.toml con [aws] deps | PASS | boto3, langgraph, psycopg |
| .gitignore | PASS | Creado tras hallazgo adversarial |
| Puerto 7020 libre | PASS | Confirmado con ss -tlnp |
| Puerto 5544 libre | PASS | Para PostgreSQL en F3 |
| No TODO/FIXME en código | PASS | grep limpio |
| No credenciales hardcoded | PASS | Solo env vars |
| boto3 no instalado en .venv | ESPERADO | Se instala en F2 cuando haya keys |

**Resultado**: 0 bloqueantes para F2. Los 2 ítems "ESPERADO" dependen de Phase H (keys AWS).

---

## 4. Desviaciones del plan

| Desviación | Razón | Impacto |
|------------|-------|---------|
| Región eu-central-1 en vez de us-east-1 | Override O9 del SM: servidor en Alemania, GDPR | Positivo: latencia ~5ms vs ~90ms |
| Autoría del prototipo desde cero | Override O1: el zip no existía | Neutro: corpus y tools escritos con normativa real verificable |
| .gitignore añadido (no estaba en plan v1) | Hallazgo adversarial: sin él se commitearía .venv | Positivo: fix preventivo |
| No se hizo git push (no hay remote) | Override O1: "todo es local, no hay GitHub" para Sypnose. El remote se configura en Fase H con deploy key | Neutro: commits y tag locales intactos |

---

## 5. Feedback al SM

### Sistema/Repo
- 0 hallazgos. El directorio ~/proyectos/fiscal-copilot/ estaba preparado, puertos 7020/5544 libres como indicado, Python 3.12 disponible, uv instalado.

### Prompt/Comunicación
- La secuencia de lectura (v1 → v2 overrides) fue clara y no hubo contradicciones ambiguas. El §11 (Ley del Arquitecto) permitió añadir .gitignore sin bloquear.
- Nota menor: v1 dice "us-east-1" en múltiples lugares pero v2 O9 lo sustituye por eu-central-1. Si hay futuros planes derivados del v1, podrían arrastrar us-east-1 por error. Sugerencia: actualizar v1 inline o poner un banner al inicio.

### Flujo/Proceso
- El ciclo de 6 pasos (analizar→planificar→implementar→verificar→gate→commit) funcionó limpio. La verificación adversarial detectó el .gitignore faltante antes del commit.
- Wave parallelism fue efectivo: 4 sub-agentes en Wave 1 (estructura + corpus + tools + AWS CLI) y 2 en Wave 2 (FastAPI + golden set), reduciendo el tiempo total significativamente.

---

## Estado: ESPERANDO AUDITORÍA DEL SM

El arquitecto NO se autoconcede el gate F1. Informe entregado, esperando revisión.
