# SAP Integration Suite iFlow Guide

## Objetivo

Consumir el backend FastAPI desde SAP Integration Suite para obtener histórico ST06 / OS Monitor en formato JSON.

## Endpoint Histórico ST06

Método:

```text
GET
```

URL DEV sugerida:

```text
https://<backend-host>/sap/st06/history?system_id=PRO&period=last_24_hours&host=itl-srv070&category=CPU
```

## Endpoint Histórico DB13

Endpoint legado/prototipo.

Método:

```text
GET
```

URL DEV sugerida:

```text
https://<backend-host>/sap/db13/history?system_id=DEV&period=last_90_days
```

## Endpoint Crecimiento

Endpoint legado/prototipo DB13.

```text
GET https://<backend-host>/sap/db/growth?system_id=DEV&period=last_90_days
```

## Adapter

Usar HTTP Receiver Adapter:

- Method: `GET`
- Content-Type esperado: `application/json`
- Timeout: definir según estándar corporativo.
- Retry: habilitar para errores transitorios `502`, `503`, `504`.

## Autenticación Sugerida

Para DEV:

- API key o Basic Auth solo en entornos controlados.

Para QAS/PRD:

- OAuth2 Client Credentials, mTLS o mecanismo corporativo equivalente.
- TLS obligatorio.
- Rotación de secretos mediante vault corporativo.

## Manejo De Errores

- `200`: respuesta JSON válida.
- `422`: parámetros inválidos, por ejemplo `period` mal formado.
- `500`: error interno del backend.
- `502`: error de comunicación o ejecución RFC hacia SAP.

El iFlow debería:

- Registrar `status_code` y payload de error.
- Enviar alertas ante `502` persistente.
- Evitar reintentos infinitos para errores `422`.
- Enriquecer mensajes con `system_id` y periodo solicitado.

## Ejemplo Payload Histórico ST06

```json
{
  "system_id": "PRO",
  "period": "last_24_hours",
  "host": "itl-srv070",
  "category": "CPU",
  "items": [
    {
      "timestamp": "2026-04-28T14:34:04",
      "host": "itl-srv070",
      "category": "CPU",
      "metric": "CPU Utilization",
      "value": 9,
      "unit": "%",
      "message": "Snapshot Overview"
    }
  ]
}
```

## Ejemplo Payload Histórico DB13 Legado

```json
{
  "system_id": "PRD",
  "period": "last_90_days",
  "items": [
    {
      "date": "2026-04-01",
      "job_name": "DB_BACKUP",
      "status": "SUCCESS",
      "database_size_gb": 820,
      "backup_size_gb": 210,
      "duration_minutes": 45,
      "message": "Backup completed"
    }
  ]
}
```

## Ejemplo Payload Crecimiento

```json
{
  "system_id": "PRD",
  "period": "last_90_days",
  "initial_size_gb": 800,
  "current_size_gb": 860,
  "growth_gb": 60,
  "growth_percentage": 7.5
}
```
