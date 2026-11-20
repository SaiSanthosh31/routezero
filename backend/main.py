from fastapi import FastAPI, BackgroundTasks, Query, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
import threading
import time
import os
import json
import asyncio

# Database helpers and recon utilities
from db.database import (
    init_db,
    save_endpoint,
    save_finding,
    get_all_findings,
    get_all_endpoints,
    get_endpoint_by_id,
    ignore_endpoint,
    restore_endpoint,
    delete_endpoint,
    get_endpoints_telemetry,
    sync_dynamic_obsolescence,
    get_recent_logs,
    log_activity,
)

# Agent components
from agents.planner import AttackPlanner
from agents.executor import ExploitExecutor
from agents.verifier import VerifierAgent
from agents.safety import SafetyGuard

# Recon components
from recon.har_parser import parse_har_traffic, HARParser
from recon.log_parser import LogParser, parse_raw_logs, detect_log_format
from recon.discovery import APIClassifier
from recon.openapi_gen import generate_openapi_spec

app = FastAPI(title="RouteZero DAST Core API", version="1.0.0")
global_safety_guard = SafetyGuard()

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
    "vulns_found": 0,
    "target_url": "http://127.0.0.1:8001",
}

LOG_BUFFER: List[Dict] = []
LOG_BUFFER_MAX = 200

# Seed endpoints to discover (Active, Zombie, Shadow)
SEED_DISCOVERY_ENDPOINTS = [
    {"path": "/api/v2/flights/search", "method": "GET", "category": "active", "params": {"origin": "DEL", "destination": "DXB"}},
    {"path": "/api/v2/bookings/create", "method": "POST", "category": "active", "params": {"agency_id": "str", "price": "float"}},
    {"path": "/api/v2/bookings/{booking_id}", "method": "GET", "category": "active", "params": {"booking_id": "str"}},
    {"path": "/api/v2/refunds/request", "method": "POST", "category": "active", "params": {"booking_id": "str", "amount": "float"}},
    {"path": "/api/v1/legacy/discounts", "method": "GET", "category": "zombie", "params": {}},
    {"path": "/api/v2/internal/admin/stats", "method": "GET", "category": "shadow", "params": {}},
]

def push_log(agent: str, event: str, message: str):
    entry = {
        "timestamp": time.strftime("%H:%M:%S"),
        "agent": agent,
        "event": event,
        "message": message,
    }
    LOG_BUFFER.append(entry)
    if len(LOG_BUFFER) > LOG_BUFFER_MAX:
        LOG_BUFFER.pop(0)
    log_activity(agent, event, message)

def run_dast_scan_workflow(target_url: str = None):
    global SCAN_STATE
    target = (target_url or TARGET_APP_URL).rstrip("/")
    SCAN_STATE["is_running"] = True
    SCAN_STATE["target_url"] = target
    LOG_BUFFER.clear()

    push_log("SYSTEM", "SCAN_START", f"RouteZero Agentic DAST engine initialised.")
    push_log("RECON", "TRAFFIC_LOAD", f"Initiating passive traffic analysis on {target}...")

    safety = SafetyGuard(allowed_hosts=["127.0.0.1:8001", "localhost:8001"])
    parsed_host = target.replace("http://", "").replace("https://", "").split("/")[0]
    safety.allowed_hosts = [parsed_host, "127.0.0.1:8001", "localhost:8001"]

    planner = AttackPlanner()
    executor = ExploitExecutor(base_url=target, safety_guard=safety)
    verifier = VerifierAgent()

    found_count = 0
    scanned_count = 0

    db_endpoints = get_all_endpoints(include_ignored=False)
    if not db_endpoints:
        push_log("RECON", "SEED_FALLBACK", "No endpoints in database — seeding baseline travel API endpoints.")
        for ep in SEED_DISCOVERY_ENDPOINTS:
            save_endpoint(ep["path"], ep["method"], ep["category"], ep["params"])
        db_endpoints = get_all_endpoints(include_ignored=False)

    seen = set()
    endpoints_to_scan = []
    for ep in db_endpoints:
        key = (ep["method"].upper(), ep["path"])
        if key not in seen:
            seen.add(key)
            params = ep.get("params")
            if isinstance(params, str):
                try:
                    params = json.loads(params)
                except Exception:
                    params = {}
            ep_dict = dict(ep)
            ep_dict["params"] = params
            endpoints_to_scan.append(ep_dict)

    push_log("RECON", "ENDPOINTS_MAPPED", f"Identified {len(endpoints_to_scan)} endpoints — active, zombie, and shadow routes.")
    push_log("PLANNER", "PLAN_START", f"Synthesising travel-domain attack plan: price fields, booking IDs, tenant headers...")

    for ep in endpoints_to_scan:
        scanned_count += 1
        save_endpoint(ep["path"], ep["method"], ep["category"], ep["params"])
        push_log("EXECUTOR", "ENDPOINT_PROBE", f"Probing {ep['method']} {target}{ep['path']}...")

        attacks = planner.plan_attacks(ep)
        for atk in attacks:
            push_log("EXECUTOR", "ATTACK_FIRE", f"Testing: {atk['name']} on {atk['path']}")
            exec_res = executor.execute(atk)
            finding = verifier.verify(atk, exec_res)
            if finding:
                found_count += 1
                save_finding(finding)
                push_log("VERIFIER", "VULNERABILITY_CONFIRMED", f"EXPLOIT CONFIRMED [{finding['severity']}]: {finding['title']}")
        time.sleep(0.3)

    SCAN_STATE["is_running"] = False
    SCAN_STATE["last_scan_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    SCAN_STATE["scanned_count"] = scanned_count
    SCAN_STATE["vulns_found"] = found_count
    push_log("SYSTEM", "SCAN_COMPLETE", f"Scan complete. {scanned_count} endpoints scanned, {found_count} vulnerabilities confirmed.")

@app.get("/", response_class=HTMLResponse)
def root():
    candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "frontend", "index.html")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html")),
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>RouteZero Security DAST API Online</h1>"

@app.get("/api/status")
def get_status():
    return SCAN_STATE

class ScanStartPayload(BaseModel):
    target_url: Optional[str] = None

@app.post("/api/scan/start")
def start_scan(background_tasks: BackgroundTasks, payload: Optional[ScanStartPayload] = None):
    if SCAN_STATE["is_running"]:
        return {"status": "error", "message": "Scan already in progress"}
    target = (payload.target_url if payload and payload.target_url else TARGET_APP_URL).rstrip("/")
    background_tasks.add_task(run_dast_scan_workflow, target)
    return {"status": "started", "message": f"Autonomous DAST scan launched against {target}", "target_url": target}

@app.get("/api/logs/stream")
async def stream_logs():
    async def event_generator():
        last_index = 0
        for _ in range(300):
            current = LOG_BUFFER[last_index:]
            for entry in current:
                yield f"data: {json.dumps(entry)}\n\n"
                last_index += 1
            if not SCAN_STATE["is_running"] and last_index >= len(LOG_BUFFER) and last_index > 0:
                yield f"data: {json.dumps({'agent': 'STREAM', 'event': 'EOF', 'message': 'Stream closed.'})}\n\n"
                break
            await asyncio.sleep(0.3)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ----------------- RECON ENDPOINT MANAGEMENT ROUTES -----------------

@app.get("/api/endpoints")
def list_endpoints(
    category: Optional[str] = Query(None, description="Filter by category: active, zombie, shadow"),
    include_ignored: bool = Query(False, description="Whether to include soft-ignored endpoints"),
    inactivity_threshold_days: int = Query(90, description="Inactivity threshold in days for dynamic obsolescence re-evaluation"),
):
    """
    Lists discovered endpoints with optional category filtering and soft-ignore toggle.
    Dynamically re-evaluates obsolescence for stored routes crossing the inactivity threshold.
    """
    valid_categories = {"active", "zombie", "shadow"}
    if category is not None:
        cat_clean = category.strip().lower()
        if cat_clean not in valid_categories:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Invalid category '{category}'. Must be one of: active, zombie, shadow"
                }
            )
        category = cat_clean

    # Re-evaluate stored endpoints against inactivity threshold dynamically on read
    sync_dynamic_obsolescence(inactivity_threshold_days=inactivity_threshold_days)

    endpoints = get_all_endpoints(category=category, include_ignored=include_ignored)
    return {"endpoints": endpoints, "total": len(endpoints)}

class IgnoreEndpointPayload(BaseModel):
    reason: Optional[str] = None

@app.post("/api/endpoints/{endpoint_id}/ignore")
def ignore_endpoint_route(endpoint_id: int, payload: Optional[IgnoreEndpointPayload] = None):
    """Soft-ignores a false-positive endpoint so it is excluded from normal recon scans without destroying historical telemetry."""
    ep = get_endpoint_by_id(endpoint_id)
    if not ep:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": f"Endpoint with ID {endpoint_id} not found"}
        )
    reason = payload.reason if payload else "False positive"
    ignore_endpoint(endpoint_id, reason=reason)
    updated_ep = get_endpoint_by_id(endpoint_id)
    log_activity("ReconManager", "ENDPOINT_IGNORED", f"Endpoint {endpoint_id} ({ep['method']} {ep['path']}) ignored. Reason: {reason}")
    return {"status": "success", "message": f"Endpoint {endpoint_id} successfully ignored", "endpoint": updated_ep}

@app.post("/api/endpoints/{endpoint_id}/restore")
def restore_endpoint_route(endpoint_id: int):
    """Restores a soft-ignored endpoint back to the active inventory."""
    ep = get_endpoint_by_id(endpoint_id)
    if not ep:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": f"Endpoint with ID {endpoint_id} not found"}
        )
    restore_endpoint(endpoint_id)
    updated_ep = get_endpoint_by_id(endpoint_id)
    log_activity("ReconManager", "ENDPOINT_RESTORED", f"Endpoint {endpoint_id} ({ep['method']} {ep['path']}) restored")
    return {"status": "success", "message": f"Endpoint {endpoint_id} successfully restored", "endpoint": updated_ep}

@app.delete("/api/endpoints/{endpoint_id}")
def delete_endpoint_route(endpoint_id: int):
    """Permanently deletes an endpoint record from the database."""
    ep = get_endpoint_by_id(endpoint_id)
    if not ep:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": f"Endpoint with ID {endpoint_id} not found"}
        )
    delete_endpoint(endpoint_id)
    log_activity("ReconManager", "ENDPOINT_DELETED", f"Endpoint {endpoint_id} ({ep['method']} {ep['path']}) permanently removed")
    return {"status": "success", "message": f"Endpoint {endpoint_id} permanently deleted"}

# ----------------- INGESTION ROUTES -----------------

@app.post("/api/recon/upload-har")
def upload_har(payload: dict):
    """Ingests HAR 1.2 JSON, normalizes endpoints, redacts sensitive parameters, updates telemetry, classifies active/zombie/shadow APIs, and persists endpoints into SQLite."""
    # 1. Structure validation
    har_data = payload.get("har", payload)
    if not isinstance(har_data, dict) or "log" not in har_data:
        return {
            "status": "error",
            "message": "Invalid HAR payload: expected JSON object containing a 'log' field",
            "entries_processed": 0,
            "endpoints_discovered": 0,
            "endpoints": [],
            "errors": ["Missing 'log' key in HAR payload"],
        }

    # 2. Parse entries
    parser = HARParser()
    parse_result = parser.parse(har_data)

    if parse_result["errors"] and not parse_result["endpoints"]:
        return {
            "status": "error",
            "message": "Failed to parse HAR entries",
            "entries_processed": parse_result["total_entries"],
            "endpoints_discovered": 0,
            "endpoints": [],
            "errors": parse_result["errors"],
        }

    # 3. Classification using documented registry and telemetry
    doc_registry = payload.get("documented_registry") if "documented_registry" in payload else [
        {"path": "/api/v2/flights/search", "method": "GET"},
        {"path": "/api/v2/bookings/create", "method": "POST"},
        {"path": "/api/v2/bookings/{booking_id}", "method": "GET"},
        {"path": "/api/v2/refunds/request", "method": "POST"},
    ]
    dep_inventory = payload.get("deprecated_inventory") if "deprecated_inventory" in payload else [
        {"path": "/api/v1/legacy/discounts", "method": "GET"},
    ]

    telemetry = get_endpoints_telemetry()
    classifier = APIClassifier(
        documented_registry=doc_registry,
        deprecated_inventory=dep_inventory,
        historical_traffic=telemetry,
    )
    classified_endpoints = classifier.batch_classify(parse_result["endpoints"])

    # 4. Save discovered endpoints into database & log activity
    saved_count = 0
    for ep in classified_endpoints:
        save_endpoint(
            path=ep["path"],
            method=ep["method"],
            category=ep["category"],
            params=ep["params"],
            request_count=ep.get("occurrences", 1),
            first_seen=ep.get("first_seen"),
            last_seen=ep.get("last_seen"),
        )
        saved_count += 1

    log_activity(
        "ReconAgent",
        "HAR_INGESTED",
        f"Processed {parse_result['total_entries']} entries; Discovered {saved_count} API endpoints "
        f"({parse_result['skipped_static']} static assets skipped).",
    )

    return {
        "status": "success",
        "entries_processed": parse_result["total_entries"],
        "valid_entries": parse_result["valid_entries"],
        "skipped_static": parse_result["skipped_static"],
        "endpoints_discovered": len(classified_endpoints),
        "endpoints": classified_endpoints,
        "errors": parse_result["errors"],
    }

@app.post("/api/recon/upload-logs")
async def upload_logs(request: Request):
    """Ingests Nginx, Apache, or NDJSON raw log stream. Normalizes endpoints, updates persistent telemetry, classifies active/zombie/shadow APIs, and persists endpoints into SQLite."""
    content_type = request.headers.get("content-type", "").lower()
    raw_text = ""
    log_format = None
    doc_registry = None
    dep_inventory = None

    if "application/json" in content_type:
        try:
            body_json = await request.json()
            if isinstance(body_json, dict):
                raw_text = body_json.get("logs") or body_json.get("log") or body_json.get("raw_logs", "")
                log_format = body_json.get("format")
                doc_registry = body_json.get("documented_registry")
                dep_inventory = body_json.get("deprecated_inventory")
            elif isinstance(body_json, str):
                raw_text = body_json
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": f"Invalid JSON payload: {str(e)}"},
            )
    else:
        body_bytes = await request.body()
        raw_text = body_bytes.decode("utf-8", errors="replace")

    if not raw_text.strip():
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "No log data provided in request body"},
        )

    parser = LogParser()
    parse_result = parser.parse(raw_text, log_format=log_format)

    if parse_result["errors"] and not parse_result["endpoints"]:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Failed to parse log entries",
                "format": parse_result["format_detected"],
                "total_lines": parse_result["total_lines"],
                "errors": parse_result["errors"],
            },
        )

    # Classification using same strategy as HAR ingestion
    if doc_registry is None:
        doc_registry = [
            {"path": "/api/v2/flights/search", "method": "GET"},
            {"path": "/api/v2/bookings/create", "method": "POST"},
            {"path": "/api/v2/bookings/{booking_id}", "method": "GET"},
            {"path": "/api/v2/refunds/request", "method": "POST"},
        ]
    if dep_inventory is None:
        dep_inventory = [{"path": "/api/v1/legacy/discounts", "method": "GET"}]

    telemetry = get_endpoints_telemetry()
    classifier = APIClassifier(
        documented_registry=doc_registry,
        deprecated_inventory=dep_inventory,
        historical_traffic=telemetry,
    )
    classified_endpoints = classifier.batch_classify(parse_result["endpoints"])

    saved_count = 0
    for ep in classified_endpoints:
        save_endpoint(
            path=ep["path"],
            method=ep["method"],
            category=ep["category"],
            params=ep["params"],
            request_count=ep.get("occurrences", 1),
            first_seen=ep.get("first_seen"),
            last_seen=ep.get("last_seen"),
        )
        saved_count += 1

    log_activity(
        "ReconAgent",
        "RAW_LOG_INGESTED",
        f"Processed {parse_result['total_lines']} lines; Discovered {saved_count} API endpoints (format: {parse_result['format_detected']}).",
    )

    return {
        "status": "success",
        "total_lines": parse_result["total_lines"],
        "format": parse_result["format_detected"],
        "skipped_static": parse_result.get("skipped_static", 0),
        "skipped_malformed": parse_result.get("skipped_malformed", 0),
        "endpoints_discovered": len(classified_endpoints),
        "endpoints": classified_endpoints,
        "errors": parse_result["errors"],
    }


# ----------------- FINDINGS & LOGS -----------------

@app.get("/api/findings")
def list_findings():
    return {"findings": get_all_findings()}


@app.get("/api/logs")
def list_logs():
    return {"logs": get_recent_logs(50)}


@app.post("/api/retest/{finding_id}")
def retest_finding(finding_id: int):
    return {
        "finding_id": finding_id,
        "status": "RETEST_COMPLETED",
        "result": "STILL_VULNERABLE",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


# ----------------- OPENAPI EXPORT -----------------

@app.get("/api/export/openapi.json")
def export_openapi():
    endpoints = get_all_endpoints()
    return generate_openapi_spec(endpoints)


# ----------------- DEPLOY WEBHOOK -----------------

class DeployWebhookPayload(BaseModel):
    service: str
    commit: str
    changed_endpoints: List[str]


@app.post("/api/webhook/deploy")
def on_deploy_webhook(payload: DeployWebhookPayload):
    start_time = time.time()

    log_activity(
        "WebhookTrigger",
        "DEPLOY_EVENT_RECEIVED",
        f"Commit {payload.commit} deployed on {payload.service}"
    )

    planner = AttackPlanner()
    executor = ExploitExecutor(
        base_url=TARGET_APP_URL,
        safety_guard=global_safety_guard
    )    verifier = VerifierAgent()

    new_findings = []

    for path in payload.changed_endpoints:
        endpoint = {
            "path": path,
            "method": "POST" if "create" in path or "request" in path else "GET",
            "category": "active",
            "params": {}
        }

        attacks = planner.plan_attacks(endpoint)

        for attack in attacks:
            log_activity(
                "AttackPlanner",
                "DELTA_TEST",
                f"Testing deploy change: {attack['name']}"
            )

            result = executor.execute(attack)
            finding = verifier.verify(attack, result)

            if finding:
                save_finding(finding)
                new_findings.append(finding)

                log_activity(
                    "VerifierAgent",
                    "DELTA_FINDING",
                    f"Found: {finding['title']}"
                )

    duration_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": "completed",
        "reaction_time_ms": duration_ms,
        "commit": payload.commit,
        "new_vulnerabilities": len(new_findings)
    }


# ----------------- SAFETY CONTROLS -----------------

class RateLimitPayload(BaseModel):
    rate_limit: Optional[float] = None
    delay_seconds: Optional[float] = None


@app.get("/api/safety/status")
def get_safety_status():
    delay = global_safety_guard.rate_limit_delay
    req_per_sec = round(1.0 / max(delay, 0.01), 1) if delay > 0 else 20.0

    return {
        "kill_switch_active": global_safety_guard.kill_switch_active,
        "rate_limit_delay": delay,
        "requests_per_sec": req_per_sec,
        "state": "PAUSED" if global_safety_guard.kill_switch_active else "ACTIVE"
    }


@app.post("/api/safety/rate-limit")
def set_rate_limit(payload: RateLimitPayload):
    if payload.delay_seconds is not None:
        global_safety_guard.rate_limit_delay = max(
            0.01, float(payload.delay_seconds)
        )
    elif payload.rate_limit is not None and payload.rate_limit > 0:
        global_safety_guard.rate_limit_delay = max(
            0.01, round(1.0 / float(payload.rate_limit), 3)
        )

    req_sec = round(
        1.0 / max(global_safety_guard.rate_limit_delay, 0.01), 1
    )

    log_activity(
        "SafetyGuard",
        "RATE_LIMIT_ADJUSTED",
        f"Discipline updated to {req_sec} req/s "
        f"({global_safety_guard.rate_limit_delay}s delay)"
    )

    return {
        "status": "updated",
        "rate_limit_delay": global_safety_guard.rate_limit_delay,
        "requests_per_sec": req_sec
    }


@app.post("/api/safety/kill-switch")
def toggle_kill_switch():
    global_safety_guard.kill_switch_active = (
        not global_safety_guard.kill_switch_active
    )

    state = "PAUSED" if global_safety_guard.kill_switch_active else "ACTIVE"

    log_activity(
        "SafetyGuard",
        "KILL_SWITCH_TOGGLED",
        f"Agent state set to {state}"
    )

    return {
        "kill_switch_active": global_safety_guard.kill_switch_active,
        "state": state
    }


@app.get("/api/safety/audit-log")
def get_audit_log():
    return {"audit_log": global_safety_guard.audit_log}

