# Job-Search Agent 1 — contract and watch

**Author:** Aditya Hasija (INFO 7375, Fall 2026)

The agent watches **one public job board** (Stripe on Greenhouse), reports **only postings new since the last run**, and judges each new posting twice:
- a **rule verdict**, which is a record anyone can recompute, and
- a **Claude verdict**, which is a labeled judgment that must pass a strict validator.

Every verdict cites the résumé fields and posting fields behind it. The résumé is a fictional persona, Maya Sehgal.

- **Contract (written and committed before any code):** [`CONTRACT.md`](CONTRACT.md), commit `aee1aab`
- **Sampling report:** [`experiments/sampling/REPORT.md`](experiments/sampling/REPORT.md)
- **Prompt experiment:** [`experiments/prompt/RESULTS.md`](experiments/prompt/RESULTS.md); plan in [`PLAN.md`](experiments/prompt/PLAN.md); labels in [`labels.csv`](experiments/prompt/labels.csv)
- **Action-surface comparison:** [`ACTION-SURFACE.md`](ACTION-SURFACE.md)
- **Provenance:** [`SOURCES.md`](SOURCES.md) · Honest log: [`FRICTIONAL.md`](FRICTIONAL.md)

## Language and toolchain

| | |
|---|---|
| Language | Python 3 (tested on **3.13.3**), **standard library only**: no `pip install`, no third-party packages |
| OS tested | macOS 15.5 |
| Claude | Claude Code CLI **2.1.316**, called as `claude -p` (no API key; uses your Claude Code / NEU login). Needed only for the Claude judge and the experiments. Tests and the rule judge run offline. |
| Network | one host only: `boards-api.greenhouse.io` (allow-listed in `jobwatch/fetch.py`) |

## Exact commands (from a fresh clone)

```bash
cd fall-2026/aditya-h/js1-contract-and-watch
```

```bash
python3 -m unittest discover -s tests -v
```

```bash
python3 tests/wrong_versions.py
```

The second command plants each of the contract's three wrong versions and shows the suite fails on each.

**One live watch run.** It fetches Stripe, diffs against `runs/state.json`, judges new postings, and writes the raw response, run record and report under `runs/`:

```bash
python3 -m jobwatch run --board stripe --claude
```

- Leave out `--claude` to run offline, with rule verdicts only. That needs no Claude login.
- To start a fresh baseline, point `--state` at a new path, e.g. `--state /tmp/state.json --runs-dir /tmp/runs`.
- **A SEEDED run** reads a saved response instead of fetching, and is labeled SEEDED in every output: `python3 -m jobwatch run --seeded-raw runs/raw/<file>.json --state <state> --runs-dir <dir>`

**Re-score the experiments from the saved replies.** These need no Claude calls:

```bash
python3 experiments/run_experiment.py --score
```

```bash
python3 experiments/run_sampling.py --summarize --prompt prompts/judge_v1.txt
```

```bash
python3 experiments/run_sampling.py --summarize --prompt prompts/judge_v2.txt
```

**If the fetch fails with `CERTIFICATE_VERIFY_FAILED`:** the code already falls back to `/etc/ssl/cert.pem`, with verification still on. On Linux the system bundle is normally found automatically.

## What ran (past tense only for what is shown)

| When (EDT) | What | Evidence |
|---|---|---|
| 2026-10-31 22:41 | **Live baseline**: 745 postings fetched, **0 new**, every id recorded. The first attempt failed on TLS certificates, and the state file was correctly left unwritten. | `runs/raw/stripe-20261101T024132Z.json`, `runs/state.json`, `runs/records/run-20261101T024132Z.json`, `runs/reports/report-20261101T024132Z.md` |
| 2026-10-31 ~22:50 | **Aditya ran** the 53 tests (all passed) and the wrong-version harness (all 3 caught) in their own terminal | `evidence/test-run-by-aditya-2026-10-31.md` |
| 2026-10-31 22:57 | Claude judge smoke test (one live call) | `evidence/claude-smoke-test-2026-10-31.md` |
| 2026-10-31 22:59–23:04 | Sampling, prompt v1 (20 calls), and the prompt experiment (40 calls) | `experiments/sampling/results-judge_v1.jsonl`, `experiments/prompt/results/` |
| 2026-10-31 22:59–23:05 | Action-surface runs, three modes | `experiments/action-surface/` |
| 2026-10-31 23:06–23:08 | Sampling, prompt v2 (20 calls) | `experiments/sampling/results-judge_v2.jsonl` |
| 2026-10-31 23:11 | **Live second run**, same calendar day, 30 minutes after the baseline, with `--claude`: 745 fetched, **0 new**. Stripe posted nothing in between, and the two fetches Claude Code made at 22:22 and 22:30 while choosing the board (not committed) also matched the baseline exactly. | `runs/raw/stripe-20261101T031155Z.json`, `runs/records/run-20261101T031155Z.json`, `runs/reports/report-20261101T031155Z.md` |
| 2026-10-31 23:12 | **SEEDED second run (labeled SEEDED, not a second calendar day).** The state was reconstructed by `experiments/seed_state.py` from the 23:11 live response: every posting with `first_published` before 2026-10-30 00:00 EDT counts as already seen (728 ids). The watch then ran on that saved response: **17 new**, 1 relevant by the rule, 1 relevant by Claude (prompt v2), **0 disagreements**, 0 invalid. | `runs-seeded/` (state, raw copy, record, report, all marked SEEDED) |

**Timestamps:** filenames and records use **UTC**. The baseline file is stamped `20261101T0241Z` but ran at 22:41 EDT on **Oct 31**.

## Layout

```text
CONTRACT.md            the gate: in / out / refuses / rule / wrong versions / failure sentence
jobwatch/              fetch.py (allow-list), state.py, resume.py (validation + persona guard),
                       rule.py (record), claude_judge.py (judgment + validator), watch.py, report.py
prompts/               judge_v1.txt (baseline), judge_v2.txt (adds the contract rule) — the watch uses v2
personas/              maya-sehgal.resume.json (fictional; from the-reallocation-engine)
tests/                 test_rule.py, test_watch.py, test_claude_validator.py, wrong_versions.py
runs/                  live runs: raw responses, state.json, run records (JSON), reports (Markdown)
runs-seeded/           the SEEDED second run (state reconstructed from first_published; labeled)
experiments/           sampling/, prompt/, action-surface/, select_postings.py
evidence/              Aditya's own test run, Claude smoke test
```

My real résumé is not in this repository; `.gitignore` blocks `resume.json`. Conversation transcripts stay on my machine.

---

## Sign-off — Job-Search Agent 1

*Drafted by Claude Code on 2026-10-31 for Aditya to edit, then sign or withhold.*

**Checked**
- **Only new ids are reported; the baseline reports none; a failed or empty fetch never touches state:** `tests/test_watch.py::RunWatch` (11 tests), the live baseline (0 new of 745), the live second run (0 new; the board was unchanged), and the SEEDED run (17 new, matching the 17 postings with `first_published` on or after Oct 30).
- **Only the allow-listed host is fetched:** `test_watch.py::AllowList`.
- **Persona-only résumé:** `ResumeGuard` and `test_refuses_non_persona_resume_before_fetch`.
- **The rule's verdicts match the written rule:** `tests/test_rule.py` (hand-derived cases), plus recomputation against my 20 hand labels (20/20 after two dated corrections of my own slips).
- **Each contract wrong version is caught:** `tests/wrong_versions.py` (2, 15 and 10 failing tests).
- **Claude replies outside the contract are rejected, never coerced:** `tests/test_claude_validator.py` (13 tests); 0 of 80 live replies were invalid.

**How**
- **By hand:** the 20 hand labels; reviewing the two label mismatches.
- **By tests written before reading Claude's code:** the tests were committed before the implementation (`58f25ff` before `65ddc05`; `27702b7` before `b24d8ca`). Claude wrote both, from my contract.
- **By recomputation:** rule verdicts vs hand labels; experiment scores from saved replies.
- **With Claude's help:** all code, test code, prompts, call runs and report drafts. I ran the tests myself.

**Not checked**
1. The live HTTP-error path against the real server. It's covered only by a fake fetcher in tests.
2. Whether my rule finds jobs that are actually good for Maya. Every score here measures agreement with my own rule, and I haven't validated the rule against her preferences or against hiring outcomes.
3. Claude's behavior on other models, other days, or other boards. All 80 judge calls were `claude-sonnet-5-5` on one evening.
4. Whether `claude -p` loaded a project `CLAUDE.md` in the action-surface runs made from inside the repo.
5. Long-running behavior. Two runs don't test the state file over weeks, posting churn, or concurrent runs.
6. Visa sponsorship (Maya is on H-1B). It's explicitly outside the rule.
7. A real second calendar day. The SEEDED reconstruction misses postings that were removed before 23:11, and assumes `first_published` is accurate.

**Not claiming**
- That a Claude verdict is a fact. It's a labeled judgment.
- That 10/10 on held-out means the agent works in general. Ten cases can't show that.
- That the agent applies, emails, or logs in anywhere. It never does.
- **That a second calendar day was shown.** It wasn't. The second live run happened 30 minutes after the baseline and found 0 new postings. The run with a change is SEEDED: a reconstruction from the saved response's own `first_published` dates, not an observation of the board on an earlier day.

**Signed or withheld:** ____________ (name, date)

## Driver's seat

| Task | Claude should | I should | Why that part stays mine | Where the split shows |
|---|---|---|---|---|
| The contract | draft the wording, check facts against the live board, review it as a TA would | make every decision: the rule, the phrases, the location policy, the wrong versions | Only I know what "worth a day of my life" means. A TA will ask me why a posting is relevant. | CONTRACT.md provenance; I changed "matches all" to title-only after Claude's board check |
| Hand labels | select and split the postings, recompute and compare | label every posting by hand; decide what a mismatch means | Labels are the yardstick. If Claude wrote them, it would be grading itself. | Claude refused to label ("The 20 hand labels have to be yours", Oct 31); `16a72a1`; my two slip decisions in `4158a63` |
| Code and tests | write them, from the contract, tests first | run them myself; read the failures | Running them myself is the difference between "Claude says it passes" and "I saw it pass". | `evidence/test-run-by-aditya-2026-10-31.md` |
| Attribution | draft text and mark it as drafted | own the words I sign | Misattribution is an integrity matter. | Claude declined to record the failure sentence as mine (CONTRACT.md: "drafted by Claude Code … chosen by Aditya") |
| Credentials and publishing | stop and ask | log in myself; approve every push | Credentials and public posting are mine to authorize. | I ran `/login` myself; nothing was pushed without my approval |
