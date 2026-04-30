from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import Settings, get_settings
from app.core.exceptions import SapRfcConfigurationError, SapRfcExecutionError
from app.schemas.st06 import ST06HistoryResponse
from app.services.sap_rfc_client import SAPRFCClient
from app.services.st06_service import ST06Service

router = APIRouter(prefix="/sap", tags=["sap-st06"])


def get_st06_service(settings: Settings = Depends(get_settings)) -> ST06Service:
    return ST06Service(SAPRFCClient(settings))


@router.get("/st06/history", response_model=ST06HistoryResponse)
def get_st06_history(
    system_id: str | None = Query(default=None, min_length=1, max_length=10),
    period: str = Query(default="last_24_hours", pattern=r"^last_[0-9]+_(hours|days)$"),
    host: str | None = Query(default=None, min_length=1, max_length=64),
    category: str | None = Query(default=None, min_length=1, max_length=40),
    date_from: date | None = None,
    date_to: date | None = None,
    settings: Settings = Depends(get_settings),
    service: ST06Service = Depends(get_st06_service),
) -> ST06HistoryResponse:
    resolved_system_id = system_id or settings.sap_default_system_id
    try:
        return service.get_history(
            system_id=resolved_system_id,
            period=period,
            host=host,
            category=category,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except SapRfcConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except SapRfcExecutionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

