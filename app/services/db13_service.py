from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from app.core.exceptions import SapRfcExecutionError
from app.schemas.db13 import DB13HistoryItem, DB13HistoryResponse, DBGrowthResponse
from app.services.sap_rfc_client import RFCClient


class DB13Service:
    RFC_NAME = "Z_GET_DB13_HISTORY"

    def __init__(self, rfc_client: RFCClient):
        self._rfc_client = rfc_client

    def get_history(
        self,
        *,
        system_id: str,
        period: str = "last_90_days",
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> DB13HistoryResponse:
        start_date, end_date = resolve_date_range(period, date_from, date_to)
        result = self._rfc_client.call(
            self.RFC_NAME,
            IV_DATE_FROM=start_date.strftime("%Y%m%d"),
            IV_DATE_TO=end_date.strftime("%Y%m%d"),
            IV_SYSTEM_ID=system_id,
        )
        rows = result.get("ET_DB13_HISTORY", result.get("ET_RESULTS", []))
        if not isinstance(rows, list):
            raise SapRfcExecutionError("RFC response ET_DB13_HISTORY must be a list.")

        items = [_map_db13_row(row) for row in rows]
        items.sort(key=lambda item: item.date)

        return DB13HistoryResponse(system_id=system_id, period=period, items=items)

    def get_growth(
        self,
        *,
        system_id: str,
        period: str = "last_90_days",
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> DBGrowthResponse:
        history = self.get_history(
            system_id=system_id,
            period=period,
            date_from=date_from,
            date_to=date_to,
        )

        if not history.items:
            return DBGrowthResponse(
                system_id=system_id,
                period=period,
                initial_size_gb=0,
                current_size_gb=0,
                growth_gb=0,
                growth_percentage=0,
            )

        initial_size = history.items[0].database_size_gb
        current_size = history.items[-1].database_size_gb
        growth = current_size - initial_size
        growth_percentage = 0 if initial_size == 0 else (growth / initial_size) * 100

        return DBGrowthResponse(
            system_id=system_id,
            period=period,
            initial_size_gb=round(initial_size, 2),
            current_size_gb=round(current_size, 2),
            growth_gb=round(growth, 2),
            growth_percentage=round(growth_percentage, 2),
        )


def resolve_date_range(
    period: str,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[date, date]:
    end_date = date_to or date.today()
    if date_from:
        return date_from, end_date

    if period.startswith("last_") and period.endswith("_hours"):
        raw_hours = period.removeprefix("last_").removesuffix("_hours")
        try:
            hours = int(raw_hours)
        except ValueError as exc:
            raise ValueError("period must use format last_<hours>_hours or last_<days>_days") from exc
        if hours <= 0 or hours > 87840:
            raise ValueError("period hours must be between 1 and 87840")
        return end_date - timedelta(days=max(1, (hours + 23) // 24)), end_date

    if period.startswith("last_") and period.endswith("_days"):
        raw_days = period.removeprefix("last_").removesuffix("_days")
        try:
            days = int(raw_days)
        except ValueError as exc:
            raise ValueError("period must use format last_<hours>_hours or last_<days>_days") from exc
        if days <= 0 or days > 3660:
            raise ValueError("period days must be between 1 and 3660")
        return end_date - timedelta(days=days), end_date

    raise ValueError("period must use format last_<hours>_hours or last_<days>_days")


def _map_db13_row(row: dict[str, Any]) -> DB13HistoryItem:
    try:
        return DB13HistoryItem(
            date=_parse_sap_date(row["DATE"]),
            job_name=str(row.get("JOB_NAME", "")),
            status=str(row.get("STATUS", "")),
            database_size_gb=float(row.get("DATABASE_SIZE_GB", 0)),
            backup_size_gb=float(row.get("BACKUP_SIZE_GB", 0)),
            duration_minutes=int(row.get("DURATION_MINUTES", 0)),
            message=row.get("MESSAGE"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise SapRfcExecutionError("Invalid row returned by Z_GET_DB13_HISTORY.") from exc


def _parse_sap_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError("SAP date must be a string.")

    normalized = value.replace("-", "")
    return datetime.strptime(normalized, "%Y%m%d").date()
