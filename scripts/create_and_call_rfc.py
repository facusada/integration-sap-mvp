from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.mcp.sap_tools import create_and_call_rfc_tool, create_service_tool


def _parse_json_object(raw: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"Invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise argparse.ArgumentTypeError("Value must be a JSON object.")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an RFC through Z_MCP_CREATE_SERVICE and optionally call it."
    )
    parser.add_argument("--object-name", required=True, help="Function Module to create.")
    parser.add_argument("--object-type", required=True, help="Builder object type, often the SAP table name.")
    parser.add_argument("--package", default="$TMP", help="SAP package. Defaults to $TMP.")
    parser.add_argument("--source", default="", help="Builder source/filter field. Truncated to 255 chars.")
    parser.add_argument(
        "--call-params",
        type=_parse_json_object,
        help='JSON object with call params, for example \'{"IV_KEY":"VALUE"}\'.',
    )
    parser.add_argument(
        "--create-only",
        action="store_true",
        help="Only call create_service; do not call the created RFC.",
    )
    args = parser.parse_args()

    if args.create_only:
        result = create_service_tool(
            object_name=args.object_name,
            object_type=args.object_type,
            package=args.package,
            source=args.source,
        )
    else:
        result = create_and_call_rfc_tool(
            object_name=args.object_name,
            object_type=args.object_type,
            package=args.package,
            source=args.source,
            call_params=args.call_params or {},
        )

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
