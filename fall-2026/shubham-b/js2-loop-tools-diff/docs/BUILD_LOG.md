# Build log (written by Claude, the orchestrating session)

> **What this is.** A dated, factual record kept by Claude during the build: what was tried, what happened,
> what the student accepted, changed, or rejected, with commit hashes and test names. It is raw material for
> the student's `FRICTIONAL.md`, **not** a substitute for it. It contains no judgments attributed to the student
> beyond what they said or committed. Times are America/New_York.

## 2026-10-29

**17:24 Start.** The folder was empty. Claude ran the Claude Code setup analysis and read the official JS1
assignment, the AI policy, and the Frictional guidance from the course repo.

**~17:40 Declined request.** The student asked for CONTRACT.md and FRICTIONAL.md to be written "as I am writing it
in max humanize form". Claude declined to ghostwrite either file in the student's voice and cited
`prerequisites/ai-policy.md` ("do not ask AI to invent your struggle or understanding") and `frictional/06`.
Claude offered instead a question sheet for the contract and this factual log for FRICTIONAL.

**~17:50 Judge backend probe.** Claude tested `claude -p` headless calls under the student's subscription
(no API key in the environment). The default call cost $0.17 because it loaded all plugins and hooks. `--bare`
failed ("Not logged in", because bare mode needs an API key). An isolated call from an empty folder worked at
about $0.008 and about 1.9k context tokens.

**~18:00 Persona.** The student first asked for themselves as the persona. Claude pointed out that the assignment
forbids that ("Use a fictional persona, not yourself"). The student chose "new persona modeled on you". Claude
drafted `persona/kiran-joshi.resume.example.json`: fictional, `@example.com`, 555 phone, no real names, employers,
schools, or contacts, modeled only on the role targets and skill areas in the student's local career-ops profile.

**~18:05 Board choice, and a Claude mistake.** Claude recommended Greenhouse `datadog` based on a loose title regex
that counted every "Engineer" title. When the student's draft title rule was applied, **0 of 397** Datadog postings
passed: most were Sales Engineers, and the Software Engineer titles were Senior, Staff, or Intern. Claude reported
its own error. Probing the career-ops boards under the student's title rule put Stripe first (55 title-passing:
35 with ≥2 skills, 20 with <2). The student switched to Stripe.

**18:10–19:00 Contract reviews (Claude reviewed, student wrote).**
- Draft 1: Claude flagged a baseline that conflicted with the spec ("first run reports none as new"), the missing
  validator for Claude's output, Claude's 3-label scale versus the 2-label hand labels, `C#` turning into `c` under
  punctuation stripping (`c` matched 6–9 times per board), REST/React/Express matching as plain English, and HTML
  in `content`.
- The student's next draft fixed those and moved to Stripe.
- After the hand-check candidates were fetched, the student added a hard **US-only location rule**. Bengaluru
  posting 7543868 had passed title and skills.
- Claude verified every hand-check claim against the raw file. It found one wrong path (GraphQL is
  `$.skills.backend[4]`, not `[3]`) and showed that "clearly names a US city" was not hand-predictable on Stripe's
  294 real location strings (`SF, NYC, CHI, ATL, SEA`, `Remote in Canada`, `New York or San Francisco`).
- A later draft the student pasted said the workspace lacked files that did exist. Claude flagged those
  statements as false for the repo; that draft was not committed.

**18:40 Commit `053fda0`.** First contract, the student's text, committed (on the student's request) with the
student as author. Pushed.

**22:41Z (18:41 ET) Raw evidence.** Claude saved the Stripe response byte-for-byte:
`evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.json` (734 postings, HTTP 200; sha256 in `.meta.json`).
Claude picked hand-check candidates by title only. The student hand-evaluated four of them (8249901, 7543868,
8175099, 8234357).

**~19:10 Location lists and case 4.** At the student's request ("keep the us only rule and add hand checks"),
Claude:
- turned the US-only rule into finite signal lists built from all 294 distinct `location.name` values;
- computed complete skill lists for the hand-check postings;
- found 8127182 (only Java matches) as the fewer-than-two-skills case.

**19:15 / 19:19 Commits `c1bd530`, `7aa5d0f`.** The student committed the amended contract (the student removed
§18–§19 and then the dangling §19 reference). Claude committed the data files in `ba1d9f0` (persona, raw evidence,
.gitignore). The student asked to drop the Claude co-author trailer. Amending the pushed commit needs a force push,
which Claude Code's safety classifier blocked, so `ba1d9f0` keeps its trailer and later commits have none.

**19:30 Planning.**
- A fresh planning agent wrote `docs/PLAN.md`.
- A docs agent gathered Claude Code network and flag facts (`docs/claude-code-network-facts.md`).
- Claude reviewed the plan and added amendments R1–R8. R1 replaced the undocumented `--setting-sources ""` with
  the documented `--setting-sources project --safe-mode` plus three traffic-disabling env vars. It was verified
  19:33 ET: `is_error: false`, 1,642 context tokens. R2 corrected `Write(...)` permission rules, which never
  match per the docs, to `Edit(...)`.
- Commit `33ea56e`.

**21:01 Usage limit.** Work paused until the claude.ai usage limit reset, then resumed.

**21:05–21:20 WS0 foundation.** A fresh coding agent built the toolchain, shared models, ports, config, and test
harness (commit `1493176`). Claude re-ran the acceptance independently: ruff clean, `mypy --strict` clean on 16
files, pytest 96 passed / 1 skipped (live).

**21:25 WS1–WS4 launched** in parallel git worktrees with disjoint file ownership: rule core, policy edges,
orchestration, judge/experiments.

**21:30 WS4 network failure.** The first WS4 agent died on `ENOTFOUND` (API unreachable) before writing anything. It
was relaunched fresh at 21:33 ET.

**21:42 Merge WS2** (`e57a458`): résumé gate, fsio write policy, allow-list HTTP, privacy audit. Claude re-ran the gate
on main: 261 passed, 1 skipped.

**21:46 Merge WS3** (`138bcff`): state, status, sources, events, pipeline, report, CLI. Gate: 383 passed. `jsa doctor`
passed every check against the real résumé gate.

**21:50 Merge WS1** (`e867b51`): provider, four-gate rule, evidence validator. Gate: 758 passed; meta-test 3 passed.
- Wrong version A (title-only) was killed by 9 contract tests and B (substring counting) by 12.
- All five §13 hand checks reproduced exactly.
- `jsa rule --raw ... --id 8127182` gave NO_MATCH, failed gate SKILLS, evidence Java only.
- Location labels over the 734 hand-check postings were 335 US_BASED, 332 NON_US, 67 NOT_ESTABLISHED. Claude's earlier
  throwaway script gave 339/332/63; the difference is the `Tor`/`Toro` non-US entries added afterwards.

**21:52 Run 1, live baseline** (`30304b7`): `uv run jsa run --model-backend none` at clean commit `e867b51`.
- Status BASELINE: 736 fetched, 736 unique valid IDs, new 0, state saved.
- The board had 734 postings at 18:41 ET, so it had already changed.
- Raw sha256 `8f02cbe2…`. `verify-evidence` OK; `audit-privacy` 0 findings.

**22:00–22:20 Integration.** WS3's CLI and WS4's judge had been built against guessed signatures, so the first
`jsa run` that needed a judge would have crashed with `TypeError`. An integration agent fixed the seams and removed
duplicated policy code: two `SubprocessRunner`s, two JSONPath parsers, two skill extractors, and three strict-JSON
checks. It added 7 hermetic end-to-end tests (`tests/test_integration.py`) that all fail on the pre-integration
merge `1c334e9`. The existing test `test_no_count_constant` caught the string `734` in `prompt_experiment.py`
(contract §2), which turned out to be inside a hard-coded sha256. `select` now reads the pinned digest from
`.meta.json`. Gate: 944 passed; meta 3 passed. Pushed `f2f3565`.

**22:21 Real judge probe.** `jsa doctor --probe-model`: the R1 argv on the subscription, `is_error: false`, reply
`OK`, served model `claude-sonnet-5-5`, 1,454 ms, $0.008 (`data/doctor/2026-10-30T02-21-19Z.json`).

**22:21 Seeded pair (labeled SEEDED, no network).**
- S1 replayed the 18:41 ET hand-check response: BASELINE, 734 IDs.
- S2 replayed the 21:52 ET live response: SUCCESS_WITH_NEW, 3 new, all Account Executive titles (8330791, 8316059,
  8330813). Rule NO_MATCH with failed gates recorded; Claude VALID NOT_RELEVANT for all three. `audit-privacy`:
  0 findings.

**22:22 Prompt-experiment selection.** `jsa exp prompt select` at clean commit `3f54cac`, seed 20261029, drew
10 dev and 10 held-out postings from the hand-check file. Worksheets do not show the rule verdict. `strata.json`
is committed (sha recorded) and is not to be opened until `score`.

**22:25 Google-style review** launched (fresh read-only reviewer agent).

## 2026-10-30

**00:00–02:00 Usage limit.** The Google-style review agent stopped at the 5-hour usage limit and resumed after the reset
at 02:00 ET.

**02:05 Google-style review verdict: "Not yet → LGTM with comments".**
- Must-fix: an exception inside the judge (e.g. `PathRejected` from the work-dir maker) would abort the whole run with
  no report, contradicting §9/§10 (it should be ERROR plus PARTIAL_FAILURE).
- Should-fix:
  - The `claude` child env was a denylist, which fails open.
  - Nothing stopped two runs at once.
  - Path policy had four owners, and state reads bypassed `O_NOFOLLOW`.
  - Claude free text could echo résumé values into records (§12).
  - `VerifiedResume` was constructible by anyone.
  - Pre-spawn backend failures were mislabeled ERROR instead of UNAVAILABLE.
  - Several functions were over 40 lines.
- Plus 8 nits.

**02:10–02:32 Review fixes** (`b647a82..d53dabe`, 9 commits; a fresh fix agent, test-first, each regression test
failing before its fix).
- PLAN amendments R9 (allowlist env) and R10 (`RESUME_VALUE_ECHO` validator code).
- New exit code 7 (`LOCKED`) for concurrent runs or a same-second run-ID collision.
- Gate: 988 passed, 2 skipped; meta 3 passed.

**02:33 Probe after R9.** With the allowlist-only env, the real probe still authenticated on the subscription
(`is_error: false`, reply OK): `data/doctor/2026-10-30T06-33-30Z.json`. Pushed `91256f7`.

**02:35 Ponytail audit launched.** The student installed the ponytail plugin and asked for its audit after the fixes. A
fresh read-only agent follows `skills/ponytail-audit/SKILL.md`. Its focus: what to delete, merge or split, test bloat,
and TA usability.

**02:35 Sampling deliberately not run yet.** Chapter 1 asks for the student's prediction to be written before the run.
Claude is waiting for that one line rather than running first.

**02:45 Ponytail audit result.** The audit found 6 must-fixes:
- no README;
- trial runs would rewrite graded `data/`;
- the surfaces `capture` could drop a surface;
- "repo unchanged" was false after any commit;
- all-INVALID samples were reported as "unanimous and wrong";
- a crash mid-study blocked its table.

It also found about 1,000 lines of removable code and tests: toy doubles in the pipeline tests, injection hooks, dead
code, four Protocol copies of one writer, two state readers, tests of fakes, and an "unreviewed" location snapshot.
Claude chose to fix everything except the README (written later, in the docs phase) and to delete the snapshot,
keeping the independent oracle that parses CONTRACT §6.4.

**02:50–03:10 Audit fixes** (`b3f3d30..7188965`, 13 commits, a fresh fix agent).
- New `--data-dir` (trial runs go to the gitignored `data/scratch`).
- Experiment-harness bug fixes, each with a regression test.
- Pipeline tests now run on the real provider, rule, validator, `OutputRoot` and judge.
- src net −296 lines, tests net −615 Python lines plus −2,897 lines of snapshot JSON.
- Gate: 970 passed, 1 skipped (the v2-prompt test, which waits for the student's v2); meta 3 passed.

Claude removed the four merged agent worktrees and their branches, after confirming each was an ancestor of main.

**03:11–03:13 Chapter 3, action surfaces** (`8fea85b`), real `claude -p` sessions at commit `7188965`.
- (a) No tools: reply valid under §8; nothing read, written or sent.
- (b) Read on two sandbox files: read exactly those two; reply valid.
- (c) WebFetch limited to boards-api.greenhouse.io plus Edit on sandbox `state.json`, `dontAsk`: 5 fetches,
  1 read, 1 write, 0 denials. The 6 IDs the agent added matched an independent allow-listed fetch exactly
  (missing 0, extra 0, malformed 0).
- Repo unchanged for all three.

`audit-privacy` then flagged 15 absolute project-root paths in the Claude Code transcripts. Claude replaced them with
`<repo>` as a recorded transformation (`REDACTIONS.json`: per-file sha256 before and after). The 62 remaining findings
are the fictional persona's bullets inside the payloads of surfaces (a) and (b), which are those surfaces' input by
design.

**03:15 Docs agent blocked.** Spawning a documentation agent (README, NETWORK, TRACEABILITY, experiment docs, a
SOURCES.md draft, FRICTIONAL.md headings) was denied by Claude Code's auto-mode classifier ("Auto-Mode Bypass").
Claude did not work around it and asked the student how to proceed.

**23:03 Run 2, live day 2**: `uv run jsa run --model-backend claude-cli` at clean commit `8a58a27`, a second
calendar day after the Run 1 baseline.
- Status SUCCESS_WITH_NEW: 746 fetched, 746 unique valid IDs, new 21, retried 0, pending 0, state saved.
- Rule: NO_MATCH on all 21 (mostly sales, legal and PM roles, plus four ML internships). Claude opinion: VALID
  NOT_RELEVANT on all 21. The judges never disagreed, and there is no MATCH case in this run.
- Raw sha256 `530ff442…`. `verify-evidence` OK. `audit-privacy`: 0 findings in this run (the 62 total are the known
  surface (a)/(b) payloads).

## 2026-10-31

**15:22 Run 3, live day 3** (student's request): `uv run jsa run --model-backend claude-cli` at clean commit `a06911d`.
- Status SUCCESS_NO_NEW: 745 fetched, 745 unique valid IDs, new 0, state saved. No model calls (nothing new).
- The board shrank from 746 to 745; the cumulative seen set is 757 IDs.
- Raw sha256 `b8615ebd…`. `verify-evidence` OK; `audit-privacy` 0 findings in this run.
