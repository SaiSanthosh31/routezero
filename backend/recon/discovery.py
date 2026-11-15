from typing import Dict, List, Any, Optional, Set, Tuple


class APIClassifier:
    """
    Evidence-based classifier for active, zombie, and shadow APIs.
    
    Guiding Principles:
    1. Shadow APIs: Identified by comparing traffic endpoints against a documented registry.
       An endpoint is NEVER classified as confirmed shadow solely due to keywords like /admin/ or /internal/.
    2. Zombie APIs: Identified only when route inventory, deprecation flags, or historical traffic data
       indicate the endpoint is obsolete/deprecated. An endpoint is NEVER confirmed zombie merely for /v1/.
    3. Safe Defaults: Where evidence is insufficient, category defaults to 'active', with candidate/reason
       annotations preserved in classification_details.
    """

    def __init__(
        self,
        documented_registry: Optional[List[Dict[str, str]]] = None,
        deprecated_inventory: Optional[List[Dict[str, str]]] = None,
        historical_traffic: Optional[Dict[str, Any]] = None
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

        # historical_traffic e.g. {(METHOD, PATH): {"last_seen": ..., "is_retired": True}}
        self.historical_traffic = historical_traffic or {}

    def classify_endpoint(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifies a single endpoint dictionary.
        Returns a dictionary with:
        - path: str
        - method: str
        - category: 'active' | 'zombie' | 'shadow'
        - params: dict
        - classification_details: dict with confidence, reason, and evidence
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

        # -------------------------------------------------------------
        # 1. ZOMBIE API EVALUATION
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
        elif ep_key in self.historical_traffic and self.historical_traffic[ep_key].get("is_retired"):
            category = "zombie"
            confidence = "confirmed"
            evidence.append("Historical traffic telemetry marks this route as retired.")
            reason = "Confirmed zombie API: historical traffic tracking confirms deprecation."
        elif "/v1/" in path_lower or "legacy" in path_lower:
            # Insufficient evidence to mark confirmed zombie
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
                if is_internal_pattern:
                    is_candidate = True
                    suggested_category = "shadow"
                    reason = "Candidate shadow API: Matches internal/admin pattern, but no documented catalog provided to confirm unmapped status."
                    evidence.append("Route matches administrative pattern; catalog comparison required for confirmation.")

        return {
            "path": path,
            "method": method,
            "category": category,
            "params": params,
            "classification_details": {
                "category": category,
                "confidence": confidence,
                "is_candidate": is_candidate,
                "suggested_category": suggested_category,
                "reason": reason,
                "evidence": evidence
            }
        }

    def batch_classify(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classifies a list of parsed endpoints."""
        return [self.classify_endpoint(ep) for ep in endpoints]


def classify_endpoints(
    endpoints: List[Dict[str, Any]],
    documented_registry: Optional[List[Dict[str, str]]] = None,
    deprecated_inventory: Optional[List[Dict[str, str]]] = None,
    historical_traffic: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Helper functional wrapper for APIClassifier."""
    classifier = APIClassifier(
        documented_registry=documented_registry,
        deprecated_inventory=deprecated_inventory,
        historical_traffic=historical_traffic
    )
    return classifier.batch_classify(endpoints)
