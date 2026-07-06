"""Lambda fiscal-copilot-tools — action group del Bedrock Agent.

Port stdlib-puro de app/tools/ (calcular_itbis, validar_ncf, presentar_formato_606).
Formato de eventos: Bedrock Agents function details (functionSchema).
"""
import calendar
import json
import re

TASA_ITBIS = 0.18

TIPOS_NCF = {
    "01": ("Factura de Credito Fiscal", True),
    "02": ("Factura de Consumo", False),
    "03": ("Nota de Debito", False),
    "04": ("Nota de Credito", False),
    "14": ("Regimen Especial", False),
    "15": ("Gubernamental", False),
    "31": ("Factura de Credito Fiscal Electronica", True),
    "32": ("Factura de Consumo Electronica", False),
    "33": ("Nota de Debito Electronica", False),
    "34": ("Nota de Credito Electronica", False),
}


def calcular_itbis(monto: float, incluido: bool = False) -> dict:
    if monto <= 0:
        raise ValueError("El monto debe ser mayor que 0")
    if incluido:
        base = round(monto / (1 + TASA_ITBIS), 2)
        itbis = round(monto - base, 2)
        total = round(monto, 2)
    else:
        base = round(monto, 2)
        itbis = round(monto * TASA_ITBIS, 2)
        total = round(base + itbis, 2)
    return {
        "monto_sin_itbis": base,
        "itbis": itbis,
        "monto_con_itbis": total,
        "tasa": TASA_ITBIS,
    }


def validar_ncf(ncf: str) -> dict:
    ncf = (ncf or "").strip().upper()
    errores = []
    tipo_codigo = None
    if re.fullmatch(r"B\d{10}", ncf):
        tipo_codigo = ncf[1:3]
    elif re.fullmatch(r"E\d{12}", ncf):
        tipo_codigo = ncf[1:3]
    else:
        errores.append(
            "Formato invalido: se espera B+10 digitos (fisico) o E+12 digitos (e-NCF)"
        )
    tipo_nombre = None
    da_credito = False
    if tipo_codigo is not None:
        if tipo_codigo in TIPOS_NCF:
            tipo_nombre, da_credito = TIPOS_NCF[tipo_codigo]
        else:
            errores.append(f"Tipo de NCF desconocido: {tipo_codigo}")
    return {
        "ncf": ncf,
        "valido": not errores,
        "tipo_codigo": tipo_codigo,
        "tipo_nombre": tipo_nombre,
        "da_credito_fiscal": da_credito,
        "errores": errores,
    }


def presentar_formato_606(periodo: str, registros: int) -> dict:
    if not re.fullmatch(r"\d{6}", periodo or ""):
        raise ValueError("Periodo invalido: formato AAAAMM")
    anio, mes = int(periodo[:4]), int(periodo[4:])
    if not 1 <= mes <= 12:
        raise ValueError("Periodo invalido: mes fuera de rango")
    if registros <= 0:
        raise ValueError("La cantidad de registros debe ser mayor que 0")
    mes_sig, anio_sig = (mes + 1, anio) if mes < 12 else (1, anio + 1)
    dia_limite = min(15, calendar.monthrange(anio_sig, mes_sig)[1])
    fecha_limite = f"{anio_sig:04d}-{mes_sig:02d}-{dia_limite:02d}"
    return {
        "periodo": periodo,
        "registros": registros,
        "fecha_limite": fecha_limite,
        "estado": "PENDIENTE_APROBACION",
        "mensaje": (
            f"Presentacion del formato 606 periodo {periodo} con {registros} registros "
            f"preparada. Requiere aprobacion humana antes de enviarse a la DGII "
            f"(fecha limite: {fecha_limite})."
        ),
    }


def _parametros(event: dict) -> dict:
    return {p["name"]: p.get("value") for p in event.get("parameters", [])}


def _bool(v) -> bool:
    return str(v).strip().lower() in ("true", "1", "si", "sí", "yes")


DISPATCH = {
    "calcular_itbis": lambda p: calcular_itbis(
        monto=float(p["monto"]), incluido=_bool(p.get("incluido", "false"))
    ),
    "validar_ncf": lambda p: validar_ncf(ncf=str(p["ncf"])),
    "presentar_formato_606": lambda p: presentar_formato_606(
        periodo=str(p["periodo"]), registros=int(float(p["registros"]))
    ),
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
