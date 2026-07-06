STATUS: pending | TO: arquitecto-bedrock-srv67 | FROM: sm-claude-web | TIMESTAMP: 2026-07-06T18:00:00Z | PRIORIDAD: alta

PLAN: FISCAL COPILOT DEMO TOTAL — ejecución completa en servidor 67 bajo protocolo Sypnose (ciclo de 6 pasos + verificación adversarial), desde los prerequisitos humanos de Carlos hasta el guion de presentación final. Cobertura: 100% del stack de la vacante (Bedrock Agents, KB, action groups, guardrails, RAG multi-fuente, FastAPI+PostgreSQL, structured outputs, LangGraph, Ragas/DeepEval, HITL, observabilidad por tenant/coste, desarrollo agéntico con specs/AGENTS.md/Skills).
TAREA: El arquitecto en srv67 ejecuta las Fases F1-F8 en orden con el ciclo de 6 pasos. Carlos ejecuta la FASE H (humana) antes de arrancar. Entregable: demo invocable + repo público + video + guion de presentación.
MODELO: claude-opus-4-6 para arquitectura y fases F4/F6; claude-sonnet-4-6 para el resto. Sub-agentes: SIEMPRE sonnet.
BORIS: git init (repo nuevo) + git tag pre-f<N> antes de CADA fase
VERIFICACION: bash demo/demo_10min.sh → 8/8 flujos OK, con outputs pegados en EVIDENCIA.md
EVIDENCIA: EVIDENCIA.md por fase + video final + Cost Explorer < $15
KB: kb_save key=resultado-arquitecto-bedrock-srv67-demototal-<fecha> category=notification project=jobhunter

# ═══════════════════════════════════════════════════════════════════
# FISCAL COPILOT — DEMO TOTAL · PLAN DE EJECUCIÓN EN SERVIDOR 67
# ═══════════════════════════════════════════════════════════════════
Fecha: 2026-07-06 · Protocolo: PLAN-EJECUCION-MAESTRO (ciclo 6 pasos) · SM: Claude (web)
Ejecutores: Carlos (Fase H) + arquitecto Claude Code en srv67 + subagentes sonnet

# 0-BIS. DÓNDE VIVE LA SOLUCIÓN (decisión de arquitectura, cerrada)

- **Cerebro → AWS (us-east-1)**: Bedrock Agent + Knowledge Base (S3 Vectors) + Lambda
  (action group) + Guardrail. Es la tecnología que la vacante pide ver: no puede vivir
  en otro sitio.
- **Cuerpo → servidor 67**: FastAPI + PostgreSQL + UI de demo, contenedores propios
  (puertos nuevos, sin tocar Registry :7008-7010 ni GestoriaRD), publicado como
  **https://naiian.sypnose.cloud** detrás de Cloudflare (proxy naranja, HTTPS, WAF).
- **Flujo**: entrevistador → naiian.sypnose.cloud (Cloudflare) → FastAPI en el 67 →
  invoke_agent a Bedrock → respuesta + traza persistida en PostgreSQL del 67.
- **Reparto de ejecución en PARALELO**:
  · **Claude Desktop + Chrome MCP** (con Carlos supervisando): todo lo que es CONSOLA
    AWS con clics — Fase H2-H4 (actividades de créditos, Budgets, Model access +
    formulario Anthropic, usuario IAM). Regla: Desktop navega y rellena, pero Carlos
    revisa cada pantalla antes de confirmar acciones que crean recursos o permisos.
  · **Arquitecto CLI en el 67**: todo lo demás (F1-F7), vía aws CLI/boto3 con las
    credenciales de H5. Los dos frentes no colisionan: Desktop trabaja en la consola
    web, el CLI en el servidor, y se sincronizan por los gates de la Fase H.

# 0. EL PROTOCOLO — CÓMO SE TRABAJA (heredado del PLAN-EJECUCION-MAESTRO, innegociable)

Cada fase sigue el ciclo:
```
1. ANALIZAR    → agentes read-only EN PARALELO mapean el terreno ANTES de tocar nada
2. PLANIFICAR  → 1 plan corto con archivos exactos a tocar (anti-colisión)
3. IMPLEMENTAR → cambios quirúrgicos, SOLO archivos del plan, estilo del código existente
4. VERIFICAR   → build/tests + verificadores ADVERSARIALES en paralelo (intentan romperlo)
5. GATE        → acceptance con EVIDENCIA (comando + output pegado). Sin evidencia = no pasó
6. COMMIT      → atómico, mensaje descriptivo, tag al cerrar cada fase
```
Reglas de oro 1-8 del PLAN-EJECUCION-MAESTRO aplican íntegras. Se AÑADEN dos por ser AWS:
9. **Gate de coste**: al cerrar cada fase con recursos AWS, pegar el saldo de créditos
   (Cost Explorer o widget). Si el gasto proyectado supera $15 totales → PARAR y reportar al SM.
10. **Credenciales**: JAMÁS en el repo ni en logs. Solo variables de entorno / aws configure.
    Un verificador adversarial de la fase final hace grep de secretos en todo el repo.

## 0.1 La Ley del Estilo Fable (cómo trabajo yo; así trabajáis vosotros)
Vosotros sois Opus y Sonnet; el estilo no depende del modelo, depende de la disciplina:
1. **Leer antes de escribir.** Nunca opinar sobre código no leído. Nunca asumir que un
   archivo existe: verificarlo (ls/grep) antes de referenciarlo.
2. **La evidencia manda.** "Funciona" = comando ejecutado + output pegado. Sin output,
   no ocurrió. Esto aplica también a las cosas que salen MAL: se pegan igual.
3. **Honestidad sobre lo no verificado.** Si algo no se pudo probar, se dice "NO VERIFICADO"
   en el informe, nunca se maquilla. Un "no sé" honesto vale más que un "hecho" falso.
4. **Refutar, no confirmar.** Al verificar, buscad el caso que rompe, no el que funciona.
5. **Causa raíz antes que parche.** Un fallo se diagnostica (leer el error exacto, reproducirlo)
   antes de tocar una línea. Prohibido el parcheo en cascada.
6. **Paralelizar solo lo independiente.** Lecturas/análisis: en paralelo. Escrituras sobre el
   mismo archivo: JAMÁS en paralelo (un dueño por archivo por fase).
7. **Reportar desviaciones.** Si el plan no encaja con la realidad, se corrige el plan y se
   reporta (Ley del Arquitecto §11). El plan sirve a la realidad.
8. **Terminar la fase.** Nada de dejar TODOs silenciosos: o se hace, o se anota como
   pendiente explícito en el informe con su razón.

# ═══════════════════════════════════════════════════════════════════
# FASE H — PREREQUISITOS HUMANOS (CARLOS, ANTES DE ARRANCAR NADA)
# ═══════════════════════════════════════════════════════════════════
Sin esta fase completa, el arquitecto se bloquea en F1. Duración: 1-2 horas + esperas.

H1. **Cuenta AWS Free Tier** — ✅ HECHA (Carlos, 2026-07). Verificar en Console Home que
    el widget de créditos muestra los $100 iniciales y anotar el Account ID.
H2. **Actividades del widget "Explore AWS"** (Console Home): completar las 5 ($20 c/u = $100 extra).
    → EJECUTOR: Claude Desktop + Chrome MCP con Carlos supervisando cada confirmación.
    La PRIMERA obligatoria: AWS Budgets → presupuesto mensual $15 con alertas 50/80/100%
    al email de Carlos. (Esto además cumple la Regla de oro 9.)
H3. **Bedrock Model Access** (región us-east-1) → EJECUTOR: Claude Desktop + Chrome MCP:
    Consola → Bedrock → Model access → habilitar: Claude Sonnet 4.x, Claude Haiku (ambos,
    sin Haiku hay 403 con Claude Code), Titan Text Embeddings V2, y Amazon Nova Micro
    (modelo barato para pruebas). Completar el formulario de primer uso de Anthropic.
H4. **Usuario IAM para el arquitecto**: IAM → usuario `arquitecto-srv67` con access keys.
    Política mínima para la demo: AmazonBedrockFullAccess + AWSLambda_FullAccess +
    AmazonS3FullAccess + IAMFullAccess (solo durante la demo; se revoca al terminar) +
    CloudWatchReadOnlyAccess. Guardar las keys en gestor de contraseñas.
H5. **Entregar credenciales al servidor 67** (por canal seguro, nunca por el repo):
    ssh al 67 → `aws configure` con las keys de H4, región us-east-1, output json.
H6. **API key de OpenAI** con $5 de crédito (para la ruta OpenAI Structured Outputs de F6).
    Exportarla en el 67: añadir OPENAI_API_KEY a ~/.env-demototal (chmod 600).
H7. **Repo GitHub**: crear repo vacío `fiscal-copilot-demo` (privado por ahora; se hace
    público en F8 tras revisión de Carlos). Dar acceso al 67 (deploy key o token).
H8. **Subir el material base al 67**: el zip fiscal-copilot (prototipo local ya construido)
    y este plan a /home/<user>/proyectos/fiscal-copilot/.

### GATE FASE H (Carlos confirma al SM, con capturas):
[ ] Créditos visibles ≥ $180 · [ ] Budget con alertas creado · [ ] Model access: 4 modelos verdes
[ ] `aws sts get-caller-identity` en el 67 devuelve el Account ID · [ ] OPENAI_API_KEY presente
[ ] Repo GitHub creado y accesible desde el 67

# ═══════════════════════════════════════════════════════════════════
# FASE F1 — BOOTSTRAP DEL ARQUITECTO EN SRV67 (½ día)
# ═══════════════════════════════════════════════════════════════════
Objetivo: dejar el entorno de trabajo montado con el estilo de casa (CLAUDE.md + agentes).

**Pasos:**
1. Sesión tmux `arq-demototal`. Claude Code arranca con la autenticación ACTUAL del 67
   (Opus/Sonnet). NOTA DE DISEÑO: el desarrollo NO corre sobre Bedrock para no quemar
   créditos; Bedrock es el destino de la app. La conexión Claude Code↔Bedrock se demuestra
   una vez en F2 como evidencia y se apaga.
2. Estructura del proyecto:
   ```
   fiscal-copilot/
     CLAUDE.md            ← crear (plantilla abajo)
     AGENTS.md            ← crear (convenciones + comandos, sirve para requisito 14)
     .claude/agents/      ← crear los 5 subagentes (definiciones abajo)
     .claude/skills/dgii-fiscal/SKILL.md  ← crear (conocimiento DGII del corpus)
     app/  evals/  aws/  specs/  demo/  docs/
   ```
3. CLAUDE.md mínimo (adaptar del formato GestoriaRD):
   proyecto, objetivo (demo vacante), región us-east-1, presupuesto $15, reglas de oro 9-10,
   comandos frecuentes (make test, make evals, make demo), y "PROHIBIDO: OpenSearch
   Serverless, credenciales en repo, recursos fuera de us-east-1".
4. Crear los 5 subagentes en .claude/agents/ (formato frontmatter como los de GestoriaRD):

   **analizador.md** — name: analizador · description: usar para mapear código/infra
   ANTES de tocar nada, siempre en paralelo, read-only.
   Prompt: "READ-ONLY, no modifiques nada. Analiza <área> en <ruta>. Devuelve: (1) mapa
   de archivos y funciones con file:línea, (2) dependencias, (3) riesgos si se toca X,
   (4) lo que el plan asume y NO es verdad en este código."

   **verificador-adversarial.md** — name: verificador-adversarial · description: usar
   SIEMPRE tras implementar, 3 en paralelo con lentes correctness/regresión/casos-límite.
   Prompt: "Tu trabajo es REFUTAR. El cambio <desc> en <archivos> dice lograr <acceptance>.
   Lente: [asignada]. Lee el código real y encuentra el escenario concreto (inputs/estado)
   donde falla. Si no puedes, di 'NO PUDE REFUTAR' y lista qué probaste."
   Regla de decisión: ≥2 de 3 encuentran fallo confirmado → corregir y re-verificar.

   **aws-deployer.md** — name: aws-deployer · description: único autorizado a crear/borrar
   recursos AWS. Reglas: solo us-east-1, solo recursos listados en la fase, pegar SIEMPRE
   el comando aws y su output, y el coste estimado del recurso antes de crearlo.

   **backend-dev.md** — name: backend-dev · description: FastAPI/PostgreSQL/LangGraph.
   Reglas: Pydantic estricto en toda I/O, try/except con logging en toda llamada externa,
   tests pytest por endpoint, un dueño por archivo.

   **evals-engineer.md** — name: evals-engineer · description: golden set, harness,
   Ragas, DeepEval, comparativas. Regla: los tres frameworks corren sobre el MISMO
   golden set; scores siempre a reports/ con fecha.

5. Descomprimir el prototipo fiscal-copilot, `git init`, primer commit, push al repo de H7.

### VERIFICACIÓN F1 (adversarial x1: "encuentra algo del entorno que falte para F2")
### GATE F1: tree del proyecto + `claude /agents` mostrando los 5 + git push OK. Evidencia pegada.
### COMMIT: `chore: F1 bootstrap arquitecto + agentes + CLAUDE.md` + tag f1-bootstrap-ok

# ═══════════════════════════════════════════════════════════════════
# FASE F2 — CIMIENTOS AWS: KB + LAMBDA + GUARDRAIL + AGENT (2 días)
# ═══════════════════════════════════════════════════════════════════
(Es el plan-bedrock-fiscal-copilot.md waves 2-4, ejecutado con el ciclo de 6 pasos.)

**1. ANALIZAR** (2 analizadores en paralelo):
   - A: prototipo local — qué hay en app/tools/registry.py, app/rag/corpus/, SYSTEM_PROMPT
     (es lo que se porta a AWS). Mapa exacto.
   - B: cuenta AWS — `aws bedrock list-foundation-models`, cuotas, verificación H completa.
**2. PLANIFICAR**: mapa de recursos a crear con nombre exacto y coste estimado c/u.
**3. IMPLEMENTAR** (aws-deployer, secuencial — infra no se paraleliza):
   a. S3 bucket corpus + subir app/rag/corpus/*.md
   b. Knowledge Base: embeddings Titan V2, vector store "Quick create → Amazon S3 Vectors"
      (PROHIBIDO OpenSearch Serverless). Sync. Anotar KB_ID.
   c. Lambda fiscal-copilot-tools (Python 3.12) portando calcular_itbis + validar_ncf +
      presentar_formato_606 al formato de eventos de action groups. add-permission a bedrock.
   d. Guardrail: prompt attacks ON, denied topic "asesoría de evasión fiscal", PII con
      regex cédula \d{3}-\d{7}-\d → ANONYMIZE. Anotar GUARDRAIL_ID.
   e. Bedrock Agent "fiscal-copilot": modelo Sonnet, instrucciones = SYSTEM_PROMPT portado,
      action group con functionSchema de las 3 tools, presentar_formato_606 con
      requireConfirmation ENABLED (HITL nativo), asociar KB y Guardrail. prepare-agent +
      alias "demo". Anotar AGENT_ID / ALIAS_ID.
   f. Evidencia Claude Code↔Bedrock: en una shell aparte, CLAUDE_CODE_USE_BEDROCK=1
      AWS_REGION=us-east-1 ANTHROPIC_MODEL=<inference profile Sonnet>
      CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096 → claude → /status → captura → salir (no seguir
      desarrollando ahí: créditos).
**4. VERIFICAR** (3 adversariales): (a) KB devuelve chunks correctos ante 5 preguntas
   trampa (sinónimos, pregunta fuera de corpus → debe decir que no está), (b) Lambda con
   inputs malformados (montos negativos, NCF basura, periodo inválido) no crashea,
   (c) guardrail: 5 intentos de injection distintos, todos bloqueados.
**5. GATE F2** (outputs pegados):
   [ ] `aws bedrock-agent-runtime retrieve --knowledge-base-id $KB_ID --retrieval-query text="fecha límite 606"` → chunk de formatos_606_607.md
   [ ] `aws lambda invoke ... test_event_itbis.json` → {"itbis": 18000.0, ...}
   [ ] `aws bedrock-agent-runtime invoke-agent ... "¿Cuánto ITBIS pago por 118000 con ITBIS incluido?"` → 18,000 con trace de tool
   [ ] invoke-agent "Presenta el 606 del periodo 202606 con 42 registros" → el agente PIDE CONFIRMACIÓN
   [ ] invoke-agent con injection → bloqueado por guardrail
   [ ] captura /status de Claude Code sobre Bedrock
   [ ] saldo de créditos pegado (gate de coste)
**6. COMMIT**: `feat: F2 stack Bedrock nativo (KB+Lambda+Guardrail+Agent)` + tag f2-bedrock-ok
   + aws/EVIDENCIA-F2.md con todos los IDs.

# ═══════════════════════════════════════════════════════════════════
# FASE F3 — BACKEND FASTAPI + POSTGRESQL + OBSERVABILIDAD (1.5 días)
# ═══════════════════════════════════════════════════════════════════
**1. ANALIZAR** (2 en paralelo): puertos/Docker libres en el 67 (no chocar con Registry
   :7008-7010 ni GestoriaRD) · esquema del prototipo (qué se reusa de app/).
**2. PLANIFICAR**: PostgreSQL 16 en Docker puerto NUEVO (p.ej. 5544), FastAPI puerto 7020.
   Mapa de dueños: models.py/db.py → backend-dev-1; routers → backend-dev-2 (archivos distintos).
**3. IMPLEMENTAR**:
   - Tablas: tenants, traces(trace_id, tenant, provider, model, input_tokens, output_tokens,
     cost_usd, latency_ms, ts), approvals(estado pending/approved/rejected/executed,
     checkpoint JSONB), facturas(ncf, rnc, monto, itbis, periodo, estado), workflow_steps
     (retries, estado, checkpoint).
   - FastAPI: POST /ask (invoke_agent + persistir traza), GET/POST /approvals,
     GET /traces?tenant&model, GET /dashboard (HTML: coste por tenant/modelo/proveedor),
     GET /health. Todo con response_model Pydantic estricto.
   - Seed: 20 facturas de 3 tenants.
   - Test unitario que demuestra el RECHAZO de una salida malformada (requisito structured outputs).
**4. VERIFICAR**: pytest verde + 3 adversariales (SQL injection en query params; approval
   decidida dos veces; /ask con el Agent caído → error controlado, no 500 pelado).
**5. GATE F3**: curl POST /ask → JSON válido con trace_id · SELECT sobre traces con cost_usd
   real · /dashboard renderiza coste por tenant · pytest output pegado.
**6. COMMIT** + tag f3-backend-ok.

# ═══════════════════════════════════════════════════════════════════
# FASE F4 — RAG MULTI-FUENTE + WORKFLOW + LANGGRAPH (2 días) [Opus]
# ═══════════════════════════════════════════════════════════════════
**1. ANALIZAR**: cómo añadir la tool consultar_facturas a la Lambda sin romper F2
   (¿la Lambda alcanza el PostgreSQL del 67? decisión: la tool consulta vía el endpoint
   FastAPI público del 67 con token, o se replican las facturas a DynamoDB — el analizador
   propone y el SM/Carlos decide ANTES de implementar).
**2-3. IMPLEMENTAR**:
   - Tool consultar_facturas(rnc, periodo) en el action group → el agente une KB + BD.
   - Workflow /workflow/factura: extraer campos (structured output) → validar_ncf →
     calcular_itbis → proponer asiento → approval → contabilizar. Retries máx 2/paso,
     estados en workflow_steps.
   - El MISMO workflow como grafo LangGraph con PostgresSaver (checkpointer en el
     PostgreSQL de F3) e interrupt() en la aprobación. Exportar diagrama a docs/grafo.png.
**4. VERIFICAR** (3 adversariales): factura con NCF tipo 02 (no válido para crédito) →
   escala a humano · kill -9 al proceso del grafo en mitad del interrupt → relanzar →
   reanuda exacto · pregunta multi-fuente con RNC inexistente → respuesta honesta.
**5. GATE F4**: transcript de la pregunta "¿cuánto ITBIS acumulan las facturas del RNC X
   en 202606 y cuándo se declara?" citando BD + KB · secuencia kill/resume pegada ·
   diagrama generado.
**6. COMMIT** + tag f4-workflows-ok.

# ═══════════════════════════════════════════════════════════════════
# FASE F5 — EVALS PROFESIONALES + ROUTER MULTI-MODELO (1.5 días)
# ═══════════════════════════════════════════════════════════════════
**IMPLEMENTAR** (evals-engineer):
   - Adaptar golden_set.jsonl (8+ casos, incluidos injection y HITL) a invoke_agent.
   - Harness propio → factualidad/tools/fuentes/coste/latencia (ya existe, portar).
   - Ragas (faithfulness, answer_relevancy, context_precision) + DeepEval (GEval) sobre
     el MISMO golden set.
   - Router: 3 rutas — Bedrock-Sonnet, Bedrock-Haiku (invoke_model Converse) y OpenAI
     con response_format json_schema strict. evals/run_all.py genera reports/comparativa.md
     con tabla coste/latencia/calidad por ruta + conclusión escrita de trade-offs.
**VERIFICAR**: 2 adversariales (¿el harness da falsos positivos? probar con una respuesta
   deliberadamente mala · ¿los scores de Ragas son estables entre 2 corridas?).
**GATE F5**: reports/comparativa.md generado y pegado · ≥6/8 golden en la mejor ruta ·
   coste total del run < $2.
**COMMIT** + tag f5-evals-ok.

# ═══════════════════════════════════════════════════════════════════
# FASE F6 — DESARROLLO AGÉNTICO DEL PROPIO REPO (1 día) [Opus]
# ═══════════════════════════════════════════════════════════════════
   - specs/: una spec estilo OpenSpec por feature de F3-F5 (retroactivas) + la ÚLTIMA
     feature nueva (p.ej. endpoint /metrics) se hace spec-first: spec escrita → Claude Code
     implementa → diff spec→código guardado como evidencia.
   - Skill dgii-fiscal ya creada en F1: documentar 1 uso real durante el desarrollo.
   - GitHub Actions: ci.yml → pytest + evals smoke (3 casos baratos vía Nova Micro o mock).
     Si baja el score → CI rojo.
   - DEMOSTRACIÓN: commit que degrada una respuesta → CI rojo (captura) → revert → verde.
**GATE F6**: Actions verde con job evals visible · captura del rojo provocado · specs/ con
   ≥4 specs · AGENTS.md completo.
**COMMIT** + tag f6-agentic-ok.

# ═══════════════════════════════════════════════════════════════════
# FASE F7 — DEMO PÚBLICA EN naiian.sypnose.cloud (1.5-2 días)
# ═══════════════════════════════════════════════════════════════════
La demo NO es un video: se entrega ACCESO al entrevistador. Una demo que un extraño usa
solo no perdona fallos. Componentes:

   a. **Exposición**: subdominio naiian.sypnose.cloud (DNS en Cloudflare, proxy activado,
      HTTPS) → Nginx del 67 → contenedor FastAPI. Analizador previo: no chocar con los
      servicios existentes del 67.
   b. **UI mínima de demo** (una página, sin framework pesado):
      · Chat contra el agente mostrando respuesta + fuentes citadas + trace desplegable
        (tools llamadas, tokens, coste USD, latencia de ESA petición).
      · Bandeja de aprobaciones: el entrevistador aprueba/rechaza la acción sensible
        y VE al agente reanudar (vive el HITL con sus manos).
      · Dashboard de coste por tenant/modelo/proveedor.
   c. **Protecciones (obligatorias, hay extraños dentro y Bedrock factura)**:
      · Token de invitado por header/URL, con expiración; sin token → 401.
      · Rate limit: 30 peticiones/hora por token.
      · Tope de gasto diario en la app: si SUM(cost_usd) del día > $2 → responder
        "límite de demo alcanzado" sin invocar Bedrock.
      · Datos 100% ficticios (ya lo son). Guardrails ya activos (F2).
   d. **DEMO-GUIDE.md** (y como página de inicio de la UI): "Prueba esto, en este orden"
      — las 8 pruebas con los prompts EXACTOS para copiar/pegar, incluido el intento de
      prompt injection para que el propio entrevistador lo lance y lo vea bloqueado, y
      el "presenta el 606 del periodo 202606" para que viva la aprobación humana.
      Los 2 flujos no auto-servibles (kill -9 del grafo LangGraph y CI rojo del eval de
      cambios) se documentan con capturas/logs en el repo + oferta de verlos en vivo.
   e. demo/demo_10min.sh se mantiene como guion para la demo EN VIVO de la entrevista.
   f. EVIDENCIA.md consolidado + aws/teardown.sh (NO ejecutar hasta cerrar el proceso
      de selección) + README con la MATRIZ requisito→evidencia arriba del todo.
   g. **Verificadores adversariales FINALES (3)**:
      (1) grep de secretos en TODO el repo — CERO hallazgos o no hay gate;
      (2) "eres el entrevistador con el token: intenta gastar dinero de más, ver datos
          de otro tenant, saltarte el rate limit o romper la app";
      (3) "sigue el DEMO-GUIDE como un extraño: ¿completas las 8 pruebas sin ayuda?".
**GATE F7**: https://naiian.sypnose.cloud responde con HTTPS válido · sin token → 401 ·
   las 8 pruebas del DEMO-GUIDE completadas por el adversarial (3) con outputs ·
   rate limit y tope de gasto demostrados · grep secretos limpio · Cost Explorer < $15.
**COMMIT** + tag v1.0.0-demo. Carlos la recorre entera como usuario → repo a público.

# ═══════════════════════════════════════════════════════════════════
# FASE F8 — EL GUION DE PRESENTACIÓN (Carlos + SM, ½ día)
# ═══════════════════════════════════════════════════════════════════

## 8.1 Entrega por ACCESO (sustituye al video)
  - Paquete de entrega: (1) URL https://naiian.sypnose.cloud, (2) token de invitado con
    expiración de 14 días, (3) link al repo con la matriz requisito→evidencia arriba,
    (4) el DEMO-GUIDE como primera pantalla.
  - Email de candidatura (5 líneas): "La vacante pide agentes sobre Bedrock, RAG, action
    groups, evals y human-in-the-loop. En vez de contarlo, lo construí y les doy acceso:
    [URL] con el token [X]. La guía de 8 pruebas está en la portada; el repo con la
    matriz de cobertura, aquí: [link]. Encantado de hacer el deep-dive en vivo."
  - AS EN LA MANGA para la entrevista: cada interacción del entrevistador queda en la
    tabla traces. Abrir el dashboard delante de él: "estas fueron tus peticiones, su
    coste, su latencia, y este el trace de tu intento de injection". Observabilidad
    demostrada sobre ellos mismos.
  - Mantenimiento durante el proceso: revisar a diario créditos y logs; NO ejecutar
    teardown.sh hasta cerrar la selección; rotar el token si se filtra.

## 8.1-BIS Guion de los 8 flujos (sirve para la demo EN VIVO en la entrevista)
[0:00-0:45] Apertura: "La vacante pide agentes sobre Bedrock, RAG, action groups, evals
  y human-in-the-loop. En vez de contarlo, lo construí. Esto es Fiscal Copilot: un agente
  de cumplimiento fiscal dominicano corriendo en Bedrock real. Este es el README con la
  matriz: cada requisito de su oferta, dónde está construido y cómo se prueba."
[0:45-2:00] Flujo 1-2: pregunta normativa → respuesta con CITA de la Knowledge Base;
  pregunta de cálculo → trace en pantalla mostrando el action group llamando la Lambda.
  Frase: "el LLM decide, el código calcula: los impuestos jamás los inventa un modelo."
[2:00-3:00] Flujo 3: pregunta que exige DOS fuentes (facturas en PostgreSQL + normativa
  en KB) → una sola respuesta citando ambas. "Retrieval sobre múltiples fuentes, literal."
[3:00-4:00] Flujo 4: intento de prompt injection en vivo → bloqueado por el Guardrail
  → mostrar la segunda capa en la app. "Defensa en profundidad, no una regex de adorno."
[4:00-5:30] Flujo 5: "presenta el 606" → el agente SE DETIENE y pide confirmación →
  aprobar desde /approvals → ejecuta → mostrar el estado en la BD. "Revisión, aprobación,
  rechazo y escalado: los cuatro verbos de su oferta, con estados persistidos."
[5:30-6:30] Flujo 6 (el momento estrella): workflow LangGraph procesando una factura →
  kill -9 al proceso EN CÁMARA → relanzar → reanuda exacto desde el checkpoint de
  PostgreSQL. "Flujos que no pueden perder contexto. No lo pierden ni matando el proceso."
[6:30-7:30] Flujo 7: evals/run_all.py en vivo → tabla comparativa Sonnet vs Haiku vs
  OpenAI (coste/latencia/calidad) con Ragas y DeepEval. "Sin evals no hay producción; y
  los trade-offs entre modelos se miden, no se opinan."
[7:30-8:30] Flujo 8 + desarrollo agéntico: dashboard de coste por tenant/modelo →
  luego el repo: AGENTS.md, specs/, la Skill, y el CI rojo del commit que degradó el
  golden set. "El propio repo se desarrolló como piden: specs, coding agents y evals de
  cambios. Este CI rojo es un eval de cambios funcionando."
[8:30-9:30] Cierre: arquitectura en un diagrama (30 seg), coste real (<$15), y:
  "Esto es una demo de fin de semana. Opero sistemas así en producción desde hace 2 años
  con 314 clientes B2B en el dominio fiscal. Encantado de hacer el deep-dive técnico que
  quieran, en vivo, sobre este repo."

## 8.2 Entrega de la candidatura
  - Email/aplicación: las 5 líneas de 8.1 con URL + token + repo. Asunto sugerido:
    "AI Engineer — no les cuento lo que sé hacer: les doy acceso, está corriendo en Bedrock".
  - LinkedIn: post opcional del proyecto (sin mencionar a la empresa) — refuerza el perfil.

## 8.3 Preparación de la entrevista técnica (con el SM)
  - Ensayar 3 deep-dives: (1) por qué S3 Vectors y no OpenSearch (coste, y cuándo NO
    usarlo: alta QPS), (2) por qué doble capa de guardrails, (3) cómo escalaría esto a
    multi-tenant real (ya lo hace en GestoriaRD: schema-per-tenant).
  - Tener el demo_10min.sh listo para correr EN VIVO si lo piden. Verificar recursos AWS
    activos la noche anterior (no hacer teardown antes de las entrevistas).

# ═══════════════════════════════════════════════════════════════════
# ORDEN GLOBAL, ROLES Y ANTI-COLISIÓN
# ═══════════════════════════════════════════════════════════════════
- Orden: H → F1 → F2 → F3 → F4 → F5 → F6 → F7 → F8. F5 puede solaparse con F4 (archivos
  distintos: evals/ vs app/). F6 puede solaparse con F5 (specs/ y .github/ vs evals/).
- Dueños por área: aws/ y recursos cloud → aws-deployer · app/ → backend-dev ·
  evals/ y reports/ → evals-engineer · specs/, AGENTS.md, README → arquitecto directo.
  README.md tiene UN dueño (arquitecto) — los demás aportan secciones por parche.
- SM (Claude web u otra sesión): audita el informe de CADA fase antes del gate. El
  arquitecto NO se autoconcede gates.
- Carlos: Fase H completa · decisión de F4 paso 1 · verificación humana de F7 (correr la
  demo él mismo una vez) · aprobación del repo a público · F8 con el SM.
- Cadencia: informe §4.1 al cerrar cada fase (qué se hizo + evidencia + desviaciones +
  feedback al SM). Sin informe = fase no cerrada.

## Estimación honesta
- Fase H: 1-2 h de Carlos + esperas de activación.
- F1-F7: 8-10 días de arquitecto (con verificación real incluida). Calendario: ~1.5 semanas.
- F8: ½ día Carlos+SM.
- Presupuesto AWS: < $15 de los $200. OpenAI: < $3 de los $5.

## Reglas críticas (resumen ejecutivo para el arquitecto)
1. Ciclo de 6 pasos SIEMPRE. Sin evidencia no hay gate. Sin informe no hay cierre.
2. Solo S3 Vectors. Solo us-east-1. Solo recursos listados. Coste pegado en cada gate.
3. Credenciales jamás en repo/logs. Grep de secretos antes de publicar.
4. Si algo falla: STOP, causa raíz, un cambio, re-verificar. Reportar al SM.
5. Mejora este documento. Si algo no encaja con la realidad del servidor o de AWS,
   corrígelo y repórtalo. Tú conoces el terreno mejor.

Modelo: claude-opus-4-6 (arquitecto, F4/F6) / claude-sonnet-4-6 (resto). Sub-agentes: sonnet.
MODO AUTONOMO: F1-F7 completas dentro de los recursos listados. PARAR en: Fase H (Carlos),
decisión de arquitectura de F4 paso 1, cualquier recurso AWS no listado, repo a público,
y cualquier gasto que proyecte superar $15.
