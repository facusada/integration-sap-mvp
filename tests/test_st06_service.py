from datetime import date
from typing import Any

from app.services.st06_service import ST06Service


class FakeRFCClient:
    def __init__(self, rows: list[dict[str, Any]]):
        self.rows = rows
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def call(self, function_name: str, **parameters: Any) -> dict[str, Any]:
        self.calls.append((function_name, parameters))
        return {"ET_ST06_HISTORY": self.rows}


def test_get_st06_history_calls_expected_rfc_and_maps_rows() -> None:
    fake_client = FakeRFCClient(
        [
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
    )
    service = ST06Service(fake_client)

    result = service.get_history(
        system_id="PRO",
        period="last_24_hours",
        host="itl-srv070",
        category="CPU",
        date_from=date(2026, 4, 28),
        date_to=date(2026, 4, 28),
    )

    assert fake_client.calls == [
        (
            "Z_GET_ST06_HISTORY",
            {
                "IV_DATE_FROM": "20260428",
                "IV_DATE_TO": "20260428",
                "IV_SYSTEM_ID": "PRO",
                "IV_HOST": "itl-srv070",
                "IV_CATEGORY": "CPU",
            },
        )
    ]
    assert result.system_id == "PRO"
    assert result.host == "itl-srv070"
    assert result.category == "CPU"
    assert result.items[0].timestamp.isoformat() == "2026-04-28T14:34:04"
    assert result.items[0].metric == "CPU Utilization"
    assert result.items[0].value == 9
    assert result.items[0].unit == "%"

