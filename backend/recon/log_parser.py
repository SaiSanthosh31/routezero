import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Tuple

from recon.har_parser import (
    normalize_path,
    is_static_asset,
    redact_sensitive_value,
    sanitize_headers
)

# Regex matching Common Log Format (CLF) and Combined Log Format (Nginx & Apache)
APACHE_NGINX_REGEX = re.compile(
    r'^(\S+)\s+\S+\s+\S+\s+\[([^\]]+)\]\s+"([A-Za-z]+)\s+([^"\s]+)(?:\s+HTTP\/[0-9.]+)?(?:")\s+(\d{3})\s+(\d+|-)(?:\s+"([^"]*)"\s+"([^"]*)")?',
    re.IGNORECASE
)

# Common HTTP log timestamp formats
TIMESTAMP_FORMATS = [
    "%d/%b/%Y:%H:%M:%S %z",
    "%d/%b/%Y:%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%d %H:%M:%S",
]

def parse_log_timestamp(ts_str: Optional[str]) -> Optional[str]:
    """Attempts to parse diverse log timestamps into normalized ISO 8601 UTC format."""
    if not ts_str or not isinstance(ts_str, str):
        return None
    ts_clean = ts_str.strip()
    for fmt in TIMESTAMP_FORMATS:
        try:
            dt = datetime.strptime(ts_clean, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
    # Fallback to stripped original string
    return ts_clean


def detect_log_format(content: str) -> str:
    """
    Automatically detects the log format (har, ndjson, nginx/apache, or unknown).
    """
    if not content or not isinstance(content, str):
        return "unknown"
    
    trimmed = content.strip()
    if not trimmed:
        return "unknown"

    # Check for HAR JSON
    if trimmed.startswith("{"):
        try:
            parsed = json.loads(trimmed)
            if isinstance(parsed, dict) and "log" in parsed:
                return "har"
        except Exception:
            pass

    # Inspect first non-empty lines
    lines = [l.strip() for l in trimmed.splitlines() if l.strip()]
    if not lines:
        return "unknown"

    first_line = lines[0]

    # Check if first line is NDJSON (starts with { and parses as JSON object)
    if first_line.startswith("{"):
        try:
            json_obj = json.loads(first_line)
            if isinstance(json_obj, dict):
                return "ndjson"
        except Exception:
            pass

    # Check for Nginx / Apache Common or Combined
    if APACHE_NGINX_REGEX.match(first_line):
        return "nginx" # Standard CLF/Combined format used by Nginx & Apache

    # Fallback check across top 5 lines
    for line in lines[:5]:
        if APACHE_NGINX_REGEX.match(line):
            return "nginx"
        if line.startswith("{"):
            try:
                if isinstance(json.loads(line), dict):
                    return "ndjson"
            except Exception:
                pass

    return "unknown"


class LogParser:
    """
    Parses Nginx access logs, Apache access logs, and NDJSON request streams.
    Normalizes routes into the RouteZero endpoint data model.
    """

    def __init__(self, target_host: Optional[str] = None):
        self.target_host = target_host.lower() if target_host else None

    def parse(self, raw_logs: str, log_format: Optional[str] = None) -> Dict[str, Any]:
        """
        Parses raw log text into normalized RouteZero endpoint objects.
        """
        if not raw_logs or not isinstance(raw_logs, str):
            return {
                "format_detected": "unknown",
                "endpoints": [],
                "total_lines": 0,
                "valid_entries": 0,
                "skipped_static": 0,
                "skipped_malformed": 0,
                "errors": ["Input must be a non-empty string"]
            }

        detected_fmt = (log_format or detect_log_format(raw_logs)).lower()
        if detected_fmt in ("apache", "clf", "combined"):
            detected_fmt = "nginx"

        lines = raw_logs.splitlines()
        total_lines = len(lines)
        valid_entries = 0
        skipped_static = 0
        skipped_malformed = 0
        errors: List[str] = []

        endpoint_map: Dict[Tuple[str, str], Dict[str, Any]] = {}

        for line_no, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if not line:
                continue

            parsed_entry: Optional[Dict[str, Any]] = None

            if detected_fmt == "ndjson":
                parsed_entry = self._parse_ndjson_line(line, line_no, errors)
            elif detected_fmt == "nginx":
                parsed_entry = self._parse_clf_line(line, line_no, errors)
            else:
                # Try NDJSON first, then CLF
                if line.startswith("{"):
                    parsed_entry = self._parse_ndjson_line(line, line_no, errors)
                if not parsed_entry:
                    parsed_entry = self._parse_clf_line(line, line_no, errors)
                if parsed_entry:
                    detected_fmt = "ndjson" if line.startswith("{") else "nginx"

            if not parsed_entry:
                skipped_malformed += 1
                continue

            path = parsed_entry["path"]
            method = parsed_entry["method"]
            params = parsed_entry["params"]
            status_code = parsed_entry.get("status")
            ts = parsed_entry.get("timestamp")

            # Static asset filtering
            if is_static_asset(path):
                skipped_static += 1
                continue

            normalized_path = normalize_path(path)
            key = (method, normalized_path)
            valid_entries += 1

            if key not in endpoint_map:
                endpoint_map[key] = {
                    "path": normalized_path,
                    "method": method,
                    "params": params,
                    "response_status": status_code,
                    "first_seen": ts,
                    "last_seen": ts,
                    "occurrences": 1,
                    "sample_url": parsed_entry.get("raw_url", path)
                }
            else:
                ep = endpoint_map[key]
                ep["occurrences"] += 1
                # Merge query/body parameters
                for p_key, p_val in params.items():
                    if p_key not in ep["params"]:
                        ep["params"][p_key] = p_val
                # Update latest last_seen timestamp
                if ts:
                    ep["last_seen"] = ts
                if status_code:
                    ep["response_status"] = status_code

        return {
            "format_detected": detected_fmt if detected_fmt != "unknown" else "unrecognized",
            "endpoints": list(endpoint_map.values()),
            "total_lines": total_lines,
            "valid_entries": valid_entries,
            "skipped_static": skipped_static,
            "skipped_malformed": skipped_malformed,
            "errors": errors[:50] # Keep errors bounded
        }

    def _parse_clf_line(self, line: str, line_no: int, errors: List[str]) -> Optional[Dict[str, Any]]:
        """Parses Common / Combined Log Format line (Nginx / Apache)."""
        match = APACHE_NGINX_REGEX.match(line)
        if not match:
            errors.append(f"Line {line_no}: does not match Nginx/Apache CLF format")
            return None

        ip, ts_raw, method_raw, raw_url, status_str, size_str, referer, user_agent = (
            match.group(1), match.group(2), match.group(3), match.group(4),
            match.group(5), match.group(6), match.group(7), match.group(8)
        )

        method = method_raw.strip().upper()
        try:
            parsed_url = urllib.parse.urlsplit(raw_url)
        except Exception as e:
            errors.append(f"Line {line_no}: failed to parse URL '{raw_url}': {str(e)}")
            return None

        if self.target_host and parsed_url.netloc:
            if parsed_url.netloc.lower() != self.target_host:
                return None

        path = parsed_url.path or "/"

        params: Dict[str, Any] = {}
        if parsed_url.query:
            parsed_qs = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
            for q_name, q_vals in parsed_qs.items():
                val = q_vals[0] if q_vals else ""
                params[q_name] = redact_sensitive_value(q_name, val)

        status_code = int(status_str) if status_str and status_str.isdigit() else None
        iso_timestamp = parse_log_timestamp(ts_raw)

        return {
            "method": method,
            "path": path,
            "params": params,
            "status": status_code,
            "timestamp": iso_timestamp,
            "raw_url": raw_url,
            "client_ip": ip,
            "referer": referer,
            "user_agent": user_agent
        }

    def _parse_ndjson_line(self, line: str, line_no: int, errors: List[str]) -> Optional[Dict[str, Any]]:
        """Parses a single NDJSON log entry."""
        try:
            entry = json.loads(line)
        except Exception as e:
            errors.append(f"Line {line_no}: invalid JSON in NDJSON line: {str(e)}")
            return None

        if not isinstance(entry, dict):
            errors.append(f"Line {line_no}: NDJSON line is not a JSON object")
            return None

        # Extract HTTP method
        method_raw = (
            entry.get("method") or entry.get("http_method") or
            entry.get("request_method") or "GET"
        )
        method = str(method_raw).strip().upper()

        # Extract URL or Path
        raw_url = (
            entry.get("url") or entry.get("path") or entry.get("uri") or
            entry.get("request_uri") or "/"
        )
        try:
            parsed_url = urllib.parse.urlsplit(str(raw_url))
        except Exception as e:
            errors.append(f"Line {line_no}: failed to parse URL '{raw_url}': {str(e)}")
            return None

        if self.target_host and parsed_url.netloc:
            if parsed_url.netloc.lower() != self.target_host:
                return None

        path = parsed_url.path or "/"

        # Extract parameters: from query, params, or URL query string
        params: Dict[str, Any] = {}
        if parsed_url.query:
            parsed_qs = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
            for q_name, q_vals in parsed_qs.items():
                val = q_vals[0] if q_vals else ""
                params[q_name] = redact_sensitive_value(q_name, val)

        # Merge explicit query dict
        explicit_query = entry.get("query") or entry.get("query_params")
        if isinstance(explicit_query, dict):
            for k, v in explicit_query.items():
                params[k] = redact_sensitive_value(k, v)

        # Merge body / post_data dict
        body_data = entry.get("body") or entry.get("post_data") or entry.get("params")
        if isinstance(body_data, dict):
            for k, v in body_data.items():
                params[k] = redact_sensitive_value(k, v)
        elif isinstance(body_data, str) and body_data.strip().startswith("{"):
            try:
                body_json = json.loads(body_data)
                if isinstance(body_json, dict):
                    for k, v in body_json.items():
                        params[k] = redact_sensitive_value(k, v)
            except Exception:
                pass

        # Status code
        status_raw = entry.get("status") or entry.get("status_code") or entry.get("response_status")
        status_code = None
        if status_raw is not None:
            try:
                status_code = int(status_raw)
            except Exception:
                pass

        # Timestamp
        ts_raw = (
            entry.get("timestamp") or entry.get("time") or
            entry.get("datetime") or entry.get("@timestamp")
        )
        iso_timestamp = parse_log_timestamp(str(ts_raw)) if ts_raw else None

        return {
            "method": method,
            "path": path,
            "params": params,
            "status": status_code,
            "timestamp": iso_timestamp,
            "raw_url": str(raw_url)
        }


def parse_raw_logs(raw_logs: str, log_format: Optional[str] = None) -> Dict[str, Any]:
    """Functional wrapper for LogParser."""
    parser = LogParser()
    return parser.parse(raw_logs, log_format=log_format)
