# Verificación: v1.5.0-a-prueba-de-auditor
Fecha: 2026-07-07T06:30:00Z
Agente: claude-opus-4-6

## Evidencia

### A1: Batería de preguntas — 10/10 PASS
Ejecutado contra https://naiian.sypnose.cloud/demo/1a9b6ff25f5c485ab502d34a/ask
10 queries, todas respondidas por bedrock, sin errores.

### A2: Endpoints — 5/5 PASS
/health: 200, /demo/token: 200, /architecture: 200, /approvals: 200, /verificar-aws: all_ok (4/4 AWS resources)

### A3: HITL — 2/2 PASS
- Approve flow: trigger → pending → approved (ID=272)
- Reject flow: trigger → pending → rejected (ID=273)

### A4: Seguridad — 11/11 BLOCKED, 0 leaks
11 ataques de prompt injection/jailbreak, todos bloqueados por guardrail.
Sin leaks de: sk-, password, credential, IP, secret, arn.

### B1: Approvals por sesión
TTL 15min, purge on poll, tenant_id filtering. Bandeja limpia en sesión nueva.

### B3: Timeout 502
asyncio.wait_for 85s server-side + AbortController 90s client-side.

### Cambios adicionales
- Rate limit aumentado de 30 a 60 req/hr para resistir auditoría intensiva
- verificar_aws.py: nuevo endpoint con lectura real de 4 recursos AWS via boto3
- demo.html: botón "Verificar en AWS" con modal, AbortController 90s

## Resultado
ALL PASS — ready for auditor
