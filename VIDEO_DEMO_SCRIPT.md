# RouteZero — Demo Video Script
## VoyageHack 4.0 | Track 4: Fraud Prevention & Security
### Target Duration: ~2 minutes 30 seconds

---

## [0:00 – 0:12] OPENING — Problem Hook

**[Screen: Blank / Title card with "RouteZero" on dark teal background]**

> "Travel APIs process millions of transactions daily — price lookups, booking confirmations, payment flows.
> Any one of them can be tampered with before the request even reaches the server.
> RouteZero finds those vulnerabilities before attackers do."

---

## [0:12 – 0:28] SITE OVERVIEW — Scroll through Problem & 5 Whys

**[Screen: Open https://saisanthosh31.github.io/routezero/ — scroll slowly through Problem Statement and 5 Whys section]**

> "The root cause is a missing automated security layer in the travel API pipeline.
> RouteZero is an agentic, real-time Dynamic Application Security Testing engine — built specifically for travel platforms like TBO."

---

## [0:28 – 0:42] ARCHITECTURE — Brief scroll through Architecture section

**[Screen: Scroll to Architecture section — pause on the 4-stage pipeline diagram]**

> "It runs in four stages: Discover endpoints from HAR traffic, Map the attack surface, Exploit with safe proof-of-concept payloads, and Remediate with actionable fixes — all autonomously."

---

## [0:42 – 1:05] LIVE DEMO — Execute Scan

**[Screen: Click nav item "Live Demo" — console panel comes into view]**

> "Here is the live security console. The agent has already loaded five multi-agency travel fixtures and parsed four traffic interactions from real HAR data."

**[Screen: Click "EXECUTE AUTONOMOUS SCAN" button]**

> "One click triggers the full agentic loop — no manual configuration."

**[Screen: Watch log stream appear line by line in the left panel]**

> "The planner agent identifies candidate endpoints, the executor fires safe payloads, and the verifier confirms each finding with a CWE classification."

---

## [1:05 – 1:28] FINDINGS — Inspect Vulnerability Cards

**[Screen: Right panel shows 4 confirmed vulnerability cards]**

> "Four confirmed vulnerabilities — price tampering, IDOR on booking IDs, an exposed internal endpoint, and a missing authentication check."

**[Screen: Click "Inspect Proof" on the first card — Price Tampering]**

> "Every finding comes with a reproducible proof-of-concept: the exact curl command that triggered it, the tampered parameter, and the server response that confirmed the exploit."

**[Screen: Highlight the curl command in the modal]**

> "This is not a theoretical flag — it is a live, confirmed exploit with evidence."

---

## [1:28 – 1:45] REMEDIATION & EXPORT

**[Screen: Scroll down in the modal to show the Code Fix section]**

> "Along with the proof, RouteZero generates a targeted code fix — no guessing required."

**[Screen: Close modal, click "Export OpenAPI 3.0" button in the top bar]**

> "The full scan result exports as an OpenAPI 3.0 specification — ready to integrate into any CI/CD pipeline or security dashboard."

---

## [1:45 – 2:00] SAFETY GUARDRAILS

**[Screen: Click "Safety" in the nav — scroll to Safety Guardrails section]**

> "RouteZero operates within strict boundaries. A scope allowlist prevents scanning outside the target. A rate limiter caps request throughput. And a kill switch halts all activity instantly — making it safe to run in staging or even controlled production environments."

---

## [2:00 – 2:20] CLOSING — Team & Submission

**[Screen: Scroll to footer / team section]**

> "Built by Team RouteZero for VoyageHack 4.0 — Track 4, Fraud Prevention and Security.
> Sai Santhosh, Dharani, Arun Hitesh, Mythreyan, and Ravi Kiran."

**[Screen: Show GitHub Pages URL in browser address bar]**

> "RouteZero is live at saisanthosh31.github.io/routezero. Full source code and documentation are on GitHub."

---

## [2:20 – 2:30] END CARD

**[Screen: Title card — "RouteZero | Agentic Real-Time DAST for Travel APIs"]**

> "RouteZero. Find it before they do."

---

## RECORDING NOTES

- Speak at a measured pace — do not rush the scan animation
- Pause 1–2 seconds after clicking any button before narrating the result
- Record at 1920x1080, 30fps minimum
- Use screen recording tool (OBS / ShareX) with system audio off, mic only
- Keep cursor movements slow and deliberate
- No background music needed — silence is professional
