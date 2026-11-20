RouteZero — Video Demo Guide
VoyageHack 4.0 | Track 4: Fraud Prevention & Security
Target video duration: 2 minutes 30 seconds

---

SETUP BEFORE RECORDING

1. Open Chrome. Go to: https://saisanthosh31.github.io/routezero/
2. Set browser zoom to 100%. Full-screen the window (F11).
3. Open OBS Studio or ShareX. Set resolution to 1920x1080, 30fps.
4. Record screen + microphone only. Turn off system audio.
5. Close all other tabs and notifications before starting.

---

WHAT TO SAY AND SHOW — TIMED BREAKDOWN

0:00 to 0:12 — Opening

Say this out loud:
"Travel APIs process millions of transactions daily — price lookups, booking confirmations, payment flows. Any one of them can be tampered before the request reaches the server. RouteZero finds those vulnerabilities before attackers do."

Show: Title card or just the RouteZero site hero section in full view.

---

0:12 to 0:28 — Problem Context

Say this:
"The root cause is a missing automated security layer in the travel API pipeline. RouteZero is an agentic, real-time Dynamic Application Security Testing engine — built specifically for travel platforms."

Show: Slowly scroll through the Problem Statement and 5 Whys section on the site.

---

0:28 to 0:42 — Architecture

Say this:
"It runs in four stages: Discover endpoints from live traffic, Map the attack surface, Exploit with safe proof-of-concept payloads, and Remediate with code fixes — all without human input."

Show: Scroll to the Architecture section. Pause on the 4-stage pipeline.

---

0:42 to 0:50 — Enter Target and Open Console

Say this:
"Here is the live security console. You can point it at any travel API — TBO staging, MakeMyTrip, Cleartrip, or any custom host."

Show: Click "Live Demo" in the nav. The console section comes into view. The target host field shows "https://staging.tbo.com". Leave it as is or type another travel site URL.

---

0:50 to 1:05 — Execute the Scan

Say this:
"One click triggers the full autonomous loop — no manual configuration, no scripting."

Show: Click "EXECUTE AUTONOMOUS SCAN". Watch the left panel stream log lines from RECON, PLANNER, EXECUTOR, and VERIFIER agents one by one. Let it run to completion — takes about 7 seconds.

---

1:05 to 1:28 — Findings

Say this:
"Four confirmed vulnerabilities. Price tampering — a booking was created at one dollar. Cross-agency IDOR — passenger passport numbers accessed across tenant boundaries, violating DPDP. A zombie route leaking discount codes. And a shadow admin route exposing internal credentials."

Show: The right panel now shows 4 vulnerability cards. Keep them in view.

---

1:28 to 1:45 — Inspect Proof

Say this:
"Every finding comes with a reproducible curl command and a targeted code fix. This is not a theoretical flag — it is a confirmed exploit with server response evidence."

Show: Click "Inspect Proof" on the first card — Flight Booking Price Tampering. The modal opens. Highlight the curl command block. Scroll down in the modal to show the Code Fix section.

---

1:45 to 1:55 — Export

Say this:
"The full scan result exports as an OpenAPI 3.0 specification — ready for any CI/CD pipeline or security dashboard."

Show: Close the modal. Click "Export OpenAPI 3.0" in the top bar. A JSON file downloads automatically.

---

1:55 to 2:10 — Safety

Say this:
"RouteZero operates within strict safety boundaries. A scope allowlist prevents scanning outside the target. Rate limiting caps throughput. And a kill switch halts all activity instantly."

Show: Click "Safety" in the nav. Scroll to the Safety Guardrails section. Click the "SAFETY GUARD: ARMED" toggle once to show it switches to PAUSED. Click it again to re-arm.

---

2:10 to 2:22 — Team and Links

Say this:
"Built by Team RouteZero for VoyageHack 4.0 — Sai Santhosh, Dharani, Arun Hitesh, Mythreyan, and Ravi Kiran."

Show: Scroll to the footer. The team section is visible. Then show the browser address bar with the GitHub Pages URL.

---

2:22 to 2:30 — Closing

Say this:
"RouteZero. Find it before they do."

Show: Hold on the hero section or a clean view of the site title. Fade out or cut.

---

SUBTITLE FILE INSTRUCTIONS

Your subtitle file is RouteZero_Demo_Subtitles.srt in the same folder.

How to use it in your video editor:

CapCut (desktop):
1. Import your recorded video.
2. Click "Text" in the left sidebar, then "Auto Captions" or "Import Subtitles".
3. Choose "Import Subtitles" and select RouteZero_Demo_Subtitles.srt.
4. Adjust font to something clean like Inter or Montserrat, white text, dark background bar or drop shadow.
5. Export at 1080p.

DaVinci Resolve (free):
1. Import your video clip into the timeline.
2. Go to Timeline menu — Import Subtitle — select the .srt file.
3. It will drop all subtitle clips onto a subtitle track, pre-timed.
4. Right-click the subtitle track to change font, size, and position.
5. Export via Deliver — select MP4 — Burn Subtitles: Off (they will sidecar) or On (baked in).

Premiere Pro:
1. Open the project. Go to File — Import. Select the .srt file.
2. It lands in your project panel as a caption file.
3. Drag it to the timeline above your video clip.
4. Use the "Captions" workspace to style it.

If the subtitle timing is off from your actual recording pace:
Open RouteZero_Demo_Subtitles.srt in Notepad. Each block has two timestamps like:
00:00:04,500 --> 00:00:08,500
Adjust the numbers manually to match where you actually said each line.
Format is: HH:MM:SS,milliseconds

---

RECORDING CHECKLIST

Before hitting record:
- Browser full-screen, zoom 100%
- Notifications off (Windows: Focus Assist on)
- Mic tested and levels set
- Site loaded and console visible

During recording:
- Speak at a steady pace — do not rush
- Pause 1 to 2 seconds after every click before narrating the result
- Move the cursor slowly and deliberately
- Do not click randomly — every click should be intentional

After recording:
- Trim the start and end silence in your editor
- Import the .srt file
- Export as MP4, 1080p, minimum 8 Mbps bitrate
- File name: RouteZero_VoyageHack_Demo.mp4

---

SUBMISSION CHECKLIST

Video file: RouteZero_VoyageHack_Demo.mp4
Presentation: RouteZero_VoyageHack_Submission.pptx
Live site: https://saisanthosh31.github.io/routezero/
GitHub: https://github.com/SaiSanthosh31/routezero
Topic dropdown: Fraud Prevention & security
