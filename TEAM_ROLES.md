# Team Tasks - Who Does What

### 1. You (@S4NTY3119) — The Hacker Brain
* Write the LLM agent that reads endpoints and figures out attacks (e.g. change price to 0, steal another user's booking ID).
* Send the attack requests and catch the response.
* Write the logic that confirms "Yup, this is broken" and grades the bug (Critical/High).

### 2. @dharanii-07 — Backend & Traffic Scanner
* Build the traffic parser: take network logs / crawl the target app and pull out all URLs and params.
* Label endpoints:
  * **Active:** Normal working APIs.
  * **Zombie:** Old/forgotten APIs (e.g. `/v1/` routes) that nobody uses but still run.
  * **Shadow:** APIs in use that nobody documented.
* Save everything into a local database (SQLite) and expose simple API routes for the frontend.

### 3. @arun-hitesh — Frontend: Main Dashboard
* Build the home dashboard:
  * Big numbers: Endpoints Scanned, Zombie APIs Found, Critical Bugs.
  * Live log terminal: shows what the agent is currently attacking in real time.
  * Emergency pause button (kill switch).

### 4. Frontend Teammate 2 — Frontend: Bug Details & Graph
* Visual graph/tree showing all API endpoints (green = safe/active, red = bugged, yellow = zombie).
* Bug detail card: Click a bug -> see the raw HTTP request, the payload sent, and a "Retest" button.

### 5. Ghost Guy — Dummy Data & Slides
* Give him sample JSON files to fake flight/hotel booking traffic.
* If he shows up, make him work on the final PPT. If he doesn't, ignore him, we don't need him to build the app.

---

### Folder Plan
* `/backend` -> Agent brain + DB + APIs (You + Dharanii)
* `/frontend` -> Dashboard + UI (Arun + Teammate 2)
* `/target-app` -> Fake travel site with intentional bugs for our agent to hack
