import unittest
import json
import os
import sys
import tempfile
import sqlite3
from datetime import datetime, timezone, timedelta

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
from recon.log_parser import (
    LogParser,
    parse_raw_logs,
    detect_log_format
)
from recon.discovery import APIClassifier, classify_endpoints
import db.database as db_module


class TestHARParserAndDiscovery(unittest.TestCase):

    def setUp(self):
        self.parser = HARParser()
        self.log_parser = LogParser()

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
                    "method": m.lower(),
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
        res1 = self.parser.parse("{not valid json}")
        self.assertEqual(res1["endpoints"], [])
        self.assertIn("Malformed JSON", res1["errors"][0])

        res2 = self.parser.parse({"not_log": {}})
        self.assertEqual(res2["endpoints"], [])
        self.assertIn("Missing or invalid 'log'", res2["errors"][0])

        res3 = self.parser.parse({"log": {"version": "1.2"}})
        self.assertEqual(res3["endpoints"], [])
        self.assertIn("Missing or invalid 'log.entries'", res3["errors"][0])

        res4 = self.parser.parse({"log": {"version": "1.2", "entries": [{"response": {}}]}})
        self.assertEqual(res4["valid_entries"], 0)
        self.assertTrue(len(res4["errors"]) > 0)

    # 8. Sensitive data redaction
    def test_sensitive_data_redaction(self):
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
        uninformed_classifier = APIClassifier()
        endpoint_admin = {"path": "/api/v2/internal/admin/stats", "method": "GET", "params": {}}
        res_admin = uninformed_classifier.classify_endpoint(endpoint_admin)
        self.assertEqual(res_admin["category"], "active")
        self.assertTrue(res_admin["classification_details"]["is_candidate"])
        self.assertEqual(res_admin["classification_details"]["suggested_category"], "shadow")

        doc_registry = [
            {"path": "/api/v2/flights/search", "method": "GET"},
            {"path": "/api/v2/bookings/create", "method": "POST"}
        ]
        informed_classifier = APIClassifier(documented_registry=doc_registry)
        res_admin_confirmed = informed_classifier.classify_endpoint(endpoint_admin)
        self.assertEqual(res_admin_confirmed["category"], "shadow")
        self.assertEqual(res_admin_confirmed["classification_details"]["confidence"], "confirmed")

        endpoint_v1 = {"path": "/api/v1/legacy/discounts", "method": "GET", "params": {}}
        res_v1 = uninformed_classifier.classify_endpoint(endpoint_v1)
        self.assertEqual(res_v1["category"], "active")
        self.assertTrue(res_v1["classification_details"]["is_candidate"])
        self.assertEqual(res_v1["classification_details"]["suggested_category"], "zombie")

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
        self.assertEqual(len(res["endpoints"]), 1)
        ep = res["endpoints"][0]
        self.assertEqual(ep["path"], "/api/v2/flights/search")
        self.assertEqual(ep["method"], "GET")
        self.assertIn("origin", ep["params"])
        self.assertIn("destination", ep["params"])
        self.assertEqual(ep["occurrences"], 2)

    # 11. Database integration & save_endpoint idempotency
    def test_database_persistence_and_idempotency(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_db_path = tmp.name

        original_db_path = db_module.DB_PATH
        try:
            db_module.DB_PATH = tmp_db_path
            db_module.init_db()

            db_module.save_endpoint("/api/v2/flights/search", "GET", "active", {"origin": "DEL"})
            endpoints = db_module.get_all_endpoints()
            self.assertEqual(len(endpoints), 1)
            self.assertEqual(endpoints[0]["path"], "/api/v2/flights/search")
            self.assertEqual(endpoints[0]["category"], "active")

            db_module.save_endpoint("/api/v2/flights/search", "get", "active", {"origin": "DEL", "destination": "DXB"})
            updated = db_module.get_all_endpoints()
            self.assertEqual(len(updated), 1)
            params = json.loads(updated[0]["params"])
            self.assertEqual(params["destination"], "DXB")

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
        self.assertEqual(parse_res["skipped_static"], 1)
        self.assertEqual(parse_res["valid_entries"], 6)

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

        self.assertEqual(cat_map.get("/api/v2/flights/search"), "active")
        self.assertEqual(cat_map.get("/api/v2/bookings/create"), "active")
        self.assertEqual(cat_map.get("/api/v2/bookings/{booking_id}"), "active")
        self.assertEqual(cat_map.get("/api/v2/refunds/request"), "active")
        self.assertEqual(cat_map.get("/api/v1/legacy/discounts"), "zombie")
        self.assertEqual(cat_map.get("/api/v2/internal/admin/stats"), "shadow")

    # ------------------------------------------------------------------------
    # ENHANCEMENT 1: RAW LOG STREAM PARSER TESTS
    # ------------------------------------------------------------------------
    def test_nginx_access_log_parsing(self):
        nginx_log = """
127.0.0.1 - - [16/Nov/2026:10:00:00 +0000] "GET /api/v2/flights/search?origin=DEL&destination=DXB HTTP/1.1" 200 450 "-" "Mozilla/5.0"
127.0.0.1 - - [16/Nov/2026:10:00:05 +0000] "POST /api/v2/bookings/create HTTP/1.1" 201 120 "http://example.com" "curl/7.68.0"
127.0.0.1 - - [16/Nov/2026:10:00:10 +0000] "GET /static/bundle.js HTTP/1.1" 200 8900 "-" "Mozilla/5.0"
"""
        res = self.log_parser.parse(nginx_log)
        self.assertEqual(res["format_detected"], "nginx")
        self.assertEqual(res["total_lines"], 4)
        self.assertEqual(res["skipped_static"], 1)
        self.assertEqual(res["valid_entries"], 2)
        self.assertEqual(len(res["endpoints"]), 2)

        paths = {ep["path"]: ep for ep in res["endpoints"]}
        self.assertIn("/api/v2/flights/search", paths)
        self.assertEqual(paths["/api/v2/flights/search"]["method"], "GET")
        self.assertEqual(paths["/api/v2/flights/search"]["params"]["origin"], "DEL")
        self.assertEqual(paths["/api/v2/flights/search"]["response_status"], 200)

        self.assertIn("/api/v2/bookings/create", paths)
        self.assertEqual(paths["/api/v2/bookings/create"]["method"], "POST")
        self.assertEqual(paths["/api/v2/bookings/create"]["response_status"], 201)

    def test_apache_common_log_parsing(self):
        apache_log = """
192.168.1.50 - frank [10/Oct/2026:13:55:36 -0700] "GET /api/v2/bookings/BK-1001 HTTP/1.0" 200 2326
192.168.1.50 - frank [10/Oct/2026:13:55:40 -0700] "GET /api/v1/legacy/discounts HTTP/1.0" 200 450
"""
        res = self.log_parser.parse(apache_log, log_format="apache")
        self.assertEqual(res["valid_entries"], 2)
        paths = {ep["path"]: ep for ep in res["endpoints"]}
        # Dynamic path normalization should turn BK-1001 into {booking_id}
        self.assertIn("/api/v2/bookings/{booking_id}", paths)
        self.assertIn("/api/v1/legacy/discounts", paths)

    def test_ndjson_log_parsing(self):
        ndjson_log = """
{"method": "GET", "url": "/api/v2/flights/search?origin=BOM", "status": 200, "timestamp": "2026-11-16T10:00:00Z"}
{"method": "POST", "path": "/api/v2/bookings/create", "body": {"agency_id": "AGENCY-001", "password": "pass"}, "status": 201}
{"method": "GET", "path": "/assets/style.css", "status": 200}
"""
        res = self.log_parser.parse(ndjson_log)
        self.assertEqual(res["format_detected"], "ndjson")
        self.assertEqual(res["skipped_static"], 1)
        self.assertEqual(res["valid_entries"], 2)

        paths = {ep["path"]: ep for ep in res["endpoints"]}
        self.assertIn("/api/v2/flights/search", paths)
        self.assertEqual(paths["/api/v2/flights/search"]["params"]["origin"], "BOM")

        self.assertIn("/api/v2/bookings/create", paths)
        # Verify sensitive password in body was redacted
        self.assertEqual(paths["/api/v2/bookings/create"]["params"]["password"], "[REDACTED]")
        self.assertEqual(paths["/api/v2/bookings/create"]["params"]["agency_id"], "AGENCY-001")

    def test_log_format_auto_detection(self):
        har_str = '{"log": {"version": "1.2", "entries": []}}'
        ndjson_str = '{"method": "GET", "url": "/api/test"}\n{"method": "POST", "url": "/api/test2"}'
        nginx_str = '127.0.0.1 - - [16/Nov/2026:10:00:00 +0000] "GET /api/test HTTP/1.1" 200 100'

        self.assertEqual(detect_log_format(har_str), "har")
        self.assertEqual(detect_log_format(ndjson_str), "ndjson")
        self.assertEqual(detect_log_format(nginx_str), "nginx")
        self.assertEqual(detect_log_format("not a log file"), "unknown")

    def test_malformed_log_lines_graceful_handling(self):
        dirty_log = """
127.0.0.1 - - [16/Nov/2026:10:00:00 +0000] "GET /api/v2/flights/search HTTP/1.1" 200 450
CORRUPTED JUNK LINE THAT DOES NOT MATCH CLF AT ALL
{"method": "GET", "url": "/broken/json/without/closing
127.0.0.1 - - [16/Nov/2026:10:00:05 +0000] "POST /api/v2/refunds/request HTTP/1.1" 200 120
"""
        res = self.log_parser.parse(dirty_log, log_format="nginx")
        self.assertEqual(res["valid_entries"], 2)
        self.assertEqual(res["skipped_malformed"], 2)
        self.assertEqual(len(res["endpoints"]), 2)
        self.assertTrue(len(res["errors"]) > 0)

    # ------------------------------------------------------------------------
    # ENHANCEMENT 2: HISTORICAL ROUTE TELEMETRY TESTS
    # ------------------------------------------------------------------------
    def test_telemetry_accumulation_across_observations(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_db_path = tmp.name

        original_db = db_module.DB_PATH
        try:
            db_module.DB_PATH = tmp_db_path
            db_module.init_db()

            # Batch 1: Observe 3 requests
            db_module.save_endpoint(
                path="/api/v2/flights/search",
                method="GET",
                category="active",
                params={"origin": "DEL"},
                request_count=3,
                first_seen="2026-01-01 10:00:00",
                last_seen="2026-01-01 10:05:00"
            )
            ep1 = db_module.get_all_endpoints()[0]
            self.assertEqual(ep1["request_count"], 3)
            self.assertEqual(ep1["first_seen"], "2026-01-01 10:00:00")
            self.assertEqual(ep1["last_seen"], "2026-01-01 10:05:00")

            # Batch 2: Observe 5 more requests on same endpoint
            db_module.save_endpoint(
                path="/api/v2/flights/search",
                method="GET",
                category="active",
                params={"origin": "DEL", "destination": "DXB"},
                request_count=5,
                first_seen="2026-01-02 11:00:00",
                last_seen="2026-01-02 12:00:00"
            )
            ep2 = db_module.get_all_endpoints()[0]
            # Total request count should be 3 + 5 = 8
            self.assertEqual(ep2["request_count"], 8)
            # first_seen should be preserved from Batch 1!
            self.assertEqual(ep2["first_seen"], "2026-01-01 10:00:00")
            # last_seen should be updated to Batch 2!
            self.assertEqual(ep2["last_seen"], "2026-01-02 12:00:00")
        finally:
            db_module.DB_PATH = original_db
            if os.path.exists(tmp_db_path):
                os.remove(tmp_db_path)

    def test_telemetry_survives_restart(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_db_path = tmp.name

        original_db = db_module.DB_PATH
        try:
            db_module.DB_PATH = tmp_db_path
            db_module.init_db()

            db_module.save_endpoint(
                path="/api/v2/test/restart",
                method="POST",
                category="active",
                params={},
                request_count=42,
                first_seen="2026-05-01 00:00:00",
                last_seen="2026-05-15 00:00:00"
            )

            # Re-initialize DB (simulating application restart)
            db_module.init_db()

            telemetry = db_module.get_endpoints_telemetry()
            self.assertIn(("POST", "/api/v2/test/restart"), telemetry)
            t_record = telemetry[("POST", "/api/v2/test/restart")]
            self.assertEqual(t_record["request_count"], 42)
            self.assertEqual(t_record["first_seen"], "2026-05-01 00:00:00")
            self.assertEqual(t_record["last_seen"], "2026-05-15 00:00:00")
        finally:
            db_module.DB_PATH = original_db
            if os.path.exists(tmp_db_path):
                os.remove(tmp_db_path)

    def test_obsolescence_detection_with_inactivity_threshold(self):
        ref_time = datetime(2026, 11, 16, 12, 0, 0, tzinfo=timezone.utc)
        historical_telemetry = {
            ("GET", "/api/v1/legacy/discounts"): {
                "first_seen": "2026-01-01 00:00:00",
                "last_seen": "2026-05-01 00:00:00", # ~200 days ago (>90 threshold)
                "request_count": 1500
            },
            ("GET", "/api/v2/flights/search"): {
                "first_seen": "2026-01-01 00:00:00",
                "last_seen": "2026-11-15 12:00:00", # 1 day ago (recent)
                "request_count": 50000
            },
            ("GET", "/api/v2/dormant/feature"): {
                "first_seen": "2026-01-01 00:00:00",
                "last_seen": "2026-06-01 00:00:00", # ~168 days ago (>90 threshold)
                "request_count": 200
            }
        }

        classifier = APIClassifier(
            historical_traffic=historical_telemetry,
            inactivity_threshold_days=90,
            reference_time=ref_time
        )

        # 1. Legacy route with sustained inactivity is confirmed obsolete zombie
        res_legacy = classifier.classify_endpoint({"path": "/api/v1/legacy/discounts", "method": "GET"})
        self.assertEqual(res_legacy["category"], "zombie")
        self.assertEqual(res_legacy["classification_details"]["confidence"], "confirmed")
        self.assertTrue(res_legacy["classification_details"]["inactivity_days"] > 90)

        # 2. Active route with recent traffic remains active
        res_active = classifier.classify_endpoint({"path": "/api/v2/flights/search", "method": "GET"})
        self.assertEqual(res_active["category"], "active")
        self.assertEqual(res_active["classification_details"]["confidence"], "normal")

        # 3. Standard non-legacy route with sustained inactivity is flagged as candidate zombie (not confirmed)
        res_dormant = classifier.classify_endpoint({"path": "/api/v2/dormant/feature", "method": "GET"})
        self.assertEqual(res_dormant["category"], "active")
        self.assertTrue(res_dormant["classification_details"]["is_candidate"])
        self.assertEqual(res_dormant["classification_details"]["suggested_category"], "zombie")

    # ------------------------------------------------------------------------
    # ENHANCEMENT 3: RECON ENDPOINT MANAGEMENT TESTS
    # ------------------------------------------------------------------------
    def test_category_filtering(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_db_path = tmp.name

        original_db = db_module.DB_PATH
        try:
            db_module.DB_PATH = tmp_db_path
            db_module.init_db()

            db_module.save_endpoint("/api/v2/active1", "GET", "active", {})
            db_module.save_endpoint("/api/v2/active2", "POST", "active", {})
            db_module.save_endpoint("/api/v1/zombie1", "GET", "zombie", {})
            db_module.save_endpoint("/api/v2/shadow1", "GET", "shadow", {})

            # Filter active
            actives = db_module.get_all_endpoints(category="active")
            self.assertEqual(len(actives), 2)
            self.assertTrue(all(e["category"] == "active" for e in actives))

            # Filter zombie
            zombies = db_module.get_all_endpoints(category="zombie")
            self.assertEqual(len(zombies), 1)
            self.assertEqual(zombies[0]["path"], "/api/v1/zombie1")

            # Filter shadow
            shadows = db_module.get_all_endpoints(category="shadow")
            self.assertEqual(len(shadows), 1)
            self.assertEqual(shadows[0]["path"], "/api/v2/shadow1")

            # All endpoints
            all_eps = db_module.get_all_endpoints()
            self.assertEqual(len(all_eps), 4)
        finally:
            db_module.DB_PATH = original_db
            if os.path.exists(tmp_db_path):
                os.remove(tmp_db_path)

    def test_soft_ignore_and_restore(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_db_path = tmp.name

        original_db = db_module.DB_PATH
        try:
            db_module.DB_PATH = tmp_db_path
            db_module.init_db()

            db_module.save_endpoint("/api/v2/normal", "GET", "active", {})
            db_module.save_endpoint("/api/v2/false-positive", "GET", "shadow", {})

            all_init = db_module.get_all_endpoints()
            self.assertEqual(len(all_init), 2)

            # Ignore false-positive endpoint
            target_id = next(e["id"] for e in all_init if e["path"] == "/api/v2/false-positive")
            ignored_ok = db_module.ignore_endpoint(target_id, reason="Approved internal admin route")
            self.assertTrue(ignored_ok)

            # Normal listing MUST exclude ignored endpoint
            active_list = db_module.get_all_endpoints(include_ignored=False)
            self.assertEqual(len(active_list), 1)
            self.assertEqual(active_list[0]["path"], "/api/v2/normal")

            # include_ignored=True includes it
            all_with_ignored = db_module.get_all_endpoints(include_ignored=True)
            self.assertEqual(len(all_with_ignored), 2)
            ignored_record = next(e for e in all_with_ignored if e["id"] == target_id)
            self.assertEqual(ignored_record["is_ignored"], 1)
            self.assertEqual(ignored_record["ignore_reason"], "Approved internal admin route")

            # Restore endpoint
            restored_ok = db_module.restore_endpoint(target_id)
            self.assertTrue(restored_ok)

            # Should be back in normal listing
            restored_list = db_module.get_all_endpoints(include_ignored=False)
            self.assertEqual(len(restored_list), 2)
            restored_record = next(e for e in restored_list if e["id"] == target_id)
            self.assertEqual(restored_record["is_ignored"], 0)
        finally:
            db_module.DB_PATH = original_db
            if os.path.exists(tmp_db_path):
                os.remove(tmp_db_path)

    def test_endpoint_deletion(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_db_path = tmp.name

        original_db = db_module.DB_PATH
        try:
            db_module.DB_PATH = tmp_db_path
            db_module.init_db()

            db_module.save_endpoint("/api/v2/delete-me", "DELETE", "active", {})
            endpoints = db_module.get_all_endpoints()
            self.assertEqual(len(endpoints), 1)
            ep_id = endpoints[0]["id"]

            deleted_ok = db_module.delete_endpoint(ep_id)
            self.assertTrue(deleted_ok)

            after_del = db_module.get_all_endpoints(include_ignored=True)
            self.assertEqual(len(after_del), 0)

            # Deleting non-existent returns False
            self.assertFalse(db_module.delete_endpoint(99999))
        finally:
            db_module.DB_PATH = original_db
            if os.path.exists(tmp_db_path):
                os.remove(tmp_db_path)


if __name__ == "__main__":
    unittest.main()
