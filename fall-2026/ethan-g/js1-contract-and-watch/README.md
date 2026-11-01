# Job-Search Agent 1 — The Contract and the Watch

INFO 7375 · Ethan Gomes · Fall 2026 · Chapters 1–3

The agent watches **one public job board**: Samsara's board on Greenhouse's public JSON API (`boards-api.greenhouse.io`). It looks for
**data engineering and data analyst roles that ask for up to 5 years of experience**, located in the US (remote, or on-site with relocation),
and marks Boston and roles asking 0–4 years as preferred. Each run saves the raw response, remembers posting ids, and reports only postings new
since the last run. Each new data-titled posting gets two verdicts for one **fictional** résumé (Evan Gordon, ~4 years as a data engineer):
a **record** from a written rule anyone can recompute, and a **judgment** from Claude under a prompt contract, validated or rejected.

> **Tested extension (not part of this layer):** the same code can watch many boards. With `--boards config/boards_all.json` it ran across
> 131 Greenhouse boards (14,412 postings) on 2026-10-31. Their files are not included in this submission.
> The submission follows the brief's "one public job board."

Start with [CONTRACT.md](CONTRACT.md). Started the contract based on the input given and the resume.json. Additions were made in the contracts.md to target specific experience levels.
## Language and toolchain

| | |
|---|---|
| Language | Python 3 (ran on **3.11.14**, macOS). Standard library only: **no `pip install`** |
| Tests | `unittest` (stdlib) |
| Network | HTTPS to `boards-api.greenhouse.io` only (`config/allowlist.json`). Each run makes one list request for the board plus one detail request per new data-titled posting |
| Claude judge | Claude Code CLI in headless mode (`claude -p`, tested with v2.1.314), model `claude-sonnet-5-5`. Needs a logged-in Claude Code. Set `CLAUDE_BIN` if `claude` isn't on your PATH. **Not needed** for tests, the rule judge, or the replay |

## Exact commands (from a fresh clone)

```bash
cd fall-2026/ethan-g/js1-contract-and-watch

# 1. Offline tests: contract, allow-list, board config, résumé refusal, rule R1-R5, state (incl. per-board baseline),
#    Claude-output validator, wrong versions W1-W4, and an end-to-end replay of saved run folders
python3 -m unittest discover -s tests -t . -v        # 75 tests, no network

# 2. Show the wrong-version tests can actually fail (audit sabotaged -> every W1/W2 test goes red)
python3 scripts/sabotage_check.py

# 3. Recompute Run 1 -> Run 2 offline from the committed raw run folders (temp dir, touches nothing)
./scripts/replay_runs.sh

# 4. Your own live run of the Samsara board (baseline). Use a temp state so the committed evidence is untouched
python3 -m jsagent.watch --resume persona/evan-gordon.resume.json \
    --state /tmp/js1/state.json --raw-dir /tmp/js1/raw --runs-dir /tmp/js1/runs --no-claude
#    run it again later to see new-since-last; drop --no-claude to add the Claude judgment
#    optional extension: add --boards config/boards_all.json to watch 131 boards

# 5. Experiments (need Claude Code; see each report for order)
python3 experiments/prompt_experiment/label.py                 # hand labels (human only)
python3 experiments/sampling/run_sampling.py                   # 5 postings x 4 fresh calls
python3 experiments/prompt_experiment/run_experiment.py --help
CLAUDE_BIN=... python3 experiments/action_surface/run_surfaces.py
```

## What ran (2026-10-31, ET)

All of this ran on 2026-10-31. Console output is in `evidence/runs/run*_console.txt`, and the full reports are the JSON files next to them.

| # | When | Source | Postings | New (data-titled) | What it shows |
|---|---|---|---|---|---|
| — | 21:24:33 | **live** fetch of Samsara's board | 323 | — | raw: `evidence/raw/2026-10-31T212433_live/boards/samsara.json` |
| — | 21:24 | **SEEDED, constructed** from that response by removing 6 real postings (`scripts/make_seeded_baseline.py`; note in `_SEEDED.json`) | 317 | — | stands in for "an earlier day". Nothing invented or edited |
| **Run 1** | 21:24:33 | **SEEDED** folder above | 317 | **0** | baseline: every id recorded, none reported |
| **Run 2** | 21:24:33 | **live** fetch (saved as `…212433_live_2`, because it ran in the same second as the source fetch and raw files are never overwritten) | 323 | **6 (5)** | exactly the 6 removed postings. The 5 with data titles were judged twice (details in `…212433_live_2/jobs/`). The audit passed |
| Run 3 | 21:24:53 | **live** fetch | 323 | **0** | nothing changed in 20 s, so nothing was reported |

**Seeded, stated plainly:** the change between Run 1 and Run 2 is constructed. There was no second calendar day before the deadline. All
323 postings are real Samsara postings fetched live that evening. The 6 removed postings exercise the rule: 2 it calls relevant, 1 Canada-only,
2 over 5 years, and 1 non-data sales role.

**Run 2 results** (`evidence/runs/2026-10-31T212433_live.json`). "Pref" = preferred location / preferred years, reported only, never part of the verdict:

| Posting | Rule verdict (record) | Pref | Claude verdict (judgment, sonnet-5-5) |
|---|---|---|---|
| 8250423 Data Engineer, Remote - Canada | not_relevant (R3✗) | — | not_relevant |
| 8141959 Data Engineer, Remote - US, "4+ years" | **relevant** | years | relevant |
| 8281491 Senior AI Data & Analytics Engineer II, Remote - MA, "8+ years" | not_relevant (R5✗) | — | not_relevant |
| 8039914 Senior Data Engineer II, Remote - US, "10+ years" | not_relevant (R5✗) | — | not_relevant |
| 7922530 Software Engineer - Data Platform, Remote - US, "4+ years" | **relevant** | years | relevant (flags the BI-heavy risk) |
| *(8304547 Account Executive: new but not data-titled, so counted, not judged)* | | | |

The judges agreed **5/5** in this run. **7922530 is the borderline case.** In some runs Claude said not relevant, because "the posting says it is
not an analytics or business data engineering role". The raw text does say: "This role is not an analytics or business data engineering role. If your
experience is primarily focused on SQL modeling, BI dashboards, ETL tools…". Evan's background includes dbt modeling and BI dashboards, so not relevant
is a defensible judgment the rule cannot make. **Across nine Run 2s of this same posting** (v2.0–v2.5, the 131-board v3.0 and v3, and this run), Claude
said relevant 6 times and not relevant 3 times, with no persona change bearing on it in most of those runs. With one call per run, a repeated or flipped
verdict says nothing about correctness by itself. That's the Chapter 1 point.

**Bugs found and fixed along the way:**
- **Truncated input to Claude (v2.0).** The judge sent only 6,000 characters, hiding a "10+ years" requirement at character 6,284. Now 20,000, flagged if truncated,
  regression-tested (`test_long_content_sent_whole_or_flagged`). The original run files were removed before submission.
- **Overwritten raw file (v2.2).** Two fetches in one second shared a filename. Raw files are now never overwritten (you can see `_2` above), and the replay
  reads raw paths from state. Ethan's replay exposed it.
- **Empty boards not remembered (v3.0, found in the multi-board extension).** "Seen boards" came from postings, so boards with zero jobs were never recorded.
  Now every successfully fetched board counts as seen, with a regression test.

## Layout

```
CONTRACT.md                  the gate: v1 written first 
config/                      allowlist.json (one host) · boards.json (the one board: samsara) · boards_all.json (131-board optional extension)
jsagent/                     fetch.py (allow-list, board list, job details, raw save) · state.py (per-board baseline) · resume.py (refusals)
                             rule.py (R1-R5 record) · audit.py · claude_judge.py (prompt contract + validator) · watch.py (CLI)
tests/                       test_contract.py · test_wrong_versions.py · test_claude_validator.py · test_watch_multi.py · fixtures/ (constructed)
persona/                     evan-gordon.resume.json (fictional) · SCHEMA.md
prompts/                     judge_v1_baseline.txt · judge_v2_revision.txt
evidence/raw/<run>/          boards/samsara.json, jobs/samsara_<id>.json for judged postings; the SEEDED folder has _SEEDED.json
evidence/runs/               per-run JSON reports + console output
state/seen_ids.json          ids and boards seen + run history (source, raw folder, digest, counts)
experiments/source_raw/      the 7 saved board responses (with descriptions) that the 20-posting experiment set is drawn from
experiments/sampling/        SAMPLING_REPORT.md · run_sampling.py · results.jsonl
experiments/prompt_experiment/  PROMPT_EXPERIMENT.md · LABELING_RULE.md · labels.csv (+ first/second-pass snapshots) · label.py · run_experiment.py · results/
experiments/action_surface/  ACTION_SURFACE.md · run_surfaces.py · out/ (raw CLI results)
scripts/                     replay_runs.sh · sabotage_check.py · make_seeded_baseline.py · rejudge_run.py
SOURCES.md
```

Earlier versions' run files were removed before submission.

---

## Sign-off — Job-Search Agent 1



**Checked**
- New-since-last by id, baseline reports 0, per-board baseline (a board seen for the first time, including an empty one, reports nothing new), a failed
  board loses nothing, duplicate ids across boards stop the run: `TestState`. Run 1 → 2 → 3 on Samsara's board showed 0 → 6 → 0 new, and
  `scripts/replay_runs.sh` recomputes Run 1 → 2 offline with the same 6 new postings and the same 5 verdicts. End-to-end offline multi-board replay: `tests/test_watch_multi.py`.
- Board config: `config/boards.json` is exactly the one board, `samsara`, and every token in the optional extension list `config/boards_all.json` is unique and on the allow-list (`test_board_list_config`). Job-detail URLs only take numeric ids.
- Allow-list: `TestAllowList` (other host, lookalike host, plain http, bad board token, off-list redirect). Raw evidence is never overwritten: `test_raw_files_never_overwritten`. The Claude
  agent surface was separately denied an off-list fetch (`experiments/action_surface/out/c_agent_probe_offlist.json`).
- Résumé refusals (non-example email, non-555 phone, unmarked file, hidden email; contact fields never sent to Claude): `TestResume`.
- Rule verdicts match hand computation on 9 constructed postings, plus focused R1–R5 cases (25 location strings for R3, Boston-preferred, relocate/remote flags, 0–4 preferred years, preferences never change the verdict): `TestRule`.
- R3 run over all 208 distinct location strings in the saved responses: 107 pass, and every pass was a real US location (checked by reading the list).
- Wrong versions W1 (mislabeled pairing), W2 (empty or invented citations), W3 (baseline reports new), and W4 (a board's first appearance reports
  everything as new) are caught: `tests/test_wrong_versions.py`. `scripts/sabotage_check.py` shows those tests go red when the audit is disabled.
- Claude output validator rejects fences, prose, extra or missing keys, bad verdicts, wrong ids, nonexistent résumé paths,
  and contact-field citations. Long postings are sent whole or flagged: `tests/test_claude_validator.py`.
- R5's years extraction was spot-checked on 8 random Samsara postings: 7 matched the stated requirement, and 1 had no numeric phrase.

**How**
- Tests: written by Claude Code from CONTRACT.md *before* the matching implementation (v1, then again for v2), then
  run. **Ethan re-ran the suite himself on 2026-10-31 (~18:30 ET): 65/65 OK** (before v3), and **75/75 OK after v3 (~19:29 ET)**
  I read the wrong versions and decided the changes to be made based on the results.
- Expected rule verdicts in `TestRule`: computed by hand from R1–R5. **Ethan re-derived two by hand:** fixture 1004 (relevant, Boston and years preferred) and 1003 (fails R3, Remote - Canada).
- The truncation diagnosis: by recomputation (character position of "10+ years" in the raw response), done in the Claude Code session.

**Not checked**
1. **R4 counts keywords, not requirements.** "Nice to have" and "technologies we use" lists count the same as requirements (shown in v1, not re-measured for v2).
2. **R3 knows only listed US places.** Bare "Remote" with no country fails on purpose. A US city that isn't listed and has no state (e.g. "Remote - Boise") fails. Uppercase state codes could false-match a non-US string, though none did across 208 real locations. Relocation is within the US (confirmed).
3. **R5 reads only the first years phrase** and only digits. "Bachelor's + 4 or Master's + 2" counts as 4, and "three years" is missed. It was spot-checked on 8 postings, not measured.
4. No real second calendar day. The change was seeded. Greenhouse behavior over time (re-posted ids, id reuse across boards) is untested.
5. Greenhouse's terms of use were not read in full. The agent makes one list GET plus a few detail GETs per run to the documented public Job Board API. (The 131-board extension makes ~131.)
6. The validator checks Claude's *format and citations*, not whether its `reason` is true. The Run-2 reasons were checked by hand.
7. **Data analyst roles are lightly tested on real data.** Samsara has none. The 131-board extension (files not included) judged one (CarGurus), and the experiment set has one (Brex "Data Analyst II"). Tableau and Power BI were added (v2.2), but R4 matches them only when spelled exactly that way ("PowerBI" as one word is missed, as a test shows), and Looker is not on the persona.
8. Postings longer than 20,000 characters are still truncated (now flagged). None in this run were.
9. **One board only.** Samsara has 323 postings, but only ~13 with data titles, so the watch sees few relevant roles. The 131-board extension (files not included) found 52 rule-relevant roles across 31 companies on the same day.
10. **The Boston preference is literal.** Somerville and Cambridge (Greater Boston) aren't marked preferred. Claude noticed this for Formlabs, and the rule can't.
11. Sampling was small for data roles (4 calls on 5 postings. Every verdict repeated, but rare flips weren't measured).

**Not claiming**
- That any verdict is correct for a real job seeker. "Relevant" means relevant under R1–R5 (record) or in Claude's judgment.
- That Claude's judgments are stable or accurate in general. See the sampling report and the prompt experiment, both n ≤ 10.
- That this covers other Samsara-like companies, other ATS vendors (Ashby, Lever, …), or other personas (one board, one persona).

**Signed or withheld:** Ethan Gomes (31st October)

## Driver's seat



| Part of the task | Claude did | Ethan does | Why it stays Ethan's | Evidence |
|---|---|---|---|---|
| What to search for | built v1 (new-grad SWE) | **switched the target to data engineers with 2–5 years** after seeing v1's results, then **added data analyst**, then **Tableau and Power BI**, then **US-only / will relocate / Boston preferred**, then **0–4 years preferred** and the name **Evan Gordon**, then an updated education and timeline for a ~4-year data engineer, then tried **every known Greenhouse board**, and finally **returned to one board** to follow the brief (the multi-board run kept as an extension) | what job is worth a day of my life is the whole point, and Claude can't know it | CONTRACT.md and the persona file |
| Contract | drafted from the assignment based on Ethan's input and the resume.json, then a numbered In/Out/Refuses/Rule/Wrong versions/Failure version | **edited the final CONTRACT.md himself** (wording, sample résumé, refusals, dates), and owns the rule and failure sentences | the rule *is* the definition of "worth my time" | Ethan's edits to CONTRACT.md  |
| Board(s) + persona | scanned 49 then 338 board names, counted data roles, proposed Samsara and a fictional persona, built the 131-board watch | chose Samsara, tried every known board (v3), then **chose to submit one board** as the brief asks | which jobs to watch, and how to read the brief, is a personal call | `config/boards.json` (one board) |
| Code + tests | wrote `jsagent/`, tests, scripts | runs the tests, reads the wrong-version tests, re-derives the hand-computed verdicts | "tests pass" only means something if I know what they test | Ethan's replay run exposed the overwritten-raw bug. Ethan's test runs (65/65, then 75/75) and hand checks of fixtures 1004 and 1003 |
| Hand labels (20) | built `label.py`, which hides all model output | **labels every posting** | the labels are the ground truth. If Claude makes them, the experiment grades Claude against Claude | `labels.csv` |
| Prompt revision | runs the experiment harness | picks the **one** change from dev failures | deciding what failure matters is the judgment being taught | `prompts/judge_v2_revision.txt` |
| The truncation bug | found it by checking Claude's "content shown" remark against the raw text, fixed it, and re-judged | decides whether the fix and re-judge are presented honestly | evidence handling is my responsibility | `test_long_content_sent_whole_or_flagged` |
| Sign-off |  Ethan Gomes | signs or withholds | only I can say what I verified | this section |
