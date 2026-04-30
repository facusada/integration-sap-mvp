from datetime import date
from typing import Any

from fastapi.testclient import TestClient

from app.api.routes.sap_db13 import get_db13_service
from app.main import create_app
from app.services.db13_service import DB13Service


class FakeRFCClient:
    def call(self, function_name: str, **parameters: Any) -> dict[str, Any]:
        return {
            "ET_DB13_HISTORY": [
                {
                    "DATE": "20260101",
                    "JOB_NAME": "DB_BACKUP",
                    "STATUS": "SUCCESS",
                    "DATABASE_SIZE_GB": 800,
                    "BACKUP_SIZE_GB": 200,
                    "DURATION_MINUTES": 40,
                    "MESSAGE": "Backup completed",
                },
                {
                    "DATE": "20260401",
                    "JOB_NAME": "DB_BACKUP",
                    "STATUS": "SUCCESS",
                    "DATABASE_SIZE_GB": 860,
                    "BACKUP_SIZE_GB": 210,
                    "DURATION_MINUTES": 45,
                    "MESSAGE": "Backup completed",
                },
            ]
        }


def _client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_db13_service] = lambda: DB13Service(FakeRFCClient())
    return TestClient(app)


def test_db13_history_route_returns_expected_contract() -> None:
    client = _client()

    response = client.get(
        "/sap/db13/history",
        params={
            "system_id": "PRD",
            "period": "last_90_days",
            "date_from": date(2026, 1, 1).isoformat(),
            "date_to": date(2026, 4, 1).isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "system_id": "PRD",
        "period": "last_90_days",
        "items": [
            {
                "date": "2026-01-01",
                "job_name": "DB_BACKUP",
                "status": "SUCCESS",
                "database_size_gb": 800,
                "backup_size_gb": 200,
                "duration_minutes": 40,
                "message": "Backup completed",
            },
            {
                "date": "2026-04-01",
                "job_name": "DB_BACKUP",
                "status": "SUCCESS",
                "database_size_gb": 860,
                "backup_size_gb": 210,
                "duration_minutes": 45,
                "message": "Backup completed",
            },
        ],
    }


def test_db_growth_route_returns_expected_contract() -> None:
    client = _client()

    response = client.get(
        "/sap/db/growth",
        params={
            "system_id": "PRD",
            "period": "last_90_days",
            "date_from": "2026-01-01",
            "date_to": "2026-04-01",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "system_id": "PRD",
        "period": "last_90_days",
        "initial_size_gb": 800,
        "current_size_gb": 860,
        "growth_gb": 60,
        "growth_percentage": 7.5,
    }


def test_invalid_period_returns_422() -> None:
    client = _client()

    response = client.get("/sap/db13/history", params={"period": "90_days"})

    assert response.status_code == 422

