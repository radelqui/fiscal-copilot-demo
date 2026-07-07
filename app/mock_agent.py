"""Mock agent that simulates Bedrock Agent behavior using local tools.

When USE_MOCK_AGENT=1, this replaces the real Bedrock invoke_agent call.
It parses the user query and routes to the appropriate local tool.
"""

import re
from typing import Any

from app.tools.explicar_componente import explicar_componente, COMPONENTES
from app.tools.donde_verificar import donde_verificar
from app.tools.generar_reporte_arquitectura import generar_reporte_arquitectura
from app.tools.explicar_componente import detectar_requisito
from app.agent.system_prompt import SYSTEM_PROMPT


def _detect_intent(query: str) -> str:
    # Check for vacancy requirement match FIRST
    from app.tools.explicar_componente import detectar_requisito as _dr
    if _dr(query) is not None:
        return "requisito_vacante"
    q = query.lower()
    if any(w in q for w in ["reporte", "report", "genera", "publica"]):
        return "generar_reporte_arquitectura"
    if any(w in q for w in ["verificar", "verifico", "donde ver", "dónde ver", "registry", "comprobar"]):
        return "donde_verificar"
    for comp in COMPONENTES:
        comp_words = comp.replace("_", " ").split()
        if any(w in q for w in comp_words):
            return "explicar_componente"
    if any(w in q for w in ["agente", "agent", "bedrock", "construido", "hecho", "arquitectura"]):
        return "explicar_componente"
    if any(w in q for w in ["rag", "knowledge", "corpus", "fuente"]):
        return "explicar_componente"
    if any(w in q for w in ["tool", "herramienta", "action", "lambda"]):
        return "explicar_componente"
    if any(w in q for w in ["hitl", "human", "aprobación", "aprobacion", "confirmación"]):
        return "explicar_componente"
    if any(w in q for w in ["guardrail", "seguridad", "inyección", "injection"]):
        return "explicar_componente"
    if any(w in q for w in ["eval", "calidad", "ragas", "deepeval", "faithfulness"]):
        return "explicar_componente"
    if any(w in q for w in ["observ", "métrica", "metrica", "traza", "dashboard", "coste"]):
        return "explicar_componente"
    if any(w in q for w in ["backend", "fastapi", "postgresql", "postgres"]):
        return "explicar_componente"
    return "knowledge_base"


def _detect_componente(query: str) -> str:
    q = query.lower()
    mapping = [
        (["bedrock", "agente", "agent"], "bedrock_agent"),
        (["rag", "knowledge base", "corpus", "kb", "s3 vector"], "rag"),
        (["action group", "lambda", "tool", "herramienta"], "action_groups"),
        (["hitl", "human in the loop", "aprobación", "aprobacion", "confirmación", "confirmacion"], "hitl"),
        (["guardrail", "seguridad", "inyección", "injection", "protección"], "guardrails"),
        (["eval", "calidad", "ragas", "deepeval", "golden"], "evals"),
        (["observ", "métrica", "metrica", "traza", "dashboard", "coste", "latencia"], "observabilidad"),
        (["backend", "fastapi", "postgresql", "postgres", "api"], "backend"),
    ]
    for keywords, comp in mapping:
        if any(kw in q for kw in keywords):
            return comp
    return "bedrock_agent"


def mock_invoke_agent(query: str) -> dict[str, Any]:
    intent = _detect_intent(query)
    tools_used: list[dict[str, Any]] = []

    if intent == "explicar_componente":
        comp = _detect_componente(query)
        result = explicar_componente(comp)
        tools_used.append({
            "tool_name": "explicar_componente",
            "tool_input": {"componente": comp},
            "tool_output": {
                "nombre": result.nombre,
                "descripcion": result.descripcion,
                "modelo": result.modelo,
                "recursos": result.recursos,
            },
        })
        response = (
            f"**{result.nombre}**\n\n"
            f"{result.descripcion}\n\n"
            f"- **Modelo**: {result.modelo}\n"
            f"- **Región**: {result.region}\n"
            f"- **Recursos**: {', '.join(result.recursos)}\n"
            f"- **Archivo clave**: `{result.archivo_clave}`\n\n"
            f"Puedes verificarlo: registry.sypnose.cloud/demo > `{result.archivo_clave}`"
        )

    elif intent == "requisito_vacante":
        req_result = detectar_requisito(query)
        comp_details = []
        for comp_id in req_result.componentes:
            try:
                comp = explicar_componente(comp_id)
                comp_details.append(f"- **{comp.nombre}**: {comp.descripcion} → `{comp.archivo_clave}`")
            except ValueError:
                pass
        tools_used.append({
            "tool_name": "explicar_componente",
            "tool_input": {"requisito": query},
            "tool_output": {
                "requisito_id": req_result.requisito_id,
                "confirma": req_result.confirma,
                "componentes": req_result.componentes,
            },
        })
        response = (
            f"✅ Sí, cumplo este requisito: {req_result.confirma}\n\n"
            f"**Componentes involucrados:**\n"
            + "\n".join(comp_details)
            + "\n\nVerifícalo en: registry.sypnose.cloud/demo"
        )

    elif intent == "donde_verificar":
        comp = _detect_componente(query)
        result = donde_verificar(comp)
        tools_used.append({
            "tool_name": "donde_verificar",
            "tool_input": {"componente": comp},
            "tool_output": {
                "registry_url": result.registry_url,
                "registry_path": result.registry_path,
                "architecture_page": result.architecture_page,
            },
        })
        response = (
            f"Para verificar **{comp}**:\n\n"
            f"- **Registry**: [{result.registry_path}]({result.registry_url})\n"
            f"- **Arquitectura**: {result.architecture_page}"
        )

    elif intent == "generar_reporte_arquitectura":
        result = generar_reporte_arquitectura("todas")
        tools_used.append({
            "tool_name": "generar_reporte_arquitectura",
            "tool_input": {"secciones": "todas"},
            "tool_output": {
                "secciones": result.secciones,
                "estado": result.estado,
                "mensaje": result.mensaje,
            },
        })
        response = result.mensaje

    else:
        response = _kb_response(query)

    return {
        "response": response,
        "tools_used": tools_used,
    }


def _kb_response(query: str) -> str:
    return (
        "Soy ¿Cómo Estoy Hecho?, un agente de IA que explica su propia arquitectura. "
        "Puedo explicarte cómo funciona mi Bedrock Agent, mi RAG multi-fuente, "
        "mis action groups, mi HITL, mis guardrails, mis evaluaciones y mi observabilidad. "
        "¿Qué componente quieres explorar?"
    )
