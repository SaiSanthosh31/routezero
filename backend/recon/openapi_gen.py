import json
from typing import List, Dict

def generate_openapi_spec(endpoints: List[Dict]) -> Dict:
    """
    Transforms inferred active, zombie, and shadow endpoints into a valid OpenAPI 3.0.0 specification.
    """
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "RouteZero Inferred API Catalog (TBO Travel Platform)",
            "version": "1.0.0",
            "description": "Auto-generated OpenAPI specification inferred via RouteZero Autonomous DAST Reconnaissance."
        },
        "servers": [
            {"url": "http://127.0.0.1:8001", "description": "TBO Staging Environment"}
        ],
        "paths": {}
    }

    for ep in endpoints:
        path = ep["path"]
        method = ep["method"].lower()
        category = ep.get("category", "active").upper()

        if path not in spec["paths"]:
            spec["paths"][path] = {}

        summary = f"[{category}] Inferred {ep['method']} {path}"
        description = f"Endpoint discovered automatically. Status category: {category}."
        if category == "ZOMBIE":
            description += " WARNING: Deprecated legacy route. Recommend immediate decommissioning."
        elif category == "SHADOW":
            description += " ALERT: Unmapped internal route discovered without access governance."

        operation = {
            "summary": summary,
            "description": description,
            "tags": [category],
            "responses": {
                "200": {
                    "description": "Successful response"
                }
            }
        }

        # Add parameters or request body if available
        params = ep.get("params")
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except Exception:
                params = {}

        if method == "get" and params:
            operation["parameters"] = [
                {
                    "name": k,
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"}
                }
                for k in params.keys()
            ]
        elif method in ["post", "put"] and params:
            operation["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {k: {"type": "string"} for k in params.keys()}
                        }
                    }
                }
            }

        spec["paths"][path][method] = operation

    return spec
