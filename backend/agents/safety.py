import urllib.parse
import time
from typing import Dict, Optional

class SafetyGuard:
    def __init__(self, allowed_hosts: list = None):
        self.allowed_hosts = allowed_hosts or ["127.0.0.1:8001", "localhost:8001"]
        self.kill_switch_active = False
        self.rate_limit_delay = 0.25 # seconds
        self.test_credentials = {
            "agency_alpha": {"agency_id": "AGENCY-001", "token": "Bearer tok_alpha_111"},
            "agency_beta":  {"agency_id": "AGENCY-002", "token": "Bearer tok_beta_222"},
            "admin":        {"agency_id": "ADMIN-ROOT",  "token": "Bearer tok_admin_999"},
        }
        self.audit_log = []

    def check_scope(self, url: str) -> bool:
        """Ensures the agent NEVER sends payloads to unapproved external domains."""
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc
        if not netloc:
            # Relative path is considered safe within default target
            return True
        return netloc in self.allowed_hosts

    def log_request(self, method: str, url: str, headers: Dict, payload: Optional[Dict], status_code: int):
        entry = {
            "timestamp": time.time(),
            "method": method,
            "url": url,
            "headers": {k: v for k, v in headers.items() if k.lower() != "authorization"}, # mask auth
            "has_payload": payload is not None,
            "status_code": status_code
        }
        self.audit_log.append(entry)

    def is_safe_to_execute(self, url: str) -> (bool, str):
        if self.kill_switch_active:
            return False, "Execution blocked by Kill Switch."
        if not self.check_scope(url):
            return False, f"Target URL {url} is OUT OF SCOPE. Execution blocked."
        return True, "OK"
