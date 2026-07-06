# Formatos 606, 607 y 608 — Declaraciones de Compras y Ventas DGII

## Contexto General

Los Formatos 606, 607 y 608 son declaraciones informativas obligatorias que todo contribuyente inscrito en la DGII debe presentar mensualmente. Su propósito es registrar todas las transacciones de compra, venta y comprobantes anulados del período, permitiendo a la DGII realizar cruces de información para verificar la veracidad de las declaraciones de ITBIS y otras obligaciones.

---

## Formato 606 — Compras de Bienes y Servicios

**Nombre oficial**: "Formato de Envío de Compras de Bienes y Servicios"

### Quién debe presentarlo
Todo contribuyente registrado como persona jurídica o persona física con actividad económica formal.

### Qué se declara
Todas las compras y gastos respaldados con NCF válido realizados durante el período reportado, incluyendo:
- Compras de mercancías e insumos
- Servicios recibidos (profesionales, arrendamientos comerciales, publicidad, etc.)
- Gastos operativos con comprobante fiscal

### Campos requeridos por registro

| Campo | Descripción |
|-------|-------------|
| RNC o Cédula del proveedor | Identificación fiscal del emisor del NCF |
| Tipo de NCF | Código de 2 dígitos (01, 11, 13, etc.) |
| NCF | Número completo del comprobante |
| Fecha del comprobante | Fecha de emisión del NCF |
| Fecha de pago | Fecha en que se realizó el pago |
| Monto servicios | Monto gravado correspondiente a servicios |
| Monto bienes | Monto gravado correspondiente a bienes |
| Total facturado | Suma total incluyendo ITBIS |
| ITBIS facturado | ITBIS total que aparece en el comprobante |
| ITBIS retenido | ITBIS retenido por el comprador (si aplica) |
| Retención ISR | Retención de impuesto sobre la renta aplicada |

---

## Formato 607 — Ventas de Bienes y Servicios

**Nombre oficial**: "Formato de Envío de Ventas de Bienes y Servicios"

### Quién debe presentarlo
Los mismos contribuyentes obligados al 606.

### Qué se declara
Todas las ventas y servicios prestados con NCF en el período reportado.

### Campos requeridos por registro

| Campo | Descripción |
|-------|-------------|
| RNC o Cédula del cliente | Solo para NCF tipo 01 y 15; opcional en tipo 02 |
| Tipo de NCF | Código del tipo de comprobante emitido |
| NCF | Número completo del comprobante |
| Fecha de comprobante | Fecha de la transacción |
| Monto facturado | Valor total de la venta |
| ITBIS cobrado | ITBIS incluido en la factura |
| Tipo de ingreso | Clasificación del ingreso (bienes/servicios) |

---

## Formato 608 — Comprobantes Anulados

**Nombre oficial**: "Formato de Envío de Comprobantes Anulados"

Reporta todos los NCF emitidos y posteriormente anulados durante el período. Cada NCF anulado debe registrarse con su número completo, tipo y fecha de anulación.

---

## Plazos de Presentación

| Formato | Plazo |
|---------|-------|
| 606, 607, 608 | Día **15 del mes siguiente** al período reportado |

Si el día 15 cae en fin de semana o feriado, el plazo se extiende al siguiente día hábil.

### Medio de presentación
Exclusivamente a través de la **Oficina Virtual Fiscal (OFV)** de la DGII en dgii.gov.do. Los archivos deben cargarse en formato **.txt o .csv** siguiendo las especificaciones técnicas publicadas por la DGII (separador de campos, codificación de caracteres, etc.).

---

## Sanciones por Incumplimiento

| Infracción | Multa |
|-----------|-------|
| No presentar o presentar fuera de plazo (primera vez) | RD$5,000 |
| Reincidencia | Hasta RD$25,000 |
| Datos incorrectos que afecten la determinación del impuesto | Multa adicional + recargos |

---

## Cruces de Información por la DGII

La herramienta más poderosa de fiscalización de la DGII es el **cruce automático** entre el 606 del comprador y el 607 del vendedor. Para cada NCF reportado en un 606, la DGII verifica que el mismo NCF aparezca en el 607 del proveedor con montos consistentes.

### Errores comunes que generan inconsistencias

1. **RNC del proveedor incorrecto**: el NCF no puede vincularse al emisor real
2. **Tipo de NCF equivocado**: mismatch entre lo declarado por comprador y vendedor
3. **NCF duplicado**: el mismo comprobante aparece dos veces en las declaraciones
4. **Montos diferentes**: el comprador declara un monto distinto al declarado por el vendedor
5. **NCF no emitido por el proveedor**: uso de comprobantes falsos o de otro emisor

Cualquier inconsistencia puede resultar en una **notificación de auditoría** o **ajuste de impuestos** por parte de la DGII.
