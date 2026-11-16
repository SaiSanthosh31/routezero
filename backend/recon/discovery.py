from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set, Tuple


def _parse_iso_or_clf(ts_val: Any) -> Optional[datetime]:
    """Helper to parse timestamps from SQLite or log metadata into UTC datetime."""
    if not ts_val:
        return None
    if isinstance(ts_val, datetime):
        return ts_val if ts_val.tzinfo else ts_val.replace(tzinfo=timezone.utc)
    ts_str = str(ts_val).strip()
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%d/%b/%Y:%H:%M:%S %z",
        "%d/%b/%Y:%H:%M:%S",
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(ts_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue
    return None


class APIClassifier:
    """
    Evidence-based classifier for active, zombie, and shadow APIs.
    
    Guiding Principles:
    1. Shadow APIs: Identified by comparing traffic endpoints against a documented registry.
       An endpoint is NEVER classified as confirmed shadow solely due to keywords like /admin/ or /internal/.
    2. Zombie APIs: Identified only when route inventory, deprecation flags, or historical traffic data
       indicate the endpoint is obsolete/deprecated. An endpoint is NEVER confirmed zombie merely for /v1/
       without deprecation evidence or sustained historical inactivity beyond a configured threshold.
    3. Safe Defaults: Where evidence is insufficient, category defaults to 'active', with candidate/reason
       annotations preserved in classification_details.
    4. Historical Route Telemetry: Inactivity threshold evaluated against first_seen, last_seen, and
       historical request counts to flag candidate obsolete routes without deleting historical data.
    """

    def __init__(
        self,
        documented_registry: Optional[List[Dict[str, str]]] = None,
        deprecated_inventory: Optional[List[Dict[str, str]]] = None,
        historical_traffic: Optional[Dict[Any, Dict[str, Any]]] = None,
        inactivity_threshold_days: int = 90,
        reference_time: Optional[datetime] = None
    ):
        # Set of normalized (METHOD, PATH) tuples for fast lookup
        self.documented_endpoints: Set[Tuple[str, str]] = set()
        if documented_registry:
            for item in documented_registry:
                m = item.get("method", "GET").upper()
                p = item.get("path", "")
                if p:
                    self.documented_endpoints.add((m, p))

        self.deprecated_endpoints: Set[Tuple[str, str]] = set()
        if deprecated_inventory:
            for item in deprecated_inventory:
                m = item.get("method", "GET").upper()
                p = item.get("path", "")
                if p:
                    self.deprecated_endpoints.add((m, p))

        # historical_traffic: map of (METHOD, PATH) -> telemetry dict
        # Supports keys as (METHOD, PATH) tuple or string "METHOD PATH"
        self.historical_traffic: Dict[Tuple[str, str], Dict[str, Any]] = {}
        if historical_traffic:
            for k, v in historical_traffic.items():
                if isinstance(k, tuple) and len(k) == 2:
                    self.historical_traffic[(k[0].upper(), k[1])] = v
                elif isinstance(k, str) and " " in k:
                    parts = k.split(" ", 1)
                    self.historical_traffic[(parts[0].upper(), parts[1])] = v

        self.inactivity_threshold_days = max(1, int(inactivity_threshold_days))
        self.reference_time = reference_time or datetime.now(timezone.utc)

    def classify_endpoint(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifies a single endpoint dictionary.
        Returns a dictionary with:
        - path: str
        - method: str
        - category: 'active' | 'zombie' | 'shadow'
        - params: dict
        - classification_details: dict with confidence, reason, evidence, telemetry
        """
        path = endpoint.get("path", "")
        method = endpoint.get("method", "GET").upper()
        params = endpoint.get("params", {})
        headers = endpoint.get("response_headers", [])
        
        ep_key = (method, path)
        path_lower = path.lower()

        evidence: List[str] = []
        category = "active"
        confidence = "normal"
        is_candidate = False
        suggested_category: Optional[str] = None
        reason = "Normal active production endpoint."

        # Check for response deprecation headers (RFC 8594 Sunset / Deprecation headers)
        has_sunset_header = False
        if headers:
            for h in headers:
                h_name = h.get("name", "").lower()
                if h_name in ("deprecation", "sunset"):
                    has_sunset_header = True
                    evidence.append(f"HTTP response header '{h_name}: {h.get('value')}' detected.")

        # Telemetry evaluation
        telemetry = self.historical_traffic.get(ep_key) or {}
        last_seen_dt = _parse_iso_or_clf(endpoint.get("last_seen") or telemetry.get("last_seen"))
        inactivity_days = None
        if last_seen_dt:
            inactivity_days = max(0, (self.reference_time - last_seen_dt).days)

        # -------------------------------------------------------------
        # 1. ZOMBIE / OBSOLESCENCE API EVALUATION
        # -------------------------------------------------------------
        if ep_key in self.deprecated_endpoints:
            category = "zombie"
            confidence = "confirmed"
            evidence.append("Endpoint listed in deprecated/sunset route inventory.")
            reason = "Confirmed zombie API: listed in decommissioned route inventory."
        elif has_sunset_header:
            category = "zombie"
            confidence = "confirmed"
            evidence.append("Confirmed zombie API via HTTP Sunset/Deprecation response header.")
            reason = "Endpoint response explicitly signals deprecation/sunset."
        elif telemetry.get("is_retired"):
            category = "zombie"
            confidence = "confirmed"
            evidence.append("Historical traffic telemetry marks this route as retired.")
            reason = "Confirmed zombie API: historical traffic tracking confirms deprecation."
        elif inactivity_days is not None and inactivity_days >= self.inactivity_threshold_days:
            # Endpoint has sustained inactivity beyond threshold
            req_count = telemetry.get("request_count", endpoint.get("occurrences", 1))
            if "/v1/" in path_lower or "legacy" in path_lower:
                category = "zombie"
                confidence = "confirmed"
                evidence.append(
                    f"Legacy endpoint with historical traffic ({req_count} requests) inactive for "
                    f"{inactivity_days} days (threshold: {self.inactivity_threshold_days} days)."
                )
                reason = f"Confirmed obsolete zombie API: inactive for {inactivity_days} days."
            else:
                is_candidate = True
                suggested_category = "zombie"
                evidence.append(
                    f"Route inactive for {inactivity_days} days (threshold: {self.inactivity_threshold_days} days). "
                    f"Historical observations: {req_count} requests."
                )
                reason = f"Candidate obsolete route: inactive for {inactivity_days} days beyond threshold."
        elif "/v1/" in path_lower or "legacy" in path_lower:
            # Insufficient evidence to mark confirmed zombie without deprecation registry or inactivity
            is_candidate = True
            suggested_category = "zombie"
            reason = "Candidate zombie API: Contains legacy route pattern, but awaiting historical traffic confirmation."
            evidence.append("Legacy path prefix observed without deprecation registry entry.")

        # -------------------------------------------------------------
        # 2. SHADOW API EVALUATION
        # -------------------------------------------------------------
        # Only evaluate shadow if not already confirmed zombie
        if category != "zombie":
            registry_available = len(self.documented_endpoints) > 0
            is_internal_pattern = any(x in path_lower for x in ("/internal/", "/admin/", "/debug/", "/private/"))

            if registry_available:
                if ep_key not in self.documented_endpoints:
                    category = "shadow"
                    if is_internal_pattern:
                        confidence = "confirmed"
                        evidence.append("Missing from documented OpenAPI catalog AND matches internal/admin route pattern.")
                        reason = "Confirmed shadow API: undocumented internal route detected in traffic."
                    else:
                        confidence = "high"
                        evidence.append("Observed in network traffic but absent from official documented catalog.")
                        reason = "Shadow API: undocumented route absent from API catalog."
                else:
                    # Documented route is legitimate
                    category = "active"
                    reason = "Verified documented route."
            else:
                # No documented registry provided for comparison
                # Preserve existing shadow classification unless official catalog proves it is legitimate
                existing_cat = str(telemetry.get("category", "")).lower()
                if existing_cat == "shadow":
                    category = "shadow"
                    confidence = "confirmed"
                    reason = "Preserved shadow classification: route remains absent from documented API catalog."
                    evidence.append("Preserved historical shadow API classification.")
                elif is_internal_pattern:
                    is_candidate = True
                    suggested_category = "shadow"
                    reason = "Candidate shadow API: Matches internal/admin pattern, but no documented catalog provided to confirm unmapped status."
                    evidence.append("Route matches administrative pattern; catalog comparison required for confirmation.")

        return {
            "path": path,
            "method": method,
            "category": category,
            "params": params,
            "first_seen": endpoint.get("first_seen") or telemetry.get("first_seen"),
            "last_seen": endpoint.get("last_seen") or telemetry.get("last_seen"),
            "occurrences": endpoint.get("occurrences", 1),
            "request_count": telemetry.get("request_count", endpoint.get("occurrences", 1)),
            "classification_details": {
                "category": category,
                "confidence": confidence,
                "is_candidate": is_candidate,
                "suggested_category": suggested_category,
                "reason": reason,
                "evidence": evidence,
                "inactivity_days": inactivity_days
            }
        }

    def batch_classify(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classifies a list of parsed endpoints."""
        return [self.classify_endpoint(ep) for ep in endpoints]


def classify_endpoints(
    endpoints: List[Dict[str, Any]],
    documented_registry: Optional[List[Dict[str, str]]] = None,
    deprecated_inventory: Optional[List[Dict[str, str]]] = None,
    historical_traffic: Optional[Dict[Any, Dict[str, Any]]] = None,
    inactivity_threshold_days: int = 90,
    reference_time: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Helper functional wrapper for APIClassifier."""
    classifier = APIClassifier(
        documented_registry=documented_registry,
        deprecated_inventory=deprecated_inventory,
        historical_traffic=historical_traffic,
        inactivity_threshold_days=inactivity_threshold_days,
        reference_time=reference_time
    )
    return classifier.batch_classify(endpoints)
