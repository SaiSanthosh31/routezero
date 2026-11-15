# VoyageHack 4.0 — Track 4: Agentic Real-Time DAST
## Team Execution Plan & Role Assignments (5 Members)

### 📌 Project Vision: **WatchDog DAST (Autonomous Travel API AppSec Agent)**
An autonomous security testing agent that continuously monitors B2B travel APIs, auto-maps active/zombie/shadow endpoints without documentation, safely executes targeted business-logic attacks (IDOR, price tampering, auth bypass), and generates instant verified vulnerability reports with reproduction proofs.

---

### 👥 Team Member Roles & Responsibilities

#### 1. Lead Backend & Agent Engine (You - Tech Lead)
* **What you build:**
  * **Agent Orchestrator & Attack Planner:** Uses an LLM (Gemini / Claude / local) to analyze discovered endpoints and decide intelligent business-logic attack strategies (e.g. IDOR, price/markup tampering, coupon reuse, role escalation).
  * **Exploit Executor & Safety Guard:** Safely executes the payloads with rate-limiting, scope checks, and safe test credentials.
  * **Verifier & Triage Agent:** Confirms whether an attack succeeded, eliminates false positives, and generates reproduction proofs (curl scripts + business impact score).

#### 2. Backend & Fullstack Co-Developer (Backend + Integrations)
* **What you build:**
  * **Recon & Traffic Sniffer:** Ingests traffic logs/HAR files or crawls the app to infer the API schema without Swagger/OpenAPI.
  * **Zombie & Shadow API Engine:** Flags endpoints that are live but unused (Zombie) or active in traffic but undocumented (Shadow).
  * **Backend API & Database:** Stores findings, endpoints, and audit logs (FastAPI/Express + SQLite/Postgres), and provides REST/WebSocket endpoints for the frontend.

#### 3. Frontend Lead 1 (Security Command Center & Ops Dashboard)
* **What you build:**
  * **Main Dashboard:** High-level metrics (Total endpoints scanned, Active vs Zombie vs Shadow count, Critical/High vulnerabilities found).
  * **Live Activity Feed:** Real-time log showing the agent discovering endpoints, testing attacks, and flagging issues.
  * **Safety Controls & Human Review:** Kill-switch toggle, rate-limit slider, and a modal for human approval on high-risk tests.

#### 4. Frontend Lead 2 (API Knowledge Graph & Exploit PoC Inspector)
* **What you build:**
  * **Visual API Topology Graph:** Interactive visual tree/graph showing all discovered routes color-coded by status (Green = Active, Yellow = Zombie, Red = Shadow / Vulnerable).
  * **Vulnerability Details & PoC Viewer:** Clean ticket modal showing vulnerability description, business risk, affected endpoint, and side-by-side HTTP request/response proofs with a 1-click "Retest" button.

#### 5. Target App & Red Team Demo Lead (The 5th Member)
* **Why this role is crucial:** Judges need to see the agent attack a *real, working app* live on screen.
* **What you build:**
  * **Vulnerable B2B Travel Target API:** A lightweight mock travel service with 4-5 key endpoints:
    * Search Flights/Hotels (`/api/v2/search`)
    * Booking & Pricing (`/api/v2/bookings` with a price parameter that can be manipulated)
    * View Booking (`/api/v2/bookings/{id}` vulnerable to IDOR across agencies)
    * Zombie Endpoint (`/api/v1/legacy-discount` that still gives unauthorized 50% discounts)
    * Shadow Endpoint (`/api/v2/internal/admin-payouts` accidentally exposed)
  * **Demo Flow & Presentation:** Owns the 3-minute hackathon demo script that proves to judges how the agent catches newly deployed bugs in real time.

---

### 🚀 Recommended Tech Stack
* **Agent Core & Backend:** Python (FastAPI + LangChain / LiteLLM / Requests)
* **Frontend:** React / Next.js + Tailwind CSS + Lucide Icons + React Flow (for API graph)
* **Target Vulnerable App:** Python (FastAPI) or Node.js (Express)
* **Database:** SQLite (fastest for hackathons) or PostgreSQL
