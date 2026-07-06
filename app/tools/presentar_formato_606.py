import re
from dataclasses import dataclass


@dataclass
class Resumen606:
    periodo: str
    cantidad_registros: int
    fecha_limite: str
    estado: str
    mensaje: str


def presentar_formato_606(periodo: str, registros: int) -> Resumen606:
    """Generate a summary for formato 606 filing."""
    if not isinstance(periodo, str):
        raise TypeError(f"periodo must be a string, got {type(periodo).__name__}")
    if not isinstance(registros, int):
        raise TypeError(f"registros must be an integer, got {type(registros).__name__}")

    periodo = periodo.strip()
    if not re.match(r"^\d{6}$", periodo):
        raise ValueError(f"periodo must be YYYYMM format, got '{periodo}'")

    year = int(periodo[:4])
    month = int(periodo[4:6])
    if month < 1 or month > 12:
        raise ValueError(f"Month must be 1-12, got {month}")
    if year < 2000 or year > 2099:
        raise ValueError(f"Year must be 2000-2099, got {year}")

    if registros < 0:
        raise ValueError("registros must be non-negative")

    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1
    fecha_limite = f"{next_year}-{next_month:02d}-15"

    meses = [
        "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    ]

    if registros == 0:
        estado = "sin_movimiento"
        mensaje = (
            f"El formato 606 del periodo {meses[month]} {year} no tiene registros. "
            f"Se debe presentar declaración sin movimiento antes del {fecha_limite}."
        )
    else:
        estado = "pendiente_envio"
        mensaje = (
            f"El formato 606 del periodo {meses[month]} {year} contiene {registros} "
            f"registro{'s' if registros != 1 else ''} de compras. "
            f"Fecha límite de presentación: {fecha_limite} ante la DGII."
        )

    return Resumen606(
        periodo=periodo,
        cantidad_registros=registros,
        fecha_limite=fecha_limite,
        estado=estado,
        mensaje=mensaje,
    )
