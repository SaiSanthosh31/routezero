"""
RouteZero Reconnaissance Package
HAR parsing, raw log parsing, endpoint normalization, API classification, and OpenAPI generation.
"""

# Unified imports handling both package and relative contexts
try:
    from .har_parser import HARParser, parse_har, normalize_path, is_static_asset
    from .log_parser import LogParser, parse_raw_logs, detect_log_format
    from .discovery import APIClassifier, classify_endpoints
    from .openapi_gen import generate_openapi_spec
except ImportError:
    # Fallback for direct import paths when package is not installed as a module
    from recon.har_parser import HARParser, parse_har, normalize_path, is_static_asset
    from recon.log_parser import LogParser, parse_raw_logs, detect_log_format
    from recon.discovery import APIClassifier, classify_endpoints
    from recon.openapi_gen import generate_openapi_spec

__all__ = [
    "HARParser",
    "parse_har",
    "LogParser",
    "parse_raw_logs",
    "detect_log_format",
    "normalize_path",
    "is_static_asset",
    "APIClassifier",
    "classify_endpoints",
    "generate_openapi_spec",
]
