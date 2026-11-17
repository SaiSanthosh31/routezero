# RouteZero — Idea Submission Deck (VoyageHack 4.0)
**Track 4: Agentic Real-Time DAST (Fraud Prevention & Security)**  
**Live Interactive Platform:** https://saisanthosh31.github.io/routezero/  
**Source Code:** https://github.com/SaiSanthosh31/routezero  

---

## SLIDE 1: Cover Slide
* **Title:** RouteZero
* **Subtitle:** Autonomous Real-Time Application Security Agents for B2B Travel Platforms
* **Context:** VoyageHack 4.0 | Track 4: Agentic Real-Time DAST
* **Team:** RouteZero
* **Links:** Live Web App: https://saisanthosh31.github.io/routezero/ | GitHub: https://github.com/SaiSanthosh31/routezero

---

## SLIDE 2 (Content Slide 1 of 2): Problem & Architectural Solution

### B2B Travel AppSec Bottlenecks (Status Quo)
1. **Frequent Deploys vs Periodic Scans:** TBO deploys flight/hotel microservice updates daily; weekly/monthly scanners leave dangerous multi-day zero-day exploit windows.
2. **Blind to Business Logic:** Generic scanners spray basic SQLi/XSS but fail to catch devastating business-logic abuse: $1 flight price tampering, cross-agency IDOR passport leaks, and unchecked duplicate refund loops.
3. **Zombie & Shadow API Exposure:** Deprecated legacy routes (e.g. `/v1/` discount endpoints) and undocumented internal debug routes (`/internal/stats`) remain live in production without governance.
4. **False Positive Alert Fatigue:** Security teams drown in 100-page scanner PDF dumps lacking reproducible proofs.

### RouteZero Agentic Architecture (Our Innovation)
1. **Autonomous Recon (Zero-Spec):** Ingests raw network traffic (HAR) and crawls UI to map live endpoints, query params, and body schemas without needing Swagger/OpenAPI docs.
2. **Shadow & Zombie Inventory:** Automatically maps and classifies active routes vs forgotten `/v1` endpoints (Zombie) vs undocumented internal endpoints (Shadow).
3. **LLM-Driven Attack Planner:** Inspects the business context of each route to craft targeted exploit strategies (IDOR, price override, coupon reuse) rather than brute-force spraying.
4. **Safe Execution Layer:** Built with scope allowlisting, multi-tenant test credential vault, adaptive rate-limiting, and an interactive Kill Switch.
5. **Verifier & Proof Engine:** Discards false positives, produces verified 1-click reproduction curl commands, assigns team ownership, and auto-generates an OpenAPI 3.0 spec as a by-product.

---

## SLIDE 3 (Content Slide 2 of 2): Continuous Workflow, Validation & Business Impact

### Continuous Autonomous Loop & Validated PoCs
* **<50ms Deploy-to-Detection Reaction:** CI/CD deploy webhooks trigger automated delta-scans against modified routes instantly.
* **Proved 5 Real Business Exploits on Live Target:**
  * **Critical:** Overrode $450 flight ticket to $1.00 via client parameter tampering (`/api/v2/bookings/create`).
  * **Critical:** Agency-002 accessed Agency-001's passenger passport PII via cross-agency IDOR (`/api/v2/bookings/{id}`).
  * **High:** Extracted valid 50% discount voucher from unauthenticated legacy route (`/api/v1/legacy/discounts`).
  * **High:** Publicly leaked DB connection string from internal telemetry endpoint (`/api/v2/internal/admin/stats`).
  * **High:** Executed infinite duplicate refund loops without booking state validation (`/api/v2/refunds/request`).
* **Actionable Developer Tickets:** Findings include side-by-side HTTP proofs, CWE tagging, team assignment (`@tbo-booking-core`), and copy-paste remediation code patches.

### Enterprise Impact & TBO ROI
1. **Direct Revenue Protection:** Stops revenue leakage from fare manipulation, coupon abuse, and escrow payout drains across massive travel transaction volumes.
2. **DPDP Act 2023 Compliance:** Prevents severe statutory penalties by eliminating cross-agency IDOR leaks exposing passenger passport and contact PII.
3. **Sub-Minute MTTR (Mean Time to Remediation):** Developers receive actionable curl reproduction scripts and exact code patches within minutes of deploying.
4. **Zero Vendor Lock-in & Low Cost:** Operates on lightweight heuristics with multi-LLM support; generates OpenAPI 3.0 specs to enforce platform-wide API governance.

---

## SLIDE 4: Thank You Slide
* **Heading:** Thank You
* **Subheading:** RouteZero — Autonomous Real-Time AppSec Agent
* **Live Interactive Demo:** https://saisanthosh31.github.io/routezero/
* **GitHub Repository:** https://github.com/SaiSanthosh31/routezero
