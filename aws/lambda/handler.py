"""Lambda demo-naiian-tools — action group del Bedrock Agent.

3 tools de composicion: explicar_componente, donde_verificar, generar_reporte_arquitectura.
Formato de eventos: Bedrock Agents function details (functionSchema).
"""
import json

COMPONENTES = {
    "bedrock_agent": {"nombre": "Bedrock Agent", "descripcion": "Agent ID 2BOPZRAI7X, Claude Sonnet 4.6, eu-central-1. Orquesta KB, tools y guardrail.", "modelo": "eu.anthropic.claude-sonnet-4-6", "region": "eu-central-1", "recursos": ["Agent 2BOPZRAI7X", "Alias TJRZR1FCDY"], "archivo_clave": "app/bedrock_agent.py"},
    "rag": {"nombre": "Knowledge Base (RAG)", "descripcion": "KB 5I5RDNA2V1 con S3 Vectors y Titan Embedding V2 (1024d). Corpus multi-fuente.", "modelo": "amazon.titan-embed-text-v2:0", "region": "eu-central-1", "recursos": ["KB 5I5RDNA2V1", "DataSource WEIATOAQ9Y"], "archivo_clave": "app/bedrock_agent.py"},
    "action_groups": {"nombre": "Action Groups (Tools)", "descripcion": "Lambda con 3 funciones: explicar_componente, donde_verificar, generar_reporte_arquitectura.", "modelo": "N/A", "region": "eu-central-1", "recursos": ["Lambda demo-naiian-tools"], "archivo_clave": "aws/lambda/handler.py"},
    "hitl": {"nombre": "Human-in-the-Loop", "descripcion": "generar_reporte_arquitectura con requireConfirmation. returnControl + bandeja aprobacion.", "modelo": "N/A", "region": "N/A", "recursos": ["returnControl", "approvals table"], "archivo_clave": "app/routers/demo.py"},
    "guardrails": {"nombre": "Guardrails", "descripcion": "Guardrail xgn38kcg6hrq: denied topics + content filters + PROMPT_ATTACK.", "modelo": "N/A", "region": "eu-central-1", "recursos": ["Guardrail xgn38kcg6hrq"], "archivo_clave": "N/A"},
    "evals": {"nombre": "Evaluaciones LLM", "descripcion": "golden_set + Ragas + DeepEval + router comparativa.", "modelo": "N/A", "region": "N/A", "recursos": ["golden_set.jsonl"], "archivo_clave": "evals/run_all.py"},
    "observabilidad": {"nombre": "Observabilidad", "descripcion": "Traces PostgreSQL: tokens, coste, latencia. /metrics + /dashboard.", "modelo": "N/A", "region": "N/A", "recursos": ["/metrics", "/dashboard"], "archivo_clave": "app/routers/traces.py"},
    "backend": {"nombre": "Backend FastAPI", "descripcion": "FastAPI + PostgreSQL. Auth token, rate limiting, cost cap.", "modelo": "N/A", "region": "eu-central-1", "recursos": ["FastAPI :7020", "PostgreSQL :5544"], "archivo_clave": "app/main.py"},
    "desarrollo_agentico": {"nombre": "Desarrollo Agéntico", "descripcion": "Specs escritas antes del código (specs/), coding agents (Claude Code + arquitectos), Skills (.claude/skills/), AGENTS.md como manifiesto del equipo, y evals que verifican cada cambio.", "modelo": "N/A", "region": "N/A", "recursos": ["specs/", ".claude/skills/", "AGENTS.md"], "archivo_clave": "AGENTS.md"},
    "multi_model": {"nombre": "Comparativa Multi-Modelo", "descripcion": "Comparativa de rutas de modelo (Bedrock Sonnet/Haiku, OpenAI GPT-4o-mini, Nova Micro) por coste, latencia y calidad. Router en evals/router.py, resultados en reports/comparativa.md.", "modelo": "N/A", "region": "N/A", "recursos": ["evals/router.py", "reports/comparativa.md"], "archivo_clave": "evals/router.py"},
}

REQUISITOS = {
    "workflows_structured_outputs": {
        "keywords": ["workflow", "structured output", "tool calling", "pydantic"],
        "componentes": ["action_groups", "backend"],
        "confirma": "Sí. Construyo workflows con structured outputs (schemas Pydantic estrictos I/O) y tool calling (action group Lambda con functionSchema tipado).",
    },
    "agentes_bedrock": {
        "keywords": ["action flow", "permisos", "estados", "trazabilidad", "agentes sobre", "bedrock agent"],
        "componentes": ["bedrock_agent", "action_groups", "hitl", "observabilidad"],
        "confirma": "Sí. Soy un Bedrock Agent (2BOPZRAI7X) con action flows (action group → Lambda), permisos (rol IAM del agente + de la Lambda), estados (sesión + HITL returnControl con checkpoints) y trazabilidad (cada paso emite trace events que persisto en PostgreSQL).",
    },
    "rag_multifuente": {
        "keywords": ["rag", "retrieval", "source attribution", "trazabilidad de contexto", "múltiples fuentes", "multi-fuente"],
        "componentes": ["rag"],
        "confirma": "Sí. RAG con Knowledge Base sobre S3 Vectors, corpus multi-fuente, y cada respuesta cita la fuente recuperada (source attribution).",
    },
    "eval_harness": {
        "keywords": ["eval harness", "factualidad", "completitud", "medir", "ragas", "deepeval"],
        "componentes": ["evals", "observabilidad"],
        "confirma": "Sí. Eval harness con golden set + Ragas (faithfulness/relevancy) + DeepEval (GEval) para factualidad y completitud, y trazas que miden coste y latencia reales por request.",
    },
    "human_in_the_loop": {
        "keywords": ["human-in-the-loop", "human in the loop", "revisión", "aprobación", "rechazo", "escalado", "retries", "checkpoints"],
        "componentes": ["hitl"],
        "confirma": "Sí. HITL con returnControl de Bedrock: acciones sensibles pausan y piden aprobación humana (aprobar/rechazar), con estado persistido para no perder contexto al reanudar.",
    },
    "guardrails_controles": {
        "keywords": ["guardrail", "límites", "controles", "prompt injection", "inyección"],
        "componentes": ["guardrails", "backend"],
        "confirma": "Sí. Guardrail de Bedrock (denied topics + prompt-attack) contra inyección, más límites de rate y de coste en el backend.",
    },
    "desarrollo_agentico": {
        "keywords": ["desarrollo agéntico", "desarrollo agentico", "coding agent", "specs", "skills"],
        "componentes": ["desarrollo_agentico"],
        "confirma": "Sí. Me construí con desarrollo agéntico: specs primero (specs/), coding agents (Claude Code + arquitectos), Skills (.claude/skills/), AGENTS.md, y evals que verifican cada cambio.",
    },
    "trade_offs_modelos": {
        "keywords": ["trade-off", "tradeoff", "trade off", "coste", "latencia", "calidad", "contexto", "portabilidad", "comparativa", "entre modelos"],
        "componentes": ["multi_model"],
        "confirma": "Sí. Comparo rutas de modelo (Bedrock/OpenAI/Nova) por coste, latencia y calidad; ver reports/comparativa.md.",
    },
    "backend_python": {
        "keywords": ["backend python", "fastapi", "manejo de errores", "apis de llm", "postgresql"],
        "componentes": ["backend", "observabilidad"],
        "confirma": "Sí. Backend FastAPI con manejo robusto de errores, integración con APIs de LLM (Bedrock) y PostgreSQL para traces y approvals.",
    },
}

VERIFICACION = {
    "bedrock_agent": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > demo-naiian > app/bedrock_agent.py", "architecture": "/architecture (nodo AGENT)"},
    "rag": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > demo-naiian > app/bedrock_agent.py", "architecture": "/architecture (nodo KB)"},
    "action_groups": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > demo-naiian > aws/lambda/handler.py", "architecture": "/architecture (nodo LAMBDA)"},
    "hitl": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > demo-naiian > app/routers/demo.py", "architecture": "/architecture (nodo HITL)"},
    "guardrails": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > demo-naiian", "architecture": "/architecture (nodo GUARDRAIL)"},
    "evals": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > demo-naiian > evals/", "architecture": "N/A"},
    "observabilidad": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > demo-naiian > app/routers/traces.py", "architecture": "/architecture (nodo PostgreSQL)"},
    "backend": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > demo-naiian > app/main.py", "architecture": "/architecture (nodo FastAPI)"},
}


def explicar_componente(componente: str) -> dict:
    componente = (componente or "").strip().lower().replace(" ", "_").replace("-", "_")
    # Check if it's a requirement query (from the vacancy)
    req_match = None
    req_score = 0
    for req_id, req in REQUISITOS.items():
        score = sum(1 for kw in req["keywords"] if kw in componente.lower())
        if score > req_score:
            req_score = score
            req_match = req_id
    if req_score > 0 and req_match:
        req = REQUISITOS[req_match]
        detalles = []
        for cid in req["componentes"]:
            if cid in COMPONENTES:
                c = COMPONENTES[cid]
                detalles.append({"componente": cid, "nombre": c["nombre"], "archivo_clave": c["archivo_clave"]})
        return {
            "requisito_id": req_match,
            "confirma": req["confirma"],
            "componentes": req["componentes"],
            "detalles": detalles,
        }
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
