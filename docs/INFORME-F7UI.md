# INFORME F7-UI — Demo UI + Token Auth + Bedrock Client

**Fase**: F7-UI (sin AWS)  
**Fecha**: 2026-07-06  
**Estado**: COMPLETO — esperando auditoría SM  
**Tests**: 74/74 passed (17 nuevos F7 + 57 previos F1/F3)

---

## Entregables

### A. Backend en tmux (NO systemd)
- `tmux new-window -t arq-demototal -n api` con `USE_MOCK_AGENT=1`
- Puerto 7020, uvicorn foreground, logs a `/tmp/fiscal-copilot-api.log`
- Corrección SM aplicada: eliminado systemd --user del plan

### B. Demo UI (HTML+JS vanilla)
- **Archivo**: `app/static/demo.html` (1253 líneas)
- Chat 68%/32% split con sidebar de aprobaciones
- Dark theme profesional, responsive (<900px stacks vertical)
- Trace desplegable: provider, model, tokens in/out, cost_usd, latency_ms, tools
- Approvals sidebar auto-refresh 5s con botones aprobar/rechazar
- 5 chips de ejemplo en footer (ITBIS, NCF, 606, fecha límite, prueba seguridad)
- XSS protegido: `escapeHtml()` via `textContent` en todos los renders

### C. Token auth path-based
- **Archivo**: `app/auth.py` (132 líneas)
- Tabla `demo_tokens`: token TEXT PK, expires_at TIMESTAMPTZ
- Token generado automáticamente al startup (14 días, 24 chars hex)
- Endpoint: `/demo/{token}` sirve HTML con globals inyectados
- Rate limit: 30 req/hora por token (in-memory `_request_log`)
- Cost cap: $2/día (SUM cost_usd de traces del día actual)
- 401 token inválido/expirado, 429 rate limit / cost cap

### D. Bedrock Agent client con fallback
- **Archivo**: `app/bedrock_agent.py` (207 líneas)
- Lee `aws/ids.env` (AGENT_ID, ALIAS_ID, GUARDRAIL_ID)
- `is_bedrock_available()`: True solo si boto3 + AGENT_ID + ALIAS_ID
- `invoke_agent()`: auto-fallback a mock si Bedrock no disponible
- `_invoke_bedrock()`: maneja `requireConfirmation` para HITL
- `_estimate_cost()`: pricing Sonnet (0.003/0.015 per 1K tokens)
- Actualmente AGENT_ID/ALIAS_ID vacíos → fallback automático a mock

### E. Demo router
- **Archivo**: `app/routers/demo.py` (193 líneas)
- GET `/demo/{token}` — HTML con `DEMO_TOKEN`/`API_BASE` inyectados
- POST `/demo/{token}/ask` — auth + rate limit + cost cap + invoke_agent + persist trace + auto-approval HITL
- GET `/demo/{token}/approvals` — lista con filtro status
- POST `/demo/{token}/approvals/{id}/decide` — approve/reject con guards 404/409/422

### F. Tests
- **Archivo**: `tests/test_f7.py` (280 líneas, 17 tests)
- TestTokenValidation: 6 tests (401 invalid, 200 HTML, token inyectado)
- TestDemoAsk: 4 tests (response+trace, 422 empty/oversized, persist DB)
- TestDemoApprovals: 5 tests (list, create+decide, 404, 409, 422)
- TestRateLimit: 1 test (31 requests → 429)
- TestCostCap: 1 test (insert $2.50 trace → 429)

---

## Verificación adversarial (3 lentes)

### Seguridad
- XSS: PASS (escapeHtml client-side, json.dumps server-side)
- SQL Injection: PASS (parameterized queries everywhere)
- Path Traversal: PASS (token validated against DB)
- SSRF: PASS (no user-controlled URLs)
- Info disclosure: FIXED (cost cap detail genericizado post-audit)
- Rate limit bypass: KNOWN (in-memory, single-worker demo, aceptable)

### Edge cases
- KeyError result["response"]: FIXED (cambiado a .get())
- Cost cap detail leak: FIXED (mensaje genérico)
- Race conditions: KNOWN (single-worker uvicorn, aceptable para demo)
- Test isolation: module-scoped fixtures, cleanup manual en cost cap test

### Integración
- ALL PASS: demo.py → bedrock_agent → mock_agent chain works
- demo.html JS response mapping matches demo.py JSON shape
- lifespan order correct: init_db → ensure_demo_token → log URL
- Approval decide/list shapes match frontend expectations

---

## Archivos nuevos/modificados

| Archivo | Acción | Líneas |
|---------|--------|--------|
| app/auth.py | nuevo | 132 |
| app/bedrock_agent.py | nuevo | 207 |
| app/static/demo.html | nuevo | 1253 |
| app/routers/demo.py | nuevo | 193 |
| app/main.py | modificado | 35 |
| tests/test_f7.py | nuevo | 280 |
| docs/INFORME-F7UI.md | nuevo | este archivo |

---

## Evidencia

```
$ pytest tests/ -v
74 passed in 1.20s

$ curl localhost:7020/health
{"status":"ok","version":"0.1.0","mock_mode":true,"db_connected":true,"db_tables":6}

$ curl localhost:7020/demo/INVALID -o /dev/null -w "%{http_code}"
401

$ curl -X POST localhost:7020/demo/TOKEN/ask -d '{"query":"ITBIS de 50000"}'
{"response":"Para un monto de RD$50,000.00 sin ITBIS:...","trace":{"provider":"mock",...}}
```

---

## Limitaciones conocidas (aceptables para demo)

1. Rate limit in-memory: reset on restart, no comparte entre workers
2. Cost cap TOCTOU: requests concurrentes pueden exceder ligeramente
3. Token en URL: visible en logs y browser history (diseño path-based)
4. Sin HTTPS: demo local, producción necesitará TLS

## Pendiente para F2 (cuando lleguen AWS keys)

- Agregar AGENT_ID y ALIAS_ID a aws/ids.env
- is_bedrock_available() retornará True automáticamente
- invoke_agent() usará Bedrock real sin cambios de código
