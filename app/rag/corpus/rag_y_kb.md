# RAG y Knowledge Base — Recuperación Semántica en Este Demo

## Knowledge Base en AWS Bedrock

Este proyecto usa una Knowledge Base de Bedrock con ID `5I5RDNA2V1`, configurada en `eu-central-1`.  
La KB indexa el corpus de arquitectura del propio proyecto — es decir, los documentos que explican cómo está construido este demo.

## Motor de Embeddings

- **Modelo**: Amazon Titan Embeddings V2  
- **Dimensiones**: 1024  
- Los documentos se fragmentan automáticamente por Bedrock antes de indexar.

## Almacenamiento: S3 Vectors (No OpenSearch)

El backend de vectores es **S3 Vectors**, no OpenSearch Serverless.  
Esta decisión fue deliberada y tiene impacto directo en el coste:

| Opción | Coste mensual aproximado |
|---|---|
| OpenSearch Serverless | ~$700/mes (mínimo 2 OCUs) |
| S3 Vectors | ~$0 en volúmenes de demo |

Para una demo técnica con corpus pequeño (~20 documentos), OpenSearch Serverless es desproporcionado. S3 Vectors fue introducido por AWS en 2025 precisamente para este caso de uso.

## Qué Contiene el Corpus

El corpus está en `app/rag/corpus/` y contiene documentos Markdown sobre:
- Cómo funciona el Bedrock Agent (action groups, tools, trace)
- La configuración del Knowledge Base (este documento)
- El sistema HITL y los Guardrails de seguridad
- Observabilidad, métricas y evaluaciones

Todos los documentos describen la **arquitectura del propio demo** — no contienen información sobre legislación ni casos de uso fiscales.

## Atribución de Fuentes

Cuando Bedrock responde usando la KB, las respuestas incluyen referencias a los chunks recuperados (`retrievedReferences`). El frontend muestra estas fuentes como "Fuente: [nombre del documento]" debajo de cada respuesta generada vía KB.

## Modo Mock

Con `USE_MOCK_AGENT=1`, el agente local lee directamente los archivos `.md` del corpus y realiza búsqueda por similitud semántica usando embeddings locales, sin llamar a AWS. Esto permite desarrollar y probar el flujo RAG sin coste.

## Actualizar el Corpus

Para añadir documentación nueva:
1. Colocar el archivo `.md` en `app/rag/corpus/`
2. Ejecutar `make sync-kb` para re-indexar en S3 Vectors
3. Bedrock sincroniza automáticamente en minutos
