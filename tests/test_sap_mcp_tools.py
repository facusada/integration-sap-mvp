from typing import Any

from app.core.config import Settings
from app.mcp.sap_tools import (
    create_and_call_rfc_tool,
    create_service_tool,
    rfc_call_function_tool,
    rfc_get_function_interface_tool,
    z_get_db13_history_tool,
    z_get_st06_history_tool,
)
from scripts.create_and_call_rfc import _parse_json_object


class FakeRFCClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def call(self, function_name: str, **parameters: Any) -> dict[str, Any]:
        self.calls.append((function_name, parameters))
        return {"FUNCTION": function_name, "PARAMETERS": parameters}


class FakeBuilderRFCClient:
    def __init__(self, builder_exists: bool = True) -> None:
        self.builder_exists = builder_exists
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def call(self, function_name: str, **parameters: Any) -> dict[str, Any]:
        self.calls.append((function_name, parameters))
        if function_name == "RFC_GET_FUNCTION_INTERFACE":
            funcname = parameters["FUNCNAME"]
            if funcname == "Z_MCP_CREATE_SERVICE" and not self.builder_exists:
                raise RuntimeError("FU_NOT_FOUND")
            return {"FUNCNAME": funcname}
        if function_name == "Z_MCP_CREATE_SERVICE":
            return {"EV_SUCCESS": "X", "EV_MESSAGE": "Created"}
        return {"CALLED": function_name, "PARAMETERS": parameters}


def test_rfc_call_function_tool_returns_result_envelope() -> None:
    fake_client = FakeRFCClient()

    result = rfc_call_function_tool(
        "stfc_connection",
        {"REQUTEXT": "ping"},
        rfc_client=fake_client,
    )

    assert result == {
        "result": {
            "FUNCTION": "STFC_CONNECTION",
            "PARAMETERS": {"REQUTEXT": "ping"},
        }
    }
    assert fake_client.calls == [("STFC_CONNECTION", {"REQUTEXT": "ping"})]


def test_rfc_get_function_interface_tool_calls_standard_rfc() -> None:
    fake_client = FakeRFCClient()

    result = rfc_get_function_interface_tool(
        "z_get_db13_history",
        rfc_client=fake_client,
    )

    assert result["result"]["FUNCTION"] == "RFC_GET_FUNCTION_INTERFACE"
    assert result["result"]["PARAMETERS"] == {"FUNCNAME": "Z_GET_DB13_HISTORY"}


def test_z_get_db13_history_tool_maps_filters_to_import_params() -> None:
    fake_client = FakeRFCClient()
    settings = Settings(SAP_RFC_MOCK_MODE=True, SAP_DEFAULT_SYSTEM_ID="DEV")

    result = z_get_db13_history_tool(
        date_from="2026-01-01",
        date_to="2026-04-24",
        system_id="PRD",
        status="SUCCESS",
        action="BACKUP",
        job_name="DB_BACKUP",
        rfc_client=fake_client,
        settings=settings,
    )

    assert result["result"]["FUNCTION"] == "Z_GET_DB13_HISTORY"
    assert result["result"]["PARAMETERS"] == {
        "IV_DATE_FROM": "20260101",
        "IV_DATE_TO": "20260424",
        "IV_SYSTEM_ID": "PRD",
        "IV_STATUS": "SUCCESS",
        "IV_ACTION": "BACKUP",
        "IV_JOBNAME": "DB_BACKUP",
    }


def test_z_get_db13_history_tool_returns_error_for_invalid_date() -> None:
    result = z_get_db13_history_tool(date_from="2026", date_to="2026-04-24")

    assert result == {"error": "date values must use YYYYMMDD or YYYY-MM-DD format"}


def test_z_get_st06_history_tool_maps_filters_to_import_params() -> None:
    fake_client = FakeRFCClient()
    settings = Settings(SAP_RFC_MOCK_MODE=True, SAP_DEFAULT_SYSTEM_ID="PRO")

    result = z_get_st06_history_tool(
        date_from="2026-04-28",
        date_to="2026-04-28",
        system_id="PRO",
        host="itl-srv070",
        category="CPU",
        rfc_client=fake_client,
        settings=settings,
    )

    assert result["result"]["FUNCTION"] == "Z_GET_ST06_HISTORY"
    assert result["result"]["PARAMETERS"] == {
        "IV_DATE_FROM": "20260428",
        "IV_DATE_TO": "20260428",
        "IV_SYSTEM_ID": "PRO",
        "IV_HOST": "itl-srv070",
        "IV_CATEGORY": "CPU",
    }


def test_create_service_validates_builder_and_maps_response() -> None:
    fake_client = FakeBuilderRFCClient()
    source = "x" * 300

    result = create_service_tool(
        object_name="z_get_db13_history",
        object_type="rfc",
        package="$TMP",
        source=source,
        rfc_client=fake_client,
    )

    assert result == {
        "success": True,
        "message": "Created",
        "raw": {"EV_SUCCESS": "X", "EV_MESSAGE": "Created"},
    }
    assert fake_client.calls[0] == (
        "RFC_GET_FUNCTION_INTERFACE",
        {"FUNCNAME": "Z_MCP_CREATE_SERVICE"},
    )
    assert fake_client.calls[1] == (
        "Z_MCP_CREATE_SERVICE",
        {
            "IV_OBJECT_NAME": "Z_GET_DB13_HISTORY",
            "IV_OBJECT_TYPE": "RFC",
            "IV_PACKAGE": "$TMP",
            "IV_SOURCE": "x" * 255,
        },
    )


def test_create_service_returns_clear_error_when_builder_is_missing() -> None:
    fake_client = FakeBuilderRFCClient(builder_exists=False)

    result = create_service_tool(
        object_name="Z_GET_DB13_HISTORY",
        object_type="RFC",
        rfc_client=fake_client,
    )

    assert result["success"] is False
    assert "Z_MCP_CREATE_SERVICE does not exist" in result["message"]


def test_create_and_call_rfc_creates_validates_and_calls_created_function() -> None:
    fake_client = FakeBuilderRFCClient()

    result = create_and_call_rfc_tool(
        object_name="Z_GET_DB13_HISTORY",
        object_type="RFC",
        call_params={"IV_SYSTEM_ID": "DES"},
        rfc_client=fake_client,
    )

    assert result["success"] is True
    assert result["create"]["success"] is True
    assert result["call"] == {
        "result": {
            "CALLED": "Z_GET_DB13_HISTORY",
            "PARAMETERS": {"IV_SYSTEM_ID": "DES"},
        }
    }
    assert fake_client.calls[-2] == (
        "RFC_GET_FUNCTION_INTERFACE",
        {"FUNCNAME": "Z_GET_DB13_HISTORY"},
    )
    assert fake_client.calls[-1] == ("Z_GET_DB13_HISTORY", {"IV_SYSTEM_ID": "DES"})


def test_create_and_call_cli_json_parser_accepts_object() -> None:
    assert _parse_json_object('{"IV_KEY":"VALUE"}') == {"IV_KEY": "VALUE"}
