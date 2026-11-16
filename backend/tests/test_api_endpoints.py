import unittest
import os
import sys
import tempfile
import json
from starlette.testclient import TestClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import db.database as db_module
from main import app


class TestReconAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.tmp_db = cls.tmp_file.name
        cls.tmp_file.close()

        cls.orig_db = db_module.DB_PATH
        db_module.DB_PATH = cls.tmp_db
        db_module.init_db()

        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        db_module.DB_PATH = cls.orig_db
        if os.path.exists(cls.tmp_db):
            try:
                os.remove(cls.tmp_db)
            except Exception:
                pass

    def test_01_upload_logs_nginx_clf(self):
        nginx_data = (
            '127.0.0.1 - - [16/Nov/2026:10:00:00 +0000] "GET /api/v2/flights/search?origin=DEL HTTP/1.1" 200 450\n'
            '127.0.0.1 - - [16/Nov/2026:10:00:05 +0000] "POST /api/v2/bookings/create HTTP/1.1" 201 120\n'
            '127.0.0.1 - - [16/Nov/2026:10:00:10 +0000] "GET /static/app.js HTTP/1.1" 200 8900\n'
            'CORRUPT MALFORMED LINE\n'
        )
        resp = self.client.post(
            "/api/recon/upload-logs",
            content=nginx_data,
            headers={"Content-Type": "text/plain"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["format"], "nginx")
        self.assertEqual(data["skipped_static"], 1)
        self.assertEqual(data["skipped_malformed"], 1)
        self.assertEqual(data["endpoints_discovered"], 2)

    def test_02_upload_logs_ndjson(self):
        ndjson_body = {
            "logs": (
                '{"method": "GET", "url": "/api/v1/legacy/discounts", "status": 200}\n'
                '{"method": "GET", "url": "/api/v2/internal/admin/stats", "status": 200}\n'
            )
        }
        resp = self.client.post(
            "/api/recon/upload-logs",
            json=ndjson_body
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["format"], "ndjson")
        self.assertEqual(data["endpoints_discovered"], 2)

    def test_03_category_filtering_and_validation(self):
        # Valid category filtering
        resp_active = self.client.get("/api/endpoints?category=active")
        self.assertEqual(resp_active.status_code, 200)
        for ep in resp_active.json()["endpoints"]:
            self.assertEqual(ep["category"], "active")

        resp_zombie = self.client.get("/api/endpoints?category=zombie")
        self.assertEqual(resp_zombie.status_code, 200)
        for ep in resp_zombie.json()["endpoints"]:
            self.assertEqual(ep["category"], "zombie")

        resp_shadow = self.client.get("/api/endpoints?category=shadow")
        self.assertEqual(resp_shadow.status_code, 200)
        for ep in resp_shadow.json()["endpoints"]:
            self.assertEqual(ep["category"], "shadow")

        # Invalid category validation (must return 400)
        resp_invalid = self.client.get("/api/endpoints?category=not_a_category")
        self.assertEqual(resp_invalid.status_code, 400)
        self.assertIn("Invalid category", resp_invalid.json()["message"])

    def test_04_ignore_and_restore_endpoints(self):
        # Fetch current list
        all_eps = self.client.get("/api/endpoints").json()["endpoints"]
        self.assertTrue(len(all_eps) > 0)
        target = all_eps[0]
        t_id = target["id"]

        # Soft ignore endpoint
        ignore_resp = self.client.post(
            f"/api/endpoints/{t_id}/ignore",
            json={"reason": "False positive test route"}
        )
        self.assertEqual(ignore_resp.status_code, 200)
        self.assertEqual(ignore_resp.json()["endpoint"]["is_ignored"], 1)
        self.assertEqual(ignore_resp.json()["endpoint"]["ignore_reason"], "False positive test route")

        # GET /api/endpoints should now exclude it
        after_ignore = self.client.get("/api/endpoints").json()["endpoints"]
        self.assertNotIn(t_id, [e["id"] for e in after_ignore])

        # GET /api/endpoints?include_ignored=true should include it
        with_ignored = self.client.get("/api/endpoints?include_ignored=true").json()["endpoints"]
        self.assertIn(t_id, [e["id"] for e in with_ignored])

        # Restore endpoint
        restore_resp = self.client.post(f"/api/endpoints/{t_id}/restore")
        self.assertEqual(restore_resp.status_code, 200)
        self.assertEqual(restore_resp.json()["endpoint"]["is_ignored"], 0)

        # GET /api/endpoints should now include it again
        after_restore = self.client.get("/api/endpoints").json()["endpoints"]
        self.assertIn(t_id, [e["id"] for e in after_restore])

    def test_05_delete_endpoint(self):
        # Create dedicated endpoint to delete
        db_module.save_endpoint("/api/v2/temp_to_delete", "DELETE", "active", {})
        ep = [e for e in db_module.get_all_endpoints(include_ignored=True) if e["path"] == "/api/v2/temp_to_delete"][0]
        t_id = ep["id"]

        del_resp = self.client.delete(f"/api/endpoints/{t_id}")
        self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(del_resp.json()["status"], "success")

        # Verify deletion
        remaining = [e["id"] for e in db_module.get_all_endpoints(include_ignored=True)]
        self.assertNotIn(t_id, remaining)

        # Deleting non-existent returns 404
        del_404 = self.client.delete("/api/endpoints/999999")
        self.assertEqual(del_404.status_code, 404)

    def test_06_ignore_nonexistent_returns_404(self):
        resp = self.client.post("/api/endpoints/999999/ignore", json={"reason": "test"})
        self.assertEqual(resp.status_code, 404)

        resp_rest = self.client.post("/api/endpoints/999999/restore")
        self.assertEqual(resp_rest.status_code, 404)

    def test_07_dynamic_obsolescence_on_get_endpoints(self):
        # 1. Seed legacy dormant route as active
        db_module.save_endpoint(
            path="/api/v1/dormant/discounts",
            method="GET",
            category="active",
            params={},
            request_count=10,
            first_seen="2026-01-01 00:00:00",
            last_seen="2026-01-01 00:00:00"
        )
        # 2. Seed non-legacy route with old last_seen
        db_module.save_endpoint(
            path="/api/v2/old/active_route",
            method="GET",
            category="active",
            params={},
            request_count=10,
            first_seen="2026-01-01 00:00:00",
            last_seen="2026-01-01 00:00:00"
        )
        # 3. Seed ignored legacy route
        db_module.save_endpoint(
            path="/api/v1/dormant/ignored_route",
            method="GET",
            category="active",
            params={},
            request_count=5,
            first_seen="2026-01-01 00:00:00",
            last_seen="2026-01-01 00:00:00"
        )
        ep_ign = [e for e in db_module.get_all_endpoints(include_ignored=True) if e["path"] == "/api/v1/dormant/ignored_route"][0]
        db_module.ignore_endpoint(ep_ign["id"], reason="False positive legacy test")

        # Call GET /api/endpoints with 30-day threshold
        resp = self.client.get("/api/endpoints?inactivity_threshold_days=30&include_ignored=true")
        self.assertEqual(resp.status_code, 200)
        eps = {e["path"]: e for e in resp.json()["endpoints"]}

        # Legacy route crossing threshold must be dynamically updated to zombie
        self.assertEqual(eps["/api/v1/dormant/discounts"]["category"], "zombie")
        # Non-legacy route crossing threshold must NOT be converted to zombie
        self.assertEqual(eps["/api/v2/old/active_route"]["category"], "active")
        # Ignored endpoint must remain ignored
        self.assertEqual(eps["/api/v1/dormant/ignored_route"]["is_ignored"], 1)

    def test_08_har_historical_timestamps_and_no_backwards_drift(self):
        har_stream = {
            "log": {
                "version": "1.2",
                "entries": [
                    {
                        "startedDateTime": "2026-05-01T10:00:00.000Z",
                        "request": {"method": "GET", "url": "http://127.0.0.1:8001/api/v2/test/har_timestamps"}
                    },
                    {
                        "startedDateTime": "2026-05-01T12:00:00.000Z",
                        "request": {"method": "GET", "url": "http://127.0.0.1:8001/api/v2/test/har_timestamps"}
                    }
                ]
            }
        }
        resp = self.client.post("/api/recon/upload-har", json=har_stream)
        self.assertEqual(resp.status_code, 200)

        ep = [e for e in db_module.get_all_endpoints() if e["path"] == "/api/v2/test/har_timestamps"][0]
        self.assertEqual(ep["first_seen"], "2026-05-01 10:00:00")
        self.assertEqual(ep["last_seen"], "2026-05-01 12:00:00")
        self.assertEqual(ep["request_count"], 2)

        # Ingest an older entry (earlier first_seen, but older than current last_seen)
        older_har = {
            "log": {
                "version": "1.2",
                "entries": [
                    {
                        "startedDateTime": "2026-04-15T08:00:00.000Z",
                        "request": {"method": "GET", "url": "http://127.0.0.1:8001/api/v2/test/har_timestamps"}
                    },
                    {
                        "startedDateTime": "2026-05-01T11:00:00.000Z",
                        "request": {"method": "GET", "url": "http://127.0.0.1:8001/api/v2/test/har_timestamps"}
                    }
                ]
            }
        }
        resp2 = self.client.post("/api/recon/upload-har", json=older_har)
        self.assertEqual(resp2.status_code, 200)

        ep_updated = [e for e in db_module.get_all_endpoints() if e["path"] == "/api/v2/test/har_timestamps"][0]
        # first_seen should move to the true earlier date (2026-04-15)
        self.assertEqual(ep_updated["first_seen"], "2026-04-15 08:00:00")
        # last_seen should NOT move backwards to 11:00:00 (keeps latest 12:00:00)
        self.assertEqual(ep_updated["last_seen"], "2026-05-01 12:00:00")
        self.assertEqual(ep_updated["request_count"], 4)

    def test_09_protect_shadow_classification_without_catalog(self):
        # 1. Seed endpoint as shadow
        db_module.save_endpoint(
            path="/api/v2/internal/debug_protect",
            method="GET",
            category="shadow",
            params={}
        )
        ep = [e for e in db_module.get_all_endpoints() if e["path"] == "/api/v2/internal/debug_protect"][0]
        self.assertEqual(ep["category"], "shadow")

        # 2. Upload raw log containing this route with NO documented catalog
        raw_log = '{"method": "GET", "url": "/api/v2/internal/debug_protect", "status": 200}\n'
        resp = self.client.post(
            "/api/recon/upload-logs",
            json={"logs": raw_log, "documented_registry": []}
        )
        self.assertEqual(resp.status_code, 200)

        # Verify category was NOT demoted to active
        ep_after = [e for e in db_module.get_all_endpoints() if e["path"] == "/api/v2/internal/debug_protect"][0]
        self.assertEqual(ep_after["category"], "shadow")

        # 3. Now upload log WITH documented catalog verifying this route
        resp_doc = self.client.post(
            "/api/recon/upload-logs",
            json={
                "logs": raw_log,
                "documented_registry": [{"path": "/api/v2/internal/debug_protect", "method": "GET"}]
            }
        )
        self.assertEqual(resp_doc.status_code, 200)

        # Now that it's documented, it should legitimately become active
        ep_doc = [e for e in db_module.get_all_endpoints() if e["path"] == "/api/v2/internal/debug_protect"][0]
        self.assertEqual(ep_doc["category"], "active")


if __name__ == "__main__":
    unittest.main()
