from __future__ import annotations

import logging
from datetime import date
from typing import Any, Protocol

from app.core.config import Settings
from app.core.exceptions import SapRfcConfigurationError, SapRfcExecutionError

logger = logging.getLogger(__name__)


class RFCClient(Protocol):
    def call(self, function_name: str, **parameters: Any) -> dict[str, Any]:
        """Call an RFC-enabled SAP function module."""


class SAPRFCClient:
    def __init__(self, settings: Settings):
        self._settings = settings

    def call(self, function_name: str, **parameters: Any) -> dict[str, Any]:
        logger.info("Calling SAP RFC %s", function_name)

        if self._settings.sap_rfc_mock_mode:
            return self._mock_call(function_name, **parameters)

        connection_params = self._validated_connection_params()

        try:
            from pyrfc import Connection
        except ImportError as exc:
            raise SapRfcConfigurationError(
                "PyRFC is not installed. Install the SAP extra and SAP NW RFC SDK before disabling mock mode."
            ) from exc

        try:
            with Connection(**connection_params) as connection:
                return connection.call(function_name, **parameters)
        except Exception as exc:  # pragma: no cover - depends on external SAP runtime.
            logger.exception("SAP RFC call failed: %s", function_name)
            raise SapRfcExecutionError(f"SAP RFC call failed: {function_name}") from exc

    def _validated_connection_params(self) -> dict[str, str]:
        params = self._settings.sap_connection_params()
        missing = [name for name, value in params.items() if name != "lang" and not value]
        if missing:
            raise SapRfcConfigurationError(
                "Missing SAP RFC configuration values: " + ", ".join(sorted(missing))
            )
        return params

    def _mock_call(self, function_name: str, **parameters: Any) -> dict[str, Any]:
        if function_name == "RFC_PING":
            return {}

        if function_name == "STFC_CONNECTION":
            return {
                "ECHOTEXT": parameters.get("REQUTEXT", ""),
                "RESPTEXT": "Mock SAP RFC connection ok",
            }

        if function_name == "RFC_GET_FUNCTION_INTERFACE":
            return self._mock_function_interface(parameters)

        if function_name == "Z_GET_ST06_HISTORY":
            return self._mock_st06_history(parameters)

        if function_name != "Z_GET_DB13_HISTORY":
            raise SapRfcExecutionError(f"Unsupported mock RFC: {function_name}")

        system_id = str(parameters.get("IV_SYSTEM_ID") or self._settings.sap_default_system_id)
        logger.info("Returning mock DB13 history for system %s", system_id)

        return {
            "ET_DB13_HISTORY": [
                {
                    "DATE": "20260124",
                    "JOB_NAME": "DB_BACKUP",
                    "STATUS": "SUCCESS",
                    "DATABASE_SIZE_GB": 800,
                    "BACKUP_SIZE_GB": 205,
                    "DURATION_MINUTES": 42,
                    "MESSAGE": "Mock backup completed",
                },
                {
                    "DATE": date.today().strftime("%Y%m%d"),
                    "JOB_NAME": "DB_BACKUP",
                    "STATUS": "SUCCESS",
                    "DATABASE_SIZE_GB": 860,
                    "BACKUP_SIZE_GB": 218,
                    "DURATION_MINUTES": 47,
                    "MESSAGE": "Mock backup completed",
                },
            ]
        }

    def _mock_function_interface(self, parameters: dict[str, Any]) -> dict[str, Any]:
        function_name = str(parameters.get("FUNCNAME", "")).upper()
        if function_name == "Z_GET_ST06_HISTORY":
            return {
                "FUNCNAME": "Z_GET_ST06_HISTORY",
                "IMPORT_PARAMETER": [
                    {"PARAMETER": "IV_DATE_FROM", "FIELDNAME": "DATS", "OPTIONAL": ""},
                    {"PARAMETER": "IV_DATE_TO", "FIELDNAME": "DATS", "OPTIONAL": ""},
                    {"PARAMETER": "IV_SYSTEM_ID", "FIELDNAME": "CHAR10", "OPTIONAL": ""},
                    {"PARAMETER": "IV_HOST", "FIELDNAME": "CHAR64", "OPTIONAL": "X"},
                    {"PARAMETER": "IV_CATEGORY", "FIELDNAME": "CHAR40", "OPTIONAL": "X"},
                ],
                "TABLES_PARAMETER": [
                    {"PARAMETER": "ET_ST06_HISTORY", "STRUCTURE": "ZST06_HISTORY_S", "OPTIONAL": ""}
                ],
                "EXCEPTION_LIST": [],
            }

        if function_name != "Z_GET_DB13_HISTORY":
            raise SapRfcExecutionError(f"Mock interface not available for RFC: {function_name}")

        return {
            "FUNCNAME": "Z_GET_DB13_HISTORY",
            "IMPORT_PARAMETER": [
                {"PARAMETER": "IV_DATE_FROM", "FIELDNAME": "DATS", "OPTIONAL": ""},
                {"PARAMETER": "IV_DATE_TO", "FIELDNAME": "DATS", "OPTIONAL": ""},
                {"PARAMETER": "IV_SYSTEM_ID", "FIELDNAME": "CHAR10", "OPTIONAL": ""},
                {"PARAMETER": "IV_STATUS", "FIELDNAME": "CHAR20", "OPTIONAL": "X"},
                {"PARAMETER": "IV_ACTION", "FIELDNAME": "CHAR40", "OPTIONAL": "X"},
                {"PARAMETER": "IV_JOBNAME", "FIELDNAME": "CHAR64", "OPTIONAL": "X"},
            ],
            "TABLES_PARAMETER": [
                {"PARAMETER": "ET_RESULTS", "STRUCTURE": "ZDB13_HISTORY_S", "OPTIONAL": ""}
            ],
            "EXCEPTION_LIST": [],
        }

    def _mock_st06_history(self, parameters: dict[str, Any]) -> dict[str, Any]:
        host = str(parameters.get("IV_HOST") or "itl-srv070")
        category = str(parameters.get("IV_CATEGORY") or "CPU")
        today = date.today().strftime("%Y%m%d")
        return {
            "ET_ST06_HISTORY": [
                {
                    "TIMESTAMP": f"{today}143404",
                    "HOST": host,
                    "CATEGORY": "Info",
                    "METRIC": "Operating system",
                    "VALUE": "Linux itl-srv070 4.18.0-305.el8.x86_64",
                    "UNIT": "",
                    "MESSAGE": "Mock ST06 snapshot",
                },
                {
                    "TIMESTAMP": f"{today}143404",
                    "HOST": host,
                    "CATEGORY": category,
                    "METRIC": "CPU Utilization",
                    "VALUE": 9,
                    "UNIT": "%",
                    "MESSAGE": "Mock ST06 snapshot",
                },
                {
                    "TIMESTAMP": f"{today}143404",
                    "HOST": host,
                    "CATEGORY": category,
                    "METRIC": "Idle",
                    "VALUE": 91,
                    "UNIT": "%",
                    "MESSAGE": "Mock ST06 snapshot",
                },
            ]
        }
