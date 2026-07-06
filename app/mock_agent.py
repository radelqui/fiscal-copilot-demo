"""Mock agent that simulates Bedrock Agent behavior using local tools.

When USE_MOCK_AGENT=1, this replaces the real Bedrock invoke_agent call.
It parses the user query and routes to the appropriate local tool.
"""

import re
from typing import Any

from app.tools.calcular_itbis import calcular_itbis
from app.tools.validar_ncf import validar_ncf
from app.tools.presentar_formato_606 import presentar_formato_606
from app.agent.system_prompt import SYSTEM_PROMPT


def _extract_number(text: str) -> float | None:
    """Extract the first number from text."""
    numbers = re.findall(r"[\d,]+(?:\.\d+)?", text.replace(",", ""))
    if numbers:
        return float(numbers[0])
    return None


def _detect_intent(query: str) -> str:
    query_lower = query.lower()
    if any(w in query_lower for w in ["itbis", "impuesto", "18%", "calcul"]):
        if any(w in query_lower for w in ["ncf", "comprobante", "valid"]):
            return "validar_ncf"
        return "calcular_itbis"
    if any(w in query_lower for w in ["ncf", "comprobante", "valid", "e01", "b01"]):
        return "validar_ncf"
    if any(w in query_lower for w in ["606", "formato", "presenta"]):
        return "presentar_formato_606"
    return "knowledge_base"


def mock_invoke_agent(query: str) -> dict[str, Any]:
    """Simulate a Bedrock Agent invocation using local tools."""
    intent = _detect_intent(query)
    tools_used: list[dict[str, Any]] = []

    if intent == "calcular_itbis":
        monto = _extract_number(query)
        if monto is None:
            return {
                "response": "No pude identificar el monto para calcular el ITBIS. "
                "Por favor, indica el monto numérico.",
                "tools_used": [],
            }
        incluido = any(w in query.lower() for w in ["incluido", "incluye", "con itbis", "incluído"])
        result = calcular_itbis(monto, incluido=incluido)
        tools_used.append({
            "tool_name": "calcular_itbis",
            "tool_input": {"monto": monto, "incluido": incluido},
            "tool_output": {
                "monto_sin_itbis": result.monto_sin_itbis,
                "itbis": result.itbis,
                "monto_con_itbis": result.monto_con_itbis,
            },
        })
        if incluido:
            response = (
                f"Para un monto de RD${monto:,.2f} con ITBIS incluido:\n"
                f"- Monto sin ITBIS: RD${result.monto_sin_itbis:,.2f}\n"
                f"- ITBIS (18%): RD${result.itbis:,.2f}\n"
                f"- Total: RD${result.monto_con_itbis:,.2f}"
            )
        else:
            response = (
                f"Para un monto de RD${monto:,.2f} sin ITBIS:\n"
                f"- Monto base: RD${result.monto_sin_itbis:,.2f}\n"
                f"- ITBIS (18%): RD${result.itbis:,.2f}\n"
                f"- Total con ITBIS: RD${result.monto_con_itbis:,.2f}"
            )

    elif intent == "validar_ncf":
        ncf_match = re.search(r"[EeBb]\d{12}", query)
        if not ncf_match:
            ncf_match = re.search(r"[EeBb]\d{2}\d+", query)
        if ncf_match:
            ncf_str = ncf_match.group()
            result = validar_ncf(ncf_str)
            tools_used.append({
                "tool_name": "validar_ncf",
                "tool_input": {"ncf": ncf_str},
                "tool_output": {
                    "valido": result.valido,
                    "tipo_codigo": result.tipo_codigo,
                    "tipo_nombre": result.tipo_nombre,
                    "errores": result.errores,
                },
            })
            if result.valido:
                response = (
                    f"El NCF {result.ncf} es **válido**.\n"
                    f"- Serie: {result.serie}\n"
                    f"- Tipo: {result.tipo_codigo} — {result.tipo_nombre}"
                )
            else:
                errores_str = "\n".join(f"  - {e}" for e in result.errores)
                response = f"El NCF {result.ncf} es **inválido**:\n{errores_str}"
        else:
            return {
                "response": "No pude identificar un NCF en tu consulta. "
                "El formato esperado es E010000000001 (letra E o B + 12 dígitos).",
                "tools_used": [],
            }

    elif intent == "presentar_formato_606":
        periodo_match = re.search(r"(\d{6})", query)
        registros = _extract_number(query.split("registro")[0]) if "registro" in query.lower() else _extract_number(query)
        periodo = periodo_match.group(1) if periodo_match else None

        if not periodo:
            # If this looks like a general knowledge question (e.g. "fecha límite del 606"),
            # fall through to knowledge base instead of asking for periodo.
            q = query.lower()
            if any(w in q for w in ["fecha", "plazo", "límite", "limite", "cuándo", "cuando", "qué", "que es"]):
                return {
                    "response": _kb_response(query),
                    "tools_used": [],
                }
            return {
                "response": "Necesito el periodo en formato YYYYMM (ej: 202606) para preparar el formato 606.",
                "tools_used": [],
            }

        # For 606, the number of registros — skip "606"/"607" (format names)
        nums = re.findall(r"\d+", query)
        skip = {periodo, "606", "607", "608"}
        reg_count = None
        for n in nums:
            if n not in skip and len(n) <= 4:
                reg_count = int(n)
                break
        if reg_count is None:
            reg_count = 0

        result = presentar_formato_606(periodo, reg_count)
        tools_used.append({
            "tool_name": "presentar_formato_606",
            "tool_input": {"periodo": periodo, "registros": reg_count},
            "tool_output": {
                "periodo": result.periodo,
                "cantidad_registros": result.cantidad_registros,
                "fecha_limite": result.fecha_limite,
                "estado": result.estado,
            },
        })
        response = result.mensaje

    else:
        # Knowledge base query - return a canned response from corpus knowledge
        response = _kb_response(query)

    return {
        "response": response,
        "tools_used": tools_used,
    }


def _kb_response(query: str) -> str:
    """Simple keyword-based response from corpus knowledge for mock mode."""
    q = query.lower()
    if "fecha" in q and ("606" in q or "607" in q):
        return (
            "Los formatos 606 (compras) y 607 (ventas) deben presentarse antes del "
            "día 15 del mes siguiente al periodo reportado, a través de la Oficina "
            "Virtual de la DGII (OFV)."
        )
    if "itbis" in q and ("tasa" in q or "porcentaje" in q or "cuánto" in q or "cuanto" in q):
        return (
            "La tasa general del ITBIS en República Dominicana es del 18%, "
            "establecida por la Ley 11-92 (Código Tributario) y sus modificaciones. "
            "Se aplica a la transferencia de bienes industrializados y la prestación "
            "de servicios gravados."
        )
    if "exent" in q or "exoner" in q:
        return (
            "Están exentos de ITBIS: productos de la canasta básica (arroz, habichuelas, "
            "pollo, huevos, leche), servicios de salud, educación, alquiler de vivienda, "
            "servicios financieros y combustibles (que tienen su propio impuesto)."
        )
    if "calendario" in q or "fecha" in q or "plazo" in q:
        return (
            "Calendario fiscal mensual:\n"
            "- Día 3: Seguridad Social (TSS)\n"
            "- Día 10: Retenciones IR-17 (ITBIS e ISR)\n"
            "- Día 15: Formatos 606, 607 y 608\n"
            "- Día 20: Declaración ITBIS (IT-1)\n\n"
            "Anuales: IR-2 corporativo a los 120 días del cierre fiscal. "
            "IR-1 personas físicas: 31 de marzo."
        )
    if "retenc" in q:
        return (
            "Retenciones principales:\n"
            "- ITBIS: 30% del ITBIS facturado (servicios profesionales)\n"
            "- ITBIS: 100% cuando proveedor es persona física\n"
            "- ISR: 10% sobre honorarios profesionales\n"
            "- ISR: 25% sobre alquileres\n"
            "Se declaran con el IR-17 antes del día 10 del mes siguiente."
        )
    return (
        "Soy Fiscal Copilot, tu asistente de cumplimiento fiscal dominicano. "
        "Puedo ayudarte con cálculos de ITBIS, validación de NCF, preparación "
        "de formatos 606/607, y consultas sobre el calendario fiscal. "
        "¿En qué puedo asistirte?"
    )
