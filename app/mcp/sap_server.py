from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from app.mcp.sap_tools import (
    create_and_call_rfc_tool,
    create_service_tool,
    rfc_call_function_tool,
    rfc_get_function_interface_tool,
    z_get_db13_history_tool,
    z_get_st06_history_tool,
)

mcp = FastMCP("SAP RFC MCP Server")


@mcp.tool()
def rfc_call_function(function_name: str, params: dict[str, Any]) -> dict[str, Any]:
    """Call any SAP RFC-enabled Function Module using PyRFC."""
    return rfc_call_function_tool(function_name=function_name, params=params)


@mcp.tool()
def rfc_get_function_interface(function_name: str) -> dict[str, Any]:
    """Validate that an RFC exists and retrieve its interface using RFC_GET_FUNCTION_INTERFACE."""
    return rfc_get_function_interface_tool(function_name=function_name)


@mcp.tool()
def create_service(
    object_name: str,
    object_type: str,
    package: str = "$TMP",
    source: str = "",
) -> dict[str, Any]:
    """Create an ABAP service by calling the existing SAP builder RFC Z_MCP_CREATE_SERVICE."""
    return create_service_tool(
        object_name=object_name,
        object_type=object_type,
        package=package,
        source=source,
    )


@mcp.tool()
def create_and_call_rfc(
    object_name: str,
    object_type: str,
    call_params: dict[str, Any] | None = None,
    package: str = "$TMP",
    source: str = "",
) -> dict[str, Any]:
    """Create an RFC through Z_MCP_CREATE_SERVICE and call it if creation succeeds."""
    return create_and_call_rfc_tool(
        object_name=object_name,
        object_type=object_type,
        call_params=call_params,
        package=package,
        source=source,
    )


@mcp.tool()
def z_get_db13_history(
    date_from: str,
    date_to: str,
    system_id: str | None = None,
    status: str | None = None,
    action: str | None = None,
    job_name: str | None = None,
) -> dict[str, Any]:
    """Execute custom RFC Z_GET_DB13_HISTORY for DB13 historical data."""
    return z_get_db13_history_tool(
        date_from=date_from,
        date_to=date_to,
        system_id=system_id,
        status=status,
        action=action,
        job_name=job_name,
    )


@mcp.tool()
def z_get_st06_history(
    date_from: str,
    date_to: str,
    system_id: str | None = None,
    host: str | None = None,
    category: str | None = None,
) -> dict[str, Any]:
    """Execute custom RFC Z_GET_ST06_HISTORY for ST06 operating system history."""
    return z_get_st06_history_tool(
        date_from=date_from,
        date_to=date_to,
        system_id=system_id,
        host=host,
        category=category,
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
