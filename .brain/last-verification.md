# Verificación: Demo route fix — normalización centralizada en invoke_agent

## Fecha: 2026-07-07 ~06:00 UTC

## Qué se cambió
- app/bedrock_agent.py: _normalize_query movido aquí (cubre /ask Y /demo/token/ask)
- app/bedrock_agent.py: _guardrail_fallback para fast-path local si guardrail bloquea requisito
- app/routers/ask.py: eliminada _normalize_guardrail_query duplicada

## Evidencia

### Tests: 81/81 PASS
```
======================== 81 passed, 1 warning in 1.52s =========================
```

### Gate 9+HITL contra URL PÚBLICA (https://naiian.sypnose.cloud/demo/.../ask):
```
workflows_structured_outputs: PASS (bedrock)
agentes_bedrock: PASS (bedrock)
rag_multifuente: PASS (bedrock)
eval_harness: PASS (bedrock)
human_in_the_loop: PASS (bedrock)
guardrails_controles: PASS (bedrock)
desarrollo_agentico: PASS (bedrock)
trade_offs_modelos: PASS (bedrock)
backend_python: PASS (bedrock)
HITL: PASS (bedrock)
FINAL GATE: ALL PASS
```

### Server: mock_mode false, PID 2297115
