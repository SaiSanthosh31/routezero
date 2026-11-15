import json
from typing import List, Dict, Any

def parse_har_traffic(har_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parses a HAR (HTTP Archive) JSON structure and extracts discovered endpoints,
    methods, query parameters, request bodies, and response codes.
    """
    endpoints = []
    seen = set()

    entries = har_data.get("log", {}).get("entries", [])
    for entry in entries:
        req = entry.get("request", {})
        res = entry.get("response", {})
        url = req.get("url", "")
        method = req.get("method", "GET").upper()

        # Extract relative path from URL
        path = "/" + "/".join(url.split("://")[-1].split("/")[1:]) if "://" in url else url
        path = path.split("?")[0] # remove query params from base path

        if not path or path in seen:
            continue

        seen.add(path)

        # Detect category based on route pattern and response
        category = "active"
        if "/v1/" in path or "legacy" in path or "old" in path:
            category = "zombie"
        elif "/internal/" in path or "admin" in path or "debug" in path or "stats" in path:
            category = "shadow"

        # Extract parameters
        query_params = {q.get("name"): q.get("value") for q in req.get("queryString", [])}
        
        # Extract body schema
        body_params = {}
        post_data = req.get("postData", {})
        if post_data.get("mimeType") == "application/json":
            try:
                body_json = json.loads(post_data.get("text", "{}"))
                if isinstance(body_json, dict):
                    body_params = {k: type(v).__name__ for k, v in body_json.items()}
            except Exception:
                pass

        merged_params = {**query_params, **body_params}

        endpoints.append({
            "path": path,
            "method": method,
            "category": category,
            "params": merged_params,
            "response_status": res.get("status", 200)
        })

    return endpoints
