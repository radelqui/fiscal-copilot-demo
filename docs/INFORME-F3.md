# INFORME F3 — Backend FastAPI + PostgreSQL + Observabilidad

**Fecha**: 2026-07-06
**Arquitecto**: arquitecto-bedrock-srv67 (Claude Opus 4.6)
**Tag**: `f3-backend-ok`

---

## 1. Qué se hizo

### 1.1 PostgreSQL 16 en Docker
- Container: `fiscal-copilot-db` (postgres:16-alpine)
- Puerto: 5544 (confirmado libre, no colisiona con nada)
- Volumen persistente: `fiscal-copilot_fiscal-copilot-pgdata`
- Config: docker-compose.f3.yml

### 1.2 Esquema de base de datos (5 tablas)
| Tabla | Columnas clave | Índices |
|-------|---------------|---------|
| tenants | id PK, name | — |
| traces | trace_id PK, tenant_id FK, query, response, provider, model, input/output_tokens, cost_usd, latency_ms, tools_used JSONB | tenant_id, model, created_at |
| approvals | id SERIAL PK, trace_id FK, tenant_id FK, action, payload JSONB, status CHECK(pending/approved/rejected/executed), decided_by, decided_at | status |
| facturas | id SERIAL PK, ncf, rnc, razon_social, monto, itbis, periodo, tipo_ncf, estado CHECK, tenant_id FK | tenant_id, rnc, periodo |
| workflow_steps | id SERIAL PK, workflow_id, step_name, status CHECK, retries, max_retries, checkpoint JSONB, error, tenant_id FK | workflow_id |

### 1.3 Seed data
- 3 tenants: ACME Distribuciones SRL, Global Trading Corp, Caribe Services SA
- 20 facturas distribuidas: acme=8, global=7, caribe=5
- Montos y ITBIS realistas, periodos 202605-202607, tipos NCF variados (01/02/03/04/11/14/15)

### 1.4 Endpoints FastAPI
| Método | Ruta | Función |
|--------|------|---------|
| GET | /health | Status + db_connected + db_tables + mock_mode |
| POST | /ask | Invoke agent (mock/real) + persistir trace + crear approval si 606 |
| GET | /approvals | Listar con filtros status/tenant_id |
| POST | /approvals/{id}/decide | Aprobar/rechazar (409 si ya decidido, 404 si no existe) |
| GET | /traces | Listar con filtros tenant_id/model/limit |
| GET | /dashboard | HTML con tablas coste por tenant/modelo/proveedor |

### 1.5 Observabilidad
- Cada /ask persiste automáticamente: trace_id, tenant, provider, model, tokens, cost_usd, latency_ms, tools_used
- Dashboard HTML renderiza 3 tablas de coste con totales
- Filtros por tenant y modelo en /traces

### 1.6 HITL (Human-in-the-Loop)
- POST /ask con formato 606 → crea approval con status=pending automáticamente
- POST /approvals/{id}/decide con decision=approved|rejected
- Protección: 409 si se intenta decidir dos veces, 422 si decision inválida

---

## 2. Evidencia

### 2.1 Tests: 57/57 passed
```
tests/test_api.py: 11 passed (F1, actualizado)
tests/test_f3.py: 20 passed (F3 integration)
tests/test_tools.py: 26 passed (F1, sin regresión)
======================== 57 passed in 0.44s =========================
```

### 2.2 Test de RECHAZO de salida malformada (requisito structured outputs)
```python
# test_f3.py::TestMalformedOutputRejection
test_pydantic_rejects_missing_required_field  PASSED  # AskResponse sin provider/model → ValidationError
test_pydantic_rejects_wrong_types             PASSED  # input_tokens="not_a_number" → ValidationError
test_pydantic_rejects_invalid_approval_decision PASSED # decision="maybe" → ValidationError
test_pydantic_rejects_empty_query             PASSED  # query="" → 422
test_pydantic_rejects_oversized_query         PASSED  # 2001 chars → 422
```

### 2.3 Smoke test servidor (curl)
```
GET /health → {"status":"ok","version":"0.1.0","mock_mode":true,"db_connected":true,"db_tables":5}

POST /ask (ITBIS 200000) → {
  "trace_id":"c72ca5b9-...",
  "response":"Para un monto de RD$200,000.00 sin ITBIS:\n- Monto base: RD$200,000.00\n- ITBIS (18%): RD$36,000.00\n- Total con ITBIS: RD$236,000.00",
  "provider":"mock","model":"local-tools","cost_usd":0.0,"latency_ms":0.23
}

POST /ask (606 → approval creado) → trace_id persistido + approval pending en DB

GET /traces?tenant_id=tenant-acme → {"total":8,"traces":[...]}

GET /approvals?status=pending → 5 approvals pendientes con payload JSONB

GET /dashboard → HTML con tablas coste por tenant/modelo/proveedor
```

### 2.4 SELECT sobre traces con cost_usd
```
traces en DB: 31 filas (acumuladas de tests + smoke tests)
facturas: 20 (3 tenants, montos reales)
```

### 2.5 DB seed
```
Seed complete: 3 tenants, 20 facturas
  tenant-acme:   8 facturas, monto=1,787,500.00, itbis=313,650.00
  tenant-caribe: 5 facturas, monto=725,200.00,   itbis=130,536.00
  tenant-global: 7 facturas, monto=2,246,500.00, itbis=307,170.00
```

### 2.6 Git log F3
```
cb7cfed test: F3 integration tests — 57 total, malformed output rejection
d162f46 feat: F3 integrar DB en main/ask/health + fix mock agent registros
0af5969 feat: F3 routers — /approvals HITL, /traces observabilidad, /dashboard HTML
dd1ce00 feat: F3 PostgreSQL 16 layer — 5 tablas, pool psycopg3, seed 20 facturas
```

---

## 3. Verificación adversarial (3 lentes)

### 3.1 SQL Injection (5 tests)
| Vector | Resultado |
|--------|-----------|
| /traces?tenant_id=acme' OR 1=1 -- | PASS (total=0, literal) |
| /traces?model=x'; DROP TABLE traces; -- | PASS (tabla intacta) |
| /approvals?status=pending' OR '1'='1 | PASS (total=0) |
| /ask con query inyectada | PASS (guardado como literal) |
| Health post-inyección | PASS (db_connected=true, tables=5) |
**Causa**: psycopg3 con %s parameterized queries en todos los routers.

### 3.2 XSS en /dashboard
- **HALLAZGO**: tenant_id con `<script>alert(1)</script>` se renderizaba raw en HTML
- **FIX APLICADO**: `html.escape(str(key))` en dashboard.py línea 70
- **VERIFICADO**: 0 ocurrencias de `<script>alert` en dashboard post-fix

### 3.3 Edge cases (9 tests)
| Test | Resultado |
|------|-----------|
| Approval decidido 2 veces | PASS → 409 |
| Approval inexistente | PASS → 404 |
| Agent down (mock off) | PASS → 503 (no 500) |
| Tenant inexistente en /traces | PASS → lista vacía |
| Dashboard sin datos | PASS → no crash |
| Query 2000 chars (max válido) | PASS → 200 |
| Query 2001 chars (excede max) | PASS → 422 |
| /health con DB | PASS → db_connected=true |
| Regresión F1 tests | PASS → 26/26 tools |

### 3.4 Readiness para F4
| Item | Estado |
|------|--------|
| facturas con data | PASS (20 rows, 3 tenants) |
| workflow_steps schema | PASS (9 columnas correctas) |
| Índices facturas (rnc, periodo) | PASS |
| approvals HITL completo | PASS |
| psycopg instalado | PASS (3.3.4) |
| langgraph deps en pyproject.toml | PASS |
| Docker volumen persistente | PASS |

---

## 4. Desviaciones del plan

| Desviación | Razón | Impacto |
|------------|-------|---------|
| XSS fix añadido (no en plan v1) | Hallazgo adversarial: stored XSS en dashboard | Positivo: seguridad mejorada |
| Mock agent fix registros | Bug: "formato 606 con 25 registros" extraía 606 | Positivo: respuestas correctas |
| conftest.py para tests | TestClient necesita lifespan para DB pool | Neutro: patrón estándar pytest |
| No se hizo push (sin remote) | Proyecto local, remote se configura en Fase H | Neutro: commits y tags intactos |

---

## 5. Feedback al SM

### Sistema/Repo
- PostgreSQL 16 en Docker funciona perfecto en puerto 5544. No colisiona con nada.
- El servidor tiene 15Gi RAM disponible y 127GB disco — sin preocupaciones de recursos.
- Los containers existentes (postiz, temporal) no se tocaron.

### Prompt/Comunicación
- El prompt F3 fue claro y completo. La lista de tablas/endpoints/tests fue exacta.
- Nota: el plan v1 dice "Test unitario que demuestra el RECHAZO de una salida malformada (requisito structured outputs)" — implementé 5 tests de rechazo Pydantic que cubren: campos faltantes, tipos incorrectos, decisión inválida, query vacío, query excesivo.

### Flujo/Proceso
- El ciclo de 6 pasos funcionó limpio. La verificación adversarial encontró el XSS en dashboard que se corrigió antes del commit.
- Wave parallelism: 3 agentes Wave 1 (DB layer + routers + Docker/seed), 2 agentes Wave 2 (modify existing + tests). Un fix adicional para el mock agent.
- El hallazgo XSS demuestra el valor de los verificadores adversariales — sin ellos habría pasado a producción.

---

## Estado: ESPERANDO AUDITORÍA DEL SM

El arquitecto NO se autoconcede el gate F3. Informe entregado, esperando revisión.
