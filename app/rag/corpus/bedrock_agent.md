# Bedrock Agent — Cómo Funciona el Núcleo de Este Demo

## Identidad del Agente

El agente central de este proyecto corre en AWS Bedrock, región `eu-central-1` (Frankfurt).  
- **Agent ID**: `2BOPZRAI7X`  
- **Modelo**: Claude Sonnet 4.6 via inference profile `eu.anthropic.claude-sonnet-4-6-v1:0`  
- La región Frankfurt se eligió porque el servidor de ejecución está en Alemania (~5ms latencia) y permite usar GDPR como argumento de arquitectura en entrevistas.

## Action Group: fiscal-tools

El agente tiene un único action group llamado `fiscal-tools`, que apunta a la Lambda `fiscal-copilot-tools`.  
El action group define el contrato OpenAPI con tres herramientas disponibles:

| Herramienta | Qué hace |
|---|---|
| `explicar_componente` | Devuelve documentación sobre un componente de la arquitectura (ej: "¿qué es el Knowledge Base?") |
| `donde_verificar` | Indica dónde en el código o en AWS Console se puede verificar un comportamiento específico |
| `generar_reporte_arquitectura` | Genera un informe completo de todos los componentes activos — tiene HITL habilitado |

## Trazabilidad y Extracción de Tokens

El cliente invoca al agente con `enableTrace=True`. Esto es obligatorio para extraer el uso de tokens, que no viene en la respuesta final sino en los eventos de trace.

El flujo de extracción de tokens es:
1. Iterar sobre los eventos de `response_stream`
2. Buscar eventos donde `event['trace']['trace']['orchestrationTrace']` exista
3. Dentro de la traza de orquestación, buscar `modelInvocationOutput.metadata.usage`
4. Sumar `inputTokens` y `outputTokens` de cada evento encontrado

El código completo de invocación vive en `app/bedrock_agent.py`. El cliente usa `boto3.client('bedrock-agent-runtime')` con la región configurada por variable de entorno `AWS_REGION`.

## Modo Mock (Desarrollo Local)

Para desarrollo sin consumir créditos AWS, se puede activar `USE_MOCK_AGENT=1`.  
En este modo, `app/bedrock_agent.py` reemplaza la llamada a Bedrock con un agente local que usa LangGraph + búsqueda en el corpus RAG. Los tokens se simulan y el coste reportado es $0.00.

## Punto de Entrada

La API FastAPI en `app/main.py` expone `POST /chat` que acepta `{session_id, message}` y devuelve `{response, tokens_in, tokens_out, cost_usd, latency_ms, tools_used}`.
