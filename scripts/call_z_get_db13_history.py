from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.mcp.sap_tools import z_get_db13_history_tool


def main() -> None:
    parser = argparse.ArgumentParser(description="Call SAP RFC Z_GET_DB13_HISTORY through PyRFC.")
    parser.add_argument("--date-from", required=True, help="Start date as YYYYMMDD or YYYY-MM-DD.")
    parser.add_argument("--date-to", required=True, help="End date as YYYYMMDD or YYYY-MM-DD.")
    parser.add_argument("--system-id", help="SAP logical system id. Defaults to SAP_DEFAULT_SYSTEM_ID.")
    parser.add_argument("--status", help="Optional status filter if supported by the RFC.")
    parser.add_argument("--action", help="Optional action filter if supported by the RFC.")
    parser.add_argument("--job-name", help="Optional job name filter if supported by the RFC.")
    args = parser.parse_args()

    result = z_get_db13_history_tool(
        date_from=args.date_from,
        date_to=args.date_to,
        system_id=args.system_id,
        status=args.status,
        action=args.action,
        job_name=args.job_name,
    )
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
