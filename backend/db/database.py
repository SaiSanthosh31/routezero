import sqlite3
import json
import os
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "routezero.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Endpoints table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS endpoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL,
        method TEXT NOT NULL,
        category TEXT NOT NULL, -- active, zombie, shadow
        params TEXT,
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        request_count INTEGER DEFAULT 1,
        is_ignored INTEGER DEFAULT 0,
        ignore_reason TEXT DEFAULT NULL,
        UNIQUE(path, method)
    )
    """)

    # Safe migration: ensure new telemetry & management columns exist for older databases
    cursor.execute("PRAGMA table_info(endpoints)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    if "first_seen" not in existing_cols:
        cursor.execute("ALTER TABLE endpoints ADD COLUMN first_seen TIMESTAMP")
    if "last_seen" not in existing_cols:
        cursor.execute("ALTER TABLE endpoints ADD COLUMN last_seen TIMESTAMP")
    if "request_count" not in existing_cols:
        cursor.execute("ALTER TABLE endpoints ADD COLUMN request_count INTEGER DEFAULT 1")
    if "is_ignored" not in existing_cols:
        cursor.execute("ALTER TABLE endpoints ADD COLUMN is_ignored INTEGER DEFAULT 0")
    if "ignore_reason" not in existing_cols:
        cursor.execute("ALTER TABLE endpoints ADD COLUMN ignore_reason TEXT DEFAULT NULL")

    # Findings / Vulnerabilities table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        severity TEXT NOT NULL, -- CRITICAL, HIGH, MEDIUM, LOW
        vuln_type TEXT NOT NULL,
        cwe_id TEXT DEFAULT '',
        owner TEXT DEFAULT '@tbo-security',
        endpoint TEXT NOT NULL,
        method TEXT NOT NULL,
        description TEXT NOT NULL,
        business_impact TEXT NOT NULL,
        remediation TEXT DEFAULT '',
        remediation_code TEXT DEFAULT '',
        reproduction_curl TEXT NOT NULL,
        proof_request TEXT NOT NULL,
        proof_response TEXT NOT NULL,
        status TEXT DEFAULT 'CONFIRMED', -- CONFIRMED, RESOLVED
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Agent live activity logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def log_activity(agent: str, action: str, details: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO activity_logs (agent, action, details) VALUES (?, ?, ?)", (agent, action, details))
    conn.commit()
    conn.close()

def save_endpoint(
    path: str,
    method: str,
    category: str,
    params: dict,
    request_count: int = 1,
    first_seen: Optional[str] = None,
    last_seen: Optional[str] = None
):
    """
    Upserts endpoint while accumulating telemetry and preserving ignore status.
    Compatible with existing 4-argument calls.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    norm_method = method.upper()
    serialized_params = json.dumps(params)
    count = max(1, int(request_count))

    cursor.execute("""
    INSERT INTO endpoints (
        path, method, category, params,
        first_seen, last_seen, request_count, is_ignored
    )
    VALUES (
        ?, ?, ?, ?,
        COALESCE(?, CURRENT_TIMESTAMP),
        COALESCE(?, CURRENT_TIMESTAMP),
        ?, 0
    )
    ON CONFLICT(path, method) DO UPDATE SET
        category = excluded.category,
        params = excluded.params,
        first_seen = CASE
            WHEN endpoints.first_seen IS NULL THEN excluded.first_seen
            WHEN excluded.first_seen IS NOT NULL AND excluded.first_seen < endpoints.first_seen THEN excluded.first_seen
            ELSE endpoints.first_seen
        END,
        last_seen = CASE
            WHEN endpoints.last_seen IS NULL THEN excluded.last_seen
            WHEN excluded.last_seen IS NOT NULL AND excluded.last_seen > endpoints.last_seen THEN excluded.last_seen
            ELSE endpoints.last_seen
        END,
        request_count = endpoints.request_count + excluded.request_count
    """, (path, norm_method, category, serialized_params, first_seen, last_seen, count))

    conn.commit()
    conn.close()

def get_endpoint_by_id(endpoint_id: int) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM endpoints WHERE id = ?", (endpoint_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def ignore_endpoint(endpoint_id: int, reason: Optional[str] = None) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE endpoints SET is_ignored = 1, ignore_reason = ? WHERE id = ?",
        (reason, endpoint_id)
    )
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def restore_endpoint(endpoint_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE endpoints SET is_ignored = 0, ignore_reason = NULL WHERE id = ?",
        (endpoint_id,)
    )
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def delete_endpoint(endpoint_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM endpoints WHERE id = ?", (endpoint_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def get_all_endpoints(category: Optional[str] = None, include_ignored: bool = False) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM endpoints WHERE 1=1"
    args = []

    if not include_ignored:
        query += " AND (is_ignored = 0 OR is_ignored IS NULL)"

    if category:
        query += " AND LOWER(category) = LOWER(?)"
        args.append(category.strip())

    query += " ORDER BY id ASC"

    cursor.execute(query, tuple(args))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def sync_dynamic_obsolescence(inactivity_threshold_days: int = 90, reference_time: Optional[Any] = None) -> int:
    """
    Dynamically re-evaluates stored endpoints against the inactivity threshold.
    Updates persisted classifications to 'zombie' for inactive legacy routes.
    Preserves soft-ignored endpoints and candidate logic for non-legacy routes.
    """
    from datetime import datetime, timezone

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, path, method, category, last_seen, request_count, is_ignored FROM endpoints")
    rows = cursor.fetchall()

    ref_dt = reference_time or datetime.now(timezone.utc)
    if isinstance(ref_dt, str):
        try:
            ref_dt = datetime.fromisoformat(ref_dt)
        except Exception:
            ref_dt = datetime.now(timezone.utc)
    if ref_dt.tzinfo is None:
        ref_dt = ref_dt.replace(tzinfo=timezone.utc)

    updated_count = 0
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%d/%b/%Y:%H:%M:%S %z",
        "%d/%b/%Y:%H:%M:%S",
    ]

    for r in rows:
        path = r["path"]
        path_lower = path.lower()
        last_seen_str = r["last_seen"]
        current_cat = str(r["category"]).lower()

        # Only routes with legacy patterns crossing threshold become confirmed zombie
        is_legacy = "/v1/" in path_lower or "legacy" in path_lower
        if not is_legacy or not last_seen_str:
            continue

        last_dt = None
        for fmt in fmts:
            try:
                dt = datetime.strptime(str(last_seen_str).strip(), fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                last_dt = dt.astimezone(timezone.utc)
                break
            except Exception:
                continue

        if last_dt:
            inactivity_days = max(0, (ref_dt - last_dt).days)
            if inactivity_days >= inactivity_threshold_days and current_cat != "zombie":
                cursor.execute(
                    "UPDATE endpoints SET category = 'zombie' WHERE id = ?",
                    (r["id"],)
                )
                updated_count += 1

    if updated_count > 0:
        conn.commit()
    conn.close()
    return updated_count

def get_endpoints_telemetry() -> Dict[tuple, Dict[str, Any]]:
    """Returns mapping of (METHOD, PATH) to telemetry stats for discovery and obsolescence tracking."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT path, method, category, first_seen, last_seen, request_count, is_ignored FROM endpoints")
    rows = cursor.fetchall()
    conn.close()
    return {(r["method"].upper(), r["path"]): dict(r) for r in rows}

def save_finding(finding: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO findings (title, severity, vuln_type, cwe_id, owner, endpoint, method, description, business_impact, remediation, remediation_code, reproduction_curl, proof_request, proof_response, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        finding["title"],
        finding["severity"],
        finding["vuln_type"],
        finding.get("cwe_id", ""),
        finding.get("owner", "@tbo-security"),
        finding["endpoint"],
        finding["method"],
        finding["description"],
        finding["business_impact"],
        finding.get("remediation", ""),
        finding.get("remediation_code", ""),
        finding["reproduction_curl"],
        finding["proof_request"],
        finding["proof_response"],
        finding.get("status", "CONFIRMED")
    ))
    conn.commit()
    conn.close()

def get_all_findings():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM findings ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_logs(limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
