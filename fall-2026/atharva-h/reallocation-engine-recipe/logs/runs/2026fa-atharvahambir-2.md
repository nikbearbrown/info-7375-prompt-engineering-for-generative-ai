# Run 2 — data-roles daily check — 2026-10-03

## Executive summary

This records the first live run of the daily data-role checker, against one real company's job board (Robinhood). The candidate was a fictional persona. The board had 162 postings and none fit entry-level data work. Once a named person confirmed the company's legal name and stated its E-Verify status, the company came out as a sponsor on record to network into rather than apply to. A deliberate typo in the board link made the run stop cleanly. Two display bugs found here were fixed.

## Record

*Paths below are as they were at run time; the folder and recipe were renamed from `atharvahambir-data-roles-opt90-h1b-daily` to `atharvahambir-reallocation-engine` on 2026-10-03 (current recipe: `recipes/cases/2026fa/atharvahambir-reallocation-engine.md`).*

- **Recipe:** atharvahambir-data-roles-opt90-h1b-daily v0.1.0 (`recipes/cases/2026fa/atharvahambir-data-roles-opt90-h1b-daily.md`)
- **Mode:** live (board API `boards-api.greenhouse.io`), three steps
- **Commands:** exact commands and output in `course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/step1-command-output.txt`, `step2-command-output.txt`, `step3-command-output.txt`; write-up in `course/2026fa/submissions/atharvahambir/WORKED-RUN.md`
- **Inputs:** candidate `search/examples/atharva/daily-check.candidate.json` (fictional) · targets `course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/targets.step1.json` / `targets.step2.json` / `targets.step3-break.json` · sponsorship CSV sha256 `eccdee2addf472b1…` · board response sha256 `a6ac36d2a87278…` (1,751,334 bytes, identical in steps 1 and 2; kept local, not committed)
- **Outputs:** `course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/step1/`, `course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/step2/`, `course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/step3/` → `daily-check.{json,md}` (+ `state.json` for steps 1–2)
- **Result:**
  - Step 1: boards read 1/1 · listed 162 · matching 0 · network 0. Robinhood "no row"; the hint named `ROBINHOOD MARKETS INC`.
  - Step 2: listed 162 · matching 0 · network 1 (Robinhood, Proven: 824 approvals, 97.2%).
  - Step 3: exit 4, board 404.
- **Gates:**
  - G0: passed.
  - G1: step 3 board unreadable (404), so exit 4.
  - G2: 162 postings listed (record).
  - G3: factor 0.633 (start 2026-11-28, deadline 2026-12-17, 19 days slack against a 30-day buffer).
  - G4: E-Verify enrolled, stated by Atharva Hambir.
  - G5: `csv_name` confirmed by Atharva Hambir.
  - G6: scorer not called (nothing matched).
- **Human decision (G7):** gate answers G4 and G5 given by Atharva Hambir on 2026-10-03. After reading the reports, Atharva Hambir, 2026-10-03 — "Reviewed; the result makes sense. I would network into Robinhood rather than apply today: find a data or analytics contact on LinkedIn, ask for an informational chat, and keep rechecking the board for a matching entry-level role."
- **Open issues:**
  - Fixed: the similar-name hint was printed twice (step 1 report kept as produced), and the stop-report wording pointed the wrong way. Tests re-run after both fixes: 18 OK, 4/4 mutants caught.
  - The title phrases miss data-analyst roles worded differently ("Data Solutions & Analytics … Analyst"); a near-miss list is proposed.
  - E-Verify is user-stated, not verified.
  - No live matching posting was available to exercise live scoring.
