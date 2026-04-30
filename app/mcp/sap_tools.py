from __future__ import annotations

import logging
from typing import Any

from app.core.config import Settings, get_settings
from app.core.exceptions import SapBridgeError
from app.services.sap_rfc_client import RFCClient, SAPRFCClient

logger = logging.getLogger(__name__)

BUILDER_RFC_NAME = "Z_MCP_CREATE_SERVICE"


def rfc_call_function_tool(
    function_name: str,
    params: dict[str, Any] | None = None,
    *,
    rfc_client: RFCClient | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Call any RFC-enabled function module and return a sanitized result envelope."""
    if not function_name or not function_name.strip():
        return {"error": "function_name is required"}

    resolved_params = params or {}
    client = rfc_client or SAPRFCClient(settings or get_settings())

    try:
        logger.info("MCP RFC call requested for %s", function_name)
        result = client.call(function_name.strip().upper(), **resolved_params)
        return {"result": result}
    except SapBridgeError as exc:
        logger.warning("MCP RFC call failed for %s: %s", function_name, exc)
        return {"error": str(exc)}
    except Exception as exc:
        logger.exception("Unexpected MCP RFC call failure for %s", function_name)
        return {"error": f"Unexpected RFC call failure: {type(exc).__name__}"}


def create_service_tool(
    object_name: str,
    object_type: str,
    package: str = "$TMP",
    source: str = "",
    *,
    rfc_client: RFCClient | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Create an ABAP service through the existing SAP builder RFC."""
    if not object_name or not object_name.strip():
        return {"success": False, "message": "object_name is required", "raw": {}}
    if not object_type or not object_type.strip():
        return {"success": False, "message": "object_type is required", "raw": {}}

    client = rfc_client or SAPRFCClient(settings or get_settings())

    interface_check = rfc_call_function_tool(
        "RFC_GET_FUNCTION_INTERFACE",
        {"FUNCNAME": BUILDER_RFC_NAME},
        rfc_client=client,
    )
    if "error" in interface_check:
        return {
            "success": False,
            "message": f"{BUILDER_RFC_NAME} does not exist or is not callable. Install the ABAP builder first.",
            "raw": interface_check,
        }

    raw_result = rfc_call_function_tool(
        BUILDER_RFC_NAME,
        {
            "IV_OBJECT_NAME": object_name.strip().upper(),
            "IV_OBJECT_TYPE": object_type.strip().upper(),
            "IV_PACKAGE": package.strip() or "$TMP",
            "IV_SOURCE": source[:255],
        },
        rfc_client=client,
    )
    if "error" in raw_result:
        return {"success": False, "message": raw_result["error"], "raw": raw_result}

    raw = raw_result["result"]
    success = raw.get("EV_SUCCESS") == "X"
    message = str(raw.get("EV_MESSAGE") or "")
    return {"success": success, "message": message, "raw": raw}


def create_and_call_rfc_tool(
    object_name: str,
    object_type: str,
    call_params: dict[str, Any] | None = None,
    package: str = "$TMP",
    source: str = "",
    *,
    rfc_client: RFCClient | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Create an ABAP RFC through the builder and call it if creation succeeds."""
    client = rfc_client or SAPRFCClient(settings or get_settings())
    creation = create_service_tool(
        object_name=object_name,
        object_type=object_type,
        package=package,
        source=source,
        rfc_client=client,
    )
    if not creation.get("success"):
        return {"success": False, "create": creation, "call": None}

    interface_check = rfc_call_function_tool(
        "RFC_GET_FUNCTION_INTERFACE",
        {"FUNCNAME": object_name.strip().upper()},
        rfc_client=client,
    )
    if "error" in interface_check:
        return {
            "success": False,
            "create": creation,
            "call": interface_check,
        }

    call_result = rfc_call_function_tool(
        object_name.strip().upper(),
        call_params or {},
        rfc_client=client,
    )
    return {
        "success": "result" in call_result,
        "create": creation,
        "call": call_result,
    }


def rfc_get_function_interface_tool(
    function_name: str,
    *,
    rfc_client: RFCClient | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Inspect whether an RFC-enabled function exists and retrieve its interface metadata."""
    return rfc_call_function_tool(
        "RFC_GET_FUNCTION_INTERFACE",
        {"FUNCNAME": function_name.strip().upper()},
        rfc_client=rfc_client,
        settings=settings,
    )


def z_get_db13_history_tool(
    date_from: str,
    date_to: str,
    system_id: str | None = None,
    status: str | None = None,
    action: str | None = None,
    job_name: str | None = None,
    *,
    rfc_client: RFCClient | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Execute Z_GET_DB13_HISTORY with optional filters supported by the custom RFC."""
    resolved_settings = settings or get_settings()
    try:
        params: dict[str, Any] = {
            "IV_DATE_FROM": _normalize_sap_date(date_from),
            "IV_DATE_TO": _normalize_sap_date(date_to),
            "IV_SYSTEM_ID": system_id or resolved_settings.sap_default_system_id,
        }
    except ValueError as exc:
        return {"error": str(exc)}

    optional_params = {
        "IV_STATUS": status,
        "IV_ACTION": action,
        "IV_JOBNAME": job_name,
    }
    params.update({key: value for key, value in optional_params.items() if value})

    return rfc_call_function_tool(
        "Z_GET_DB13_HISTORY",
        params,
        rfc_client=rfc_client,
        settings=resolved_settings,
    )


def z_get_st06_history_tool(
    date_from: str,
    date_to: str,
    system_id: str | None = None,
    host: str | None = None,
    category: str | None = None,
    *,
    rfc_client: RFCClient | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Execute Z_GET_ST06_HISTORY with optional host/category filters."""
    resolved_settings = settings or get_settings()
    try:
        params: dict[str, Any] = {
            "IV_DATE_FROM": _normalize_sap_date(date_from),
            "IV_DATE_TO": _normalize_sap_date(date_to),
            "IV_SYSTEM_ID": system_id or resolved_settings.sap_default_system_id,
        }
    except ValueError as exc:
        return {"error": str(exc)}

    if host:
        params["IV_HOST"] = host
    if category:
        params["IV_CATEGORY"] = category

    return rfc_call_function_tool(
        "Z_GET_ST06_HISTORY",
        params,
        rfc_client=rfc_client,
        settings=resolved_settings,
    )


def _normalize_sap_date(value: str) -> str:
    normalized = value.replace("-", "").strip()
    if len(normalized) != 8 or not normalized.isdigit():
        raise ValueError("date values must use YYYYMMDD or YYYY-MM-DD format")
    return normalized
