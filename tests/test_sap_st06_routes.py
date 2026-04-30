from typing import Any

from fastapi.testclient import TestClient

from app.api.routes.sap_st06 import get_st06_service
from app.main import create_app
from app.services.st06_service import ST06Service


class FakeRFCClient:
    def call(self, function_name: str, **parameters: Any) -> dict[str, Any]:
        return {
            "ET_ST06_HISTORY": [
                {
                    "TIMESTAMP": "20260428143404",
                    "HOST": "itl-srv070",
                    "CATEGORY": "CPU",
                    "METRIC": "CPU Utilization",
                    "VALUE": 9,
                    "UNIT": "%",
                    "MESSAGE": "Snapshot",
                }
            ]
        }


def _client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_st06_service] = lambda: ST06Service(FakeRFCClient())
    return TestClient(app)


def test_st06_history_route_returns_expected_contract() -> None:
    client = _client()

    response = client.get(
        "/sap/st06/history",
        params={
            "system_id": "PRO",
            "period": "last_24_hours",
            "host": "itl-srv070",
            "category": "CPU",
            "date_from": "2026-04-28",
            "date_to": "2026-04-28",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
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
                "value": 9.0,
                "unit": "%",
                "message": "Snapshot",
            }
        ],
    }


def test_st06_invalid_period_returns_422() -> None:
    client = _client()

    response = client.get("/sap/st06/history", params={"period": "24_hours"})

    assert response.status_code == 422

