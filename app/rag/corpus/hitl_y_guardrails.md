# HITL y Guardrails — Seguridad y Control Humano en Este Demo

## Human-in-the-Loop (HITL)

La herramienta `generar_reporte_arquitectura` tiene `requireConfirmation=ENABLED` en la definición del action group. Esto activa el mecanismo HITL nativo de Bedrock Agents.

### Flujo HITL Paso a Paso

1. El usuario solicita un reporte de arquitectura
2. El agente decide invocar `generar_reporte_arquitectura`
3. En lugar de ejecutar la Lambda, Bedrock emite un evento `returnControl` en el stream
4. El backend (`app/bedrock_agent.py`) detecta el evento `returnControl` en lugar de una respuesta final
5. El backend crea un registro de aprobación en PostgreSQL con `status=pending` y un `approval_id` único
6. La respuesta al frontend incluye `requires_approval=true` junto con el `approval_id`
7. El frontend muestra un panel de aprobación con descripción de la acción pendiente
8. El frontend hace polling cada **5 segundos** a `GET /approvals/{approval_id}`
9. Cuando el usuario aprueba (`POST /approvals/{approval_id}/approve`), el backend reanuda la invocación del agente pasando el resultado de la herramienta
10. Si el usuario rechaza, el agente recibe el rechazo y responde explicando que la acción fue cancelada

## Guardrails de Bedrock

El agente tiene asociado el Guardrail con ID `xgn38kcg6hrq`, configurado con:

| Protección | Configuración |
|---|---|
| Denied Topics | Filtra temas que salen del alcance del demo |
| Content Filters | MEDIUM en violencia, odio, contenido inapropiado |
| PROMPT_ATTACK Detection | Habilitado — detecta intentos de jailbreak e inyección de prompts |

El guardrail se evalúa **antes** de que el agente procese el input del usuario y **después** de que genere la respuesta.

## Seguridad Multi-Capa

La seguridad del demo está implementada en tres capas independientes:

1. **Guardrail en Bedrock** — primera línea, evalúa inputs/outputs a nivel de LLM
2. **Rate Limiting en la API** — `app/middleware.py` limita a 20 requests/minuto por IP usando un sliding window en memoria
3. **Protección XSS en el Frontend** — todas las respuestas del agente se sanitizan antes de renderizar en el DOM; no se usa `innerHTML` con contenido del agente

## Por Qué HITL en Una Demo

HITL demuestra un patrón crítico en sistemas de producción: operaciones irreversibles o de alto impacto no deben ejecutarse sin confirmación humana. En este demo, `generar_reporte_arquitectura` sirve como ejemplo ilustrativo de esa categoría — una acción costosa que conviene aprobar antes de lanzar.
