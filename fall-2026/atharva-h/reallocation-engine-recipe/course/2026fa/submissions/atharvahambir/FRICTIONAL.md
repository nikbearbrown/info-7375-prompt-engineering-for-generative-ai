# FRICTIONAL — Data Analyst / OPT-90 / H-1B recipe

## Executive summary

This is an honest log of what happened while setting up and planning this assignment: what was tried, what was expected, what broke, how it was fixed, and who did what. The work so far was done in one session with an AI coding agent (Claude Code). The agent ran the commands, diagnosed the errors and proposed the fixes; I chose the career situation, supplied my visa facts, approved the one download, set the rule that everything stays local until I know where to push, and rejected the agent's suggestion to use a fictional persona for my own runs. Five things broke or surprised us during setup; all five are recorded below with the output that shows them.

---

## Record

- **Student:** Atharva Hambir (GitHub `AtharvaHambir`)
- **Agent:** Claude Code (Claude Opus), run from the desktop app
- **Repo state:** fresh clone of `nikbearbrown/the-reallocation-engine` at commit `015843d`; no commits made, push disabled locally
- **Raw evidence:** `runs/baseline-2026-09-30/` (terminal output captured at the time, unedited except one redaction noted in entry 6)
- **Log policy:** entries are appended in order; nothing earlier is rewritten.

**Who did what — key used below:** **Me** = my decision or input. **AI** = done by the agent. **AI → Me** = agent proposed, I accepted / modified / rejected.

---

## Entries

### 1. `npm run verify` fails on a fresh clone — 2026-09-30

- **Tried (AI):** `npm install`, then `npm run doctor` and `npm run verify` as the assignment's setup step 3.
- **Expected:** both pass; the assignment lists the local-wage script as a fresh-clone failure (Fact 7), but not `verify`.
- **Happened:** `doctor` passed ("environment: ✓ runnable"). `verify` exited 1: conformance passed, then `manifest-check` crashed with `ModuleNotFoundError: No module named 'yaml'`. It shells out to bare `python3`, which on this Mac is Python 3.14 without PyYAML.
- **Response (AI):** confirmed `.venv/` is gitignored, created `.venv` with Python 3.12, installed `pyyaml`, re-ran `verify` inside it → passed with 3 warnings. Nothing tracked changed.
- **Learned:** Fact 7's missing-venv problem is wider than the assignment says — it also breaks `verify`, the command every PR must paste. Anyone running `verify` needs `source .venv/bin/activate` first.
- **Open:** is this a known issue or specific to machines whose default `python3` lacks PyYAML? Not yet checked on another machine.
- **Trace:** `runs/baseline-2026-09-30/baseline-verify.txt` (failure), `baseline-verify-venv.txt` (pass).

### 2. `verify` warns that private folders aren't gitignored — 2026-09-30

- **Happened:** `manifest-check` printed `W2 private path not gitignored (PII/secret risk): private/` and the same for `data/ats/`, which contradicts the assignment's statement that both are gitignored.
- **Checked (AI):** `git check-ignore -v` on files inside each folder → ignored by `/private/*` and `/data/ats/*`; only `private/README.md`, `private/.gitkeep`, `data/ats/portals.example.yml` are tracked.
- **Learned:** false alarm — the check tests the directory path, not its contents. Recorded so I don't "fix" `.gitignore` (weakening it is itself a zero-condition offense).

### 3. `ats:scan --dry-run` needs a config the clone doesn't have — 2026-09-30

- **Tried (AI):** `npm run ats:scan -- --dry-run` exactly as written in the assignment.
- **Happened:** `Error: portals.yml not found. Run onboarding first.` (exit 1).
- **Response (AI):** read `scripts/ats/scan.mjs` — it reads `REALLOCATION_ENGINE_PORTALS` or defaults to `data/ats/portals.yml`. Ran with `REALLOCATION_ENGINE_PORTALS=data/ats/portals.example.yml` instead of copying a file into the repo → 1 company (Databricks), 878 jobs, 71 after title/location filters.
- **Learned:** the assignment's command does not run on a fresh clone as written. The env-var route avoids creating any file.
- **Trace:** `runs/baseline-2026-09-30/baseline-ats-scan.txt`.

### 4. Liveness: missing browser, then a redirect loop — 2026-09-30

- **Tried (AI):** `npm run ats:liveness -- <Databricks analyst posting>`.
- **Happened (a):** Playwright's headless Chromium wasn't installed.
- **Response:** AI → Me: the agent asked before downloading (~95 MB); **I approved**; the agent ran `npx playwright install chromium`.
- **Happened (b):** the Databricks posting came back `⚠️ uncertain … ERR_TOO_MANY_REDIRECTS` — on both the company-site URL and the Greenhouse URL, because Databricks' Greenhouse board redirects back to its own site.
- **Checked (AI):** a fake job ID (`…/databricks/jobs/1111111111`) → `❌ expired`; a real Airbnb analytics posting → `✅ active` (exit 0). So the checker works; Databricks specifically can't be read.
- **Learned, and it changed the design:** the checker has three outcomes, not two, and its exit code (1 for anything not active) can't tell "uncertain" from "expired." The recipe's liveness gate now holds `uncertain` roles for a human instead of scoring them as live or dead. A large sponsor landing in "uncertain" means this will be common, not rare.
- **Also noticed:** the first Databricks match for "analyst" was a "P2P Data & Automation Lead" — keyword matching picks wrong roles. Fed into prediction 1 of the brief.
- **Trace:** `baseline-liveness.txt`, `baseline-liveness-gh.txt`, `baseline-liveness-dead.txt`, `baseline-liveness-airbnb.txt`.

### 5. The data can't support what the recipe first assumed — 2026-09-30

- **Tried (AI):** profiled the sponsorship CSV and the Form D samples before writing the brief.
- **Expected:** a usable funding join and broad H-1B coverage (the dataset is described as "30,000+ leads").
- **Happened:** only 1,557 of 30,369 rows carry H-1B fields; 34 list a "data analyst" title; there is no SOC column. The 196 Form D sample companies match **0** CSV companies by normalized name (the first attempt reported 1 name / 0 matches because the script read the wrong JSON key; fixed by reading `company.company_name_normalized`). Two companies (APRICUS / ASCUS BIOSCIENCES) have identical H-1B records — a likely join artifact.
- **Response:** funding is reported as unavailable on sample data rather than used; "no record" is treated as Unknown, never as "doesn't sponsor."
- **Trace:** `CHANGE-BRIEF.md` §2, §4.

### 6. Decisions I made, and the privacy correction they caused — 2026-09-30

- **Me:** chose the situation — MS student, Data Analyst roles, OPT **end date** ~90 days out (when the agent asked whether I meant end date or unemployment days, I clarified: end date), targeting H-1B sponsors.
- **Me:** told the agent my program is STEM. **AI:** added a dated revision to the brief — 150-day unemployment ceiling; the current end date still bounds the search because the extension needs an E-Verify employer; new E-Verify gate and failure case F7. The agent flagged that the E-Verify/extension reasoning is its understanding and must be confirmed with my DSO — **open until I do that.**
- **AI → Me, rejected:** after reading DATA_CONTRACT §Zero-Conditions, the agent pointed out the brief contained my real OPT end date (immigration details = PII if committed) and proposed switching to a fictional persona. **I rejected using a persona for my own runs** — I will use this tool for my actual search. **Resolution (AI, accepted by me):** real profile in `private/profile.yml` (gitignored, confirmed with `git status --ignored`); the brief says "about 90 days out"; committed fixtures and the worked run will use an invented persona; the prototype takes `--profile` with no default so committed code never reads `private/`.
- **Me:** decided nothing goes to GitHub until I know where to push; all work stays local.
- **AI:** while copying baseline output into this folder, `pii-scan.mjs` flagged an npm package author's email inside `npm-install.txt` (npm deprecation notice). Redacted in our copy only. The same address in `package-lock.json` is upstream and not mine.
- **Trace:** `CHANGE-BRIEF.md` → *Revisions* r1; `pii-scan.mjs` output (to be pasted in TEST-REPORT).

### 7. Design change: from "score roles" to a daily checker — 2026-09-30

- **Before:** the plan (brief §1–§5) scored a list of roles I had already found, using the sponsorship CSV.
- **Me — the idea:** I didn't want a scorer for roles I'd already found. I wanted a checker over *my own* target companies' job boards (Greenhouse, Ashby and similar): I pick the companies and supply their board links, and the recipe runs daily to find new postings worth my time.
- **AI:** checked what already exists before designing: `scripts/ats/scan.mjs` already reads Greenhouse / Lever / Ashby boards and remembers what it has seen (the "new since yesterday" core); `scripts/ats/providers/` has one small file per board. Found one gap: the providers return title / link / location only — no job text, so an experience filter needs new code.
- **AI → Me, answered:** the agent asked eight design questions; my answers are the spec:
  - one command I run each morning (no automatic schedule yet);
  - titles: Data Analyst, Data Analyst I, Associate Data Analyst, Business Analyst, Business Intelligence Analyst, Analytics Engineer, Data Engineer, Data Engineer I, Associate Data Engineer — no senior roles, 0–3 years of experience;
  - postings that don't state experience: keep and flag, never guess;
  - location: any US city or US-remote;
  - every new posting gets scored (sponsorship, E-Verify, liveness, timeline), not just listed;
  - hiring time: one default plus per-company overrides — **I set the default to 8 weeks**;
  - slug renamed to `data-roles-opt90-h1b-daily`, because Data Engineer maps to a different occupation code than Data Analyst;
  - **modified the agent's proposal:** it recommended marking Workday / iCIMS / other boards "out of scope." I chose Greenhouse + Ashby now and adding **one source at a time** later, so the tool grows with my search.
- **Consequence the AI pointed out:** a posting returned by the company's own board is a *record* that it's open, which is better liveness evidence than the browser check that looped on Databricks (entry 4).
- **Trace:** `CHANGE-BRIEF.md` → *Revisions* r2 (new failure cases F8–F10).

### 8. Building the prototype — 2026-09-30

- **AI — reuse before writing:** before writing code the agent found the repo's `greenhouse-watch` skill (described in its own docs as the default recipe for this term) and reused its fetcher — `board_url()`, `fetch_board()`, `normalize_jobs()` — instead of writing a new one: it already covers Greenhouse + Ashby, returns the job text the experience filter needs, and enforces the host allow-list with no redirects. SmartRecruiters is already in it, so it's the obvious "next source" when I add one.
- **AI — constraints found by reading the repo, not guessed:** CI runs Node 20 and Python 3.12; the conformance check skips folders named `data`/`output`/`tools`; `pii-scan.mjs` flags files *named* `profile.yml` / `resume.json` anywhere in the working tree, ignored or not. So the prototype is stdlib-only Python, reads JSON (YAML optional), and uses its own `candidate.json` format.
- **Tried (AI):** first offline sample run.
- **Expected:** a prediction written before running — Apply 6 · Consider 1 · Skip 2 · Held 4, 1 network target, 2 boards not checked.
- **Happened:** the counts matched exactly, but reading the report row by row found real problems the counts hid:
  - Coinbase was reported "no row in the sponsorship data" — wrong. The data has it as `COINBASE GLOBAL INC`; the exact name match missed, and the "did you mean" hint only listed companies *with* H-1B data, so it said nothing. My F2 test case had silently become an F1 case.
  - Apricus was labeled "no record" although a record exists — it is *untrusted* (duplicate of ASCUS), which is different.
  - the scorer's own line said "Apply 8" while the report said Apply 6, with nothing explaining the gap (the recipe's E-Verify gate applies after the scorer).
- **Response (AI):** hints now include rows without H-1B data; each held row names its exact status; the report explains that the scorer's counts come before the recipe's gates; the fixture gets `csv_name: COINBASE GLOBAL INC` so F2 is really exercised.
- **Learned:** matching counts proved nothing — the content was wrong in three places. Real employer names differ from legal names often enough (Notion → NOTION LABS INC, Coinbase → COINBASE GLOBAL INC, Chime → CHIME INC vs CHIME FINANCIAL INC) that the exact-match rule needs the `csv_name` field and the hint.
- **Tested (AI):** 18 offline tests pass (`test_daily_check.py`). **Deliberate breaks:** three one-line mutants — let a past OPT date through; score "unknown sponsorship" as a non-sponsor; ignore the E-Verify gate — each made the suite fail; the original was restored and byte-compared.
- **AI → Me, not yet reviewed:** migrated my real profile to `private/daily-check/candidate.json` + `targets.json` and removed `private/profile.yml` (same content; the old name kept tripping the PII scan). A run on my real inputs stops at the intake gate — unemployment days used, buffer days and my fit values are still empty, by design.
- **Open:** the filters have only run on synthetic postings; how they behave on real boards (prediction 1 in the brief) is untested until a live run.
- **Trace:** `scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/`; `runs/prototype-2026-09-30/mutation-check.txt`.

### 9. A fictional persona of my own, repeatable break attempts, a local branch — 2026-10-03

- **Why (AI, from reading CONTRIBUTING.md and the PR template):** two gaps against the repo's own rules — break-attempt mutants are expected as `BROKEN-*` files in `fixtures/` (mine existed only as a saved log of hand edits), and the PR's privacy box asks that demos use fictional personas in `search/examples/` (my sample used a stand-in file inside my own folder).
- **Me:** I chose to create **my own** fictional persona instead of reusing one of the four existing personas, and told the agent not to use (or read) the others. Following the assignment's rule — real data stays private; an invented persona uses `@example.com` addresses — the persona is fictional: invented school, jobs, city and dates, a 555 phone number, an `@example.com` email, but the same *shape* of situation as mine (MS, entry-level data roles, OPT ending about 90 days out, STEM, needs H-1B and an E-Verify employer).
- **AI:** wrote the persona pack (`profile.yml`, `resume.example.json`, `gaps.md`, and `daily-check.candidate.json` in the checker's input format) under `search/examples/`; switched the sample run and tests to it; removed the old stand-in fixture after checking its values were identical. `pii-scan.mjs` raises nothing on the persona.
- **AI — repeatable break attempts:** `fixtures/BROKEN-mutants.json` lists four mutants as exact one-line edits (past OPT date passes the intake gate; "no sponsorship record" scored as a non-sponsor; E-Verify gate ignored; a start date after the deadline gets 0.5 instead of 0). `break_attempts.py` builds each in a temporary copy — the real file is never edited — runs the suite with `DAILY_CHECK_SCRIPT` pointed at it, and requires a named test to fail. **Result: all 4 caught.** Needed one code change: the script now finds the repo root by walking up, so a copy can run from a temporary folder.
- **AI — branch:** created `contrib/2026fa-atharvahambir-data-roles-opt90-h1b-daily` locally; no commits; pushing to the instructor's repo stays disabled. **Me:** everything stays local until I know where to push.
- **AI — evidence:** the outputs saved earlier the same day no longer matched the changed code, so they were re-captured (tests 18/18, sample run, conformance, verify, doctor, PII scan, git status, break attempts) and the index notes the overwrite.
- **Trace:** `search/examples/<persona>/`; `scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/{break_attempts.py,fixtures/BROKEN-mutants.json}`; `runs/evidence-2026-10-03/09-break-attempts.txt`; `runs/INDEX.md`.

### 10. Writing the recipe and card — 2026-10-03

- **AI:** read the style references (`recipes/local-wage-adjustment.md` + `.card.md`, `recipes/scan.md`, `recipes/_shared.md`), entered plan mode (the repo's `CLAUDE.md` requires it before editing `recipes/`), and proposed a section-by-section plan.
- **AI → Me, two decisions I made:**
  - *Lifecycle status.* The agent pointed out that `SNICKERDOODLE.md` requires zero open TODOs for SPECIFIED, while the assignment requires the proposed additions to be listed as TODOs. **I chose the assignment's way:** RUNNABLE-SAMPLE. I accepted it because there is a reproducible sample run (tests, break mutants, saved output) but no live-run evidence, so RUNNABLE-LIVE is not claimed and the attestation stays null. The seven proposed additions are framed as roadmap items outside the demonstrated sample path.
  - *Parameters.* I reviewed and approved the four parameter groups the agent had proposed while building: sponsorship tiers, timeline curve, title word rules, title→SOC mapping. I kept the tiers as **user-defined heuristics, not verified DOL facts**, and the SOC mapping **display-only**, because the BLS wage doesn't feed the scorer.
- **Me — I reviewed the plan and sent back seven corrections before anything was written:**
  1. Don't say the TODOs block SPECIFIED while claiming RUNNABLE-SAMPLE (internally inconsistent).
  2. Sponsorship must stay a **vote**. Missing evidence is an *evidence-sufficiency* hold ("Needs you"), never a sponsorship gate, never p = 0 or "non-sponsor".
  3. Don't claim "no model-judgment" if text heuristics infer things. The recipe now says no language model is called, and names the three fixed text rules as rule readings of record text.
  4. Don't call the PII scan clean while it reports a finding. Show a baseline-vs-branch comparison.
  5. Reword git status as "all changed files confined to my assigned namespaces".
  6. Write an actual `logs/runs/` entry, not just a template.
  7. Name the OPT end date and the unemployment allowance as **two separate clocks**, and phrase E-Verify as **my** search constraint for the STEM-OPT pathway, not something the program determines.

  All seven were applied.
- **AI:** wrote `recipes/cases/2026fa/atharvahambir-data-roles-opt90-h1b-daily.md` (gates G0–G7, closed decisions, a verified-vs-inferred table, output contract, next action per result, the 8 "facts that bite", 7 typed proposed additions, failure cases mapped to tests, a run-log template), the card, and `logs/runs/2026fa-atharvahambir-1.md`. The run log leaves the human decision **pending** until I review the sample report myself.
- **Learned / honest gap found while writing:** failure case F5 (a sponsor on record with no matching title) shows in the report but has no dedicated test assertion; the recipe says so instead of claiming it's tested.
- **Broke during verification, fixed (AI):** the path check found my run log used `…/` to mean the evidence folder while the recipe used it to mean the prototype folder — both now spell out full paths. The PII baseline-vs-branch comparison first reported an extra finding: the output file was being written inside the repo while the scan ran, so the scan read its own half-written output (with the email not yet redacted). Redone writing outside the repo first → identical findings, 0 added.
- **Trace:** the recipe, card and run log above; `runs/evidence-2026-10-03/10-recipe-checks.txt`, `11-pii-baseline-vs-branch.txt`.

### 11. Worked run on a real board, and the domain justification — 2026-10-03

- **Me:** chose the worked run's target: Robinhood (`https://job-boards.greenhouse.io/robinhood`), my real target company, run as the fictional persona so no personal data is committed. I also added it to my private daily list.
- **Tried (AI):** step 1, a live run with the target exactly as I gave it. **Expected:** maybe one or two matching postings. **Happened:** 162 postings, **0 matching** (the closest were a Business Analyst *intern* and senior analyst roles). Robinhood came back "no row" because the CSV has it as `ROBINHOOD MARKETS INC`; the report suggested that row instead of calling Robinhood a non-sponsor.
- **Me, at the human gates:**
  - **G5:** confirmed Robinhood = `ROBINHOOD MARKETS INC` → `csv_name`.
  - **G4:** stated "it is E-verified" → recorded as my input, *not verified by the tool*.
- **AI:** step 2 → Proven (824 approvals, 97.2%) on the "Network, don't apply" list. Step 3, a deliberate typo in the board name → HTTP 404 → exit 4, nothing invented. Then a hand cross-check against CSV row 22735 (matched) and a sha256 comparison showing both live fetches read identical bytes.
- **Broke, fixed (AI):**
  - The step 1 report printed the similar-name hint twice.
  - The step 3 stop report said "fix what is named above" while the cause was listed below.

  Both are fixed in `daily_check.py`; tests and break mutants were re-run (18 OK, 4/4 caught). Also, one saved test capture first recorded a literal placeholder instead of the exit code (a quoting slip in the capture command); it was redone to record the real code.
- **Learned:**
  - The human gate mattered on real data: one answer turned "unknown" into a sourced sponsor record.
  - My title phrases miss data roles worded differently ("Data Solutions & Analytics Senior Analyst"), so prediction 1 in my brief was partly right. The proposed fix is a near-miss list in the report.
- **AI:** wrote `DOMAIN-JUSTIFICATION.md` (time saved stated as an estimate from listed assumptions, not a measurement), `WORKED-RUN.md` (real output pasted, verified-vs-inferred table, attestation) and `logs/runs/2026fa-atharvahambir-2.md`. **Open:** the attestation's sign-off box is unchecked until I read the reports myself.
- **Trace:** `runs/worked-run-2026-10-03/` (`step1–3-command-output.txt`, `cross-check.txt`, `after-fix-tests-and-breaks.txt`); `WORKED-RUN.md`; `logs/runs/2026fa-atharvahambir-2.md`.

### 12. Packaging the submission and the clean-checkout test — 2026-10-03

- **Me — where it goes:** the course repo, in my own folder `fall-2026/atharva-h/`, in a subfolder `reallocation-engine-recipe/` next to my Week 1 work. Inside it, the assignment's own layout: `recipes/cases/2026fa/…`, `scripts/contrib/2026fa/…`, `logs/runs/…`, `course/2026fa/submissions/…` (plus the persona under `search/examples/`). Local commits only; **nothing is pushed until I say so**. No pull request to the engine repo.
- **AI — the course repo's own rules, read before committing:** its `AGENTS.md` asks for one commit per lesson directory and no push without the user's authorization. Its CI (`scripts/validate_course.py`) fails on any `.js`/`.ts` file, any `.py` that doesn't parse, and any relative markdown link to a missing file. Those rules, run on my folder alone, flagged one thing: the README's link to this test report, which didn't exist yet.
- **AI — the clean-checkout test:** a fresh engine clone at `015843d` plus exactly the files staged for commit, copied in with the README's own `cp -R` command. `doctor` and `verify` behave identically before and after my files. The sample came out 6 / 1 / 2 / 4, 18 tests OK, 4/4 mutants caught. The past-OPT and missing-value runs stop with exit 2; the offline guard exits 1. The diff is only my namespaced paths. The PII finding is identical to the engine's own.
- **Broke during testing, fixed (AI):** the first capture saved `tail`'s exit code instead of the command's (`verify` without PyYAML showed `EXIT=0`); redone with `pipefail`. The comparison of committed and tested files was first planned for *after* the commit, which can't work because the result has to be inside the commit; moved to just before it. Reading the clean sample report showed run log 1 had Pinterest's preview score as 0.368; the report prints 0.367; corrected.
- **AI also wrote:** `SOURCES.md`, the CHANGE-BRIEF revision r3 (how each prediction turned out), the folder README, and `TEST-REPORT.md`.
- **Open:**
  - The assignment's PR to `the-reallocation-engine`, and its "CI green", aren't part of this submission location.
  - The engine's PII scan fails on its own lockfile.
  - My own read-through and sign-off of the reports is still to do.
- **Trace:** `TEST-REPORT.md`; `runs/clean-checkout-2026-10-03/` (`00`–`18`, `clean_test.sh.txt`); `SOURCES.md`; `CHANGE-BRIEF.md` → r3.

### 13. Fork, PR plan, and the slug rename — 2026-10-03

- **Me:** asked whether a fork existed (it didn't) and had one made: `AtharvaHambir/the-reallocation-engine`. The PR to `nikbearbrown/the-reallocation-engine` will come from it, and **the PR commit is the commit of record** for the Canvas ZIP. The course-repo folder carries an identical copy.
- **Me — renamed the slug** from `atharvahambir-data-roles-opt90-h1b-daily` to `atharvahambir-reallocation-engine`. That renames the prototype folder, the recipe and card files, and the branch (`contrib/2026fa-atharvahambir-reallocation-engine`). I kept my full name in the docs.
- **AI:** applied the rename to the code (the recipe id the script uses to find its own folder), README, recipe, card, persona profile and SOURCES. Saved terminal output under `runs/` was **not** edited, because it records what actually ran; WORKED-RUN and the two run logs carry a note that their pasted paths use the old name. Entries 1–12 above keep the old name too. After the rename: 18 tests OK, 4/4 mutants caught, sample unchanged (6 / 1 / 2 / 4). The clean-checkout test was rerun under the new name (`runs/clean-checkout-2026-10-03-renamed/`).
- **AI — remotes:** in the local clone, `origin` is now my fork, and the instructor's repo is `upstream` with pushing disabled.
- **Trace:** `TEST-REPORT.md`; `runs/clean-checkout-2026-10-03-renamed/`.

---

## What I accepted, modified, rejected (summary)

| AI proposal | My response |
|---|---|
| `.venv` + PyYAML to make `verify` pass | accepted |
| Env-var route for `ats:scan` instead of copying a config | accepted |
| Download Playwright Chromium | accepted (asked first) |
| Hold "uncertain" liveness for a human | accepted |
| Fictional persona instead of my own profile | **rejected** for my own runs; accepted for committed files only |
| Lowercase handle in folder names | accepted (renaming later is trivial) |
| Score a list of already-found roles | **replaced** with my daily-checker design (entry 7) |
| Other job boards "out of scope" | **modified**: Greenhouse + Ashby now, one new source at a time later |
| 8-week default hiring time | accepted (my number) |
| Reuse an existing persona from `search/examples/` | **rejected** — I had my own fictional persona created |
| Lifecycle: follow the constitution (DRAFT) or the assignment (RUNNABLE-SAMPLE) | chose **RUNNABLE-SAMPLE** (the assignment's way), no live-run claim |
| Four proposed parameter groups (tiers, timeline curve, title rules, SOC map) | **accepted** after review — tiers as heuristics, SOC map display-only |
| The recipe plan as first proposed | **modified** — I sent seven corrections; all applied |
| Worked-run target | **my choice**: Robinhood, my real target, run as the fictional persona |
| `csv_name: ROBINHOOD MARKETS INC` suggested by the report | **accepted** at gate G5 (the question showed that row's approvals, denials and rate) |
| E-Verify for Robinhood | **my statement** ("it is E-verified"), recorded as unverified your-input |
| Submission location | **my decision**: course repo, `fall-2026/atharva-h/reallocation-engine-recipe/`, assignment layout inside, local commits, push only on my say-so |
| PR and slug | **my decisions**: fork + PR from `contrib/2026fa-atharvahambir-reallocation-engine`; the PR commit is the commit of record; slug renamed to `atharvahambir-reallocation-engine`; full name kept |

## Unresolved questions

- STEM extension mechanics (E-Verify employer, I-983, filing deadline) — confirm with DSO.
- Where the final work gets pushed — no instructions from the professor yet.
- Whether the `verify` / PyYAML failure should be reported upstream.
- Values still missing from my private profile: unemployment days used, buffer target.
