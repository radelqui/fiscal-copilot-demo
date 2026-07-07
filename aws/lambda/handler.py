"""Lambda fiscal-copilot-tools — action group del Bedrock Agent.

3 tools de composicion: explicar_componente, donde_verificar, generar_reporte_arquitectura.
Formato de eventos: Bedrock Agents function details (functionSchema).
"""
import json

COMPONENTES = {
    "bedrock_agent": {"nombre": "Bedrock Agent", "descripcion": "Agent ID 2BOPZRAI7X, Claude Sonnet 4.6, eu-central-1. Orquesta KB, tools y guardrail.", "modelo": "eu.anthropic.claude-sonnet-4-6", "region": "eu-central-1", "recursos": ["Agent 2BOPZRAI7X", "Alias TJRZR1FCDY"], "archivo_clave": "app/bedrock_agent.py"},
    "rag": {"nombre": "Knowledge Base (RAG)", "descripcion": "KB 5I5RDNA2V1 con S3 Vectors y Titan Embedding V2 (1024d). Corpus multi-fuente.", "modelo": "amazon.titan-embed-text-v2:0", "region": "eu-central-1", "recursos": ["KB 5I5RDNA2V1", "DataSource WEIATOAQ9Y"], "archivo_clave": "app/bedrock_agent.py"},
    "action_groups": {"nombre": "Action Groups (Tools)", "descripcion": "Lambda con 3 funciones: explicar_componente, donde_verificar, generar_reporte_arquitectura.", "modelo": "N/A", "region": "eu-central-1", "recursos": ["Lambda fiscal-copilot-tools"], "archivo_clave": "aws/lambda/handler.py"},
    "hitl": {"nombre": "Human-in-the-Loop", "descripcion": "generar_reporte_arquitectura con requireConfirmation. returnControl + bandeja aprobacion.", "modelo": "N/A", "region": "N/A", "recursos": ["returnControl", "approvals table"], "archivo_clave": "app/routers/demo.py"},
    "guardrails": {"nombre": "Guardrails", "descripcion": "Guardrail xgn38kcg6hrq: denied topics + content filters + PROMPT_ATTACK.", "modelo": "N/A", "region": "eu-central-1", "recursos": ["Guardrail xgn38kcg6hrq"], "archivo_clave": "N/A"},
    "evals": {"nombre": "Evaluaciones LLM", "descripcion": "golden_set + Ragas + DeepEval + router comparativa.", "modelo": "N/A", "region": "N/A", "recursos": ["golden_set.jsonl"], "archivo_clave": "evals/run_all.py"},
    "observabilidad": {"nombre": "Observabilidad", "descripcion": "Traces PostgreSQL: tokens, coste, latencia. /metrics + /dashboard.", "modelo": "N/A", "region": "N/A", "recursos": ["/metrics", "/dashboard"], "archivo_clave": "app/routers/traces.py"},
    "backend": {"nombre": "Backend FastAPI", "descripcion": "FastAPI + PostgreSQL. Auth token, rate limiting, cost cap.", "modelo": "N/A", "region": "eu-central-1", "recursos": ["FastAPI :7020", "PostgreSQL :5544"], "archivo_clave": "app/main.py"},
}

VERIFICACION = {
    "bedrock_agent": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > app/bedrock_agent.py", "architecture": "/architecture (nodo AGENT)"},
    "rag": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > app/bedrock_agent.py", "architecture": "/architecture (nodo KB)"},
    "action_groups": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > aws/lambda/handler.py", "architecture": "/architecture (nodo LAMBDA)"},
    "hitl": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > app/routers/demo.py", "architecture": "/architecture (nodo HITL)"},
    "guardrails": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot", "architecture": "/architecture (nodo GUARDRAIL)"},
    "evals": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > evals/", "architecture": "N/A"},
    "observabilidad": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > app/routers/traces.py", "architecture": "/architecture (nodo PostgreSQL)"},
    "backend": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > app/main.py", "architecture": "/architecture (nodo FastAPI)"},
}


def explicar_componente(componente: str) -> dict:
    componente = (componente or "").strip().lower().replace(" ", "_").replace("-", "_")
    if componente not in COMPONENTES:
        raise ValueError(f"Componente desconocido: {componente}. Validos: {', '.join(sorted(COMPONENTES))}")
    return {**COMPONENTES[componente], "componente": componente}


def donde_verificar(componente: str) -> dict:
    componente = (componente or "").strip().lower().replace(" ", "_").replace("-", "_")
    if componente not in VERIFICACION:
        raise ValueError(f"Componente desconocido: {componente}. Validos: {', '.join(sorted(VERIFICACION))}")
    return {"componente": componente, **VERIFICACION[componente]}


def generar_reporte_arquitectura(secciones: str = "todas") -> dict:
    validas = list(COMPONENTES.keys())
    if secciones.strip().lower() in ("todas", "all", ""):
        lista = validas
    else:
        lista = [s.strip().lower().replace(" ", "_").replace("-", "_") for s in secciones.split(",")]
        invalidas = [s for s in lista if s not in validas]
        if invalidas:
            raise ValueError(f"Secciones invalidas: {invalidas}")
    return {
        "secciones": lista,
        "estado": "PENDIENTE_APROBACION",
        "mensaje": f"Reporte de arquitectura ({len(lista)} secciones) preparado. Requiere aprobacion humana.",
    }


def _parametros(event: dict) -> dict:
    return {p["name"]: p.get("value", "") for p in event.get("parameters", [])}


DISPATCH = {
    "explicar_componente": lambda p: explicar_componente(p.get("componente", "")),
    "donde_verificar": lambda p: donde_verificar(p.get("componente", "")),
    "generar_reporte_arquitectura": lambda p: generar_reporte_arquitectura(p.get("secciones", "todas")),
}


def lambda_handler(event, context):
    funcion = event.get("function")
    try:
        resultado = DISPATCH[funcion](_parametros(event))
    except KeyError as e:
        resultado = {"error": f"Funcion o parametro desconocido: {e}"}
    except (ValueError, TypeError) as e:
        resultado = {"error": str(e)}
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup"),
            "function": funcion,
            "functionResponse": {
                "responseBody": {
                    "TEXT": {"body": json.dumps(resultado, ensure_ascii=False)}
                }
            },
        },
    }
