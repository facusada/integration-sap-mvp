# TDD Plan - SAP ST06 History Bridge

## Flujo

Aplicar Red -> Green -> Refactor en cada incremento.

## Casos Unitarios

1. `GET /health` devuelve `status=ok`.
2. `ST06Service.get_history` llama `Z_GET_ST06_HISTORY` con `IV_DATE_FROM`, `IV_DATE_TO`, `IV_SYSTEM_ID` y filtros opcionales.
3. `ST06Service.get_history` transforma timestamp ABAP `YYYYMMDDHHMMSS` a ISO datetime.
4. `ST06Service.get_history` normaliza filas a `host`, `category`, `metric`, `value`, `unit`.
5. `SAPRFCClient` en modo mock devuelve una tabla `ET_ST06_HISTORY` sin importar PyRFC.
6. Ruta `/sap/st06/history` devuelve contrato JSON esperado usando servicio mockeado.
7. `period` inválido devuelve HTTP 422.
8. Tests DB13 existentes permanecen como cobertura legada.

## Mocks

- No se conecta a SAP real.
- Los tests usan un fake RFC client con método `call`.
- Las rutas usan dependency overrides de FastAPI.

## Comandos

```bash
python -m pytest
```
