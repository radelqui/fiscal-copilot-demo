import re
from dataclasses import dataclass

TIPOS_NCF = {
    "01": "Factura de Crédito Fiscal",
    "02": "Factura de Consumo",
    "03": "Nota de Débito",
    "04": "Nota de Crédito",
    "11": "Comprobante de Compras",
    "12": "Registro Único de Ingresos",
    "13": "Comprobante de Gastos Menores",
    "14": "Comprobante de Regímenes Especiales",
    "15": "Comprobante Gubernamental",
    "16": "Comprobante para Exportaciones",
    "17": "Comprobante para Pagos al Exterior",
}

NCF_PATTERN = re.compile(r"^[EB]\d{2}\d{10}$")


@dataclass
class ResultadoValidacionNCF:
    valido: bool
    ncf: str
    tipo_codigo: str | None
    tipo_nombre: str | None
    serie: str | None
    errores: list[str]


def validar_ncf(ncf: str) -> ResultadoValidacionNCF:
    """Validate a Dominican NCF (Número de Comprobante Fiscal)."""
    if not isinstance(ncf, str):
        raise TypeError(f"ncf must be a string, got {type(ncf).__name__}")

    ncf = ncf.strip().upper()
    errores: list[str] = []

    if len(ncf) != 13:
        errores.append(f"Longitud inválida: {len(ncf)} (esperado: 13)")

    if not ncf:
        errores.append("NCF vacío")
        return ResultadoValidacionNCF(
            valido=False, ncf=ncf, tipo_codigo=None,
            tipo_nombre=None, serie=None, errores=errores,
        )

    serie = ncf[0] if ncf else None
    if serie not in ("E", "B"):
        errores.append(f"Serie inválida: '{serie}' (esperado: E o B)")

    tipo_codigo = ncf[1:3] if len(ncf) >= 3 else None
    tipo_nombre = TIPOS_NCF.get(tipo_codigo) if tipo_codigo else None
    if tipo_codigo and tipo_codigo not in TIPOS_NCF:
        errores.append(f"Tipo NCF inválido: '{tipo_codigo}'")

    if len(ncf) >= 3 and not ncf[3:].isdigit():
        errores.append("Secuencia contiene caracteres no numéricos")

    if not NCF_PATTERN.match(ncf):
        if not errores:
            errores.append("Formato general inválido")

    return ResultadoValidacionNCF(
        valido=len(errores) == 0,
        ncf=ncf,
        tipo_codigo=tipo_codigo,
        tipo_nombre=tipo_nombre,
        serie=serie,
        errores=errores,
    )
