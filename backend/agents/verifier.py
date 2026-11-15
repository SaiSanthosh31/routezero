import json
from typing import Dict, Any, Optional

class VerifierAgent:
    def verify(self, attack: Dict[str, Any], exec_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyzes the execution result to confirm if the vulnerability is genuine.
        Returns a verified finding dictionary or None if false positive.
        """
        if not exec_result.get("success"):
            return None

        status_code = exec_result.get("status_code", 0)
        res_body = exec_result.get("response_body", {})
        res_text = exec_result.get("raw_response_text", "")
        atk_type = attack["type"]

        # Case 1: Price Tampering
        if atk_type == "PRICE_TAMPERING":
            if status_code == 200 and isinstance(res_body, dict):
                booking = res_body.get("booking", {})
                if booking.get("price") == 1.0:
                    return {
                        "title": "Business Logic: Unchecked Booking Price Tampering",
                        "severity": "CRITICAL",
                        "cwe_id": "CWE-472 (Parameter Tampering)",
                        "owner": "@tbo-booking-core",
                        "vuln_type": "BUSINESS_LOGIC_TAMPERING",
                        "endpoint": attack["path"],
                        "method": attack["method"],
                        "description": "The endpoint accepts client-supplied pricing without server-side validation. An attacker can set flight/hotel booking prices to $1.00.",
                        "business_impact": "Direct financial revenue loss and fraudulent ticket issuance across TBO inventory.",
                        "remediation": "Do not accept client 'price' values. Recompute verified supplier pricing server-side based on flight_id and inventory fare rules before persistence.",
                        "remediation_code": "# FIX: Compute price server-side\nfare = flight_service.calculate_fare(req.flight_number)\nbooking.price = fare.total_amount",
                        "reproduction_curl": exec_result["curl_cmd"],
                        "proof_request": json.dumps(attack.get("payload", {}), indent=2),
                        "proof_response": json.dumps(res_body, indent=2),
                        "status": "CONFIRMED"
                    }

        # Case 2: Cross-Tenant IDOR + PII Leak
        if atk_type == "IDOR_CROSS_TENANT":
            if status_code == 200 and isinstance(res_body, dict):
                booking = res_body.get("booking", {})
                if booking.get("agency_id") == "AGENCY-001":
                    return {
                        "title": "Broken Object Level Authorization (IDOR) with PII Leak",
                        "severity": "CRITICAL",
                        "cwe_id": "CWE-862 (Missing Authorization)",
                        "owner": "@tbo-identity-team",
                        "vuln_type": "ACCESS_CONTROL_IDOR",
                        "endpoint": attack["path"],
                        "method": attack["method"],
                        "description": "Booking records are accessible across agency boundaries without tenancy verification. Passenger passport numbers and travel details are leaked.",
                        "business_impact": "Severe breach of India DPDP Act 2023. Passport details and passenger records exposed to unauthorized travel agencies.",
                        "remediation": "Enforce tenancy ownership check: Validate that the authenticated session agency_id strictly matches the booking owner agency_id.",
                        "remediation_code": "# FIX: Enforce tenant ownership barrier\nif booking.agency_id != authenticated_user.agency_id:\n    raise HTTPException(status_code=403, detail='Unauthorized tenant access')",
                        "reproduction_curl": exec_result["curl_cmd"],
                        "proof_request": f"Headers: {json.dumps(attack.get('headers', {}))}",
                        "proof_response": json.dumps(res_body, indent=2),
                        "status": "CONFIRMED"
                    }

        # Case 3: Zombie API Exposure
        if atk_type == "ZOMBIE_API_EXPOSURE":
            if status_code == 200 and "SECRET" in res_text:
                return {
                    "title": "Zombie Endpoint: Deprecated API Leaking Internal Discount Codes",
                    "severity": "HIGH",
                    "cwe_id": "CWE-668 (Exposure of Resource to Wrong Sphere)",
                    "owner": "@tbo-promotions",
                    "vuln_type": "ZOMBIE_API",
                    "endpoint": attack["path"],
                    "method": attack["method"],
                    "description": "Deprecated /v1 route is still alive in production staging and serves confidential 50% discount codes without authentication.",
                    "business_impact": "Margin erosion via unauthorized voucher extraction; unmonitored legacy attack surface.",
                    "remediation": "Decommission the deprecated /v1/ legacy controller and block route traffic at the API gateway layer.",
                    "remediation_code": "# FIX: Deprecate route and return 410 Gone\n@app.get('/api/v1/legacy/discounts')\ndef legacy_discount():\n    raise HTTPException(status_code=410, detail='Route decommissioned')",
                    "reproduction_curl": exec_result["curl_cmd"],
                    "proof_request": "GET /api/v1/legacy/discounts",
                    "proof_response": json.dumps(res_body, indent=2),
                    "status": "CONFIRMED"
                }

        # Case 4: Shadow API Exposure
        if atk_type == "SHADOW_API_UNPROTECTED":
            if status_code == 200 and "environment" in res_text:
                return {
                    "title": "Shadow Endpoint: Internal System Metrics & DB Connection String Exposed",
                    "severity": "HIGH",
                    "cwe_id": "CWE-200 (Information Disclosure)",
                    "owner": "@tbo-devops",
                    "vuln_type": "SHADOW_API",
                    "endpoint": attack["path"],
                    "method": attack["method"],
                    "description": "Undocumented /internal endpoint is publicly reachable and leaks database connection details and internal telemetry.",
                    "business_impact": "Internal architecture disclosure facilitating targeted lateral attacks and privilege escalation.",
                    "remediation": "Restrict /internal/* routes to private VPC ingress only. Require administrative mTLS or OAuth scopes.",
                    "remediation_code": "# FIX: Restrict to private VPC or admin scope\n@app.get('/api/v2/internal/admin/stats', dependencies=[Depends(require_admin_role)])",
                    "reproduction_curl": exec_result["curl_cmd"],
                    "proof_request": "GET /api/v2/internal/admin/stats",
                    "proof_response": json.dumps(res_body, indent=2),
                    "status": "CONFIRMED"
                }

        # Case 5: Duplicate Refund
        if atk_type == "LOGIC_DUPLICATE_REFUND":
            if status_code == 200 and "REFUNDED" in res_text:
                return {
                    "title": "Business Logic: Double Refund Without State Verification",
                    "severity": "HIGH",
                    "cwe_id": "CWE-840 (Business Logic Flaw)",
                    "owner": "@tbo-settlements",
                    "vuln_type": "BUSINESS_LOGIC_REFUND",
                    "endpoint": attack["path"],
                    "method": attack["method"],
                    "description": "Refund requests are processed repeatedly without checking whether the booking is already cancelled/refunded.",
                    "business_impact": "Financial loss through duplicate payout and unauthorized supplier escrow drain.",
                    "remediation": "Implement transactional state machine: verify booking status is not already 'REFUNDED' before initiating settlement.",
                    "remediation_code": "# FIX: Validate booking state before refund\nif booking.status == BookingStatus.REFUNDED:\n    raise HTTPException(status_code=400, detail='Booking already refunded')",
                    "reproduction_curl": exec_result["curl_cmd"],
                    "proof_request": json.dumps(attack.get("payload", {}), indent=2),
                    "proof_response": json.dumps(res_body, indent=2),
                    "status": "CONFIRMED"
                }

        return None
