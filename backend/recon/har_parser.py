import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Set

STATIC_EXTENSIONS: Set[str] = {
    ".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".otf", ".map", ".webp",
    ".mp4", ".mp3", ".webm", ".avi", ".pdf"
}

SENSITIVE_FIELD_REGEX = re.compile(
    r"(password|passwd|secret|token|api_?key|auth|bearer|credit_?card|cvv|ssn|refresh_?token|access_?token|passport)",
    re.IGNORECASE
)

SENSITIVE_HEADER_NAMES: Set[str] = {
    "authorization", "cookie", "set-cookie", "proxy-authorization",
    "x-api-key", "apikey", "x-auth-token", "token"
}

UUID_REGEX = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
PREFIXED_ID_REGEX = re.compile(r"^[A-Za-z]{2,}-\d+$")
NUMERIC_ID_REGEX = re.compile(r"^\d+$")


def parse_har_timestamp(ts_str: Optional[str]) -> Optional[str]:
    """Parses HAR ISO 8601 timestamps into normalized UTC string 'YYYY-MM-DD HH:MM:SS'."""
    if not ts_str or not isinstance(ts_str, str):
        return None
    ts_clean = ts_str.strip()
    fmts = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(ts_clean, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
    return ts_clean


def is_static_asset(path: str) -> bool:
    """Checks whether the URL path references a static file asset."""
    clean_path = path.lower().split("?")[0].split("#")[0]
    for ext in STATIC_EXTENSIONS:
        if clean_path.endswith(ext):
            return True
    return False


def normalize_path(path: str) -> str:
    """
    Normalizes dynamic path segments into template parameters.
    e.g. /api/v2/bookings/BK-1001 -> /api/v2/bookings/{booking_id}
         /api/v2/refunds/RF-9988 -> /api/v2/refunds/{refund_id}
         /api/v2/users/12345     -> /api/v2/users/{user_id}
    """
    if not path:
        return "/"

    segments = path.strip("/").split("/")
    normalized_segments = []

    for idx, seg in enumerate(segments):
        # If already parameterized like {booking_id}, retain it
        if seg.startswith("{") and seg.endswith("}"):
            normalized_segments.append(seg)
            continue

        prev_seg = segments[idx - 1].lower() if idx > 0 else ""
        is_dynamic = False
        param_name = "id"

        if UUID_REGEX.match(seg) or PREFIXED_ID_REGEX.match(seg) or NUMERIC_ID_REGEX.match(seg):
            is_dynamic = True
            if prev_seg == "bookings":
                param_name = "booking_id"
            elif prev_seg == "refunds":
                param_name = "refund_id"
            elif prev_seg == "agencies":
                param_name = "agency_id"
            elif prev_seg == "flights":
                param_name = "flight_id"
            elif prev_seg.endswith("s") and len(prev_seg) > 1:
                param_name = f"{prev_seg[:-1]}_id"
            else:
                param_name = "id"

        if is_dynamic:
            normalized_segments.append(f"{{{param_name}}}")
        else:
            normalized_segments.append(seg)

    result = "/" + "/".join(normalized_segments)
    return result


def redact_sensitive_value(key: str, value: Any) -> Any:
    """Preserves parameter key name while redacting sensitive values."""
    if SENSITIVE_FIELD_REGEX.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {k: redact_sensitive_value(k, v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_sensitive_value(key, item) for item in value]
    return value


def sanitize_headers(headers: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Sanitizes HTTP headers by replacing credentials/tokens with [REDACTED]."""
    sanitized = []
    for h in headers:
        if not isinstance(h, dict) or "name" not in h:
            continue
        name = h.get("name", "")
        value = h.get("value", "")
        if name.lower() in SENSITIVE_HEADER_NAMES or SENSITIVE_FIELD_REGEX.search(name):
            sanitized.append({"name": name, "value": "[REDACTED]"})
        else:
            sanitized.append({"name": name, "value": value})
    return sanitized


class HARParser:
    """Parses standard HAR 1.2 logs and extracts clean API endpoints and metadata."""

    def __init__(self, target_host: Optional[str] = None):
        self.target_host = target_host.lower() if target_host else None

    def parse(self, har_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parses a HAR object or raw JSON string.
        Returns a dict containing:
        - endpoints: List of discovered, normalized, and redacted endpoint dicts
        - total_entries: count of processed entries
        - valid_entries: count of accepted API entries
        - skipped_static: count of skipped static files
        - errors: parsing warnings or errors
        """
        errors = []
        if isinstance(har_data, str):
            try:
                har_dict = json.loads(har_data)
            except Exception as e:
                return {
                    "endpoints": [],
                    "total_entries": 0,
                    "valid_entries": 0,
                    "skipped_static": 0,
                    "errors": [f"Malformed JSON: {str(e)}"]
                }
        elif isinstance(har_data, dict):
            har_dict = har_data
        else:
            return {
                "endpoints": [],
                "total_entries": 0,
                "valid_entries": 0,
                "skipped_static": 0,
                "errors": ["Input must be a valid JSON string or dictionary"]
            }

        log = har_dict.get("log")
        if isinstance(log, dict) and isinstance(log.get("entries"), list):
            entries = log.get("entries")
        elif isinstance(har_dict.get("entries"), list):
            entries = har_dict.get("entries")
        else:
            return {
                "endpoints": [],
                "total_entries": 0,
                "valid_entries": 0,
                "skipped_static": 0,
                "errors": ["Missing or invalid 'log.entries' or 'entries' array in traffic data"]
            }

        total_entries = len(entries)
        valid_entries = 0
        skipped_static = 0
        endpoint_map: Dict[tuple, Dict[str, Any]] = {}

        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"Entry {idx} is not an object; skipped.")
                continue

            request = entry.get("request")
            if not isinstance(request, dict):
                errors.append(f"Entry {idx} missing 'request' object; skipped.")
                continue

            raw_url = request.get("url")
            method = request.get("method")
            if not raw_url or not method:
                errors.append(f"Entry {idx} missing 'url' or 'method'; skipped.")
                continue

            method = str(method).strip().upper()

            # Parse URL
            try:
                parsed_url = urllib.parse.urlsplit(raw_url)
            except Exception as e:
                errors.append(f"Entry {idx} failed to parse URL '{raw_url}': {str(e)}")
                continue

            # Target host filtering (if specified)
            if self.target_host and parsed_url.netloc:
                if parsed_url.netloc.lower() != self.target_host:
                    continue

            path = parsed_url.path or "/"

            # Ignore static assets
            if is_static_asset(path):
                skipped_static += 1
                continue

            normalized_path = normalize_path(path)

            # 1. Extract and sanitize query parameters
            params: Dict[str, Any] = {}
            query_items = request.get("queryString", [])
            if isinstance(query_items, list):
                for q in query_items:
                    if isinstance(q, dict) and "name" in q:
                        q_name = q.get("name")
                        q_val = q.get("value", "")
                        params[q_name] = redact_sensitive_value(q_name, q_val)

            # Fallback query parsing from URL if queryString was empty
            if not params and parsed_url.query:
                parsed_qs = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
                for q_name, q_vals in parsed_qs.items():
                    val = q_vals[0] if q_vals else ""
                    params[q_name] = redact_sensitive_value(q_name, val)

            # 2. Extract and sanitize JSON request body
            post_data = request.get("postData")
            if isinstance(post_data, dict):
                mime = post_data.get("mimeType", "")
                text = post_data.get("text", "")
                if "application/json" in mime or (text and text.strip().startswith(("{", "["))):
                    try:
                        body_json = json.loads(text)
                        if isinstance(body_json, dict):
                            for b_key, b_val in body_json.items():
                                params[b_key] = redact_sensitive_value(b_key, b_val)
                    except Exception:
                        pass
                elif "application/x-www-form-urlencoded" in mime and text:
                    try:
                        form_data = urllib.parse.parse_qs(text, keep_blank_values=True)
                        for f_key, f_vals in form_data.items():
                            val = f_vals[0] if f_vals else ""
                            params[f_key] = redact_sensitive_value(f_key, val)
                    except Exception:
                        pass

            # 3. Sanitize request headers
            req_headers = request.get("headers", [])
            sanitized_headers = sanitize_headers(req_headers) if isinstance(req_headers, list) else []

            # 4. Extract response metadata and timestamps
            response = entry.get("response", {})
            status_code = response.get("status") if isinstance(response, dict) else None
            response_headers = response.get("headers", []) if isinstance(response, dict) else []
            sanitized_resp_headers = sanitize_headers(response_headers) if isinstance(response_headers, list) else []

            entry_ts_raw = entry.get("startedDateTime")
            entry_ts = parse_har_timestamp(entry_ts_raw)

            key = (method, normalized_path)
            valid_entries += 1

            if key not in endpoint_map:
                endpoint_map[key] = {
                    "path": normalized_path,
                    "method": method,
                    "params": params,
                    "headers": sanitized_headers,
                    "response_status": status_code,
                    "response_headers": sanitized_resp_headers,
                    "sample_url": raw_url,
                    "occurrences": 1,
                    "first_seen": entry_ts,
                    "last_seen": entry_ts
                }
            else:
                # Merge newly observed parameters
                for p_key, p_val in params.items():
                    if p_key not in endpoint_map[key]["params"]:
                        endpoint_map[key]["params"][p_key] = p_val
                endpoint_map[key]["occurrences"] += 1
                # Track earliest first_seen and latest last_seen within HAR
                if entry_ts:
                    cur_first = endpoint_map[key].get("first_seen")
                    if not cur_first or entry_ts < cur_first:
                        endpoint_map[key]["first_seen"] = entry_ts
                    cur_last = endpoint_map[key].get("last_seen")
                    if not cur_last or entry_ts > cur_last:
                        endpoint_map[key]["last_seen"] = entry_ts

        return {
            "endpoints": list(endpoint_map.values()),
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "skipped_static": skipped_static,
            "errors": errors
        }


def parse_har(har_data: Union[str, Dict[str, Any]], target_host: Optional[str] = None) -> Dict[str, Any]:
    """Helper functional wrapper for HARParser."""
    parser = HARParser(target_host=target_host)
    return parser.parse(har_data)


def parse_har_traffic(har_data: Union[str, Dict[str, Any]], target_host: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience backward-compatible function to parse HAR data and return a list of classified endpoint dicts.
    """
    parser = HARParser(target_host=target_host)
    result = parser.parse(har_data)
    try:
        from .discovery import APIClassifier
    except ImportError:
        from recon.discovery import APIClassifier
    classifier = APIClassifier()
    return classifier.batch_classify(result.get("endpoints", []))

