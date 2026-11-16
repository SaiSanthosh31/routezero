import unittest
import json
import os
import sys
import tempfile
import sqlite3

# Ensure backend directory is in path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from recon.har_parser import (
    HARParser,
    normalize_path,
    is_static_asset,
    redact_sensitive_value,
    sanitize_headers
)
from recon.discovery import APIClassifier, classify_endpoints
import db.database as db_module


class TestHARParserAndDiscovery(unittest.TestCase):

    def setUp(self):
        self.parser = HARParser()

    # 1. Valid HAR parsing
    def test_valid_har_parsing(self):
        har_data = {
            "log": {
                "version": "1.2",
                "entries": [
                    {
                        "request": {
                            "method": "GET",
                            "url": "http://127.0.0.1:8001/api/v2/flights/search",
                            "queryString": [{"name": "origin", "value": "DEL"}],
                            "headers": [{"name": "Accept", "value": "application/json"}]
                        },
                        "response": {
                            "status": 200,
                            "headers": [{"name": "Content-Type", "value": "application/json"}]
                        }
                    }
                ]
            }
        }
        res = self.parser.parse(har_data)
        self.assertEqual(res["total_entries"], 1)
        self.assertEqual(res["valid_entries"], 1)
        self.assertEqual(len(res["endpoints"]), 1)
        ep = res["endpoints"][0]
        self.assertEqual(ep["method"], "GET")
        self.assertEqual(ep["path"], "/api/v2/flights/search")
        self.assertIn("origin", ep["params"])
        self.assertEqual(ep["params"]["origin"], "DEL")
        self.assertEqual(ep["response_status"], 200)

    # 2. Multiple HTTP methods
    def test_multiple_http_methods(self):
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        entries = []
        for m in methods:
            entries.append({
                "request": {
                    "method": m.lower(), # test lower to uppercase normalization
                    "url": f"http://127.0.0.1:8001/api/v2/resource_{m.lower()}"
                }
            })
        har_data = {"log": {"version": "1.2", "entries": entries}}
        res = self.parser.parse(har_data)
        parsed_methods = [ep["method"] for ep in res["endpoints"]]
        for m in methods:
            self.assertIn(m, parsed_methods)

    # 3. Query parameter extraction
    def test_query_parameter_extraction(self):
        har_data = {
            "log": {
                "version": "1.2",
                "entries": [
                    {
                        "request": {
                            "method": "GET",
                            "url": "http://127.0.0.1:8001/api/v2/flights?from=DEL&to=DXB",
                            "queryString": [
                                {"name": "from", "value": "DEL"},
                                {"name": "to", "value": "DXB"}
                            ]
                        }
                    }
                ]
            }
        }
        res = self.parser.parse(har_data)
        params = res["endpoints"][0]["params"]
        self.assertEqual(params.get("from"), "DEL")
        self.assertEqual(params.get("to"), "DXB")

    # 4. JSON request body extraction
    def test_json_request_body_extraction(self):
        har_data = {
            "log": {
                "version": "1.2",
                "entries": [
                    {
                        "request": {
                            "method": "POST",
                            "url": "http://127.0.0.1:8001/api/v2/bookings/create",
                            "postData": {
                                "mimeType": "application/json",
                                "text": json.dumps({"agency_id": "AGENCY-001", "price": 1200.5})
                            }
                        }
                    }
                ]
            }
        }
        res = self.parser.parse(har_data)
        params = res["endpoints"][0]["params"]
        self.assertEqual(params.get("agency_id"), "AGENCY-001")
        self.assertEqual(params.get("price"), 1200.5)

    # 5. Dynamic path normalization
    def test_dynamic_path_normalization(self):
        self.assertEqual(normalize_path("/api/v2/bookings/BK-1001"), "/api/v2/bookings/{booking_id}")
        self.assertEqual(normalize_path("/api/v2/refunds/RF-9988"), "/api/v2/refunds/{refund_id}")
        self.assertEqual(normalize_path("/api/v2/agencies/AGENCY-001"), "/api/v2/agencies/{agency_id}")
        self.assertEqual(normalize_path("/api/v2/users/12345"), "/api/v2/users/{user_id}")
        self.assertEqual(
            normalize_path("/api/v2/items/123e4567-e89b-12d3-a456-426614174000"),
            "/api/v2/items/{item_id}"
        )
        # Static path remains unchanged
        self.assertEqual(normalize_path("/api/v2/flights/search"), "/api/v2/flights/search")

    # 6. Static asset filtering
    def test_static_asset_filtering(self):
        self.assertTrue(is_static_asset("/static/app.js"))
        self.assertTrue(is_static_asset("/assets/style.css?v=2"))
        self.assertTrue(is_static_asset("/logo.svg"))
        self.assertTrue(is_static_asset("/favicon.ico"))
        self.assertTrue(is_static_asset("/hero.png"))
        self.assertFalse(is_static_asset("/api/v2/flights/search"))

        har_data = {
            "log": {
                "version": "1.2",
                "entries": [
                    {"request": {"method": "GET", "url": "http://example.com/bundle.js"}},
                    {"request": {"method": "GET", "url": "http://example.com/styles.css"}},
                    {"request": {"method": "GET", "url": "http://example.com/logo.png"}},
                    {"request": {"method": "GET", "url": "http://example.com/api/v2/data"}}
                ]
            }
        }
        res = self.parser.parse(har_data)
        self.assertEqual(res["total_entries"], 4)
        self.assertEqual(res["skipped_static"], 3)
        self.assertEqual(res["valid_entries"], 1)
        self.assertEqual(res["endpoints"][0]["path"], "/api/v2/data")

    # 7. Malformed HAR input
    def test_malformed_har_input(self):
        # Invalid JSON string
        res1 = self.parser.parse("{not valid json}")
        self.assertEqual(res1["endpoints"], [])
        self.assertIn("Malformed JSON", res1["errors"][0])

        # Missing log object
        res2 = self.parser.parse({"not_log": {}})
        self.assertEqual(res2["endpoints"], [])
        self.assertIn("Missing or invalid 'log'", res2["errors"][0])

        # Missing entries list
        res3 = self.parser.parse({"log": {"version": "1.2"}})
        self.assertEqual(res3["endpoints"], [])
        self.assertIn("Missing or invalid 'log.entries'", res3["errors"][0])

        # Entry with missing request
        res4 = self.parser.parse({"log": {"version": "1.2", "entries": [{"response": {}}]}})
        self.assertEqual(res4["valid_entries"], 0)
        self.assertTrue(len(res4["errors"]) > 0)

    # 8. Sensitive data redaction
    def test_sensitive_data_redaction(self):
        # Headers redaction
        headers = [
            {"name": "Authorization", "value": "Bearer super-secret-token"},
            {"name": "Cookie", "value": "session=abc12345"},
            {"name": "X-API-Key", "value": "key-xyz"},
            {"name": "Accept", "value": "application/json"}
        ]
        sanitized = sanitize_headers(headers)
        auth_header = next(h for h in sanitized if h["name"] == "Authorization")
        cookie_header = next(h for h in sanitized if h["name"] == "Cookie")
        accept_header = next(h for h in sanitized if h["name"] == "Accept")
        self.assertEqual(auth_header["value"], "[REDACTED]")
        self.assertEqual(cookie_header["value"], "[REDACTED]")
        self.assertEqual(accept_header["value"], "application/json")

        # Parameter values redaction
        har_data = {
            "log": {
                "version": "1.2",
                "entries": [
                    {
                        "request": {
                            "method": "POST",
                            "url": "http://127.0.0.1:8001/api/v2/login",
                            "postData": {
                                "mimeType": "application/json",
                                "text": json.dumps({
                                    "username": "admin",
                                    "password": "Password123!",
                                    "secret_token": "tok_9999",
                                    "credit_card": "4111111111111111"
                                })
                            }
                        }
                    }
                ]
            }
        }
        res = self.parser.parse(har_data)
        params = res["endpoints"][0]["params"]
        self.assertEqual(params["username"], "admin")
        self.assertEqual(params["password"], "[REDACTED]")
        self.assertEqual(params["secret_token"], "[REDACTED]")
        self.assertEqual(params["credit_card"], "[REDACTED]")

    # 9. Shadow and zombie classification limitations & evidence requirements
    def test_classification_limitations(self):
        # Scenario A: No documented registry provided
        # An /admin/ route MUST NOT be confirmed shadow without registry comparison!
        uninformed_classifier = APIClassifier()
        endpoint_admin = {"path": "/api/v2/internal/admin/stats", "method": "GET", "params": {}}
        res_admin = uninformed_classifier.classify_endpoint(endpoint_admin)
        self.assertEqual(res_admin["category"], "active")
        self.assertTrue(res_admin["classification_details"]["is_candidate"])
        self.assertEqual(res_admin["classification_details"]["suggested_category"], "shadow")

        # Scenario B: Documented registry provided
        # Since /internal/admin/stats is missing from documented registry, it is confirmed shadow
        doc_registry = [
            {"path": "/api/v2/flights/search", "method": "GET"},
            {"path": "/api/v2/bookings/create", "method": "POST"}
        ]
        informed_classifier = APIClassifier(documented_registry=doc_registry)
        res_admin_confirmed = informed_classifier.classify_endpoint(endpoint_admin)
        self.assertEqual(res_admin_confirmed["category"], "shadow")
        self.assertEqual(res_admin_confirmed["classification_details"]["confidence"], "confirmed")

        # Scenario C: No historical/deprecation evidence for /v1/ route
        # MUST NOT be confirmed zombie merely because it has /v1/ in path
        endpoint_v1 = {"path": "/api/v1/legacy/discounts", "method": "GET", "params": {}}
        res_v1 = uninformed_classifier.classify_endpoint(endpoint_v1)
        self.assertEqual(res_v1["category"], "active")
        self.assertTrue(res_v1["classification_details"]["is_candidate"])
        self.assertEqual(res_v1["classification_details"]["suggested_category"], "zombie")

        # Scenario D: Deprecated inventory provided
        # Route is confirmed zombie because it appears in deprecated inventory
        deprecated_inventory = [{"path": "/api/v1/legacy/discounts", "method": "GET"}]
        dep_classifier = APIClassifier(deprecated_inventory=deprecated_inventory)
        res_v1_confirmed = dep_classifier.classify_endpoint(endpoint_v1)
        self.assertEqual(res_v1_confirmed["category"], "zombie")
        self.assertEqual(res_v1_confirmed["classification_details"]["confidence"], "confirmed")

    # 10. Duplicate endpoint handling
    def test_duplicate_endpoint_handling(self):
        har_data = {
            "log": {
                "version": "1.2",
                "entries": [
                    {
                        "request": {
                            "method": "GET",
                            "url": "http://127.0.0.1:8001/api/v2/flights/search?origin=DEL",
                            "queryString": [{"name": "origin", "value": "DEL"}]
                        }
                    },
                    {
                        "request": {
                            "method": "GET",
                            "url": "http://127.0.0.1:8001/api/v2/flights/search?destination=DXB",
                            "queryString": [{"name": "destination", "value": "DXB"}]
                        }
                    }
                ]
            }
        }
        res = self.parser.parse(har_data)
        # Should merge into 1 normalized endpoint entry with both params
        self.assertEqual(len(res["endpoints"]), 1)
        ep = res["endpoints"][0]
        self.assertEqual(ep["path"], "/api/v2/flights/search")
        self.assertEqual(ep["method"], "GET")
        self.assertIn("origin", ep["params"])
        self.assertIn("destination", ep["params"])
        self.assertEqual(ep["occurrences"], 2)

    # 11. Database integration & save_endpoint idempotency
    def test_database_persistence_and_idempotency(self):
        # Create a temp DB
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_db_path = tmp.name

        original_db_path = db_module.DB_PATH
        try:
            db_module.DB_PATH = tmp_db_path
            db_module.init_db()

            # Save initial endpoint
            db_module.save_endpoint("/api/v2/flights/search", "GET", "active", {"origin": "DEL"})
            endpoints = db_module.get_all_endpoints()
            self.assertEqual(len(endpoints), 1)
            self.assertEqual(endpoints[0]["path"], "/api/v2/flights/search")
            self.assertEqual(endpoints[0]["category"], "active")

            # Save with updated params / category (simulate deduplication/replacement)
            db_module.save_endpoint("/api/v2/flights/search", "get", "active", {"origin": "DEL", "destination": "DXB"})
            updated = db_module.get_all_endpoints()
            self.assertEqual(len(updated), 1)
            params = json.loads(updated[0]["params"])
            self.assertEqual(params["destination"], "DXB")

            # Add activity log
            db_module.log_activity("ReconAgent", "HAR_INGESTED", "Test log message")
            logs = db_module.get_recent_logs(5)
            self.assertTrue(len(logs) > 0)
            self.assertEqual(logs[0]["action"], "HAR_INGESTED")
        finally:
            db_module.DB_PATH = original_db_path
            if os.path.exists(tmp_db_path):
                try:
                    os.remove(tmp_db_path)
                except Exception:
                    pass

    # 12. Full end-to-end test on sample_tbo_traffic.har
    def test_sample_tbo_traffic_fixture(self):
        fixture_path = os.path.join(os.path.dirname(__file__), "sample_tbo_traffic.har")
        with open(fixture_path, "r", encoding="utf-8") as f:
            har_data = json.load(f)

        parse_res = self.parser.parse(har_data)
        self.assertEqual(parse_res["total_entries"], 7)
        self.assertEqual(parse_res["skipped_static"], 1)  # /static/dashboard.js skipped
        self.assertEqual(parse_res["valid_entries"], 6)

        # Classify with standard documented catalog
        doc_registry = [
            {"path": "/api/v2/flights/search", "method": "GET"},
            {"path": "/api/v2/bookings/create", "method": "POST"},
            {"path": "/api/v2/bookings/{booking_id}", "method": "GET"},
            {"path": "/api/v2/refunds/request", "method": "POST"},
        ]
        dep_inventory = [
            {"path": "/api/v1/legacy/discounts", "method": "GET"}
        ]
        classifier = APIClassifier(
            documented_registry=doc_registry,
            deprecated_inventory=dep_inventory
        )
        classified = classifier.batch_classify(parse_res["endpoints"])
        cat_map = {ep["path"]: ep["category"] for ep in classified}

        # Verify active endpoints
        self.assertEqual(cat_map.get("/api/v2/flights/search"), "active")
        self.assertEqual(cat_map.get("/api/v2/bookings/create"), "active")
        self.assertEqual(cat_map.get("/api/v2/bookings/{booking_id}"), "active")
        self.assertEqual(cat_map.get("/api/v2/refunds/request"), "active")

        # Verify zombie endpoint
        self.assertEqual(cat_map.get("/api/v1/legacy/discounts"), "zombie")

        # Verify shadow endpoint (absent from documented registry)
        self.assertEqual(cat_map.get("/api/v2/internal/admin/stats"), "shadow")


if __name__ == "__main__":
    unittest.main()
