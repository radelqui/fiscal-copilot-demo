from dataclasses import dataclass

TASA_ITBIS = 0.18


@dataclass
class ResultadoITBIS:
    monto_sin_itbis: float
    itbis: float
    monto_con_itbis: float


def calcular_itbis(monto: float, incluido: bool = False) -> ResultadoITBIS:
    """Calculate ITBIS (Dominican VAT at 18%) for a given amount."""
    if not isinstance(monto, (int, float)):
        raise TypeError(f"monto must be numeric, got {type(monto).__name__}")
    if monto < 0:
        raise ValueError("monto must be non-negative")

    if incluido:
        monto_sin_itbis = round(monto / (1 + TASA_ITBIS), 2)
        itbis = round(monto - monto_sin_itbis, 2)
        monto_con_itbis = round(monto, 2)
    else:
        monto_sin_itbis = round(monto, 2)
        itbis = round(monto * TASA_ITBIS, 2)
        monto_con_itbis = round(monto_sin_itbis + itbis, 2)

    return ResultadoITBIS(
        monto_sin_itbis=monto_sin_itbis,
        itbis=itbis,
        monto_con_itbis=monto_con_itbis,
    )
