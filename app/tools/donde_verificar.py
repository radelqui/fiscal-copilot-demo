from dataclasses import dataclass

VERIFICACION = {
    "bedrock_agent": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > app/bedrock_agent.py", "architecture": "/architecture (nodo AGENT)"},
    "rag": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > app/bedrock_agent.py (retrieve)", "architecture": "/architecture (nodo KB)"},
    "action_groups": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > aws/lambda/handler.py", "architecture": "/architecture (nodo LAMBDA)"},
    "hitl": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > app/routers/demo.py", "architecture": "/architecture (nodo HITL)"},
    "guardrails": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > (configuracion AWS)", "architecture": "/architecture (nodo GUARDRAIL)"},
    "evals": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > evals/", "architecture": "N/A"},
    "observabilidad": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > app/routers/traces.py", "architecture": "/architecture (nodo PostgreSQL)"},
    "backend": {"url": "https://registry.sypnose.cloud", "path": "CodeGraph > fiscal-copilot > app/main.py", "architecture": "/architecture (nodo FastAPI)"},
}

@dataclass
class ResultadoVerificacion:
    componente: str
    registry_url: str
    registry_path: str
    architecture_page: str

def donde_verificar(componente: str) -> ResultadoVerificacion:
    componente = (componente or "").strip().lower().replace(" ", "_").replace("-", "_")
    if componente not in VERIFICACION:
        validos = ", ".join(sorted(VERIFICACION.keys()))
        raise ValueError(f"Componente desconocido: '{componente}'. Validos: {validos}")
    v = VERIFICACION[componente]
    return ResultadoVerificacion(
        componente=componente,
        registry_url=v["url"],
        registry_path=v["path"],
        architecture_page=v["architecture"],
    )
