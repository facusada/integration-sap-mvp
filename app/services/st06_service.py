from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.core.exceptions import SapRfcExecutionError
from app.schemas.st06 import ST06HistoryItem, ST06HistoryResponse
from app.services.db13_service import resolve_date_range
from app.services.sap_rfc_client import RFCClient


class ST06Service:
    RFC_NAME = "Z_GET_ST06_HISTORY"

    def __init__(self, rfc_client: RFCClient):
        self._rfc_client = rfc_client

    def get_history(
        self,
        *,
        system_id: str,
        period: str = "last_24_hours",
        host: str | None = None,
        category: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> ST06HistoryResponse:
        start_date, end_date = resolve_date_range(period, date_from, date_to)
        params: dict[str, Any] = {
            "IV_DATE_FROM": start_date.strftime("%Y%m%d"),
            "IV_DATE_TO": end_date.strftime("%Y%m%d"),
            "IV_SYSTEM_ID": system_id,
        }
        if host:
            params["IV_HOST"] = host
        if category:
            params["IV_CATEGORY"] = category

        result = self._rfc_client.call(self.RFC_NAME, **params)
        rows = result.get("ET_ST06_HISTORY", result.get("ET_RESULTS", []))
        if not isinstance(rows, list):
            raise SapRfcExecutionError("RFC response ET_ST06_HISTORY must be a list.")

        items = [_map_st06_row(row) for row in rows]
        items.sort(key=lambda item: item.timestamp)

        return ST06HistoryResponse(
            system_id=system_id,
            period=period,
            host=host,
            category=category,
            items=items,
        )


def _map_st06_row(row: dict[str, Any]) -> ST06HistoryItem:
    try:
        return ST06HistoryItem(
            timestamp=_parse_sap_timestamp(row),
            host=str(row.get("HOST") or row.get("HOSTNAME") or ""),
            category=str(row.get("CATEGORY") or row.get("MONITORING_CATEGORY") or ""),
            metric=str(row.get("METRIC") or row.get("DESCRIPTION") or ""),
            value=_parse_metric_value(row.get("VALUE")),
            unit=row.get("UNIT"),
            message=row.get("MESSAGE"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise SapRfcExecutionError("Invalid row returned by Z_GET_ST06_HISTORY.") from exc


def _parse_sap_timestamp(row: dict[str, Any]) -> datetime:
    if isinstance(row.get("TIMESTAMP"), datetime):
        return row["TIMESTAMP"]

    timestamp = row.get("TIMESTAMP")
    if isinstance(timestamp, str) and timestamp:
        normalized = timestamp.replace("-", "").replace(":", "").replace(" ", "").replace("T", "")
        if len(normalized) >= 14:
            return datetime.strptime(normalized[:14], "%Y%m%d%H%M%S")

    date_value = str(row["DATE"]).replace("-", "")
    time_value = str(row.get("TIME") or "000000").replace(":", "")
    return datetime.strptime(f"{date_value}{time_value[:6].zfill(6)}", "%Y%m%d%H%M%S")


def _parse_metric_value(value: Any) -> float | str:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        normalized = value.strip().replace(".", "").replace(",", ".")
        try:
            return float(normalized)
        except ValueError:
            return value.strip()
    return str(value)

