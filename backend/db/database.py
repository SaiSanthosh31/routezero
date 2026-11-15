import sqlite3
import json
import os

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
        UNIQUE(path, method)
    )
    """)
    
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

def save_endpoint(path: str, method: str, category: str, params: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO endpoints (path, method, category, params)
    VALUES (?, ?, ?, ?)
    """, (path, method.upper(), category, json.dumps(params)))
    conn.commit()
    conn.close()

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

def get_all_endpoints():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM endpoints ORDER BY id ASC")
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
