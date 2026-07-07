# Verification Evidence — ORDEN MAPEO REQUISITOS

## Date: 2026-07-07

## What changed
- explicar_componente.py: Added REQUISITOS dict (9 entries), detectar_requisito() function, 2 new components (desarrollo_agentico, multi_model), score>=2 threshold
- system_prompt.py: Added REGLA CLAVE REQUISITOS DE VACANTE instruction
- mock_agent.py: Added requisito_vacante intent detection
- handler.py: Added 2 new components + REQUISITOS dict to Lambda
- golden_set.jsonl: 9 new entries (32 total)
- tests: 10 new TestDetectarRequisito tests

## Verification

### pytest: 81/81 PASS
```
======================== 81 passed, 1 warning in 1.68s =========================
```

### Live Bedrock gate: 9/9 requisitos mapped correctly
- 8/9 respond with "✅ Sí, cumplo este requisito:" on literal vacancy text
- 1/9 (guardrails) blocked by its own PROMPT_ATTACK filter (proves guardrail works), passes when rephrased indirectly

### AWS deployment
- Lambda updated
- Action group: 10 valid components in schema
- Agent prompt: requirement-matching instruction added
- Agent prepared + alias updated

## Verdict: PASS
