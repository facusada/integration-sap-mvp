# SDD - SAP ST06 History Bridge

## Objetivo

Construir un backend FastAPI que actúe como puente entre SAP ECC/S/4HANA y SAP Integration Suite para exponer información histórica de ST06 / OS Monitor mediante endpoints REST JSON.

## Alcance

Incluye:

- API REST con `GET /health` y `GET /sap/st06/history`.
- Endpoints DB13 existentes quedan como prototipo legado.
- Cliente PyRFC encapsulado y mockeable.
- Configuración por variables de entorno.
- Servicios separados de rutas HTTP.
- Schemas Pydantic para contrato JSON.
- Tests unitarios y de rutas sin conexión SAP real.
- Documentación del RFC ABAP esperado `Z_GET_ST06_HISTORY`.
- Guía de consumo desde SAP Integration Suite.

No incluye:

- Conexión a SAP real.
- Implementación o transporte automático de objetos ABAP.
- Asumir tablas SAP internas como fuente definitiva.
- Persistencia local.
- Autenticación productiva completa. Se documenta como recomendación.

## Arquitectura

SAP ECC/S/4HANA -> RFC ABAP custom -> FastAPI + PyRFC -> REST JSON -> SAP Integration Suite -> dashboard/storage/API externa.

## Criterios De Aceptación

- La API inicia localmente sin credenciales SAP usando modo mock.
- `/health` devuelve estado operativo.
- `/sap/st06/history` devuelve `system_id`, `period`, host/categoría opcionales e items históricos normalizados.
- PyRFC no se importa al cargar la app; se importa de forma tardía al ejecutar llamadas reales.
- Las credenciales se leen desde variables de entorno.
- Los tests usan mocks y no dependen de SAP.
- La documentación describe contrato RFC, parámetros, seguridad y consumo desde Integration Suite.

## Edge Cases

- PyRFC no instalado: el error debe indicar dependencia faltante solo si se intenta una llamada real.
- Variables SAP incompletas: error de configuración claro en modo real.
- RFC devuelve tabla vacía: historial vacío.
- Fechas ABAP inválidas: error de ejecución claro.
- `period` inválido: HTTP 422.
- Categoría/host sin datos: respuesta vacía con filtros reflejados.

## Impacto Técnico

- El backend queda preparado para DEV y posterior transporte del RFC a QAS/PRD.
- La fuente real de ST06 queda detrás de `Z_GET_ST06_HISTORY`, evitando acoplar la API a tablas SAP internas.
- El modo mock permite desarrollar iFlows y dashboards antes de habilitar conectividad SAP.

## Decisiones Técnicas Iniciales

- Python 3.11+.
- FastAPI con Pydantic v2.
- `pydantic-settings` para configuración.
- `pytest` y `TestClient` para TDD.
- PyRFC como dependencia opcional `sap`, porque requiere SAP NW RFC SDK.
- `SAP_RFC_MOCK_MODE=true` por defecto para DEV local.
