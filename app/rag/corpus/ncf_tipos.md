# NCF — Números de Comprobantes Fiscales

## Definición y Autoridad

Los **Números de Comprobantes Fiscales (NCF)** son identificadores únicos asignados por la **DGII (Dirección General de Impuestos Internos)** a cada transacción comercial. Su propósito es rastrear, validar y cruzar todas las operaciones de compra y venta realizadas en territorio dominicano, garantizando la trazabilidad fiscal y reduciendo la evasión.

## Formatos: Legado vs. Electrónico

### Formato Legado (B-series)
Estructura: `B` + 2 dígitos de tipo + 10 dígitos de secuencia
Ejemplo: `B0100000001`
Longitud total: 13 caracteres

### Formato e-NCF (Electrónico — vigente)
La DGII inició la migración obligatoria al formato electrónico en **2019**. Todos los contribuyentes debían completar la transición. Los e-NCF son generados, transmitidos y validados electrónicamente en tiempo real.

Estructura: `E` + 2 dígitos de tipo + 10 dígitos de secuencia
Ejemplo: `E310000000001`
Longitud total: 13 caracteres

## Tipos de Comprobantes Fiscales

| Código | Nombre | Caso de Uso |
|--------|--------|-------------|
| **01** | Facturas de Crédito Fiscal | Ventas a contribuyentes del ITBIS que pueden deducir el impuesto como crédito fiscal. El comprador debe estar registrado en la DGII con RNC válido. |
| **02** | Facturas de Consumo | Ventas a consumidores finales que no pueden deducir el ITBIS. No requieren RNC del cliente. |
| **03** | Notas de Débito | Incrementan el monto de una factura previamente emitida (ej.: ajustes de precio, cargos adicionales). Deben referenciar el NCF original. |
| **04** | Notas de Crédito | Disminuyen el monto de una factura previa (ej.: devoluciones, descuentos posteriores, anulaciones parciales). Deben referenciar el NCF original. |
| **11** | Comprobantes de Compras | Registran compras a proveedores informales que no emiten NCF (ej.: personas naturales, vendedores informales). El comprador asume la responsabilidad. |
| **12** | Registro Único de Ingresos | Para contribuyentes del régimen simplificado (pequeños negocios). Registra ingresos de manera global, no por transacción individual. |
| **13** | Comprobantes de Gastos Menores | Gastos menores bajo **RD$50,000** donde no se obtuvo NCF del proveedor (parqueos, propinas, compras de emergencia). |
| **14** | Comprobantes de Regímenes Especiales | Transacciones con zonas francas, representantes diplomáticos y entidades bajo regímenes fiscales especiales exentos. |
| **15** | Comprobantes Gubernamentales | Ventas a entidades del Estado dominicano (instituciones públicas, ayuntamientos, empresas estatales). |
| **16** | Comprobantes para Exportaciones | Registran operaciones de exportación de bienes al exterior. Aplica tasa cero de ITBIS. |
| **17** | Comprobantes para Pagos al Exterior | Pagos realizados a entidades o personas físicas no residentes en República Dominicana (servicios, regalías, asistencia técnica). |

## Reglas de Validación

Para que un NCF sea válido, debe cumplir:

1. **Prefijo correcto**: `E` (electrónico) o `B` (legado aún válido en transición)
2. **Código de tipo válido**: debe ser uno de los códigos listados (01–17)
3. **Secuencia numérica**: los 10 dígitos finales deben ser estrictamente numéricos
4. **Longitud total**: exactamente 13 caracteres
5. **Autorización DGII**: el rango de secuencias debe haber sido autorizado previamente por la DGII
6. **No duplicado**: un NCF no puede usarse más de una vez por el mismo emisor

## Solicitud y Asignación de Secuencias

Los contribuyentes deben solicitar rangos de secuencias a la DGII antes de emitir comprobantes. La solicitud se realiza en la OFV (Oficina Virtual Fiscal) en dgii.gov.do. La DGII asigna rangos según el volumen histórico de transacciones y el tipo de comprobante solicitado.

## Anulación de NCF

Los NCF anulados deben reportarse en el **Formato 608** mensualmente. Un NCF anulado no puede ser reutilizado. La anulación debe realizarse en el mismo período fiscal en que fue emitido, de lo contrario requiere nota de crédito (tipo 04).

## Importancia en Declaraciones

Los NCF son el eje central de los **Formatos 606 y 607**: todas las compras y ventas declaradas deben ir acompañadas del NCF correspondiente, permitiendo a la DGII cruzar la información entre compradores y vendedores para detectar inconsistencias.
