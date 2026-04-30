# RFC Contract - Z_GET_DB13_HISTORY

## Propósito

`Z_GET_DB13_HISTORY` es un RFC ABAP custom propuesto para exponer de forma controlada información histórica de DB13, backups y crecimiento de base de datos SAP. Debe implementarse primero en ambiente DEV, revisarse técnicamente y transportarse luego a QAS/PRD mediante el flujo corporativo.

Este repositorio no aplica ni modifica objetos SAP automáticamente.

## Function Module

Nombre tentativo:

```text
Z_GET_DB13_HISTORY
```

Remote-enabled: sí.

## Import Parameters

| Parámetro | Tipo sugerido | Obligatorio | Descripción |
| --- | --- | --- | --- |
| `IV_DATE_FROM` | `DATS` | Sí | Fecha inicial en formato SAP `YYYYMMDD`. |
| `IV_DATE_TO` | `DATS` | Sí | Fecha final en formato SAP `YYYYMMDD`. |
| `IV_SYSTEM_ID` | `SYSID` o `CHAR10` | Sí | Identificador lógico del sistema consultado. |
| `IV_STATUS` | `CHAR20` | No | Filtro opcional por estado si la fuente real lo permite. |
| `IV_ACTION` | `CHAR40` | No | Filtro opcional por acción DB13 si la fuente real lo permite. |
| `IV_JOBNAME` | `CHAR64` | No | Filtro opcional por job si la fuente real lo permite. |

## Table Parameters

`ET_RESULTS` o `ET_DB13_HISTORY`.

El backend actual consume `ET_DB13_HISTORY` para los endpoints REST existentes. El MCP/script documenta `ET_RESULTS` como nombre genérico aceptable para el diseño ABAP. Antes de activar el transporte, unificar el nombre con el equipo ABAP/Basis y ajustar el mapeo si corresponde.

| Campo | Tipo sugerido | Descripción |
| --- | --- | --- |
| `DATE` | `DATS` | Fecha del evento DB13/backups. |
| `JOB_NAME` | `CHAR64` | Nombre del job o proceso. |
| `STATUS` | `CHAR20` | Estado normalizado, por ejemplo `SUCCESS`, `FAILED`, `WARNING`. |
| `DATABASE_SIZE_GB` | `DEC` | Tamaño de base en GB. |
| `BACKUP_SIZE_GB` | `DEC` | Tamaño del backup en GB. |
| `DURATION_MINUTES` | `INT4` | Duración del proceso en minutos. |
| `MESSAGE` | `STRING` | Mensaje funcional o técnico. |

## Response Example

```json
{
  "ET_DB13_HISTORY": [
    {
      "DATE": "20260401",
      "JOB_NAME": "DB_BACKUP",
      "STATUS": "SUCCESS",
      "DATABASE_SIZE_GB": 820,
      "BACKUP_SIZE_GB": 210,
      "DURATION_MINUTES": 45,
      "MESSAGE": "Backup completed"
    }
  ]
}
```

## ABAP Skeleton

```abap
FUNCTION z_get_db13_history.
*"----------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE(iv_date_from) TYPE dats
*"     VALUE(iv_date_to)   TYPE dats
*"     VALUE(iv_system_id) TYPE char10
*"     VALUE(iv_status)    TYPE char20 OPTIONAL
*"     VALUE(iv_action)    TYPE char40 OPTIONAL
*"     VALUE(iv_jobname)   TYPE char64 OPTIONAL
*"  TABLES
*"      et_results STRUCTURE zdb13_history_s
*"----------------------------------------------------------------------

  " TODO DEV:
  " 1. Validar autorizaciones.
  " 2. Validar rango de fechas.
  " 3. Obtener datos DB13/backups desde fuente aprobada por Basis.
  " 4. Normalizar estados y tamaños a GB.
  " 5. Completar ET_DB13_HISTORY.

ENDFUNCTION.
```

## Consideraciones De Seguridad

- Crear un usuario técnico RFC con permisos mínimos.
- Restringir autorización al function group correspondiente.
- No retornar credenciales, paths sensibles ni detalles internos innecesarios.
- Registrar auditoría de llamadas si la política corporativa lo requiere.
- Validar rangos de fecha para evitar consultas costosas.
- Exponer el backend FastAPI detrás de autenticación y TLS en ambientes compartidos.

## Consideraciones Técnicas

- No asumir tablas SAP internas sin validación de Basis.
- Confirmar fuente funcional de DB13/backups en DEV antes de transporte.
- Mantener compatibilidad ECC/S/4HANA revisando diferencias por versión.
- Normalizar `STATUS` antes de exponerlo al consumidor REST.
