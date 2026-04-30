from datetime import date
from typing import Any

import pytest

from app.core.config import Settings
from app.core.exceptions import SapRfcExecutionError
from app.services.db13_service import DB13Service
from app.services.sap_rfc_client import SAPRFCClient


class FakeRFCClient:
    def __init__(self, rows: list[dict[str, Any]]):
        self.rows = rows
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def call(self, function_name: str, **parameters: Any) -> dict[str, Any]:
        self.calls.append((function_name, parameters))
        return {"ET_DB13_HISTORY": self.rows}


def test_get_history_calls_expected_rfc_and_maps_rows() -> None:
    fake_client = FakeRFCClient(
        [
            {
                "DATE": "20260401",
                "JOB_NAME": "DB_BACKUP",
                "STATUS": "SUCCESS",
                "DATABASE_SIZE_GB": 820,
                "BACKUP_SIZE_GB": 210,
                "DURATION_MINUTES": 45,
                "MESSAGE": "Backup completed",
            }
        ]
    )
    service = DB13Service(fake_client)

    result = service.get_history(
        system_id="PRD",
        period="last_90_days",
        date_from=date(2026, 1, 1),
        date_to=date(2026, 4, 1),
    )

    assert fake_client.calls == [
        (
            "Z_GET_DB13_HISTORY",
            {
                "IV_DATE_FROM": "20260101",
                "IV_DATE_TO": "20260401",
                "IV_SYSTEM_ID": "PRD",
            },
        )
    ]
    assert result.system_id == "PRD"
    assert result.period == "last_90_days"
    assert result.items[0].date.isoformat() == "2026-04-01"
    assert result.items[0].database_size_gb == 820
    assert result.items[0].message == "Backup completed"


def test_get_growth_calculates_absolute_and_percentage_growth() -> None:
    fake_client = FakeRFCClient(
        [
            {
                "DATE": "20260101",
                "JOB_NAME": "DB_BACKUP",
                "STATUS": "SUCCESS",
                "DATABASE_SIZE_GB": 800,
                "BACKUP_SIZE_GB": 200,
                "DURATION_MINUTES": 40,
            },
            {
                "DATE": "20260401",
                "JOB_NAME": "DB_BACKUP",
                "STATUS": "SUCCESS",
                "DATABASE_SIZE_GB": 860,
                "BACKUP_SIZE_GB": 210,
                "DURATION_MINUTES": 45,
            },
        ]
    )
    service = DB13Service(fake_client)

    result = service.get_growth(
        system_id="PRD",
        period="last_90_days",
        date_from=date(2026, 1, 1),
        date_to=date(2026, 4, 1),
    )

    assert result.initial_size_gb == 800
    assert result.current_size_gb == 860
    assert result.growth_gb == 60
    assert result.growth_percentage == 7.5


def test_get_growth_returns_zero_values_when_history_is_empty() -> None:
    service = DB13Service(FakeRFCClient([]))

    result = service.get_growth(
        system_id="PRD",
        period="last_90_days",
        date_from=date(2026, 1, 1),
        date_to=date(2026, 4, 1),
    )

    assert result.initial_size_gb == 0
    assert result.current_size_gb == 0
    assert result.growth_gb == 0
    assert result.growth_percentage == 0


def test_invalid_rfc_rows_raise_execution_error() -> None:
    service = DB13Service(FakeRFCClient([{"DATE": "invalid"}]))

    with pytest.raises(SapRfcExecutionError):
        service.get_history(
            system_id="PRD",
            period="last_90_days",
            date_from=date(2026, 1, 1),
            date_to=date(2026, 4, 1),
        )


def test_sap_rfc_client_mock_mode_returns_history_without_pyrfc() -> None:
    settings = Settings(SAP_RFC_MOCK_MODE=True, SAP_DEFAULT_SYSTEM_ID="DEV")
    client = SAPRFCClient(settings)

    result = client.call(
        "Z_GET_DB13_HISTORY",
        IV_DATE_FROM="20260101",
        IV_DATE_TO="20260401",
        IV_SYSTEM_ID="DEV",
    )

    assert "ET_DB13_HISTORY" in result
    assert result["ET_DB13_HISTORY"][0]["JOB_NAME"] == "DB_BACKUP"

