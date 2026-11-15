# VoyageHack 4.0 — Track 4: Agentic Real-Time DAST
## Team Execution Plan & Role Assignments

### 👥 Team Roster & Tasks

---

#### 1. @S4NTY3119 (You - Lead Backend & AI Agent Engine)
* **Status:** Active (Core Owner)
* **What you own:**
  * **LLM Attack Planner:** Uses Gemini / LLM to inspect discovered endpoints and plan targeted business-logic exploits (IDOR, price tampering, coupon reuse, role escalation).
  * **Exploit Executor & Safety Engine:** Safely executes the payloads with rate-limiting, scope checks, and safe test credentials.
  * **Verifier & Triage:** Confirms successful exploits with reproducible proof (curl + HTTP response snippets) and assigns business risk severity scores.
  * REST API endpoints that trigger agent runs and return scan status.

---

#### 2. @dharanii-07 (Backend & Recon / API Data Engine)
* **Status:** Active
* **What he owns:**
  * **Recon & Endpoint Discovery:** Scans/crawls target web app and parses traffic logs (HAR files) to infer endpoints, query params, and request bodies without Swagger.
  * **Zombie & Shadow API Engine:** Compares inferred routes against traffic history to label endpoints as `Active`, `Zombie` (old, uncalled), or `Shadow` (called but unmapped).
  * **Database & Persistence:** Stores discovered endpoints, vulnerability tickets, and audit logs (FastAPI + SQLite/Postgres).

---

#### 3. @arun-hitesh (Frontend 1 - SOC Command Center & Live Feed)
* **Status:** Active
* **What he owns:**
  * **Main Security Dashboard:** High-level stat cards (Total endpoints scanned, Zombie/Shadow count, Critical/High vulnerabilities).
  * **Live Agent Activity Stream:** Terminal-like or event-card stream showing the AI agent actively discovering routes, launching tests, and reporting findings in real-time.
  * **Safety Controls:** Emergency Kill Switch toggle, rate-limiting slider, and human approval modal for high-risk exploits.

---

#### 4. Frontend Teammate 2 (Frontend 2 - API Topology & Exploit Inspector)
* **Status:** Active
* **What he owns:**
  * **Interactive API Topology Map:** Visual graph / tree showing all discovered endpoints color-coded (Green = Active, Yellow = Zombie, Red = Shadow / Vulnerable).
  * **Vulnerability Ticket & PoC Inspector:** Click into any finding to see:
    * Vulnerability title, severity badge, and business impact description.
    * Side-by-side HTTP Request (with malicious payload) and Response proof.
    * 1-Click **"Retest"** button to rerun the verification.

---

#### 5. Teammate 5 (Backup / Easy Task: Seed Data & Target Scenarios)
* **Status:** Low-dependency (Can't block the team)
* **What he owns:**
  * **Sample Data & Presentation:**
    * Create sample travel booking JSON payloads and realistic HAR/traffic log files.
    * Test the target app manually to verify standard user flows.
    * Help put together the 5-minute demo script & slide deck.
  *(Note: If he doesn't show up, backend can auto-generate the mock data in 5 minutes!)*

---

### 📂 Repository Structure

```text
├── backend/
│   ├── agents/          # LLM Attack Planner, Exploit Executor, Verifier (@S4NTY3119)
│   ├── recon/           # Traffic sniffer & Zombie/Shadow detector (@dharanii-07)
│   ├── db/              # Models, SQLite storage & repository (@dharanii-07)
│   ├── routes/          # REST API & WebSockets for frontend (@S4NTY3119 & @dharanii-07)
│   └── main.py          # FastAPI app entrypoint
├── target-app/          # Mock vulnerable B2B travel portal for testing
├── frontend/            # Next.js / React + Tailwind CSS (@arun-hitesh & Teammate 2)
│   ├── components/      # LiveFeed, StatCards, ApiGraph, VulnModal
│   └── pages/
├── data/                # Sample HAR logs, seed travel datasets (Teammate 5)
├── TEAM_ROLES.md
└── README.md
```

