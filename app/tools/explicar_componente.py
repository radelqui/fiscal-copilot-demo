from dataclasses import dataclass, field

COMPONENTES = {
    "bedrock_agent": {
        "nombre": "Bedrock Agent",
        "descripcion": "Agent ID 2BOPZRAI7X, Claude Sonnet 4.6, eu-central-1 (Frankfurt). Orquesta KB, tools y guardrail.",
        "modelo": "eu.anthropic.claude-sonnet-4-6",
        "region": "eu-central-1",
        "recursos": ["Agent 2BOPZRAI7X", "Alias TJRZR1FCDY"],
        "archivo_clave": "app/bedrock_agent.py",
    },
    "rag": {
        "nombre": "Knowledge Base (RAG)",
        "descripcion": "KB 5I5RDNA2V1 con S3 Vectors y Titan Embedding V2 (1024d). Corpus multi-fuente sobre la propia arquitectura.",
        "modelo": "amazon.titan-embed-text-v2:0",
        "region": "eu-central-1",
        "recursos": ["KB 5I5RDNA2V1", "DataSource WEIATOAQ9Y", "S3 demo-naiian-corpus"],
        "archivo_clave": "app/bedrock_agent.py",
    },
    "action_groups": {
        "nombre": "Action Groups (Tools)",
        "descripcion": "Lambda demo-naiian-tools con 3 funciones: explicar_componente, donde_verificar, generar_reporte_arquitectura. FunctionSchema con structured outputs.",
        "modelo": "N/A",
        "region": "eu-central-1",
        "recursos": ["Lambda demo-naiian-tools"],
        "archivo_clave": "aws/lambda/handler.py",
    },
    "hitl": {
        "nombre": "Human-in-the-Loop",
        "descripcion": "generar_reporte_arquitectura tiene requireConfirmation=ENABLED. El agente devuelve returnControl, el frontend muestra bandeja de aprobacion, el usuario aprueba/rechaza, el agente reanuda.",
        "modelo": "N/A",
        "region": "N/A",
        "recursos": ["returnControl event", "approvals table PostgreSQL"],
        "archivo_clave": "app/routers/demo.py",
    },
    "guardrails": {
        "nombre": "Guardrails",
        "descripcion": "Guardrail xgn38kcg6hrq: 5 denied topics (infra externa, credenciales, prompt verbatim, jailbreak, contenido fiscal) + 6 content filters + PROMPT_ATTACK input.",
        "modelo": "N/A",
        "region": "eu-central-1",
        "recursos": ["Guardrail xgn38kcg6hrq"],
        "archivo_clave": "N/A (configurado en AWS Console/API)",
    },
    "evals": {
        "nombre": "Evaluaciones LLM",
        "descripcion": "golden_set.jsonl con casos por categoria. Ragas (faithfulness, relevancy), DeepEval (GEval), router comparativa multi-modelo. Pipeline: evals/run_all.py.",
        "modelo": "N/A",
        "region": "N/A",
        "recursos": ["golden_set.jsonl", "run_all.py"],
        "archivo_clave": "evals/run_all.py",
    },
    "observabilidad": {
        "nombre": "Observabilidad",
        "descripcion": "Traces en PostgreSQL: tokens_in, tokens_out, cost_usd, latency_ms por request. Endpoints /metrics (JSON p50/p95/by_model/by_tenant) y /dashboard (HTML).",
        "modelo": "N/A",
        "region": "N/A",
        "recursos": ["PostgreSQL traces table", "/metrics", "/dashboard"],
        "archivo_clave": "app/routers/traces.py",
    },
    "backend": {
        "nombre": "Backend FastAPI",
        "descripcion": "FastAPI con auth por token, rate limiting 60 req/hr, cost cap $2/day. PostgreSQL para traces y approvals. Docker Compose.",
        "modelo": "N/A",
        "region": "eu-central-1 (servidor)",
        "recursos": ["FastAPI :7020", "PostgreSQL :5544"],
        "archivo_clave": "app/main.py",
    },
    "desarrollo_agentico": {
        "nombre": "Desarrollo Agéntico",
        "descripcion": "Specs escritas antes del código (specs/), coding agents (Claude Code + arquitectos), Skills (.claude/skills/), AGENTS.md como manifiesto del equipo, y evals que verifican cada cambio.",
        "modelo": "N/A",
        "region": "N/A",
        "recursos": ["specs/", ".claude/skills/", "AGENTS.md"],
        "archivo_clave": "AGENTS.md",
    },
    "multi_model": {
        "nombre": "Comparativa Multi-Modelo",
        "descripcion": "Comparativa de rutas de modelo (Bedrock Sonnet/Haiku, OpenAI GPT-4o-mini, Nova Micro) por coste, latencia y calidad. Router en evals/router.py, resultados en reports/comparativa.md.",
        "modelo": "N/A",
        "region": "N/A",
        "recursos": ["evals/router.py", "reports/comparativa.md"],
        "archivo_clave": "evals/router.py",
    },
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

@dataclass
class ResultadoComponente:
    componente: str
    nombre: str
    descripcion: str
    modelo: str
    region: str
    recursos: list[str] = field(default_factory=list)
    archivo_clave: str = ""

@dataclass
class ResultadoRequisito:
    requisito_id: str
    confirma: str
    componentes: list[str] = field(default_factory=list)
    detalles: list[dict] = field(default_factory=list)


def detectar_requisito(query: str) -> ResultadoRequisito | None:
    """Detect if user text matches a vacancy requirement and return confirmation."""
    q = query.lower()
    best_match = None
    best_score = 0
    for req_id, req in REQUISITOS.items():
        score = sum(1 for kw in req["keywords"] if kw in q)
        if score > best_score:
            best_score = score
            best_match = req_id
    if best_score < 2:
        return None
    req = REQUISITOS[best_match]
    detalles = []
    for comp_id in req["componentes"]:
        if comp_id in COMPONENTES:
            c = COMPONENTES[comp_id]
            detalles.append({
                "componente": comp_id,
                "nombre": c["nombre"],
                "archivo_clave": c["archivo_clave"],
                "recursos": c["recursos"],
            })
    return ResultadoRequisito(
        requisito_id=best_match,
        confirma=req["confirma"],
        componentes=req["componentes"],
        detalles=detalles,
    )


def explicar_componente(componente: str) -> ResultadoComponente:
    componente = (componente or "").strip().lower().replace(" ", "_").replace("-", "_")
    if componente not in COMPONENTES:
        validos = ", ".join(sorted(COMPONENTES.keys()))
        raise ValueError(f"Componente desconocido: '{componente}'. Validos: {validos}")
    c = COMPONENTES[componente]
    return ResultadoComponente(
        componente=componente,
        nombre=c["nombre"],
        descripcion=c["descripcion"],
        modelo=c["modelo"],
        region=c["region"],
        recursos=c["recursos"],
        archivo_clave=c["archivo_clave"],
    )
