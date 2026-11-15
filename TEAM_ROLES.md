PROBLEM STATEMENT

TBO updates their travel platform constantly with new APIs, bookings, and pricing logic. Traditional security scanners are slow, dumb, and only run generic tests. They completely miss business logic bugs—like changing a flight price to 0, getting double refunds, or viewing another travel agency's bookings (IDOR).
On top of that, old forgotten endpoints (zombie APIs) and undocumented endpoints (shadow APIs) sit open without anyone tracking them.


OUR SOLUTION

We are building an autonomous security agent for TBO travel APIs:

1. Recon: The system automatically maps all endpoints by watching traffic, without needing Swagger or documentation.
2. Inventory: It flags active APIs, forgotten zombie APIs (like old /v1/ routes), and shadow APIs.
3. AI Attack Engine: Instead of spraying random payloads, an LLM looks at the endpoints and figures out real business-logic attacks (price tampering, booking theft, auth bypass).
4. Safe Execution & Verification: The agent runs the test safely, verifies the bug with clean proof (HTTP request/response), and creates a ready-to-fix ticket with a retest option.


TEAM ROLES

1. S4NTY3119 (Backend & AI Lead)
- Build the LLM attack planner: give endpoints to the LLM to figure out smart business logic exploits.
- Build the exploit runner: safely fire the attack payloads with rate limiting.
- Build the verifier: confirm if the exploit succeeded and score the severity.

2. dharanii-07 (Backend & Recon)
- Build the traffic sniffer / log parser to extract all API routes and parameters.
- Build the zombie and shadow API detection logic.
- Set up the SQLite database to store endpoints, findings, and logs, plus basic REST APIs for the UI.

3. arun-hitesh (Frontend - Command Center)
- Main dashboard screen: total endpoints scanned, zombie count, critical bugs.
- Live attack feed: real-time stream showing what the agent is scanning and attacking.
- Safety controls: emergency pause button (kill switch).

4. Frontend Teammate 2 (Frontend - Visuals & Proofs)
- Visual API map: clean interactive tree showing all endpoints (active, zombie, shadow).
- Vulnerability modal: clicking a bug shows the exact HTTP request, response proof, and a Retest button.

5. Teammate 5 (Mock Data & Pitch)
- Generate fake travel traffic and sample booking JSONs.
- Prepare the demo script and slides for the judges.


PROJECT FOLDERS

/backend -> AI agent engine, API scanner, database, REST routes
/frontend -> Next.js / React dashboard
/target-app -> Small mock travel booking API with intentional bugs to test our agent
