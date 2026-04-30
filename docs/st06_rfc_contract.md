# RFC Contract - Z_GET_ST06_HISTORY

## Propósito

`Z_GET_ST06_HISTORY` es una RFC ABAP custom propuesta para exponer información histórica de ST06 / OS Monitor por sistema y host. Debe implementarse primero en DEV, validarse con Basis y luego transportarse a QAS/PRD.

Este repositorio no crea ni modifica objetos SAP automáticamente.

## Function Module

```text
Z_GET_ST06_HISTORY
```

Remote-enabled: sí.

## Import Parameters

| Parámetro | Tipo sugerido | Obligatorio | Descripción |
| --- | --- | --- | --- |
| `IV_DATE_FROM` | `DATS` | Sí | Fecha inicial `YYYYMMDD`. |
| `IV_DATE_TO` | `DATS` | Sí | Fecha final `YYYYMMDD`. |
| `IV_SYSTEM_ID` | `SYSID` o `CHAR10` | Sí | Sistema SAP lógico, por ejemplo `PRO` o `DES`. |
| `IV_HOST` | `CHAR64` | No | Host ST06, por ejemplo `itl-srv070`. |
| `IV_CATEGORY` | `CHAR40` | No | Categoría ST06, por ejemplo `CPU`, `Memory`, `Disk`, `LAN`, `Filesystem`. |

## Table Parameters

`ET_ST06_HISTORY`

| Campo | Tipo sugerido | Descripción |
| --- | --- | --- |
| `TIMESTAMP` | `CHAR14` o `TIMESTAMP` | Fecha/hora de snapshot en `YYYYMMDDHHMMSS`. |
| `HOST` | `CHAR64` | Host monitoreado. |
| `CATEGORY` | `CHAR40` | Categoría ST06. |
| `METRIC` | `CHAR80` | Métrica o descripción, por ejemplo `CPU Utilization`. |
| `VALUE` | `CHAR80` | Valor normalizado como texto o número. |
| `UNIT` | `CHAR20` | Unidad, por ejemplo `%`, `MB`, `/s`. |
| `MESSAGE` | `CHAR255` | Mensaje técnico/funcional opcional. |

## Response Example

```json
{
  "ET_ST06_HISTORY": [
    {
      "TIMESTAMP": "20260428143404",
      "HOST": "itl-srv070",
      "CATEGORY": "CPU",
      "METRIC": "CPU Utilization",
      "VALUE": "9",
      "UNIT": "%",
      "MESSAGE": "Snapshot Overview"
    }
  ]
}
```

## Fuente Real ST06

La fuente exacta debe confirmarla Basis. ST06/OS Monitor suele leer datos de CCMS/monitoring y snapshots de host, y puede variar por release, configuración y collector.

Opciones de investigación:

- ST06 en modo Expert View.
- RZ20 / CCMS.
- ST03N si se necesita carga/workload, no OS puro.
- `ST05` trace mientras se navega ST06 History.
- Revisión de programas/includes estándar usados por ST06.
- Tablas/vistas confirmadas por Basis.

## ABAP Skeleton

```abap
FUNCTION z_get_st06_history.
*"----------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE(iv_date_from) TYPE dats
*"     VALUE(iv_date_to)   TYPE dats
*"     VALUE(iv_system_id) TYPE char10
*"     VALUE(iv_host)      TYPE char64 OPTIONAL
*"     VALUE(iv_category)  TYPE char40 OPTIONAL
*"  TABLES
*"      et_st06_history STRUCTURE zst06_history_s
*"----------------------------------------------------------------------

  " TODO DEV:
  " 1. Validar autorizaciones.
  " 2. Validar rango de fechas.
  " 3. Confirmar fuente real ST06/CCMS con Basis.
  " 4. Leer snapshots historicos por host/categoria.
  " 5. Normalizar metricas a formato clave/valor/unidad.
  " 6. Completar ET_ST06_HISTORY.

ENDFUNCTION.
```

## Consideraciones

- No asumir tablas ST06 sin validación Basis.
- Evitar exponer datos sensibles del host.
- Limitar rangos de fecha para no ejecutar consultas costosas.
- Implementar primero en DEV y transportar mediante proceso SAP normal.

