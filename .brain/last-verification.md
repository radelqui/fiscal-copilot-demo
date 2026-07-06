# Verificación F7-UI — 2026-07-06

## Commit
678e1ad feat: F7-UI demo — token auth, Bedrock client, chat UI, 17 tests

## Tests (74/74 PASSED)
```
$ USE_MOCK_AGENT=1 .venv/bin/python -m pytest tests/ -v
74 passed in 1.20s
```

## API live (tmux window arq-demototal:api, port 7020)
```
$ curl -s http://localhost:7020/health
{"status":"ok","version":"0.1.0","mock_mode":true,"db_connected":true,"db_tables":6}
```

## Token auth (401 on invalid)
```
$ curl -s http://localhost:7020/demo/invalid-token -o /dev/null -w "%{http_code}"
401
```

## Demo ask (200 with response + trace)
```
$ curl -s -X POST http://localhost:7020/demo/TOKEN/ask -H "Content-Type: application/json" -d '{"query":"Calcula ITBIS de 50000 pesos"}'
{"response":"Para un monto de RD$50,000.00 sin ITBIS:\n- Monto base: RD$50,000.00\n- ITBIS (18%): RD$9,000.00\n- Total con ITBIS: RD$59,000.00","trace":{"provider":"mock","model":"local-tools","tokens_in":10,"tokens_out":40,"cost_usd":0.0,"latency_ms":0.22,"tools":[{"tool_name":"calcular_itbis","tool_input":{"monto":50000.0,"incluido":false},"tool_output":{"monto_sin_itbis":50000.0,"itbis":9000.0,"monto_con_itbis":59000.0}}]}}
```

## Demo page (200, HTML with injected token)
```
$ curl -s http://localhost:7020/demo/TOKEN -o /dev/null -w "HTTP %{http_code}, %{size_download} bytes"
HTTP 200, 37109 bytes
```

## Adversarial verification (3 verifiers)
- Security: XSS PASS, SQL injection PASS, path traversal PASS, SSRF PASS. Fixed: cost detail leak, KeyError.
- Edge cases: Fixed .get() for result["response"]. Known: in-memory rate limit (single worker OK).
- Integration: ALL PASS — demo.py ↔ bedrock_agent ↔ mock chain, JS response mapping, lifespan order.

## Archivos
- app/auth.py (132 LOC) — token mgmt, rate limit, cost cap
- app/bedrock_agent.py (207 LOC) — Bedrock client + auto-fallback
- app/routers/demo.py (193 LOC) — demo endpoints
- app/static/demo.html (1253 LOC) — single-page UI
- app/main.py (35 LOC) — added demo router + ensure_demo_token
- tests/test_f7.py (280 LOC) — 17 tests
- docs/INFORME-F7UI.md — informe cierre fase
