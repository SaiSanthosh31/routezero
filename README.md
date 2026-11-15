# RouteZero
Autonomous Real-Time DAST Security Agent for B2B Travel APIs. Built for **VoyageHack 4.0 (TBO.com)**.

---

## What It Does
1. **Zero-Spec Recon:** Maps travel API routes by monitoring traffic without requiring OpenAPI/Swagger specs.
2. **Zombie & Shadow API Detection:** Flags deprecated routes (like abandoned `/v1/` discount endpoints) and undocumented internal APIs (`/internal/stats`).
3. **AI Business-Logic Exploits:** Uses reasoning to generate and execute non-trivial exploits (price tampering, cross-agency IDOR, and duplicate refund loops).
4. **Reproducible Proofs:** Confirms exploits with minimal curl commands, side-by-side HTTP proofs, and 1-click retest verification.

---

## Quickstart (Run in 1 Command)

### Prerequisites
* Python 3.10+
* `pip install fastapi uvicorn requests`

### Run
```bash
python run.py
```
This automatically starts:
* **Target App (Vulnerable B2B Travel API):** `http://127.0.0.1:8001`
* **RouteZero Dashboard & DAST Engine:** `http://127.0.0.1:8000`

---

## Project Structure
```text
├── backend/            # DAST Agent brain, SQLite DB, and REST APIs
│   ├── agents/         # Attack Planner, Exploit Executor, Verifier
│   ├── db/             # Database storage & activity logs
│   └── main.py         # Core API server
├── target-app/         # Mock B2B travel portal with intentional bugs
├── frontend/           # Real-time SOC dashboard (HTML5 / Tailwind)
├── TEAM_ROLES.md       # Team responsibilities
└── run.py              # Single-command launcher
```
