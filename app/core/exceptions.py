class SapBridgeError(Exception):
    """Base exception for SAP bridge failures."""


class SapRfcConfigurationError(SapBridgeError):
    """Raised when RFC configuration is incomplete or invalid."""


class SapRfcExecutionError(SapBridgeError):
    """Raised when an RFC call fails or returns invalid data."""

