# SAP Monitoring Integration Bridge

Backend FastAPI para exponer información histórica de monitoreo SAP mediante REST JSON y MCP. El foco actual es ST06 / OS Monitor; DB13 queda como endpoint legado/prototipo.

La app corre en modo mock por defecto. No intenta conectarse a SAP real salvo que `SAP_RFC_MOCK_MODE=false`.

## Requisitos

- Python 3.11+
- Para conexión SAP real futura: SAP NW RFC SDK + `pyrfc`

## Instalación Local

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

Para instalar soporte PyRFC cuando el SDK esté disponible:

```bash
python -m pip install -e ".[dev,sap]"
```

Nota: `pyrfc` se fija en `3.3.1` porque las versiones publicadas en PyPI están marcadas como yanked y pip no resuelve `pyrfc>=...`. La instalación de Python puede completar, pero la importación real requiere SAP NW RFC SDK disponible en el sistema.

Para instalar el servidor MCP:

```bash
python -m pip install -e ".[dev,mcp]"
```

Para MCP + SAP real:

```bash
python -m pip install -e ".[dev,mcp,sap]"
```

## Ejecutar

```bash
uvicorn app.main:app --reload
```

Endpoints:

- `GET /health`
- `GET /sap/st06/history?system_id=PRO&period=last_24_hours&host=itl-srv070&category=CPU`
- `GET /sap/db13/history?system_id=DEV&period=last_90_days`
- `GET /sap/db/growth?system_id=DEV&period=last_90_days`

## Tests

```bash
python -m pytest
```

## Configuración

Variables principales:

- `SAP_RFC_MOCK_MODE`: `true` por defecto.
- `SAP_RFC_ASHOST`
- `SAP_RFC_SYSNR`
- `SAP_RFC_CLIENT`
- `SAP_RFC_USER`
- `SAP_RFC_PASSWD`
- `SAP_RFC_LANG`
- `SAP_DEFAULT_SYSTEM_ID`

No commitear `.env` ni credenciales reales.

## MCP SAP RFC

Arrancar servidor MCP stdio:

```bash
python -m app.mcp.sap_server
```

Tools disponibles:

- `rfc_call_function`
- `rfc_get_function_interface`
- `create_service`
- `create_and_call_rfc`
- `z_get_st06_history`
- `z_get_db13_history`

Guía completa: `docs/mcp_sap.md`.

Ejemplo CLI para el builder `Z_MCP_CREATE_SERVICE`:

```bash
python scripts/create_and_call_rfc.py \
  --object-name Z_GET_DB13_HISTORY \
  --object-type "<TABLA_SAP>" \
  --source "<CAMPO_FILTRO>" \
  --package '$TMP' \
  --call-params '{"IV_KEY":"<VALOR>"}'
```

## Documentación

- SDD: `docs/sdd.md`
- Spec WIP ST06: `docs/sdd/wip/sap-st06-history/spec.md`
- Spec WIP DB13 legado: `docs/sdd/wip/sap-db13-history/spec.md`
- TDD: `docs/tdd.md`
- RFC ABAP ST06 esperado: `docs/st06_rfc_contract.md`
- RFC ABAP DB13 legado: `docs/rfc_contract.md`
- SAP Integration Suite: `docs/integration_suite_iflow.md`
- MCP SAP RFC: `docs/mcp_sap.md`
# integration-sap-mvp
