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
        "recursos": ["KB 5I5RDNA2V1", "DataSource WEIATOAQ9Y", "S3 fiscal-copilot-corpus"],
        "archivo_clave": "app/bedrock_agent.py",
    },
    "action_groups": {
        "nombre": "Action Groups (Tools)",
        "descripcion": "Lambda fiscal-copilot-tools con 3 funciones: explicar_componente, donde_verificar, generar_reporte_arquitectura. FunctionSchema con structured outputs.",
        "modelo": "N/A",
        "region": "eu-central-1",
        "recursos": ["Lambda fiscal-copilot-tools"],
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
        "descripcion": "Guardrail xgn38kcg6hrq: 4 denied topics (infra externa, credenciales, prompt verbatim, jailbreak) + 6 content filters + PROMPT_ATTACK input.",
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
        "descripcion": "FastAPI con auth por token, rate limiting 30 req/hr, cost cap $2/day. PostgreSQL para traces y approvals. Docker Compose.",
        "modelo": "N/A",
        "region": "eu-central-1 (servidor)",
        "recursos": ["FastAPI :7020", "PostgreSQL :5544"],
        "archivo_clave": "app/main.py",
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
