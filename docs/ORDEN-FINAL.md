═══ EMISOR ═══ FROM: sm-claude-cli / TO: arquitecto-bedrock-srv67 / KEY: orden-final-consolidacion-260706

# GATE F5 CONCEDIDO + ORDEN FINAL: FASE CONSOLIDACIÓN

GATE F5: CONCEDIDO por el SM (74/74 y reports/comparativa.md verificados por el SM;
coste $0.018, excelente).

CONTEXTO NUEVO (verificado por el SM, no re-verificar):
- Sonnet 4.6 habilitado en la cuenta (Marketplace). El api corre en modo REAL
  (ventana tmux "api", USE_MOCK_AGENT=0, health mock_mode:false).
- GATE F2 REAL: 4/4 — cálculo con tool calcular_itbis (18,000 exactos), pregunta
  normativa vía KB, HITL (el agente PIDE confirmación en el 606), injection bloqueada
  por el guardrail. Evidencia: docs/EVIDENCIA-F2.md.
- E2E por /demo/<token>/ask con agente real: OK, traza persistida.

FASE CONSOLIDACIÓN — eres dueño de todo el repo (ya no hay sesiones paralelas):

1. **FIX observabilidad real** (lo más importante): en app/bedrock_agent.py los campos
   tokens_in/tokens_out/cost_usd/tools llegan a 0/vacíos en modo real. Extrae de los
   trace events del invoke_agent el usage real (modelInvocationOutput → metadata →
   usage) y las tools llamadas (actionGroupInvocationInput → function). Calcula
   cost_usd con el pricing de sonnet-4-6. Con test.
2. **README.md**: arriba del todo la MATRIZ requisito-de-la-vacante-NAIIAN → dónde
   vive (repo/AWS) → cómo se prueba. Después: arquitectura (diagrama ascii:
   Bedrock eu-central-1 [Agent+KB S3 Vectors+Lambda+Guardrail] ↔ srv67
   [FastAPI 7020 + PostgreSQL 5544 + UI]) y quickstart.
3. **DEMO-GUIDE.md**: las 8 pruebas en orden con prompts EXACTOS copy-paste para el
   entrevistador (normativa con cita, cálculo con trace, NCF, multi-turno, injection
   en vivo, 606 → aprobar en la bandeja → ver reanudar, dashboard, /metrics).
4. **specs/**: 1 spec retroactiva del HITL (como quedó) + 1 spec-first REAL: escribe
   specs/metrics-endpoint.md PRIMERO y LUEGO implementa GET /metrics (agregados:
   total requests, coste por tenant/modelo, latencia p50/p95) con tests. Guarda el
   diff spec→código como evidencia del flujo spec-driven.
5. **Higiene**: aws/ids.env fuera del repo (gitignore) + aws/ids.env.example con el
   formato. Verifica que no hay ningún secreto en el repo (grep de sk-, AKIA, secret).
6. **AGENTS.md** actualizado + verificación adversarial final (3 lentes) + commit de
   todo lo pendiente (incluye docs/EVIDENCIA-F2.md y aws/) + docs/INFORME-FINAL.md
   (§4.1 + Feedback al SM) + tag v1.0.0-demo. PARA a esperar auditoría final del SM.

═══ FIRMA ═══ sm-claude-cli / 260706
