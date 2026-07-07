from dataclasses import dataclass, field

@dataclass
class ResultadoReporte:
    secciones: list[str] = field(default_factory=list)
    estado: str = ""
    mensaje: str = ""
    contenido: dict = field(default_factory=dict)

def generar_reporte_arquitectura(secciones: str = "todas") -> ResultadoReporte:
    secciones_validas = ["bedrock_agent", "rag", "action_groups", "hitl", "guardrails", "evals", "observabilidad", "backend"]
    if secciones.strip().lower() in ("todas", "all", ""):
        secciones_list = secciones_validas
    else:
        secciones_list = [s.strip().lower().replace(" ", "_").replace("-", "_") for s in secciones.split(",")]
        invalidas = [s for s in secciones_list if s not in secciones_validas]
        if invalidas:
            raise ValueError(f"Secciones invalidas: {invalidas}. Validas: {secciones_validas}")

    contenido = {}
    for s in secciones_list:
        contenido[s] = f"Seccion {s} del reporte de arquitectura generada."

    return ResultadoReporte(
        secciones=secciones_list,
        estado="PENDIENTE_APROBACION",
        mensaje=f"Reporte de arquitectura con {len(secciones_list)} secciones preparado. Requiere aprobacion humana antes de publicarse.",
        contenido=contenido,
    )
