# Spec WIP - SAP ST06 History Bridge

Estado: WIP

## Objetivo

Exponer información histórica de ST06 / OS Monitor mediante un backend FastAPI que consuma una RFC ABAP custom y publique respuestas REST JSON para SAP Integration Suite.

## Alcance

- Endpoint: `/sap/st06/history`.
- RFC objetivo: `Z_GET_ST06_HISTORY`.
- Filtros: sistema, periodo, host y categoría.
- Modo mock para desarrollo local.
- Documentación de contrato RFC e iFlow.

## Criterios De Aceptación

- La solución corre localmente sin secretos.
- La capa RFC es reemplazable por mocks en tests.
- El endpoint devuelve JSON con contrato estable.
- El contrato soporta métricas heterogéneas por clave/valor/unidad.
- La especificación ABAP queda como diseño para implementar primero en DEV.

## Edge Cases

- RFC sin registros.
- Timestamps SAP inválidos.
- Variables SAP faltantes en modo real.
- PyRFC no instalado.
- Host/categoría sin datos.

## Impacto Técnico

Se crea una base evolutiva para integrar datos ST06/OS Monitor con Integration Suite sin exponer credenciales ni depender de tablas SAP internas no confirmadas.

