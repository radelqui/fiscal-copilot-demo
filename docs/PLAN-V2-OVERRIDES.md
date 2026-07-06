═══ EMISOR ═══ FROM: sm-claude-cli / TO: arquitecto-bedrock-srv67 / KEY: plan-demototal-v2-overrides-260706

# OVERRIDES v2 AL PLAN DEMO TOTAL — prevalecen sobre plan-v1-demototal.md
Fecha: 2026-07-06 · Emisor: SM Claude CLI (sesión NAIIAN, máquina Carlos) · Base: plan de sm-claude-web

Estos overrides corrigen supuestos falsos del plan v1 detectados con verificación real
(filesystem de Carlos + estado del servidor 67 a 2026-07-06 17:53 UTC) y reordenan la
ejecución a MVP-primero. Todo lo no contradicho aquí sigue vigente del v1.

## O1. REALIDAD CORREGIDA (verificada, no asumida)
- **El zip fiscal-copilot NO existe** (H8 del v1 es falso — se buscó en Downloads, Documents,
  Desktop, D:\, ~/proyectos de Carlos). F1 incluye AUTORAR el prototipo desde cero:
  · Corpus DGII: 4 documentos .md (itbis_basico.md, ncf_tipos.md, formatos_606_607.md,
    calendario_fiscal.md), 300-600 palabras c/u, normativa dominicana real y verificable
    (ITBIS 18%, tipos de NCF 01/02/14/15, fechas límite 606/607, retenciones básicas).
  · 3 tools Python puras: calcular_itbis(monto, incluido: bool), validar_ncf(ncf: str),
    presentar_formato_606(periodo, registros) — deterministas, con tests.
  · SYSTEM_PROMPT del agente fiscal (es el que luego se porta a Bedrock Agent en F2).
- **No hay aws CLI en el 67** → instalarlo en F1 sin sudo (installer v2 a ~/.local/aws-cli
  o `uv tool install awscli`). NO configurarlo: las keys llegan con la Fase H.
- **Puertos en el 67 hoy**: 7008/7009 OCUPADOS (no tocar). 7020 LIBRE (FastAPI) y
  5544 LIBRE (PostgreSQL demo) — confirmado con ss -tlnp. Re-verificar antes de F3.
- **~/proyectos no existía** — ya creado por el SM: ~/proyectos/fiscal-copilot/.
- Contenedores existentes en el 67: postiz (4007), stack temporal (8080, 7233),
  cliproxy y claw (18xxx). PROHIBIDO tocarlos.

## O2. ORDEN NUEVO: MVP-PRIMERO (sustituye la secuencia rígida F1→F8)
Regla de oro nueva: **al cierre de cada nivel debe existir una demo enseñable de punta a
punta**, aunque la entrevista fuese mañana. Niveles:
- **N1** = F1 + F2 + /ask FastAPI mínimo con traza persistida → demo enseñable (CLI + curl).
- **N2** = HITL (approvals) + UI de 1 página + exposición https://naiian.sypnose.cloud
  con token → demo entregable a un extraño. **Este es el objetivo mínimo innegociable.**
- **N3** = evals (harness + Ragas + DeepEval mínimos) + router 3 rutas + dashboard coste.
- **N4** = LangGraph kill-resume + tool consultar_facturas (multi-fuente) + CI eval-gate + specs.
Si la fecha de entrevista llega antes de terminar N4: se presenta el nivel alcanzado,
completo y pulido, y los niveles restantes se cuentan como roadmap con el repo abierto.

## O3. RIESGO #1 — MODEL ACCESS BEDROCK EN CUENTA FREE-TIER NUEVA
Las cuentas nuevas del free tier (plan gratuito 2025+) pueden tener los modelos Anthropic
restringidos o con cuota 0 hasta upgrade a plan de pago (los créditos siguen aplicando).
El gate H del v1 ("model access verde") es insuficiente:
- **Gate H real**: un invoke de prueba de ~1 token a Sonnet Y a Haiku vía
  `aws bedrock-runtime converse` que devuelva texto. Verde en consola ≠ cuota > 0.
- **Escalera de fallback** (no parar al primer fallo):
  · Plan A: Bedrock Agents nativo con Claude (ideal, es lo que pide la vacante).
  · Plan B: Bedrock Agents con Amazon Nova Pro/Micro (sigue siendo "agentes sobre Bedrock").
  · Plan C: agente propio LangGraph + Bedrock Converse API con tool calling manual
    (cubre el requisito demostrando la arquitectura por dentro — se defiende bien en entrevista).
  · OpenAI es SIEMPRE la 3ª ruta del router de F5, nunca el plan de emergencia del agente.
- PARAR y reportar al SM solo si A, B y C fallan.

## O4. DECISIÓN F4 PASO 1 — CERRADA POR EL SM (no esperar a Carlos)
La tool consultar_facturas del action group llama al endpoint FastAPI público del 67
(https://naiian.sypnose.cloud/internal/facturas) con token de servicio en header
X-Service-Token. NADA de DynamoDB ni réplicas de datos. Justificación: 1 fuente de verdad,
0 coste extra, y demuestra integración Lambda→API propia (más realista en entrevista).

## O5. RECORTES (menos teatro, misma cobertura de requisitos)
- Specs retroactivas: **1** (no 4) + **1 spec-first real** (el endpoint /metrics del v1-F6).
  AGENTS.md y la Skill dgii-fiscal sí, completos (son baratos y muy visibles).
- Video: NO es entregable principal (el v1 se contradecía — cabecera pedía video, F7 decía
  que no). Resolución: solo un respaldo de ~5 min con los 2 flujos no auto-servibles
  (kill -9 de LangGraph y CI rojo) cuando existan en N4, más plan B si la demo viva falla.
- Ragas + DeepEval: versión mínima (3 métricas Ragas + 1 GEval) sobre el MISMO golden set.
  La comparativa de valor está en el harness propio + tabla coste/latencia/calidad.

## O6. TOKEN DE INVITADO — PATH-BASED
https://naiian.sypnose.cloud/demo/<token> — el entrevistador solo hace clic en un enlace,
no configura headers. Expiración 14 días, rate-limit 30 req/h y tope $2/día como en v1.
El hostname naiian.sypnose.cloud se da de alta en el tunnel de Cloudflare del 67 en F7
(→ localhost:7020); si el arquitecto no tiene credenciales de Cloudflare, lo reporta y
lo hace Carlos/SM en el dashboard (2 min).

## O7. LO QUE SE HACE YA, SIN AWS (F1 ampliada — empezar HOY)
F1 completa + autoría del prototipo (O1) + FastAPI esqueleto con mock del agente
(flag USE_MOCK_AGENT=1 que simula invoke_agent con las tools locales reales) + tests pytest
+ estructura de evals/ con golden_set.jsonl inicial (8 casos) + git init + aws CLI instalado.
Resultado: cuando lleguen las keys de la Fase H, F2 es portar, no inventar.

## O9. REGIÓN: eu-central-1 (FRANKFURT) — SUSTITUYE A us-east-1 EN TODO EL PLAN v1
- Verificado en consola AWS 2026-07-06: el catálogo de eu-central-1 tiene Claude Sonnet
  4.6/4.5, Claude Haiku 4.5 (serverless, inferencia cross-region `eu.anthropic.*`),
  Titan Text Embeddings V2, Nova Micro/Lite/Pro. Todo lo que la demo necesita.
- Razones: el 67 está en Alemania (latencia ~5ms a Frankfurt vs ~90ms a Virginia) y el
  cliente NAIIAN es español → residencia de datos EU/GDPR como argumento de entrevista.
- La página de Model Access fue RETIRADA por AWS: los modelos serverless se activan
  automáticamente al primer invoke. El formulario de primer uso de Anthropic fue ENVIADO
  el 2026-07-06 con éxito (banner verde en consola).
- Usar inference profiles `eu.anthropic.claude-*`. Si algo faltase en Frankfurt:
  fallback us-east-1 (decisión del arquitecto con evidencia, reportada).

## O10. ESTADO FASE H A 2026-07-06 (cierre de día) + RELAJACIONES DE CARLOS
- OPENAI_API_KEY ya está en ~/.env-demototal del 67 (chmod 600) ✅
- Formulario Anthropic enviado ✅ · Región decidida ✅ · Auth Claude Code 67: en curso (OAuth)
- Presupuesto: hay $100 de créditos; el gate de coste INFORMA pero NO detiene el trabajo
  (orden directa de Carlos). Budgets/alertas: deseable, no bloqueante.
- El usuario IAM arquitecto-srv67 NO se revoca al terminar: Carlos lo reutilizará en
  futuras demos. Sigue sin subirse jamás al repo.
- Seguridad de la demo: mantener token de invitado + tope de gasto diario (barato y es
  argumento de entrevista), pero sin sobre-ingeniería adicional: es una demo, no producción.

## O8. REPORTE Y GATE
Al cerrar F1: informe §4.1 en docs/INFORME-F1.md — qué se hizo + evidencia (comandos y
outputs pegados) + desviaciones + sección "## Feedback al SM" con las 3 dimensiones
(Sistema/Repo, Prompt/Comunicación, Flujo/Proceso; si todo encajó: "0 hallazgos").
El arquitecto NO se autoconcede el gate: para tras el informe y espera auditoría del SM.

═══ FIRMA ═══ sm-claude-cli / 260706
