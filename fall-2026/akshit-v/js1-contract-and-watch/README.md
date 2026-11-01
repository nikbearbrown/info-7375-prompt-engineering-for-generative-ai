# Job-Search Agent 1: The Contract and the Watch

The agent watches one public Greenhouse board (Figma) for a fictional persona, **Jack Spencer** (a data engineer with 5 years of experience and a master's degree). For each posting that is new since the last run, it gives two verdicts:
- a **rule** verdict, which is a record anyone can recompute by hand from `CONTRACT.md`;
- a **Claude** verdict, which is a judgment, always labeled as model output.

The contract was written and committed before any code: `CONTRACT.md`, commit `3632004` (2026-10-31 19:14 ET).

## Language and toolchain
- **Python 3.12.10**, standard library only. There's nothing to `pip install`.
- **Tests:** `unittest` (standard library).
- **Claude Code CLI 2.1.316** for the Claude judge (`npm install -g @anthropic-ai/claude-code`, then run `claude` once to log in). The judge model is fixed at `claude-opus-5-5`.
  - Every judge call is a fresh `claude -p` session with `--safe-mode --tools "" --no-session-persistence`, and the prompt contract replaces the system prompt.
  - Without the CLI, use `--no-claude` and everything else still runs.
- **Network:** only `https://boards-api.greenhouse.io` (the allow-list).
- Developed on Windows 11. The commands below work in PowerShell or bash from the repo root.

## Exact commands

```bash
# 1. Tests (no network, no Claude)
python -m unittest discover -s tests -t . -v

# 2. The watch, as it was run (see "What ran")
python -m agent.fetch --board figma                                    # live fetch, saved as evidence
python scripts/make_seeded_snapshot.py evidence/raw/<stamp>_figma_live.json --remove 10   # SEEDED earlier snapshot
python -m agent.run --board figma --resume data/resume_jack_spencer.json \
    --from-file evidence/raw/<stamp>_figma_SEEDED_earlier.json         # run 1: baseline (SEEDED input)
python -m agent.run --board figma --resume data/resume_jack_spencer.json   # run 2: live fetch, both judges

# 3. Chapter artifacts
python experiments/sampling.py run --raw evidence/raw/20261031T233955Z_figma_live.json \
    --ids 6201407004 5551686004 6233040004 5551532004 5552549004 --n 4
python experiments/sampling.py report experiments/results/sampling_20261031T234336Z.json
python experiments/prompt_experiment.py --prompt prompts/judge_baseline.md --set dev
python experiments/prompt_experiment.py --prompt prompts/judge_revision.md --set dev
python experiments/prompt_experiment.py --prompt prompts/judge_baseline.md --set heldout --final
python experiments/prompt_experiment.py --prompt prompts/judge_revision.md --set heldout --final
python experiments/action_surface.py --id 6233040004
python -I scripts/recompute_rule.py        # failure condition #1: recompute run 2 by a second method
```

**To rerun from a fresh clone without touching the committed evidence,** delete or move `state/seen_ids.json` first. Otherwise run 1 is not a baseline. You can also pass `--state` and `--runs-dir` to point at scratch locations.

## What ran (2026-10-31)

| Time (UTC) | What | Evidence |
|---|---|---|
| 23:38:58 | Live fetch of the Figma board: HTTP 200, 140 postings | `evidence/raw/20261031T233858Z_figma_live.json` (+ `.meta.json` with sha256) |
| 23:39 | **SEEDED** earlier snapshot: the same response minus its 10 highest-id (newest) postings, 130 left | `evidence/raw/20261031T233858Z_figma_SEEDED_earlier.json` (+ meta listing removed ids) |
| 23:39:44 | **Run 1, baseline, on the SEEDED file.** It reported 0 new and saved 130 ids | `runs/20261031T233944Z_figma_baseline.txt` |
| 23:39:55 | **Run 2, live fetch.** 140 postings, 10 new, both judges. All 10 Claude replies passed the validator, and Claude agreed with the rule on 10 of 10 | `runs/20261031T233955Z_figma_run.txt`, `evidence/raw/20261031T233955Z_figma_live.json`, `state/seen_ids.json` |
| 23:43 | Sampling: 5 postings × 4 fresh Claude sessions. 20 of 20 replies valid, 20 distinct sessions | `experiments/results/sampling_20261031T234336Z.json` |
| 23:45 | Action-surface runs: paste, file, agent | `experiments/results/action_surface_20261031T234559Z.json` |
| 11-01 00:45–00:48 | Prompt experiment: baseline and revision on dev, then both on held-out (`--final`), after hand labels were committed (`a4d8dd2`) | `experiments/results/judge_*_{dev,heldout}_*.json` |

**The change between runs is seeded, not a real change on the board.** The two live fetches (23:38:58 and 23:39:55) had identical id sets. Run 2's 10 new ids are exactly the 10 removed to make the seeded file. I checked this by script against the meta file and the run JSON.

Tests: `python -m unittest discover -s tests -t . -v` ran 32 tests, all passing. This includes the checks that catch the contract's wrong versions:
- **W1** (verdicts paired with the wrong postings) is caught for both judges, including when Claude's replies arrive out of order.
- **W2** (substring skill matching) is caught.

The wrong versions themselves live in `tests/wrong_versions.py`.

## Failure conditions from CONTRACT.md (written before running)

| # | Condition | Status |
|---|---|---|
| 1 | A rule verdict differs from the rule applied by hand | **Did not happen.** On 2026-10-31 I applied the rule by hand to 5 postings from my labeled sets: 6201407004 Data Platform Engineer, 5551532004 Software Engineer - Machine Learning, 5552549004 Software Engineer - Distributed Systems, 5552580004 Data Scientist, and 6227402004 Product Builder, AI Insights. My verdicts matched the code's rule verdicts (the `rule` column in `experiments/results/`). None of these 5 were run-2 postings. Separately, Claude recomputed all 10 run-2 verdicts by a second method (`python -I scripts/recompute_rule.py`: token matching, rule lists copied from CONTRACT.md, does not import `agent/rule.py`): 10/10 verdicts and skill lists matched. |
| 2 | Baseline reports any posting as new, or run 2 reports an already-seen id | **Did not happen.** Run 1 reported 0 new; run 2's 10 new ids equal the seeded removals |
| 3 | Figma's "Data Platform Engineer" comes out `not_relevant` | **Happened.** The rule says `not_relevant` for posting 6201407004: the title matches "Data Platform", but its content has only 1 of Jack's 8 skills (Python). The only "AWS" is inside "Washington", correctly not counted. Claude (4/4 sampling calls) and my hand label both say `relevant`. My prediction was wrong on Data Platform Engineer. The committed contract is unchanged. |
| 4 | A Claude verdict lacks its judgment label, or an invalid answer is shown | Did not happen in run 2 (10/10 labeled and valid). No invalid answer occurred, so the rejection path ran only in tests. |
| 5 | Rule disagrees with my hand labels on more than 4 of 20 | **Did not happen.** There were 2 disagreements out of 20 (Security Scientist and Data Scientist, both held-out, both through rule branch (b)). In the 5 sampling postings, the rule also disagreed with me on 3. |

## Files
- `CONTRACT.md`: the contract.
- `agent/`: the code, with these modules:
  - `fetch.py`: allow-listed fetch and evidence.
  - `resume.py`: persona validator.
  - `rule.py`: the rule judge.
  - `claude_judge.py`: the Claude judge and its validator.
  - `watch.py`: state handling.
  - `run.py`: the driver.
- `prompts/judge_baseline.md`: the Claude prompt contract.
- `data/resume_jack_spencer.json`: the fictional persona (`@example.com`, 555 number).
- `evidence/raw/`: saved responses (live and SEEDED).
- `state/seen_ids.json`: the state file.
- `runs/`: run reports.
- `experiments/`: sampling, prompt experiment, labels, action-surface runs, and `results/`.
- `ACTION_SURFACE.md`, `SOURCES.md`, `FRICTIONAL.md`.

## Sampling report (Chapter 1)

> Results are from the files listed. The "What I can and cannot conclude" text was drafted by Claude Code. I did not edit it directly. The line "My view…" is my own words.

**Setup.** I picked 5 postings, the closest calls on the board. Claude was asked about each one in 4 fresh conversations: 20 separate sessions (`claude -p`, `claude-opus-5-5`, baseline prompt contract) on 2026-10-31 between 23:43 and 23:44 UTC. All 20 replies passed the validator. My hand labels were made blind to these replies, using `experiments/LABELING_RULE.md`, and committed (`a4d8dd2`) before I looked at them.

| id | posting | my hand label | rule | Claude, 4 fresh calls | Claude majority = my label? |
|---|---|---|---|---|---|
| 6201407004 | Data Platform Engineer | relevant | not_relevant | relevant ×4 | yes |
| 5551686004 | Software Engineer - Data Infrastructure | not_relevant | relevant | relevant ×4 | **no** |
| 6233040004 | Data & Integration Engineer, Business Systems | not_relevant* | relevant | relevant ×4 | **no** |
| 5551532004 | Software Engineer - Machine Learning | not_relevant | not_relevant | not_relevant ×4 | yes |
| 5552549004 | Software Engineer - Distributed Systems | not_relevant | not_relevant | not_relevant ×4 | yes |

\* My first label for 6233040004 was `relevant`. I changed it after Claude pointed out that Jack's résumé has no CRM/ERP experience, and I had already seen Claude's verdict on this posting in run 2 (`experiments/label_revisions.md`). So this label is not independent of Claude.

Source: `experiments/results/sampling_20261031T234336Z.json` (every reply, with its reason). Table rebuilt by `python experiments/sampling.py report …`.

**What I can and cannot conclude:**
- **Spread was zero.** Each posting got the same verdict 4 of 4 times, and the reasons were near-paraphrases of each other. With this prompt and model, Claude's verdict on these 5 postings was *repeatable*.
- **Repeatable is not correct.** Claude's majority matched my label on 3 of 5. On the two disagreements, Claude was unanimously confident and, by my labels, wrong. Agreement with itself told me nothing about agreement with me.
- **My view on the two disagreements:** I stand by my labels.
- **Claude's reasons lean on the title.** Every relevant verdict cites a title match ("matches the target title 'Data Platform'"). My labels turned on must-haves (infrastructure depth, CRM/ERP integration) that Claude treated as gaps, not as disqualifiers.
- **Limits:** 5 postings × 4 calls, one model, one prompt, one evening. All 4 calls per posting ran within about 3 seconds of each other. 4 of 4 identical verdicts is still consistent with Claude flipping on up to about 60% of calls (95% exact upper bound for 0 in 4), so "zero spread" is weak evidence. One label (*) was influenced by Claude.

## Prompt experiment (Chapter 2)

> Results are from the files listed. The "Limits" text was drafted by Claude Code. I did not edit it directly.

**Labels.** I labeled 20 real Figma postings (10 dev, 10 held-out) using `experiments/LABELING_RULE.md`, which was written before labeling. The labels and notes are in `experiments/labels.csv`, and the revisions are in `experiments/label_revisions.md`. They were committed in `a4d8dd2` before any experiment ran. How the 20 were drawn, including two earlier draws I discarded, is recorded in `experiments/make_label_sheet.py`.

**The one change.** `prompts/judge_revision.md` differs from `prompts/judge_baseline.md` in exactly one paragraph, the definition of "relevant":
- *Baseline:* "fits the job seeker's target titles, skills, and seniority, and is full-time".
- *Revision:* the four criteria from my labeling rule (the work is data engineering at its core; the level fits an IC; full-time; Jack could plausibly be shortlisted).

Check with `diff prompts/judge_baseline.md prompts/judge_revision.md`.

| Run (2026-11-01 UTC) | dev (10) | held-out (10) |
|---|---|---|
| Baseline prompt | 10/10 | 10/10 |
| Revision prompt | 10/10 | 10/10 |
| Rule (for comparison) | 10/10 | 8/10 |

A pass means the reply was valid **and** its verdict equaled my hand label. All 40 Claude replies were valid. The held-out set was run only after both dev runs, with `--final`. Results: `experiments/results/judge_{baseline,revision}_{dev,heldout}_*.json`.

**Limits:**
- **All 20 of my labels are `not_relevant`.** A prompt that always answered `not_relevant` would also score 20/20. This experiment could only catch false positives, and there were none. It says nothing about whether either prompt finds relevant postings.
- **The two prompts tied, so the revision showed no measurable improvement.** The agent still uses the baseline prompt (`agent/config.py`). For Agent 2, Claude recommended keeping the revision. Its reasoning: the revision states the same criteria my labels use, a tie means it cost nothing, and the sampling disagreements happened where Claude relied on title matches, which the revision tells it not to do. That recommendation is Claude's. The tie gives no evidence either way.
- **Ten cases per set is tiny.** 10/10 is still consistent with a true error rate of up to about 31% (95% exact upper bound for 0 errors in 10).
- **The rule was the only judge that missed any held-out labels (8/10).** It marked Security Scientist and Data Scientist `relevant` through branch (b) (4+ skills without a title match). Claude, under both prompts, agreed with me on both.
- **The sampling set (above) is where Claude and I disagreed.** That set was hand-picked close calls, not these 20.

## Sign-off: Job-Search Agent 1

> Claude Code drafted these words at my request from the session record and the files cited. The signature line is mine, and I sign only after reading every line.

**Checked:**
- **The rule computes what CONTRACT.md says.** I checked it by hand on 5 postings (README failure-condition row #1). Claude also recomputed all 10 run-2 verdicts by a second method (`scripts/recompute_rule.py`, 10/10).
- **Both wrong versions are caught.** W1 (verdicts paired with the wrong postings, for both judges, including out-of-order replies) and W2 (substring skill matching) fail their checks (`tests/test_wrong_versions.py`).
- **Refusals.** Off-list hosts and off-list redirects are refused (`tests/test_resume_and_fetch.py`). A non-persona résumé stops the run before anything prints (`tests/test_watch_and_run.py`). Malformed Claude output is rejected (`tests/test_claude_validator.py`).
- **The watch.** The baseline reported 0 new. Run 2 reported exactly the 10 ids removed to make the SEEDED file, and only those.
- **Labels.** The 25 hand labels and their notes are mine, committed (`a4d8dd2`) before any experiment ran or any sampling verdict was shown.

**How:**
- **By hand:** the 5-posting rule check, and all 25 labels.
- **By recomputation:** Claude's second-method script for run 2. Claude's script also compared run 2's new ids with the seeded file's meta.
- **By tests:** Claude wrote and ran them (32 pass, 2026-10-31). They were **not** tests I wrote before reading Claude's code.
- **With Claude's help:** Claude drafted the prompt contracts, the labeling rule, the write-ups, and this sign-off.

**Not checked:**
- **A real change on the board across two calendar days.** The second run's change was seeded, and the two live fetches had identical ids.
- **The validator's rejection path on real Claude output.** All 70 real replies were valid, so rejections were only exercised by constructed test strings.
- **Whether either prompt finds relevant postings (recall).** All 20 experiment labels are `not_relevant`.
- **Any board other than Figma, or any persona other than Jack.**
- **Whether Claude's verdicts stay stable over time.** Each posting's 4 sampling calls ran within about 3 seconds.
- **The redirect guard against a real redirect.** It was only tested by calling the handler directly.
- **My own run of the test suite, and a line-by-line review of the code.** I did neither; Claude ran the tests.

**Not claiming:**
- That Claude's verdicts are correct. They are labeled judgments, and on the 5 close calls they matched my labels 3 times out of 5.
- That the rule finds good jobs. On held-out it disagreed with my labels twice, and it missed Data Platform Engineer, which I labeled relevant.
- That the second run shows a real new posting.
- That any of this generalizes beyond one board, one persona, and one evening.

**Signed or withheld:** Akshit Verma, date: 10/31/2026

## Driver's seat

| Part of the task | What Claude did | What I did | Why that part stays mine | Where it shows |
|---|---|---|---|---|
| The contract | asked one question per section and offered options; declined to write a contract disguised as mine | made every decision, accepting the suggestions marked in the file | The contract defines what counts as success. If Claude wrote it, Claude would be setting the standard it is then judged by. | commit `3632004` (contract alone, before code); the marked lines in CONTRACT.md |
| Code and tests | wrote them against the contract, and ran them | checked the rule by hand on 5 postings; did not review the code line by line | A passing test only shows what someone decided to check. The contract's rule is what decides whether the code is right. | README failure-condition row #1; `tests/` |
| Hand labels | built a blind sheet with quoted excerpts; flagged reasons that conflicted with the posting, the résumé, or my rule; declined to suggest labels | labeled all 25 and revised 8 entries after the flags | The labels are the answer key Claude is graded against. They can't come from the thing being graded. | `experiments/labels.csv`, `experiments/label_revisions.md`, commit `a4d8dd2` |
| Is a posting worth Jack's time? | gives a judgment, labeled as model output | the record is the rule I wrote; the final call is mine | Whoever spends the day applying bears the cost of a wrong verdict, not Claude. | `runs/20261031T233955Z_figma_run.txt` (RULE vs CLAUDE lines) |
| Sign-off | drafted the words from the record | sign or withhold after reading it | Only I can be held to what I say I checked. | this section |

> The "why" column was drafted by Claude Code at my request.
