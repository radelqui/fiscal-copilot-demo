# Cómo se hizo ¿Cómo Estoy Hecho? — De requisitos NAIIAN a demo funcional

## Introducción

¿Cómo Estoy Hecho? es una demo técnica construida para la entrevista en NAIIAN, una empresa especializada en soluciones de inteligencia artificial sobre AWS. El objetivo fue demostrar competencias end-to-end sobre AWS Bedrock: no basta con invocar un modelo, hay que componer agentes con herramientas reales, asegurarlos con guardrails, evaluarlos con métricas objetivas, y operar todo con observabilidad de producción. El dominio elegido fue la autointrospección técnica del propio agente: el sistema puede explicar cómo está construido, qué componentes utiliza, cómo se conectan entre sí, y dónde verificar cada afirmación. Es un caso de uso con suficiente profundidad técnica para que la arquitectura tenga sentido real —no es un hola-mundo de chatbot— y tiene la particularidad de ser autoreferencial: el agente es exactamente la cosa que explica.

---

## 1. Bedrock Agents + Action Groups

### Requisito NAIIAN
"Building and managing Bedrock Agents with action flows"

### Decisión

La alternativa más obvia para un agente de introspección técnica era construirlo con LangChain o LangGraph: más control, más portabilidad, menos vendor lock-in. La decidimos descartar deliberadamente porque el requisito de NAIIAN pide Bedrock Agents nativos, y hay una diferencia entre conocer la abstracción y conocer el servicio. Bedrock Agents maneja el loop de razonamiento internamente —incluyendo la gestión de sesiones, el routing hacia herramientas, y el acceso a la knowledge base— lo que obliga a entender su modelo de eventos (completion stream, trace events, returnControl) en lugar de esconderlo detrás de un wrapper.

### Implementación

El agente `2BOPZRAI7X` corre en `eu-central-1` con el modelo `eu.anthropic.claude-sonnet-4-6-20250514-v1:0` (inference profile de la región). Tiene un action group `introspection-tools` que apunta a la función Lambda `fiscal-copilot-tools`, que expone tres herramientas: `explicar_componente` (explica cualquier componente del sistema con atribución de fuente), `donde_verificar` (indica dónde verificar una afirmación sobre la arquitectura), y `generar_reporte_arquitectura` (genera un reporte estructurado de la arquitectura completa). El cliente está en `app/bedrock_agent.py` e invoca el agente con `enableTrace=True`, que es el detalle crítico: sin ese flag, Bedrock no emite trace events y los tokens de uso nunca llegan. Los tokens reales se extraen acumulando `modelInvocationOutput.metadata.usage` de todos los eventos de trace en el stream de `completion`. Una invocación real típica registra 4203 tokens de entrada, 356 de salida, coste de $0.017949 y latencia de 7628ms.

---

## 2. RAG con S3 Vectors (Knowledge Base)

### Requisito NAIIAN
"RAG on Amazon Bedrock"

### Decisión

Bedrock ofrece dos opciones de vector store para sus knowledge bases: OpenSearch Serverless y S3 Vectors. OpenSearch Serverless tiene un coste fijo de ~$700/mes en modo activo, incompatible con el presupuesto de $15 de esta demo. S3 Vectors es el servicio nuevo de AWS (2025), diseñado exactamente para casos como este: bajo coste, integración nativa con Bedrock, sin infraestructura que gestionar. La elección también tiene valor narrativo en la entrevista: demuestra que se conoce el catálogo actualizado de AWS y se toman decisiones informadas de coste.

### Implementación

La Knowledge Base `5I5RDNA2V1` usa embeddings Titan V2 de 1024 dimensiones. El corpus contiene documentación técnica del propio proyecto: decisiones de arquitectura, descripción de componentes, visión general del stack, justificaciones de diseño, y guías de operación. El agente accede a la KB automáticamente en cada invocación y las respuestas incluyen atribución de fuente, lo que permite verificar que el RAG está activo: una pregunta sobre "¿qué base de datos usa este proyecto?" debe responder explicando PostgreSQL y referenciar el documento de arquitectura correspondiente. El corpus local (en `app/rag/corpus/`) replica los mismos documentos para el mock agent, garantizando que los tests sean coherentes con el comportamiento real.

---

## 3. Guardrails

### Requisito NAIIAN
"Guardrails for Amazon Bedrock"

### Decisión

Los guardrails podrían haberse implementado como filtros en la capa FastAPI (antes de invocar el agente), pero eso solo protege el perímetro externo. El valor del Guardrail de Bedrock es que opera dentro del ciclo de inferencia del agente, interceptando tanto la entrada del usuario como la salida del modelo. Esto demuestra comprensión de la arquitectura de seguridad multi-capa: validación en API (rate limiting, auth) más guardrail dentro del modelo.

### Implementación

El guardrail `xgn38kcg6hrq` está configurado con dos protecciones principales: filtro de temas fuera de scope (el agente no debe responder sobre nada que no sea la composición técnica del propio sistema) y detección de prompt injection (intentos de "ignora las instrucciones anteriores" o similares). El golden set de evaluaciones en `evals/golden_set.jsonl` incluye el caso `injection-001`, que verifica que el agente rechaza el ataque y se identifica correctamente como agente de introspección técnica. La protección de XSS complementaria vive en la UI (`app/static/demo.html`) mediante `escapeHtml` y uso de `textContent` en lugar de `innerHTML`.

---

## 4. Structured Outputs (Pydantic)

### Requisito NAIIAN
"Structured outputs using Pydantic"

### Decisión

El uso de Pydantic no es decorativo: es la interfaz de contrato entre capas. Cada endpoint de FastAPI declara su `response_model` con un modelo Pydantic, lo que hace que FastAPI valide y serialice la respuesta automáticamente. Cualquier campo incorrecto o ausente falla en tiempo de desarrollo, no en producción. Esta decisión de diseño garantiza que la especificación del endpoint y su implementación nunca diverjan silenciosamente.

### Implementación

`app/schemas.py` contiene más de diez modelos Pydantic: `TraceSchema` (registro de una invocación), `ApprovalSchema` (workflow HITL), `ApprovalDecision` (input del usuario), y los tres modelos del endpoint de métricas (`MetricsResponse`, `MetricsModelBreakdown`, `MetricsTenantBreakdown`). Las tools de la Lambda en `aws/lambda/handler.py` también tienen sus schemas JSON declarados como `functionSchema`, que es el mecanismo nativo de Bedrock para el tool calling: `explicar_componente`, `donde_verificar`, y `generar_reporte_arquitectura`. El endpoint `/metrics` es el ejemplo más claro de diseño spec-first: el schema Pydantic fue escrito en `specs/metrics-endpoint.md` antes de que existiera una sola línea de implementación en `app/routers/metrics.py`.

---

## 5. Human-in-the-Loop (HITL)

### Requisito NAIIAN
"Human-in-the-loop patterns"

### Decisión

El patrón HITL más común en demos es un checkbox "requiere aprobación" que pausa la ejecución artificialmente. La decisión fue usar el mecanismo nativo de Bedrock: `requireConfirmation=ENABLED` en la action group, que hace que el agente emita un evento `returnControl` en lugar de ejecutar la herramienta. Esto no es simulación: es el comportamiento real del servicio, lo que significa que el backend tiene que detectar ese evento, crear un registro de aprobación, y gestionar el estado de la sesión hasta que el usuario decida. La complejidad adicional vale porque demuestra comprensión del protocolo de Bedrock, no solo de la UI.

### Implementación

Cuando el usuario pide "genera un reporte de arquitectura", el agente retorna `returnControl` con `requireConfirmation=ENABLED` porque `generar_reporte_arquitectura` tiene esta opción activada. El backend, en `app/routers/demo.py` (líneas 95-104), detecta esta condición a través del parsing en `app/bedrock_agent.py` (líneas 147-157) e inserta un registro en la tabla `approvals` con `status=pending`. La UI en `app/static/demo.html` tiene un panel lateral que hace polling cada 5 segundos y muestra las aprobaciones pendientes. El usuario puede aprobar o rechazar desde ahí, lo que invoca `POST /demo/{token}/approvals/{id}/decide`. El backend valida el estado: 404 si la aprobación no existe, 409 si ya fue decidida, 422 si el valor de `decision` no es válido. La spec completa está en `specs/hitl-workflow.md` y hay cinco tests automatizados en `tests/test_f7.py::TestDemoApprovals`.

---

## 6. Evaluaciones LLM (Ragas + DeepEval)

### Requisito NAIIAN
"LLM evaluation frameworks (Ragas, DeepEval)"

### Decisión

El plan inicial era usar Ragas 0.4.3 como librería. Durante la implementación se encontró que sus imports estaban rotos en esa versión con las dependencias actuales del proyecto. La decisión fue implementar los jueces manualmente usando Bedrock Haiku como modelo evaluador, en lugar de depender de un wrapper roto. Esta decisión resultó ser mejor para la demo: un juez manual es más transparente (se puede leer el prompt exacto), más barato (Haiku en lugar de GPT-4), y más fácil de explicar en una entrevista. El mismo razonamiento aplica para DeepEval GEval: se implementó el patrón directamente con Haiku como fallback cuando OpenAI no está disponible.

### Implementación

El pipeline de evaluación en `evals/` tiene cuatro componentes. El harness en `evals/run_harness.py` ejecuta el golden set de 8 casos técnicos contra el agente y verifica respuestas con lógica OR (la respuesta debe contener al menos uno de los valores esperados). Los jueces en `evals/judges.py` implementan cuatro métricas: `faithfulness` (la respuesta está fundamentada en el contexto), `answer_relevancy` (la respuesta responde la pregunta), `context_precision` (el contexto recuperado es relevante), y `geval` (evaluación holística de calidad). El router en `evals/router.py` compara cuatro modelos —Haiku 4.5, Nova Micro, GPT-4o-mini, Sonnet 4.6— en coste, latencia y calidad. Los resultados muestran que Nova Micro es el más rápido (1473ms, $0.00004/query), Haiku el balance costo/calidad para demo ($0.0014/query), y Sonnet 4.6 el estándar de producción ($0.018/query, 7628ms). El coste total del pipeline de evaluaciones completo fue de $0.018.

---

## 7. Observabilidad por tenant y coste

### Requisito NAIIAN
(Implícito: production-ready monitoring)

### Decisión

Un agente que no registra sus invocaciones no puede ser operado en producción. La decisión fue tratar la observabilidad como un ciudadano de primera clase desde el principio: cada invocación persiste sus métricas en PostgreSQL, y hay endpoints dedicados para consultarlas. El endpoint `/metrics` fue el caso de prueba para la metodología spec-driven: se escribió la especificación completa (schema JSON, queries SQL, modelos Pydantic, criterios de aceptación) antes de escribir una sola línea de implementación.

### Implementación

La tabla `traces` en PostgreSQL persiste por cada invocación: `trace_id`, `tenant_id`, `model`, `provider`, `tokens_in`, `tokens_out`, `cost_usd`, `latency_ms`, `tools_used` (array de nombres), y `created_at`. El endpoint `GET /metrics` en `app/routers/metrics.py` computa totales acumulados, percentiles p50/p95 con `PERCENTILE_CONT` nativo de PostgreSQL, y desgloses por modelo y por tenant. El endpoint `GET /dashboard` en `app/routers/dashboard.py` renderiza la misma información como HTML con tablas navegables. Hay un detalle de implementación que merece mención: `enableTrace=True` en `invoke_agent` es obligatorio para que Bedrock emita los eventos de trace; sin él, los campos de tokens llegan a cero aunque el llamado sea exitoso. Los tokens reales se acumulan de `modelInvocationOutput.metadata.usage` en cada evento de trace, no de un campo de respuesta de alto nivel.

---

## 8. Desarrollo agéntico (spec-driven + arquitecto/sub-agentes)

### Requisito NAIIAN
"Agentic development skills"

### Decisión

"Desarrollo agéntico" puede significar muchas cosas. La interpretación adoptada fue concreta: usar Claude Code como arquitecto y sub-agentes Sonnet como implementadores, con una metodología de seis fases (métrica de éxito, investigar, blueprint, implementar, verificar, gate) aplicada rigurosamente a cada fase del proyecto. Esto no es solo un detalle de proceso: el historial de commits con `Co-Authored-By: Claude` y los informes por fase en `docs/INFORME-*.md` son evidencia auditable de cómo se construyó el sistema.

### Implementación

El proyecto se desarrolló en seis fases con gate explícito entre cada una: F1 (bootstrap, tools, mock agent, corpus), F2 (stack AWS: agente, KB, Lambda, Guardrail), F3 (backend PostgreSQL, endpoints, HITL, dashboard), F5 (pipeline de evaluaciones), F7-UI (autenticación por token, cliente Bedrock, interfaz de chat), y consolidación final (observabilidad real, README, specs, higiene de secretos). Cada fase tiene su informe en `docs/` con evidencia cuantificable de que el gate fue superado. Los sub-agentes trabajaron en paralelo sobre archivos distintos para evitar conflictos: nunca dos agentes sobre el mismo archivo en la misma wave. El patrón Mock Agent (`USE_MOCK_AGENT=1`) permitió que las fases F1, F3, F5 y F7 avanzaran completamente sin acceso a AWS, con herramientas Python locales que replican el comportamiento de la Lambda. La suite de tests creció de 57 en F1 a 82 en consolidación final, con cobertura de tools, API, auth, HITL, métricas y observabilidad.

---

## 9. Infraestructura (región + coste + seguridad)

### Decisión

La región `eu-central-1` (Frankfurt) fue elegida por dos razones complementarias. Técnicamente, el servidor donde corre FastAPI está en Alemania, lo que da aproximadamente 5ms de latencia hacia los servicios Bedrock de la misma región. Narrativamente, GDPR es un argumento de venta real: documentación técnica procesada en infraestructura europea bajo GDPR es relevante para cualquier cliente empresarial europeo o que opere en Europa.

### Implementación

FastAPI corre en el puerto 7020 con autenticación por token (tokens de 14 días de validez, 30 requests por hora, cap de $2 por día). PostgreSQL corre en el puerto 5544 con cuatro tablas: `traces`, `approvals`, `tenants`, y `facturas`. El presupuesto final fue de $15 de los $100 en créditos AWS disponibles. La seguridad de credenciales se gestionó con `aws/ids.env` en `.gitignore` y un scan de secretos antes de cada commit (0 credenciales reales encontradas en el repo). El archivo `aws/ids.env.example` documenta el formato esperado sin valores reales.

---

## Conclusión

¿Cómo Estoy Hecho? demuestra que construir con AWS Bedrock implica tomar decisiones de diseño en múltiples niveles simultáneamente: elegir entre vector stores según el modelo de coste real, entender el protocolo de eventos del agente para extraer observabilidad correctamente, implementar seguridad en capas (guardrail + rate limiting + validación de inputs), y evaluar la calidad del sistema con métricas objetivas en lugar de afirmaciones subjetivas. El proyecto no es solo un catálogo de servicios AWS utilizados: es un sistema operado con la misma disciplina que se aplicaría en producción, con tests, specs escritas antes del código, gates de calidad entre fases, y evidencia reproducible de cada decisión.
