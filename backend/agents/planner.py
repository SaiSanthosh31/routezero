import os
import json
from typing import List, Dict

class AttackPlanner:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY")

    def plan_attacks(self, endpoint: Dict) -> List[Dict]:
        """
        Takes an endpoint dict:
        {"path": "/api/v2/bookings/create", "method": "POST", "category": "active", "params": {...}}
        Returns a list of targeted attack test cases.
        """
        path = endpoint.get("path", "")
        method = endpoint.get("method", "GET").upper()
        attacks = []

        # 1. Price / Parameter Tampering Detection
        if method == "POST" and ("booking" in path.lower() or "pay" in path.lower() or "cart" in path.lower()):
            attacks.append({
                "type": "PRICE_TAMPERING",
                "name": "Zero/Manipulated Fare Exploit",
                "method": "POST",
                "path": path,
                "payload": {
                    "agency_id": "AGENCY-001",
                    "flight_number": "AI-202",
                    "passenger_name": "Attacker Test",
                    "passport_no": "X0000000",
                    "price": 1.0  # Intentional tampering: normal is $450-$1200
                },
                "headers": {"Content-Type": "application/json"},
                "expected_vulnerability_condition": "status == 200 and price == 1.0"
            })

        # 2. Insecure Direct Object Reference (IDOR)
        if method == "GET" and ("booking" in path.lower() or "order" in path.lower() or "invoice" in path.lower()):
            test_path = path.replace("{booking_id}", "BK-1001").replace("{id}", "BK-1001")
            if "{" not in test_path:
                if not test_path.endswith("BK-1001") and "search" not in test_path:
                    test_path = f"{test_path.rstrip('/')}/BK-1001"
            
            attacks.append({
                "type": "IDOR_CROSS_TENANT",
                "name": "Cross-Agency Booking IDOR & PII Exfiltration",
                "method": "GET",
                "path": test_path,
                "payload": None,
                "headers": {"X-Agency-Id": "AGENCY-002"}, # Agency 2 attempting to view Agency 1's booking
                "expected_vulnerability_condition": "status == 200 and 'BK-1001' in response and 'AGENCY-001' in response"
            })

        # 3. Zombie API Exploitation
        if "v1" in path.lower() or "legacy" in path.lower() or "old" in path.lower():
            attacks.append({
                "type": "ZOMBIE_API_EXPOSURE",
                "name": "Deprecated Unauthenticated Promo Leak",
                "method": method,
                "path": path,
                "payload": None,
                "headers": {},
                "expected_vulnerability_condition": "status == 200 and 'SECRET' in response"
            })

        # 4. Shadow / Internal API Exposure
        if "internal" in path.lower() or "admin" in path.lower() or "stats" in path.lower():
            attacks.append({
                "type": "SHADOW_API_UNPROTECTED",
                "name": "Unauthenticated Sensitive Admin Telemetry Leak",
                "method": method,
                "path": path,
                "payload": None,
                "headers": {},
                "expected_vulnerability_condition": "status == 200 and 'environment' in response"
            })

        # 5. Logic Flaw - Duplicate Refund
        if "refund" in path.lower():
            attacks.append({
                "type": "LOGIC_DUPLICATE_REFUND",
                "name": "Unchecked Double Refund Execution",
                "method": "POST",
                "path": path,
                "payload": {"booking_id": "BK-1002", "amount": 850.0},
                "headers": {"Content-Type": "application/json"},
                "expected_vulnerability_condition": "status == 200 and 'REFUNDED' in response"
            })

        return attacks
