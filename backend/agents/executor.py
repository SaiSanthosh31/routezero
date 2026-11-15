import time
import requests
import json
from typing import Dict, Any
from agents.safety import SafetyGuard

class ExploitExecutor:
    def __init__(self, base_url: str = "http://127.0.0.1:8001", safety_guard: SafetyGuard = None):
        self.base_url = base_url.rstrip("/")
        self.safety = safety_guard or SafetyGuard(allowed_hosts=["127.0.0.1:8001", "localhost:8001"])

    def execute(self, attack: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a planned attack safely and returns execution results with raw proof.
        Passes all safety guardrails: scope check, rate limiting, and request auditing.
        """
        target_url = f"{self.base_url}{attack['path']}"
        
        # 1. Safety Guardrail: Scope Check & Kill Switch
        is_safe, reason = self.safety.is_safe_to_execute(target_url)
        if not is_safe:
            return {"success": False, "error": reason, "curl_cmd": ""}

        time.sleep(self.safety.rate_limit_delay) # Rate limit discipline

        method = attack["method"].upper()
        headers = attack.get("headers", {})
        payload = attack.get("payload")

        # Format curl command for reproduction
        curl_cmd = f"curl -X {method} '{target_url}'"
        for k, v in headers.items():
            curl_cmd += f" -H '{k}: {v}'"
        if payload is not None:
            curl_cmd += f" -d '{json.dumps(payload)}'"

        start_time = time.time()
        try:
            if method == "GET":
                res = requests.get(target_url, headers=headers, timeout=5)
            elif method == "POST":
                res = requests.post(target_url, headers=headers, json=payload, timeout=5)
            elif method == "PUT":
                res = requests.put(target_url, headers=headers, json=payload, timeout=5)
            elif method == "DELETE":
                res = requests.delete(target_url, headers=headers, timeout=5)
            else:
                return {"status": "error", "message": f"Unsupported method {method}"}

            duration_ms = round((time.time() - start_time) * 1000, 2)

            # 2. Safety Guardrail: Audit Log
            self.safety.log_request(method, target_url, headers, payload, res.status_code)

            try:
                res_body = res.json()
            except Exception:
                res_body = res.text

            return {
                "success": True,
                "status_code": res.status_code,
                "duration_ms": duration_ms,
                "curl_cmd": curl_cmd,
                "request_headers": headers,
                "request_body": payload,
                "response_body": res_body,
                "raw_response_text": res.text
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "curl_cmd": curl_cmd
            }
