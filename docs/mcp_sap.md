# MCP SAP RFC Integration

## Objetivo

Exponer tools MCP para consultar SAP vía RFC usando PyRFC y SAP NW RFC SDK, sin hardcodear credenciales.

## Estado Actual Del Proyecto

- No existía MCP previamente.
- Ya existía cliente PyRFC encapsulado en `app/services/sap_rfc_client.py`.
- El MCP reutiliza ese cliente.
- No se encontró builder ABAP tipo `Z_MCP_CREATE_SERVICE` en el código.
- La creación real de `Z_GET_ST06_HISTORY` sigue siendo una tarea SAP DEV/ABAP, salvo que el cliente provea un builder RFC aprobado.

## Variables De Entorno

```env
SAP_RFC_MOCK_MODE=false
SAP_RFC_ASHOST=<sap-application-server>
SAP_RFC_SYSNR=<system-number>
SAP_RFC_CLIENT=<mandante>
SAP_RFC_USER=<usuario-rfc>
SAP_RFC_PASSWD=<password>
SAP_RFC_LANG=EN
SAP_DEFAULT_SYSTEM_ID=DEV
```

No commitear `.env` ni credenciales reales.

## Instalar Dependencias

Para ejecutar el MCP en modo mock:

```bash
source .venv/bin/activate
pip install -e ".[dev,mcp]"
```

Para conexión real SAP, además se requiere SAP NW RFC SDK instalado en el host y PyRFC:

```bash
pip install -e ".[dev,mcp,sap]"
```

`pyrfc` está fijado en `3.3.1` en `pyproject.toml`. Las releases disponibles en PyPI están marcadas como yanked, por eso no se usa un rango `pyrfc>=...`.

## Arrancar MCP Stdio

```bash
python -m app.mcp.sap_server
```

El server usa `mcp.server.fastmcp.FastMCP` y transporte `stdio`.

## Tools Expuestas

### `rfc_call_function`

Llama cualquier Function Module RFC-enabled.

Entrada:

```json
{
  "function_name": "STFC_CONNECTION",
  "params": {
    "REQUTEXT": "ping"
  }
}
```

Salida esperada:

```json
{
  "result": {
    "ECHOTEXT": "ping",
    "RESPTEXT": "..."
  }
}
```

Ante error:

```json
{
  "error": "..."
}
```

### `rfc_get_function_interface`

Valida si existe una RFC y consulta su interfaz usando `RFC_GET_FUNCTION_INTERFACE`.

Entrada:

```json
{
  "function_name": "Z_GET_DB13_HISTORY"
}
```

Equivalente RFC:

```json
{
  "function_name": "RFC_GET_FUNCTION_INTERFACE",
  "params": {
    "FUNCNAME": "Z_GET_DB13_HISTORY"
  }
}
```

### `create_service`

Replica el patron del proyecto original: el MCP Python no crea ABAP directamente. La tool llama una RFC builder que debe existir previamente en SAP:

```text
Z_MCP_CREATE_SERVICE
```

Antes de llamar el builder, valida que exista con:

```json
{
  "function_name": "RFC_GET_FUNCTION_INTERFACE",
  "params": {
    "FUNCNAME": "Z_MCP_CREATE_SERVICE"
  }
}
```

Entrada MCP:

```json
{
  "object_name": "Z_GET_DB13_HISTORY",
  "object_type": "<TABLA_SAP>",
  "package": "$TMP",
  "source": "<CAMPO_FILTRO>"
}
```

Llamada RFC ejecutada por PyRFC:

```json
{
  "function_name": "Z_MCP_CREATE_SERVICE",
  "params": {
    "IV_OBJECT_NAME": "Z_GET_DB13_HISTORY",
    "IV_OBJECT_TYPE": "<TABLA_SAP>",
    "IV_PACKAGE": "$TMP",
    "IV_SOURCE": "<CAMPO_FILTRO truncado a 255 chars>"
  }
}
```

Mapeo de respuesta:

```json
{
  "success": true,
  "message": "texto desde EV_MESSAGE",
  "raw": {
    "EV_SUCCESS": "X",
    "EV_MESSAGE": "..."
  }
}
```

Si `Z_MCP_CREATE_SERVICE` no existe, la tool devuelve `success=false` y un mensaje indicando que primero debe instalarse el builder ABAP.

### `create_and_call_rfc`

Primero llama `create_service`. Si la creacion fue exitosa:

1. Valida que el Function Module creado exista con `RFC_GET_FUNCTION_INTERFACE`.
2. Ejecuta el Function Module creado mediante `rfc_call_function`.

Entrada:

```json
{
  "object_name": "Z_GET_DB13_HISTORY",
  "object_type": "<TABLA_SAP>",
  "package": "$TMP",
  "source": "<CAMPO_FILTRO>",
  "call_params": {
    "IV_KEY": "<VALOR>"
  }
}
```

Ejemplo conceptual alineado al builder simple:

```python
create_and_call_rfc(
    object_name="Z_GET_DB13_HISTORY",
    object_type="<TABLA_SAP>",
    source="<CAMPO_FILTRO>",
    package="$TMP",
    call_params={"IV_KEY": "<VALOR>"}
)
```

En ese patron:

- `object_name` es el Function Module Z a crear.
- `object_type` se usa como tabla SAP fuente del SELECT simple.
- `source` se usa como campo filtro.
- `call_params["IV_KEY"]` es el valor usado para filtrar.

Script equivalente:

```bash
python scripts/create_and_call_rfc.py \
  --object-name Z_GET_DB13_HISTORY \
  --object-type "<TABLA_SAP>" \
  --source "<CAMPO_FILTRO>" \
  --package '$TMP' \
  --call-params '{"IV_KEY":"<VALOR>"}'
```

Para solo crear sin ejecutar:

```bash
python scripts/create_and_call_rfc.py \
  --object-name Z_GET_DB13_HISTORY \
  --object-type "<TABLA_SAP>" \
  --source "<CAMPO_FILTRO>" \
  --package '$TMP' \
  --create-only
```

### `z_get_st06_history`

Ejecuta la RFC custom propuesta para ST06.

Entrada:

```json
{
  "date_from": "2026-04-28",
  "date_to": "2026-04-28",
  "system_id": "PRO",
  "host": "itl-srv070",
  "category": "CPU"
}
```

La tool envía a SAP:

```json
{
  "IV_DATE_FROM": "20260428",
  "IV_DATE_TO": "20260428",
  "IV_SYSTEM_ID": "PRO",
  "IV_HOST": "itl-srv070",
  "IV_CATEGORY": "CPU"
}
```

### `z_get_db13_history`

Tool legada/prototipo DB13.

Ejecuta la RFC custom propuesta.

Entrada:

```json
{
  "date_from": "2026-01-01",
  "date_to": "2026-04-24",
  "system_id": "DEV",
  "status": "SUCCESS",
  "job_name": "DB_BACKUP"
}
```

La tool envía a SAP:

```json
{
  "IV_DATE_FROM": "20260101",
  "IV_DATE_TO": "20260424",
  "IV_SYSTEM_ID": "DEV",
  "IV_STATUS": "SUCCESS",
  "IV_JOBNAME": "DB_BACKUP"
}
```

## Script Para Ejecutar ST06

```bash
python scripts/call_z_get_st06_history.py \
  --date-from 2026-04-28 \
  --date-to 2026-04-28 \
  --system-id PRO \
  --host itl-srv070 \
  --category CPU
```

## Script Para Ejecutar DB13 Legado

```bash
python scripts/call_z_get_db13_history.py \
  --date-from 2026-01-01 \
  --date-to 2026-04-24 \
  --system-id DEV \
  --status SUCCESS \
  --job-name DB_BACKUP
```

## Validar Conexión

Primero usar una RFC estándar simple:

```json
{
  "function_name": "STFC_CONNECTION",
  "params": {
    "REQUTEXT": "mcp connectivity check"
  }
}
```

Luego validar interfaz:

```json
{
  "function_name": "RFC_GET_FUNCTION_INTERFACE",
  "params": {
    "FUNCNAME": "Z_GET_DB13_HISTORY"
  }
}
```

## Sobre Crear La RFC ABAP

PyRFC y este MCP no crean ABAP directamente. Para crear artefactos, el MCP debe llamar un builder ABAP/RFC existente y aprobado.

Si el sistema SAP del cliente tiene un builder RFC aprobado, por ejemplo `Z_MCP_CREATE_SERVICE`, hay que inspeccionar primero su interfaz con:

```json
{
  "function_name": "RFC_GET_FUNCTION_INTERFACE",
  "params": {
    "FUNCNAME": "Z_MCP_CREATE_SERVICE"
  }
}
```

Si ese builder solo genera consultas simples como:

```abap
SELECT * FROM <tabla> WHERE <campo> = <valor>
```

probablemente no alcanza para DB13, porque el caso requiere filtros por rango de fecha, normalización de estados, tamaños y potencialmente lógica Basis específica.

En ese caso, implementar en DEV una RFC custom `Z_GET_DB13_HISTORY` con:

- `IV_DATE_FROM`
- `IV_DATE_TO`
- `IV_SYSTEM_ID`
- `IV_STATUS` opcional
- `IV_ACTION` opcional
- `IV_JOBNAME` opcional
- `ET_RESULTS`

## Descubrir Fuente Real ST06

No se debe inventar la tabla SAP exacta. ST06 puede obtener datos desde CCMS/OS monitoring/snapshots, y la fuente depende del release y configuración Basis.

Opciones:

- Revisar ST06 en Expert View e History.
- Revisar RZ20 / CCMS.
- Hacer `ST05` trace mientras se navega ST06 History.
- Revisar programas/includes estándar usados por ST06.
- Confirmar con Basis si hay tablas/vistas internas aptas para lectura.

Para histórico ST06 real, normalmente conviene `Z_GET_ST06_HISTORY` custom con `IV_DATE_FROM`, `IV_DATE_TO`, `IV_HOST`, `IV_CATEGORY` y salida clave/valor/unidad. Un builder simple de `WHERE <campo> = IV_KEY` probablemente no alcance si se necesitan rangos y múltiples métricas.

## Descubrir Fuente Real DB13 Legado

No se debe inventar la tabla SAP exacta. La fuente depende de release, base de datos y configuración Basis.

Opciones para descubrirla:

- Revisar DB13/DBA Cockpit con Basis.
- Buscar diccionario con `DD02L`.
- Inspeccionar campos con `DD03L`.
- Usar `RFC_READ_TABLE` en DEV para análisis controlado.
- Revisar programas/includes estándar usados por DB13 en el sistema del cliente.

Ejemplo conceptual para metadatos:

```json
{
  "function_name": "RFC_READ_TABLE",
  "params": {
    "QUERY_TABLE": "DD03L",
    "DELIMITER": "|",
    "OPTIONS": [
      { "TEXT": "TABNAME = 'NOMBRE_TABLA_CANDIDATA'" }
    ],
    "FIELDS": [
      { "FIELDNAME": "TABNAME" },
      { "FIELDNAME": "FIELDNAME" },
      { "FIELDNAME": "ROLLNAME" }
    ]
  }
}
```

Usar solo en DEV y con límites de filas cuando aplique.
