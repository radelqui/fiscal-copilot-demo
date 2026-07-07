# Verificación en Vivo — Registry como Fuente de Verdad

Cada componente de Fiscal Copilot puede verificarse en tiempo real a través del
[Registry público](https://registry.sypnose.cloud).

## Tabla de Verificación

| Componente | Qué verificar | Dónde verlo en vivo |
|-----------|---------------|---------------------|
| **Bedrock Agent** | Código del cliente que invoca el agente | [registry.sypnose.cloud](https://registry.sypnose.cloud) → CodeGraph → fiscal-copilot → `app/bedrock_agent.py` |
| **RAG / Corpus** | Documentos del corpus fiscal | CodeGraph → fiscal-copilot → `app/rag/corpus/` |
| **Tools fiscales** | Implementación de calcular_itbis, validar_ncf, presentar_formato_606 | CodeGraph → fiscal-copilot → `app/tools/` y `aws/lambda/handler.py` |
| **HITL (Human-in-the-Loop)** | Flujo de aprobación returnControl | CodeGraph → fiscal-copilot → `app/routers/` (demo.py, approvals) |
| **Observabilidad** | Métricas en vivo, dashboard | Endpoints de la demo: `/metrics` (JSON) y `/dashboard` (HTML) |
| **Flujo completo** | Diagrama Mermaid interactivo | Página `/architecture` de la propia demo |
| **Estructura del proyecto** | Archivos, rutas, dependencias | [registry.sypnose.cloud/registry/project/fiscal-copilot](https://registry.sypnose.cloud) → proyecto fiscal-copilot |
| **Evaluaciones** | Golden set, judges, router comparativa | CodeGraph → fiscal-copilot → `evals/` |
| **Specs** | Especificaciones HITL y metrics | CodeGraph → fiscal-copilot → `specs/` |

## Cómo usar el Registry

1. Abre [registry.sypnose.cloud](https://registry.sypnose.cloud)
2. Busca el proyecto **fiscal-copilot** en la lista
3. Haz click en **CodeGraph** para ver la estructura del código
4. Navega a cualquier archivo y haz click para verlo como texto

## Cómo usar /architecture

1. Desde la demo, haz click en el botón **◈ Arquitectura**
2. El diagrama Mermaid muestra el flujo completo: Browser → FastAPI → Bedrock Agent → KB/Lambda/Guardrail → PostgreSQL
3. Haz click en cualquier nodo para ver el archivo o recurso correspondiente
