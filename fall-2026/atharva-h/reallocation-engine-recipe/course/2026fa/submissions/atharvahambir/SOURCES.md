# SOURCES — what this work is built on, and who did what

## Executive summary

This page credits everything this submission uses: the repository and its rules, the data it reads, the code it reuses, the outside services it contacted, and the tools that built it. It also says plainly which parts an AI agent produced and which parts I decided, checked, changed or rejected. All the code and most of the text were written by an AI coding agent working at my direction. The career situation, the design of the daily checker, the filters, the persona, the gate answers and the lifecycle claim are my decisions. I read the final reports and signed the worked-run attestation.

---

## The repository and its rules

| Source | Use |
|---|---|
| `nikbearbrown/the-reallocation-engine`, cloned at commit `015843d` (2026-09-30) — code MIT, book CC BY 4.0 (per its `status.md`) | the engine this recipe extends |
| `SNICKERDOODLE.md` | labels, gates, lifecycle, attestation format |
| `DOMAIN.md` (incl. *Known gaps*), `status.md` | what runs today; the facts the recipe accounts for |
| `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/workflows/contrib-gate.yml` | namespaces, `BROKEN-*` mutant convention, what CI checks (Node 20, Python 3.12) |
| `DATA_CONTRACT.md` §Zero-Conditions | why the committed runs use a fictional persona |
| `recipes/README.md`, `recipes/_shared.md` | recipe contract; run-log entry format |
| `recipes/local-wage-adjustment.md` + `.card.md`, `recipes/scan.md` | style models for the recipe and card (and, for `scan.md`, patterns to avoid) |
| `book/chapters/10-the-visa-timeline-manager.md` (read in part), `book/chapters/07-who-sponsors-the-80-days-sponsorship-scorer.md` (searched) | the timeline factor's three worked cases; Unknown ≠ Avoid; tier cut-offs unpinned |
| The course assignment, *The Reallocation Engine — Recipe Design Assignment* (INFO 7375, Fall 2026) | requirements, rubric, file layout |

The 3-3-2 essay is referred to only as the framing the assignment gives. **None of its figures are cited.**

## Data read

| Data | Path | Notes |
|---|---|---|
| 80 Days to Stay sponsorship CSV | `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` | sha256 `eccdee2addf472b1639269f42eec693b083b7ce251347d5fd0b2856cfdae6270`; 30,369 rows, 1,557 with H-1B fields; fiscal years not documented |
| BLS / O*NET compact table | `data/bls/compact/soc_occupation_compact.csv` | national median wages, display only |
| SEC Form D samples | `data/sec/form-d/processed/sample/*.sample.json` | checked: 0 of 196 companies match the CSV, so not used |
| Scorer example | `data/examples/ch11-roles.json` | input shape, and the Proven/Likely p values 0.9 / 0.6 |
| Fixtures (synthetic) | `scripts/contrib/2026fa/atharvahambir-reallocation-engine/fixtures/` | invented postings in the Greenhouse/Ashby API shapes; E-Verify values made up for tests |
| Fictional persona | `search/examples/atharva/` | first name only; every other detail invented |

## Code reused (not copied)

- `.claude/skills/greenhouse-watch/scripts/greenhouse_watch.py` — `board_url()`, `fetch_board()`, `normalize_jobs()`, imported unmodified.
- `scripts/score/role-scorer.mjs` — run as a subprocess; makes every Apply / Consider / Skip call.
- Run during setup and checks: `scripts/ats/scan.mjs`, `scripts/ats/check-liveness.mjs`, `scripts/conformance.mjs`, `scripts/manifest-check.mjs`, `scripts/doctor.mjs`, `scripts/pii-scan.mjs`.

## Outside services contacted

- **Greenhouse boards API** (`boards-api.greenhouse.io`). Setup probes (Databricks, Airbnb, Stripe and others, to find boards with data roles); the live worked run (Robinhood).
- **Ashby posting API** (`api.ashbyhq.com`). Exploratory probes only (Benchling, Notion, Plaid and others); no submitted run fetched Ashby live.
- **Company careers pages**, through `npm run ats:liveness` during setup (Databricks, Airbnb).
- **npm registry** (`npm install`) and **Playwright's browser download** (Chrome Headless Shell 151, approved by me) during setup.
- **GitHub API**, read-only via `gh`, to see the course repo's folder layout and my access.

## Tools

- **Claude Code** (Anthropic's Claude, running as a coding agent in the Claude desktop app), the AI agent for this work.
- Python 3.12 (a `.venv` with PyYAML) and 3.14, Node 26 locally (the code also targets Node 20, which CI uses), git, the GitHub CLI.

## Collaborators

None.

## What the AI did vs. what I did

| Area | AI agent | Me |
|---|---|---|
| Career situation | — | chose it: entry-level data roles, OPT end date ~90 days out, needs H-1B; then STEM eligibility |
| Design | first proposed scoring a list of roles from the CSV | **replaced it** with a daily checker over my own target companies' boards; Greenhouse + Ashby first, more sources one at a time |
| Filters and parameters | proposed the tier cut-offs, timeline curve, title word rules (incl. excluding "intern") and SOC mapping | set the titles, 0–3 years, US / US-remote, keep-and-flag for unstated experience, 8-week default; **approved** the four parameter groups as heuristics |
| Code, tests, fixtures, break mutants | wrote all of it; found and fixed the bugs logged in FRICTIONAL | reviewed the results it reported |
| Persona | built it from scratch without reading the other personas | **rejected** using an existing persona; asked for the name "Atharva"; chose to move every other detail away from mine |
| Recipe and card | read the style models and wrote them; entered plan mode as the repo requires | chose RUNNABLE-SAMPLE (the assignment's way); **sent seven corrections** to the plan, all applied |
| Worked run | ran the commands; did the CSV cross-check and the break attempt | chose Robinhood; answered gates G5 (legal name) and G4 (E-Verify, my statement) |
| Privacy | flagged that real immigration details can't be committed; kept my data in `private/` | decided the tool is for me and my real data stays private |
| Submission | prepared the folder, commits and ZIP | chose the push location; push only on my say-so |
| Checking the final outputs | ran every check and saved the output | read the reports; recorded my decisions in both run logs and signed the worked-run attestation (2026-10-03) |

Full chronology with traces: `FRICTIONAL.md` in this folder.
