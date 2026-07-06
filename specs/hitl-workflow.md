# Spec: HITL Workflow (Retroactive)

**Status**: Implementado  
**Fecha**: 2026-07-06  
**Tipo**: Retroactive (documenta implementación existente)

## Objetivo

Acciones fiscales sensibles (presentar formato 606) requieren aprobación humana antes de ejecutarse. El agente Bedrock pide confirmación, el backend crea un registro de aprobación, y el usuario decide en la UI.

## Flujo

1. Usuario envía query que invoca `presentar_formato_606`
2. Bedrock Agent retorna `returnControl` con `requireConfirmation=ENABLED`
3. Backend (`app/routers/demo.py:95-104`) inserta en tabla `approvals` con status=pending
4. UI muestra la aprobación pendiente en sidebar (polling cada 5s)
5. Usuario decide: `POST /demo/{token}/approvals/{id}/decide` con `{decision: "approved"|"rejected"}`
6. Backend valida: 404 si no existe, 409 si ya decidida, 422 si decision inválida
7. Actualiza `approvals.status`, `decided_by`, `decided_at`

## Tabla: approvals

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | SERIAL PK | Auto-increment |
| trace_id | TEXT FK → traces | Traza asociada |
| tenant_id | TEXT FK → tenants | Tenant |
| action | TEXT | Nombre de la acción (ej: presentar_formato_606) |
| payload | JSONB | Parámetros de la acción |
| status | TEXT CHECK | pending, approved, rejected, executed |
| decided_by | TEXT | Quién decidió |
| decided_at | TIMESTAMPTZ | Cuándo se decidió |
| created_at | TIMESTAMPTZ | Cuándo se creó |

## Endpoints

### GET /demo/{token}/approvals?status=pending
Lista aprobaciones, opcionalmente filtradas por status.

### POST /demo/{token}/approvals/{id}/decide
```json
{
  "decision": "approved",  // o "rejected"
  "decided_by": "demo-user"
}
```

Respuestas:
- 200: `{"ok": true, "id": 1, "decision": "approved"}`
- 401: Token inválido
- 404: Approval no encontrada
- 409: Ya decidida
- 422: Decision inválida (no es approved/rejected)

## Configuración AWS

- Action Group: `fiscal-tools`
- Función: `presentar_formato_606`
- `requireConfirmation`: ENABLED
- El agente muestra mensaje de confirmación al usuario antes de que el backend cree el approval

## Archivos involucrados

- `app/routers/demo.py` — endpoints de aprobación
- `app/bedrock_agent.py` — detecta returnControl/requireConfirmation
- `app/db.py` — tabla approvals
- `app/schemas.py` — ApprovalDecision, ApprovalSchema
- `app/static/demo.html` — sidebar de aprobaciones
- `tests/test_f7.py` — TestDemoApprovals (5 tests)
