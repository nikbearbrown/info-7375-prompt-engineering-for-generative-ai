# Job-Search Agent 2: The Loop, the Tools, and the Diff

Riya Kapadnis · INFO 7375 · Fall 2026 · Assignment JS2 · 2026-11-10

**Started from:** my JS1 agent (`../js1-contract-and-watch/`, commit `3c098e1`): its rule, validators, fictional persona
(Arya Sahni) and Databricks state. Board slugs come from the instructor's Lectern `ATS.md`, re-probed by hand.
No Lectern or Reallocation Engine code. Details and who did what: `SOURCES.md`.

JS1 watched one board. JS2 is a **bounded loop** over six boards on **three** applicant-tracking systems (Greenhouse,
Ashby, SmartRecruiters). It has written exits, budgets, a repeat rule and an error policy (`GATE.md`, committed before any
code). It uses tools only through a **permission policy enforced in code** (`jsagent/policy.py`). Its one Claude-made change
went through an evidence-based review (`review/`). It never applies, emails, messages, logs in, or sends anything but a GET.

## Where each deliverable is

| The brief asks for | Here |
|---|---|
| GATE.md (exits, budgets, repeat rule, error policy, permission policy, wrong versions) | `GATE.md`, commit `61c093d`, **before any JS2 code** |
| The loop: ≥3 boards, ≥2 systems, budget, exit status, record of every observation | `jsagent/loop.py`, `jsagent/ats.py`, `boards.json`; each run writes a report and a `trace/*.jsonl` |
| A board that fails on purpose, handled without inventing a value | `ashby:notarealco-js2` (404 → `failed`, `postings: null`): `TRACE.md` §1 |
| Agent trace of one real run, including the deliberate failure | `runs/trace/20261109T203203Z-live-day1.jsonl`, annotated in `TRACE.md` §1 |
| A finished wrong answer + the independent check that catches it | `TRACE.md` §2: naive run says `finished`; `tools/independent_check.py` says `CONTRADICTED` |
| Permission policy in code + ≥10 predicted boundary cases | `jsagent/policy.py`; `BOUNDARY.md` (17 cases, predictions committed `2b6071e` before the code); `tests/test_policy.py` |
| Review packet | `review/REVIEW_PACKET.md` (+ `patch_prompt.md`, `patch.diff`, `claude_patch_response.json`, `patch_session_tool_calls.md`) |
| Sign-off and driver's seat | `SIGNOFF.md` |
| Saved raw responses | `runs/raw/`, `runs/demo-naive/raw/`, `runs/demo-naive/checks/raw/` |
| SOURCES.md, FRICTIONAL.md | here |

## Language and toolchain

- **Python 3.13.7**, standard library only (urllib, json, re, html, pathlib, os, unittest, argparse).
- **Claude Code CLI 2.1.321** was used only to make the reviewed patch (`review/`). Nothing in the agent, the tests or the
  independent check calls Claude or needs an account.
- macOS only: python.org Python has no CA certificates for live fetches (`CERTIFICATE_VERIFY_FAILED`). Fix:
  `pip install certifi` and prefix live commands with `SSL_CERT_FILE=$(python3 -m certifi)`. Tests and seeded runs are offline.

## Exact commands (from a fresh clone)

```bash
cd fall-2026/riya-k/js2-loop-tools-diff

# 1. All tests, offline (57 tests, under 1 s)
python3 -m unittest discover -s tests -v

# 2. Plant each GATE.md wrong version into a temp copy of the code; every one must be caught (offline, ~2 s)
python3 tools/check_wrong_versions.py

# 3. Seeded run (offline): replay day-1's saved responses for the 4 real boards → exit "finished"
python3 -m jsagent.loop run --config demo/good4.json --out /tmp/js2-seeded \
  --fixtures runs/raw --fixture-tag 20261109T203203Z-live-day1 --label seeded-good4

# 4. Independent check of the committed demo report, offline part only (recount from raw + exit consistency)
python3 tools/independent_check.py runs/demo-naive/report-20261109T205704Z-live-naive.json --config demo/naive.json --offline

# 5. The Intern defect, before/after (prints the rule's verdict for real posting 6866538002)
python3 review/reproduce.py

# --- live (network; public GET only) ---
# 6. The real loop: 6 boards. Exit code 3 = incomplete, which is expected (two boards are planted).
#    Use a fresh --out to start your own baseline instead of continuing mine.
SSL_CERT_FILE=$(python3 -m certifi) python3 -m jsagent.loop run --out /tmp/js2-live --label live

# 7. The finished-wrong-answer demo, then the independent check that catches it (check exit code 1 = CONTRADICTED)
SSL_CERT_FILE=$(python3 -m certifi) python3 -m jsagent.loop run --config demo/naive.json --out /tmp/js2-naive --no-empty-guard
SSL_CERT_FILE=$(python3 -m certifi) python3 tools/independent_check.py /tmp/js2-naive/report-*.json --config demo/naive.json

# 8. The write that needs approval: erasing a board's memory
python3 -m jsagent.loop reset --out /tmp/js2-live --board greenhouse:anthropic            # REFUSED, nothing written
python3 -m jsagent.loop reset --out /tmp/js2-live --board greenhouse:anthropic --approve  # allowed
```

Exit codes of `jsagent.loop run`: 0 finished · 3 incomplete · 4 budget_exhausted · 5 error.

## What ran (all UTC)

| Run | When | Who ran it | Kind | Exit | Notes |
|---|---|---|---|---|---|
| Live day 1 | 2026-11-09 20:32 | me | **live** | incomplete | Databricks 80 new since 2026-11-01; 3 boards baseline; 404 board failed; hubspot suspect_empty. Run **before** amendments 3–4 |
| Finished-wrong-answer | 2026-11-09 20:57 | me | **live, demonstration** (`--no-empty-guard`) | finished (wrong) | independent check: CONTRADICTED, hubspotjobs has 126 postings |
| Seeded 4 boards | 2026-11-09 20:53 | Claude Code | **seeded** (day-1 responses replayed) | finished | shows the `finished` exit |
| Live day 2 | 2026-11-10 19:45 | me | **live** | incomplete | the TA's "two real calendar days": new since day 1: Databricks 10, Anthropic 12, OpenAI 26, Notion 3; 1 relevant; a Notion intern posting excluded by amendments 3–4; Databricks took 34 s (`TRACE.md` §4) |

Not submitted: a smoke run Claude made into a scratch folder at 20:27 UTC, before my day-1 run, to check that the code worked.

## Folder map

| Path | What |
|---|---|
| `GATE.md` | exits, budgets, repeat rule, error and permission policy, wrong versions (my decisions) |
| `RULE.md` | the relevance rule: JS1 rule + amendment 3 (no internships) + amendment 4 (full-time only) |
| `BOUNDARY.md` | 17 boundary cases, predicted before the code, with what was observed |
| `TRACE.md` | annotated runs: deliberate failure, finished-wrong-answer + independent check, seeded finished, live day 2 |
| `jsagent/loop.py` | the loop, budgets, repeat rule, error policy, exits, reports, `reset` |
| `jsagent/policy.py` | host/method/scheme/credential checks; read/write/approval checks on real paths |
| `jsagent/ats.py` | Greenhouse, Ashby, SmartRecruiters URL + parser into one posting shape |
| `jsagent/rules.py`, `contract.py` | the rule (a record) and validators, from JS1 + amendments |
| `tools/independent_check.py` | recount from raw, second source, exit consistency |
| `tools/check_wrong_versions.py` | mutation check for GATE.md wrong versions |
| `tests/` | `test_loop.py`, `test_policy.py`, `test_intern.py`, `test_fulltime.py`, `test_rules.py` (JS1), `fixtures/` |
| `review/` | the review packet |
| `runs/` | live reports, traces, raw responses, state; `runs/seeded/`, `runs/demo-naive/` |
| `boards.json`, `demo/` | board lists (budgets are not configurable there, on purpose) |
| `persona/arya-sahni.json` | fictional persona (`@example.com`, 555 phone) |
