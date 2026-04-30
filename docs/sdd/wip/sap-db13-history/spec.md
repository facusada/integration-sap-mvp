# Spec WIP - SAP DB13 History Bridge

Estado: WIP

## Objetivo

Exponer información histórica de DB13/backups/crecimiento de base de datos SAP mediante un backend FastAPI que consuma un RFC ABAP custom y publique respuestas REST JSON para SAP Integration Suite.

## Alcance

- Endpoints: `/health`, `/sap/db13/history`, `/sap/db/growth`.
- RFC objetivo: `Z_GET_DB13_HISTORY`.
- Sin conexión SAP real en esta etapa.
- Modo mock para desarrollo local.
- Documentación de contrato RFC e iFlow.

## Criterios De Aceptación

- La solución corre localmente sin secretos.
- La capa RFC es reemplazable por mocks en tests.
- Los endpoints devuelven JSON con contrato estable.
- El cálculo de crecimiento se deriva del histórico.
- La especificación ABAP queda como diseño para implementar primero en DEV.

## Edge Cases

- RFC sin registros.
- Fechas inválidas.
- Variables SAP faltantes en modo real.
- PyRFC no instalado.
- Estado DB13 no reconocido.

## Impacto Técnico

Se crea una base evolutiva para integrar SAP ECC/S/4HANA con Integration Suite sin exponer credenciales ni depender todavía de objetos ABAP transportados.

