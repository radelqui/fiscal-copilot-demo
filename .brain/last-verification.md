# Verificación: Q6+HITL fixes

## Fecha: 2026-07-07 ~05:30 UTC

## Qué se cambió
- app/bedrock_agent.py: Parse functionInvocationInput para HITL + compose response cuando agent pausa
- app/routers/ask.py: Integración agente real (invoke_agent) + normalización de query para los 9 requisitos

## Evidencia

### Tests: 81/81 PASS
```
======================== 81 passed, 1 warning in 1.73s =========================
```

### Gate 9 requisitos contra agente REAL (USE_MOCK_AGENT=0):
```
workflows_structured_outputs: PASS
agentes_bedrock: PASS
rag_multifuente: PASS
eval_harness: PASS
human_in_the_loop: PASS
guardrails_controles: PASS
desarrollo_agentico: PASS
trade_offs_modelos: PASS
backend_python: PASS
HITL: PASS
FINAL GATE: ALL PASS
```

### HITL test (agente real):
```
Provider: bedrock
Response: 🔒 Acción sensible: generar_reporte_arquitectura requiere aprobación humana. Checkpoint creado — aprueba o rechaza en la bandeja de aprobaciones.
Approval creada en BD: action=generar_reporte_arquitectura, status=pending
```

### Guardrail actualizado:
```
Guardrail xgn38kcg6hrq v2: READY
Blocked messages: 🛡️ Guardrail en acción... (sin mención fiscal)
Agent updated + prepared + alias PREPARED
```

### Server health (mock_mode: false):
```json
{"status": "ok", "version": "0.1.0", "mock_mode": false, "db_connected": true, "db_tables": 6}
```
