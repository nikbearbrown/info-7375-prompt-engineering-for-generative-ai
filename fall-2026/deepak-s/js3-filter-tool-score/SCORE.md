# SCORE.md: what moves the score

Job-Search Agent 3. Facts written by Claude Code (claude-opus-5-5) on 2026-11-25 from FILTER.md and the code; each row cites file:line. Sections 4 and 5 are Deepak's.

## 1. Where every number and setting came from

Origin: **hand-set (Deepak)** = chosen by Deepak in FILTER.md or at a gate; **hand-set (Claude Code)** = chosen by Claude Code while building, not by Deepak; **inherited** = carried from JS1 or JS2 unchanged; **fitted** = chosen by measuring on labels. No number in this agent was fitted on labels: the Gate 3b candidates were measured on the audit labels, and all five were rejected (FILTER.md section 8), so v1 is unchanged.

| Number or setting | Value | Where (file:line) | Origin |
|---|---|---|---|
| Role weight | 5 | FILTER.md:101; jobwatch/filter.py:46 | hand-set (Deepak) |
| Location weight | 2 | FILTER.md:101; jobwatch/filter.py:47 | hand-set (Deepak) |
| Topic weight (each topic once) | 1 | FILTER.md:101; jobwatch/filter.py:48 | hand-set (Deepak) |
| Threshold T | 8 | FILTER.md:103; jobwatch/filter.py:30 | hand-set (Deepak) |
| E01 maximum minimum-experience | 5 years | FILTER.md:90; jobwatch/filter.py:45 | hand-set (Deepak) |
| Role, location and exclusion word lists | R01-R05, L01-L05 terms, X01-X06 | FILTER.md section 1 table; jobwatch/filter.py V1 | inherited (JS1 persona, examples/persona_resume.json:11-13) |
| Added rule words | X07-X09, R06-R10, T01-T18 | FILTER.md section 1 table; jobwatch/filter.py V1 | hand-set (Deepak) |
| US tokens for Remote | us, usa, united states, u s | FILTER.md:71; jobwatch/filter.py:65 | hand-set (Deepak, Gate 1 decision A) |
| E01 skip words and experience words | preferred, nice to have, bonus, ideally, plus; experience, experienced | FILTER.md:90; jobwatch/filter.py:71-72 | hand-set (Deepak, Gate 1 decision C) |
| Boilerplate share | 50% of one board's postings | FILTER.md:119; jobwatch/dataset.py:27 | hand-set (Deepak) |
| Close-call counts | 10 rejected, 5 kept | FILTER.md:105; jobwatch/audit.py:27 | hand-set (Deepak) |
| Random audit sizes | 30 rejects, 10 keeps | brief (at least 30) and Phase 3b plan; jobwatch/audit.py:27 | hand-set (Deepak's plan) |
| Near-decision group | all role-matched rejects | FILTER.md:106; jobwatch/audit.py `near_decision` | hand-set (Deepak, after measuring v1) |
| Held-out sizes | A 30, B 10 | FILTER.md:176; jobwatch/heldout.py:22 | hand-set (Deepak) |
| Held-out word lists | stratum A 6 words; broad 14 words | FILTER.md:176; jobwatch/heldout.py:19-21 | hand-set (Deepak, Gate 0) |
| Held-out seeds | A 7375011, B 7375012 | labels/heldout.csv header; commit 30c52ef | hand-set (Claude Code) |
| Audit seed | 7375031 | audit/audit-v1.csv header; commit 8be6822 | hand-set (Claude Code) |
| Draw method | sort by tie order, random.Random(seed).sample | FILTER.md:107; jobwatch/heldout.py, jobwatch/audit.py | hand-set (Deepak, Gate 1 V7) |
| Gate 3b adoption criterion | fixes at least one audit error and creates none | FILTER.md section 8 rows; jobwatch/measure.py | hand-set (Deepak, before measuring) |
| JS1 normalization steps | two html.unescape passes, tags stripped, whitespace collapsed | FILTER.md section 1; jobwatch/text.py | inherited (JS1 Amendment A3), changed by Deepak: no 6000-character truncation (JS1 jobwatch/postings.py:10 kept the limit) |
| Sentence rule | ., ! or ? before whitespace or end; end of p, li, h1-h6, div, br | FILTER.md section 1; jobwatch/text.py `_BOUNDARY` | hand-set (Deepak, Gate 1 M4; wording from a claude.ai chat) |
| Loop budgets | max_boards 6, max_requests 20, max_seconds 120, request_timeout 10 s, 1 s between same-host requests, 1 retry, 2 s backoff | config/budgets.json:5-11 | inherited (JS2 b2ac533, byte-identical) |
| Judge model | claude-sonnet-5-5 | jobwatch/claude_judge.py:20 | inherited (JS1 jobwatch/judge.py:13) |
| Judge CLI flags | -p, --output-format json, --system-prompt, --tools "", --strict-mcp-config, --safe-mode, --disable-slash-commands, --no-session-persistence, --model | jobwatch/judge_cli.py:33-36 | inherited (JS1 Amendment A14) |
| Judge timeout | 120 s | jobwatch/judge_cli.py:24 | inherited (JS1) |
| Claims prompt | prompts/js3_claims_v1.md | whole file | hand-set (Claude Code) |
| Claims per posting from the judge | at most 2 | jobwatch/shortlist.py:31 | hand-set (Deepak's Phase 4 plan) |
| E3 relevance prompt | prompts/js3_relevance_v1.md (quotes FILTER.md section 0) | whole file | hand-set (Claude Code; the rule text is Deepak's) |
| Tool server protocol | 2026-07-28 | jobwatch/mcp_server.py:37 | hand-set (Deepak's pre-set rule, applied to the probe) |
| Tool server cache hint | ttlMs 300000, cacheScope public | jobwatch/mcp_server.py:137, 139 | hand-set (Claude Code) |
| Labeler page size, override reason length | 30 lines; 15 characters (family mode) | jobwatch/label.py:37, 61 | hand-set (Claude Code; 15 characters by Deepak) |
| E2 setting | location weight 0 | jobwatch/experiments.py:33 | hand-set (Claude Code, from FILTER.md:102) |

## 2. Experiments, one change to one object at a time, on the held-out postings

The held-out postings are the 40 drawn in 30c52ef (stratum A 30, stratum B 10), found by redrawing with the recorded seeds. Labels: Deepak's first pass (8625eea), committed empty in e6fe828 after a `label --clear` and restored to the first-pass content in 3d130ae; the report uses 3d130ae. The label-based numbers (agreement, precision, recall and their exact intervals) are produced by `python -m jobwatch experiment-report` into `experiments/results.md` (section 3).

### E1. The filter file: v1 against the final version

- Object changed: none. No Gate 3b candidate was adopted, so the final filter version is v1 (FILTER.md section 8; AUDIT.md section 6b). For information, each rejected candidate C1 to C5 was also run on the held-out postings; that measurement chose nothing.
- Commit: decisions in 3f782ce (`experiments/E1-decisions.json`, by `python -m jobwatch experiment-filter`).
- Counts: v1, the final version and each of C1 to C5 reject all 40 held-out postings: stratum A 30/30 rejected, 0 kept, 0 abstained; stratum B 10/10 rejected, 0 kept, 0 abstained. With 0 kept, precision has no denominator in either stratum.

### E2. A setting: the location weight, 2 → 0

- Object changed: `location_weight` (FILTER.md:101-102 keeps it in the score "so that it can be changed as a setting in Phase 6"); T stays 8. The threshold itself was hand-set, not fitted on audit labels, so the plan's threshold experiment does not apply; this is the setting FILTER.md names for Phase 6.
- Commit: decisions in 3f782ce (`experiments/E2-decisions.json`).
- Counts: both arms reject all 40 held-out postings (A 30/30, B 10/10). No held-out posting passes the role and location gates, so the location weight cannot change any decision on this set.

### E3. The context given to Claude: title only against title plus text

- Object changed: the context given to Claude. Baseline: the posting title and its normalized text; change: the title alone. Location is in neither arm. Prompt `prompts/js3_relevance_v1.md` (it quotes the FILTER.md section 0 labeling rule), JS1 claude-cli backend, model claude-sonnet-5-5 (reported by the CLI for all 120 calls).
- Order: the unchanged baseline twice first, then the change once: title+text run 1 (21:28:26Z to 21:29:37Z), run 2 (21:29:38Z to 21:30:43Z), title only (21:30:44Z to 21:31:57Z), all 2026-11-25 (`experiments/E3/*.json`; every call's prompt, argv, raw response and metadata in `experiments/E3/<arm>-run<N>/`). Commit fefe60e.
- Counts: every one of the 120 answers is not_relevant: stratum A 30/30 and stratum B 10/10 in each run; 0 calls without a usable answer.
- Movement between the two identical baseline runs: 0 of 30 (A), 0 of 10 (B). Movement between the baseline and the change: 0 of 30 (A), 0 of 10 (B), against either baseline run.
- The change moved no more labels than the identical baseline runs moved (0 and 0), so no conclusion about the change can be drawn from this run. With every answer not_relevant in every arm, the context change and the run-to-run noise are both invisible on these 40 postings.

## 3. Results against the held-out labels

From `experiments/results.md` and `experiments/results.json`, written by Deepak with `python -m jobwatch experiment-report --dataset data/postings-20261125T200226Z.jsonl --heldout-seed-a 7375011 --heldout-seed-b 7375012` and committed in db0670b (on the held-out labels of 3d130ae). Per stratum, never pooled. Rates are k/n with the exact (Clopper-Pearson) 95% interval; abstentions (none here) would be excluded.

- Held-out labels: stratum A 20 of 30 relevant, stratum B 8 of 10 relevant; 2 OVERRIDEs.
- E1 (v1 = final, and each rejected candidate C1 to C5): every arm keeps 0, rejects 30 (A) and 10 (B), abstains 0. Agreement with the labels: A 10/30 = 0.333 [0.173, 0.528]; B 2/10 = 0.200 [0.025, 0.556]. Precision: no denominator (0 kept). Recall: A 0/20 = 0.000 [0.000, 0.168]; B 0/8 = 0.000 [0.000, 0.369]. The arms do not differ on any count.
- E2 (location weight 2 → 0): both arms identical to E1's numbers (A agreement 10/30, recall 0/20; B 2/10, 0/8). The setting changes no decision on this set.
- E3 (title plus text, twice; title only, once): every run said not_relevant to all 40. Agreement A 10/30 = 0.333 [0.173, 0.528], B 2/10 = 0.200 [0.025, 0.556] in every run; precision no denominator; recall A 0/20, B 0/8. Labels moved: baseline run 1 vs run 2 0/30 (A), 0/10 (B); baseline vs title only 0/30 (A), 0/10 (B). The change moved no more than the identical runs, so no conclusion about the context change can be drawn.
- Known limits of these labels: they are the first labeling pass (8625eea, restored in 3d130ae), made before the labeler's "r does not mean reject" hint and never relabeled; the audit's first pass from the same session had mis-keys (AUDIT.md section 1).

## 4. What persistence is not proof of

Several things in this project made behavior persist across sessions: CLAUDE.md, the .mcp.json registration, the committed FILTER.md, and the labeler resuming from the first empty row. None of them trained a model. The Claude judge giving the same answer in every run is not evidence that it learned anything either; it is the same model reading the same prompt.

## 5. Deepak's reading of E1 to E3

E1 (the filter file) and E2 (the location weight) changed nothing: every arm rejected all 40 held-out postings, including all 30 in stratum A, where my labels mark 20 as relevant. That fact does not depend on the labels: v1 keeps none of the held-out postings, which agrees with the audit that v1 is too strict. The label-based numbers are weaker than they look. My held-out labels are my first pass (8625eea), never relabeled, and they mark 8 of 10 stratum B titles relevant, which is the same kind of mis-key I found in the audit's first pass. So I do not read the recall of 0/20 and 0/8 as a precise measurement. E3 (title only against title plus text given to the Claude judge) moved nothing: the judge answered "not relevant" in all 120 calls, both identical baselines included, so no conclusion can be drawn about context.
