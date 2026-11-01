# Job-Search Agent 1 — The Contract and the Watch

**Omkar Salian (omkar-s) · INFO 7375 Fall 2026 · Chapters 1–3**

The agent watches **one** public job board (Klaviyo on Greenhouse) for **one** fictional résumé (Aarav Patel). It reports only postings that are **new since the last run**. Each new posting gets two verdicts: a **record** from my written rule, which anyone can recompute, and a **judgment** from Claude under a prompt contract, labelled as one.

> **Status (2026-10-30):** everything has run (see *What ran*). Omkar ran the tests himself, computed the hand cases and made the autonomy choice. Signed by Omkar 2026-10-30. Driver's-seat reasons: contract, tests and autonomy in Omkar's words; labels not filled.

## Toolchain

| | |
|---|---|
| Language | Python 3 (tested on 3.14.2; written for ≥ 3.10), **standard library only** — no `pip install` |
| Claude judge | Claude Code CLI (`claude -p`, 2.1.292), signed in. Each call runs in an empty temp dir with `--tools ""`, `--setting-sources ""`, `--no-session-persistence` → a fresh conversation that can read only the prompt |
| Network | HTTPS to `boards-api.greenhouse.io` only (allow-list in `jsagent/fetch.py`) |
| OS | macOS 15 (Darwin 24.6) |

## Commands (run from this folder)

```bash
# tests (no network, no Claude)
python3 -m unittest discover -s tests -v

# the two wrong versions from CONTRACT.md must each be KILLED by the tests
python3 tests/run_mutants.py

# the watch, rule judge only (first run = baseline, reports none)
python3 -m jsagent.watch --board klaviyo --resume persona/aarav-patel.example.json \
    --state runs/klaviyo.state.json --out runs/

# the watch with the Claude judge too
python3 -m jsagent.watch --board klaviyo --resume persona/aarav-patel.example.json \
    --state runs/klaviyo.state.json --out runs/ --claude --prompt prompts/baseline.txt

# a SEEDED run against a saved earlier response (no network; labelled SEEDED in the report)
python3 -m jsagent.watch ... --fixture evidence/pre-build-curl/klaviyo-2026-10-25T19-09-13Z.json
```

Experiments: `experiments/prompt/` (select → label → dev runs → lock → held-out runs → score) and `experiments/sampling/` (run → summarize). Each script has its command in its docstring.

## What is in this folder

| Path | What |
|---|---|
| `CONTRACT.md` | The gate, with my decisions and their status |
| `jsagent/` | fetch (allow-list), persona (fictional-only check), rule (record), claude_judge (judgment + validator), watch (state, diff, reports) |
| `tests/` | unit tests, constructed fixtures, `mutants/` (the wrong versions), `omkar_hand_cases.csv` (my hand-computed verdicts) |
| `runs/` | raw responses, the state file, and a JSON + Markdown report per run |
| `evidence/pre-build-curl/` | one curl snapshot taken before any code existed |
| `prompts/` | baseline prompt contract; `revision.txt` = baseline + Omkar's labeling rule (the one change) |
| `experiments/` | the sampling report and the prompt experiment |
| `action-surface/` | the three-way comparison |
| `SOURCES.md`, `FRICTIONAL.md` | credits; my log |

## What ran

Only runs that actually happened are listed, each with its date and file.

| When (UTC) | What | Result | Evidence |
|---|---|---|---|
| 2026-10-25 19:09 | plain `curl` of the board, before any code | 160 postings | `evidence/pre-build-curl/` |
| 2026-10-25 22:58 | Omkar's failure sentence written | — | CONTRACT.md |
| 2026-10-25 ~22:59 | `unittest` (run by Claude Code) | 30 tests: 29 OK, 1 skipped (hand cases empty) | — |
| 2026-10-25 ~22:59 | `run_mutants.py` (run by Claude Code) | 3/3 wrong versions KILLED | — |
| 2026-10-25 22:59 | live baseline, attempt 1 | **failed**: TLS CA bundle missing | `evidence/failed-attempts/` |
| 2026-10-25 22:59:08 | live baseline | HTTP 200, 160 postings, **0 new** (baseline) | `runs/*2026-10-25T22-59-08Z*`, `runs/klaviyo.state.json` |
| 2026-10-25 ~23:10 | whole-board dry run of the rule (contract **v1**) | 18 / 160 relevant (13 senior/lead titles) | `experiments/whole-board-2026-10-25-contract-v1.md` |
| 2026-10-26 ~01:55 | contract **v2** (clause B = any US location, Omkar's decision); tests rerun by Claude Code | 31 tests: 30 OK, 1 skipped; 3/3 mutants KILLED; whole board 19 / 160 relevant | `experiments/whole-board-2026-10-25-contract-v2.md`, CONTRACT.md change log |
| 2026-10-26 16:37:30 | second live run (Mon), with `--claude` | HTTP 200, 160 postings, **0 new, 0 removed**: the board did not change since Sunday, so Claude was never called | `runs/*2026-10-26T16-37-30Z*` |
| 2026-10-26 16:38:29 | re-check one minute later (redundant; kept) | 0 new | `runs/*16-38-29Z*` |
| **2026-10-26 18:58:14** | **live run that saw a real change**, with `--claude` | 160 postings: **2 new, 2 removed**. Both new postings are "Senior Lead AI Engineer – G&A Systems" (SF and Boston). **Record: not_relevant** (fails A). **Judgment: not_relevant** (it cites "5+ years"). The two agree, and both outputs passed the validator | `runs/run-klaviyo-2026-10-26T18-58-14Z.md`, `runs/claude-raw/` |
| 2026-10-27 16:48:05 | live run (day 3), with `--claude` | 161 postings: **4 new, 5 removed**. New: 2× Lead Integrations Engineer – G&A Systems, Senior Director Customer Success APJ, Sr. Payroll Specialist. Record **and** judgment: not_relevant on all 4 | `runs/run-klaviyo-2026-10-27T16-48-05Z.md` |
| 2026-10-30 08:13:44 | live run (day 4), with `--claude` | 154 postings: **1 new, 13 removed**. New: Sr. Product Manager, Growth (PLG). Record and judgment: not_relevant | `runs/run-klaviyo-2026-10-30T08-13-44Z.md` |
| 2026-10-30 19:36 UTC | **tests + mutants, run by Omkar himself** in his terminal | 31 tests OK (1 skipped: hand cases empty); 3/3 mutants KILLED | his terminal output |
| 2026-10-30 19:51 UTC | **tests rerun by Omkar** with his 3 hand cases | **31/31 OK**; his hand verdicts (jobs 2, 14, 16) match the code; 3/3 KILLED | `tests/omkar_hand_cases.csv` |
| 2026-10-26 01:35–01:37 | sampling: 5 postings × 4 fresh `claude -p` calls | 20/20 valid; **0 spread** (5/5 postings 4/4 the same); modal = Omkar's label on **1/5** | `experiments/sampling/SAMPLING-REPORT.md` |
| 2026-10-26 01:38 | action surface, three ways, one posting | 3/3 valid "relevant"; surface 3 never saw the ad text | `action-surface/` |
| 2026-10-27 ~17:00–17:08 | prompt experiment: Omkar's 20 labels → baseline + revision ("add my labeling rule") on dev → lock → both on held-out | baseline 4/10 dev, 6/10 held-out; revision **identical** (0 of 20 verdicts changed) | `experiments/prompt/PROMPT-EXPERIMENT.md` |

## Sign-off — Job-Search Agent 1

```text
Checked:      (selected by Omkar 2026-10-30 20:27 UTC; wording typed by Claude from his picks)
              - The 31 tests and the wrong-version check: I ran them myself in my
                terminal on 2026-10-30. 31/31 OK; all 3 mutants KILLED.
              - My rule on 3 real postings (jobs 2, 14, 16): I worked out the verdicts
                myself, and test_rule_matches_omkars_hand_verdicts passed.
              - I signed the claude CLI in myself so the judge could run.
How:          - Tests: Claude wrote them; I ran them (with Claude's help).
              - Hand checks: by recomputation. I counted the skills with my own grep
                command; the title and location I read myself.
              - Watch, sampling, experiment and action-surface runs: run by Claude
                Code, not by me.
Not checked:  (selected by Omkar 2026-10-30 20:24 UTC from a list of true gaps Claude wrote)
              1. The "US remote" part of clause B: no Klaviyo posting was remote,
                 so it was only tested on constructed fixtures.
              2. The ~140 postings the rule rejected: I did not read them, so I
                 don't know how many good jobs it missed.
              3. The code itself: Claude wrote it. I ran the tests and hand-checked
                 3 postings, but I did not read the code line by line.
              4. Only 4 days of watching (10-25 to 10-30), never on a schedule.
              5. Claude's judge on a NEW SWE posting: all 7 new postings in the
                 watch were non-SWE.
              6. Only one model (claude-sonnet-5-5) with default settings.
Not claiming: (selected by Omkar 2026-10-30 20:27 UTC from options Claude wrote)
              A "relevant" verdict means the posting matched my rule, not that the
              job is good or worth applying to.
Signed or withheld: Signed — Omkar Salian, 2026-10-30 (23:54 ET / 2026-10-31 03:54 UTC)
```

## Driver's seat

The "Claude did", "I did" and "Evidence" columns were written by Claude Code from the dated record (FRICTIONAL Part 2). The "Why that part stays mine" column is Omkar's own words, quoted as typed.

| Part of the task | Claude did | I did | Why that part stays mine | Evidence |
|---|---|---|---|---|
| Contract | offered options, typed my choices | chose board, persona, rule, wrong versions; wrote the failure sentence (2026-10-25 22:58 UTC) | "because i know what i want and what i am doijng" (Omkar, typed 2026-10-27, reused for this column at his request 2026-10-31) | CONTRACT.md "[Omkar, verbatim]" lines; FRICTIONAL Part 2, 2026-10-25 ~20:30 |
| Code + tests | wrote `jsagent/`, tests, mutants | ran the tests and mutants myself (2026-10-30 19:36 and 19:51 UTC); hand-computed 3 cases with my own grep | "it is better to check what the results are rather than just asking claude to do things for you" (Omkar, 2026-10-31 22:35 UTC) | `tests/omkar_hand_cases.csv`; FRICTIONAL Part 2, 2026-10-30 |
| Labels | built the selection script and runners | labeling rule (2026-10-26), 20 labels incl. the 5 sampling postings (2026-10-27) | *(not filled)* | `labels.csv`, `LABELING-RULE.md` |
| Autonomy choice | ran the three ways, drafted the comparison table | chose way 1 (2026-10-30) | "i will go with way 1 because claude only reads the postings and gets it to me" (Omkar, typed 2026-10-30, reused at his request 2026-10-31) | `ACTION-SURFACE.md` |
