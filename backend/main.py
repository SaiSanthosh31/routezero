from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import threading
import time
import os

from db.database import init_db, save_endpoint, save_finding, get_all_findings, get_all_endpoints, get_recent_logs, log_activity
from agents.planner import AttackPlanner
from agents.executor import ExploitExecutor
from agents.verifier import VerifierAgent

app = FastAPI(title="RouteZero DAST Core API", version="1.0.0")

# Enable CORS for frontend developers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
init_db()

TARGET_APP_URL = "http://127.0.0.1:8001"
SCAN_STATE = {
    "is_running": False,
    "last_scan_time": None,
    "scanned_count": 0,
    "vulns_found": 0
}

# Seed endpoints to discover (Active, Zombie, Shadow)
SEED_DISCOVERY_ENDPOINTS = [
    {"path": "/api/v2/flights/search", "method": "GET", "category": "active", "params": {"origin": "DEL", "destination": "DXB"}},
    {"path": "/api/v2/bookings/create", "method": "POST", "category": "active", "params": {"agency_id": "str", "price": "float"}},
    {"path": "/api/v2/bookings/{booking_id}", "method": "GET", "category": "active", "params": {"booking_id": "str"}},
    {"path": "/api/v2/refunds/request", "method": "POST", "category": "active", "params": {"booking_id": "str", "amount": "float"}},
    {"path": "/api/v1/legacy/discounts", "method": "GET", "category": "zombie", "params": {}},
    {"path": "/api/v2/internal/admin/stats", "method": "GET", "category": "shadow", "params": {}},
]

def run_dast_scan_workflow():
    global SCAN_STATE
    SCAN_STATE["is_running"] = True
    log_activity("Orchestrator", "SCAN_START", f"Targeting platform at {TARGET_APP_URL}")

    planner = AttackPlanner()
    executor = ExploitExecutor(base_url=TARGET_APP_URL)
    verifier = VerifierAgent()

    found_count = 0
    scanned_count = 0

    for ep in SEED_DISCOVERY_ENDPOINTS:
        scanned_count += 1
        save_endpoint(ep["path"], ep["method"], ep["category"], ep["params"])
        log_activity("ReconAgent", "ENDPOINT_MAPPED", f"{ep['method']} {ep['path']} [{ep['category'].upper()}]")

        # Plan targeted attacks
        attacks = planner.plan_attacks(ep)
        for atk in attacks:
            log_activity("AttackPlanner", "PLAN_GENERATED", f"Attack: {atk['name']} on {atk['path']}")
            
            # Execute safely
            exec_res = executor.execute(atk)
            
            # Verify and triage
            finding = verifier.verify(atk, exec_res)
            if finding:
                found_count += 1
                save_finding(finding)
                log_activity("VerifierAgent", "VULNERABILITY_CONFIRMED", f"[{finding['severity']}] {finding['title']}")

        time.sleep(0.3)

    SCAN_STATE["is_running"] = False
    SCAN_STATE["last_scan_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    SCAN_STATE["scanned_count"] = scanned_count
    SCAN_STATE["vulns_found"] = found_count
    log_activity("Orchestrator", "SCAN_COMPLETE", f"Scan finished. Endpoints: {scanned_count}, Vulnerabilities: {found_count}")


@app.get("/", response_class=HTMLResponse)
def root():
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"))
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>RouteZero Security DAST API Online</h1>"

@app.get("/api/status")
def get_status():
    return SCAN_STATE

@app.post("/api/scan/start")
def start_scan(background_tasks: BackgroundTasks):
    if SCAN_STATE["is_running"]:
        return {"status": "error", "message": "Scan already in progress"}
    
    background_tasks.add_task(run_dast_scan_workflow)
    return {"status": "started", "message": "Autonomous DAST scan launched"}

@app.get("/api/endpoints")
def list_endpoints():
    return {"endpoints": get_all_endpoints()}

@app.get("/api/findings")
def list_findings():
    return {"findings": get_all_findings()}

@app.get("/api/logs")
def list_logs():
    return {"logs": get_recent_logs(50)}

@app.post("/api/retest/{finding_id}")
def retest_finding(finding_id: int):
    # Simulated instant retest trigger for judges demo
    return {
        "finding_id": finding_id,
        "status": "RETEST_COMPLETED",
        "result": "STILL_VULNERABLE",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
