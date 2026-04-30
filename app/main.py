import logging

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.sap_db13 import router as sap_db13_router
from app.api.routes.sap_st06 import router as sap_st06_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)

    application = FastAPI(
        title="SAP Monitoring Integration Bridge",
        version="0.1.0",
        description="FastAPI bridge for SAP monitoring data exposed through custom RFCs.",
    )
    application.include_router(health_router)
    application.include_router(sap_db13_router)
    application.include_router(sap_st06_router)
    return application


app = create_app()
