---
name: dgii-fiscal
description: "Conocimiento de normativa fiscal dominicana (DGII): ITBIS, NCF, formatos 606/607, calendario fiscal, retenciones."
---

# Skill: Normativa Fiscal Dominicana (DGII)

## Cuándo usar este skill
Cuando el agente necesite responder preguntas sobre:
- ITBIS (Impuesto a la Transferencia de Bienes Industrializados y Servicios)
- NCF (Números de Comprobantes Fiscales)
- Formatos 606 (compras) y 607 (ventas)
- Calendario fiscal y fechas límite
- Retenciones de ITBIS e ISR

## Conocimiento base

### ITBIS
- Tasa general: 18%
- Se aplica a bienes y servicios gravados
- Fórmula ITBIS incluido: monto / 1.18 * 0.18
- Fórmula ITBIS no incluido: monto * 0.18
- Exentos: canasta básica, salud, educación, alquiler vivienda

### Tipos de NCF
| Tipo | Código | Uso |
|------|--------|-----|
| Factura con valor fiscal | 01 | Ventas a contribuyentes |
| Factura de consumo | 02 | Ventas a consumidores finales |
| Nota de débito | 03 | Ajustes que aumentan valor |
| Nota de crédito | 04 | Ajustes que disminuyen valor |
| Comprobante de compras | 11 | Compras a informales |
| Registro único de ingresos | 12 | Ingresos menores |
| Gastos menores | 13 | Gastos sin NCF |
| Regímenes especiales | 14 | Zonas francas, etc. |
| Gubernamental | 15 | Ventas al gobierno |

### Formato NCF
- Serie: E (electrónico) o B (físico)
- Estructura: E310000000001 (E + 2 dígitos tipo + 10 dígitos secuencia)
- Validación: letra E/B + 2 dígitos tipo válido + 10 dígitos numéricos

### Formatos 606/607
- **606**: Formato de compras y gastos — lo presenta el COMPRADOR
- **607**: Formato de ventas — lo presenta el VENDEDOR
- Fecha límite: día 15 del mes siguiente al periodo
- Contenido 606: RNC proveedor, NCF, fecha, monto, ITBIS
- Contenido 607: RNC cliente, NCF, fecha, monto, ITBIS

### Calendario fiscal
| Obligación | Frecuencia | Fecha límite |
|------------|------------|--------------|
| 606/607 | Mensual | Día 15 del mes siguiente |
| IT-1 (ITBIS) | Mensual | Día 20 del mes siguiente |
| IR-17 (retenciones) | Mensual | Día 10 del mes siguiente |
| ISR (IR-2) | Anual | 120 días después del cierre fiscal |
| ITBIS retenido | Mensual | Día 10 del mes siguiente |

### Retenciones comunes
- ITBIS: 30% del ITBIS facturado (servicios profesionales)
- ITBIS: 100% cuando el proveedor es persona física
- ISR: 10% sobre honorarios profesionales
- ISR: 25% sobre alquileres
