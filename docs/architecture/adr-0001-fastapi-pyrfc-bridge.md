# ADR 0001 - FastAPI + PyRFC Bridge

## Estado

Aceptado.

## Contexto

Se necesita exponer datos SAP DB13 a consumidores HTTP sin acoplar SAP Integration Suite directamente a detalles RFC, credenciales SAP o tablas internas.

## Decisión

Crear un backend FastAPI con PyRFC encapsulado en una capa de cliente y servicios de dominio para publicar contratos REST JSON.

## Consecuencias

- Facilita testing con mocks.
- Permite evolucionar autenticación, observabilidad y resiliencia sin cambiar el RFC.
- Requiere SAP NW RFC SDK solo cuando se habilita conectividad SAP real.

