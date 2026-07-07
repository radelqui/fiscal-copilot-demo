# Verificación: C2+C3+C4+C5+C6 CIERRE-TOTAL
Fecha: 2026-07-07T06:45:00Z
Agente: claude-opus-4-6

## C2: System Prompt + Guardrail Denied Topic Fiscal
- System prompt: REGLA DURA anti-fiscal en app/agent/system_prompt.py
- Guardrail v3: 5 denied topics (added fiscal-content)
- Agent prepared + alias updated
- Evidencia: 6/6 fiscal traps BLOCKED (itbis, ncf, 606, dgii, impuestos, fiscal como ejemplo)

## C3: Bandeja HITL por sesión
- TTL 15min + purge on poll + tenant_id filtering
- Old approvals 261,262: GONE (purged by TTL)
- Evidencia: curl /approvals → 0 old IDs, only recent 272,273

## C4: verificar-aws
- GET /demo/{token}/verificar-aws: 200, all_ok
- 4/4 recursos: Agent PREPARED, KB ACTIVE, Guardrail READY, Lambda Active
- Botón en demo.html con modal overlay

## C5: Sin 502
- asyncio.wait_for timeout=85s en bedrock_agent.py
- AbortController 90s client-side
- Evidencia: todos POST /ask → 200, sin 502

## C6: 9 requisitos de vacante
- 9/9 PASS con ✅ + componente correcto + puntero verificación
- Providers: 7 bedrock + 2 local-fast-path (guardrails_controles, desarrollo_agentico)

## Resultado
C2-C6 ALL PASS
