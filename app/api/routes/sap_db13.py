from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import Settings, get_settings
from app.core.exceptions import SapRfcConfigurationError, SapRfcExecutionError
from app.schemas.db13 import DB13HistoryResponse, DBGrowthResponse
from app.services.db13_service import DB13Service
from app.services.sap_rfc_client import SAPRFCClient

router = APIRouter(prefix="/sap", tags=["sap-db13"])


def get_db13_service(settings: Settings = Depends(get_settings)) -> DB13Service:
    return DB13Service(SAPRFCClient(settings))


@router.get("/db13/history", response_model=DB13HistoryResponse)
def get_db13_history(
    system_id: str | None = Query(default=None, min_length=1, max_length=10),
    period: str = Query(default="last_90_days", pattern=r"^last_[0-9]+_days$"),
    date_from: date | None = None,
    date_to: date | None = None,
    settings: Settings = Depends(get_settings),
    service: DB13Service = Depends(get_db13_service),
) -> DB13HistoryResponse:
    resolved_system_id = system_id or settings.sap_default_system_id
    try:
        return service.get_history(
            system_id=resolved_system_id,
            period=period,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except SapRfcConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except SapRfcExecutionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/db/growth", response_model=DBGrowthResponse)
def get_db_growth(
    system_id: str | None = Query(default=None, min_length=1, max_length=10),
    period: str = Query(default="last_90_days", pattern=r"^last_[0-9]+_days$"),
    date_from: date | None = None,
    date_to: date | None = None,
    settings: Settings = Depends(get_settings),
    service: DB13Service = Depends(get_db13_service),
) -> DBGrowthResponse:
    resolved_system_id = system_id or settings.sap_default_system_id
    try:
        return service.get_growth(
            system_id=resolved_system_id,
            period=period,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except SapRfcConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except SapRfcExecutionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

