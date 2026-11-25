# What moves the score (JS3 2.4)

**Question:** where does every number and prompt in the scorer come from? And when one of them changes, alone, does the result move on labels nobody tuned on?

Written 2026-11-25. Everything below comes from files in this repo, and each claim names its file.

## 1. Where every number comes from

Three origins: **hand-set** means I decided it from the persona or my own judgment, without looking at labels. **Fitted** means it was chosen after looking at labels or results. **Inherited** means it was taken over from an earlier version and not re-decided.

How the list was built: every literal in `personas/aarav-patel.profile.json`, `data/*.json`, `prompts/`, `job_agent/judges/`, `job_agent/loop/budget.py` and `GATE.md`, plus the module-level constants that `grep -rnE "^[A-Z_]+ *= *[0-9\"'(\[]" job_agent reports` finds. Constants that only name things (ATS names, field names, file suffixes) are left out.

### Filter (rule judge)

| Number / list | Where | Origin | Evidence |
|---|---|---|---|
| `min_salary` 75,000 | profile | hand-set (JS1 persona) | profile committed `a1f0ee6` 2026-10-31 13:56, before any label (`ab1e292` 18:16) |
| `years_experience` 2 | profile | hand-set, from the fictional résumé (Infosys 2021-06 to 2023-07) | same commit |
| `years_stretch` 2 (so 2 + 2 = 4) | profile | hand-set (JS1). Since FILTER v2 its reason is a ratio ("at least half"), which gives the same line for 2 years | FILTER.md rule 4; D8 |
| `target_roles` (5), `exclude_title_words` (12) | profile | hand-set (JS1), never changed | `git log -- personas/aarav-patel.profile.json`: 2 commits, neither touches these |
| `locations`: boston, us remote, us | profile | hand-set (JS1) | `a1f0ee6` |
| `locations`: + "united states" | profile | **fitted on observed data**: added after JS2 runs showed real US postings cut (JS2 D7), not on labels | `4d1a32c` 2026-11-08 |
| skills threshold ≥ 1 | `checks.py` `skills` | inherited from JS1 CONTRACT. ≥ 2 was measured against my audit labels and rejected | FILTER.md §5 (v2 C) |
| 13 no-sponsorship phrases (14 since v2.1), 10 skill aliases | `data/` | hand-set (JS1). One phrase was **fitted on a held-out posting** (H01) in v2.1 | `a1f0ee6`; FILTER.md §5 v2.1 |
| rule 4: largest years number + new-grad ceiling | `checks.py` `years`, `words.py` | **fitted on my 50 audit labels** (S01, S16, S20), 2026-11-25 | FILTER.md §5, `14a0b41` |
| rule 4 v1: smallest number | — (v1) | inherited from JS1 CONTRACT "Numbers", replaced in v2 | `audit/v1/` |
| rule 6: largest `$NNN,NNN` | `checks.py`, `words.py` | inherited from JS1 CONTRACT | FILTER.md rule 6 |
| "missing field = pass" (rules 2, 4, 6) | `checks.py` | hand-set (JS1 CONTRACT), confirmed as D3 2026-11-24 | FILTER.md §2 |

### Claude judge

| Number / text | Where | Origin | Evidence |
|---|---|---|---|
| model `claude-sonnet-5-5` | `judges/claude.py` | hand-set (my choice, JS1 PLAN 2026-10-30) | code comment |
| prompt v1 | `prompts/claude_judge.v1.md` | hand-set (JS1) | `reports/prompt_experiment.md` |
| prompt v2 (strictness paragraph) | `prompts/claude_judge.v2.md` | **fitted on JS1 dev labels** (chosen from v1's 2 dev misses) | `reports/prompt_experiment.md` "The one change" |
| prompt v3 (years line) | `prompts/claude_judge.v3.md` | **fitted**: written from FILTER v2 rule 4, which came from my audit labels | `66d2c73` |
| default prompt the agent runs | `pipeline.py` `DEFAULT_PROMPT` | was v1, **inherited and never updated** after JS1 measured v2 better (9/10 vs 7/10); set to v3 on 2026-11-25 (D10) | `reports/prompt_experiment.md`; `pipeline.py:27` |
| one call's timeout 300 s | `claude_cli.py` | hand-set (JS2 GATE §2) | GATE.md |

### Loop budgets (JS2 GATE)

| Number | Where | Origin |
|---|---|---|
| 4 boards, 10 board requests, 120 s per run without Claude, 10 s per request | GATE.md §2 | hand-set (JS2) |
| 30 Claude calls and 300 s per run, 480 s total | GATE.md §2, `loop/budget.py` | hand-set (JS2, D20) |
| 3 attempts per board (1 + 2 retries) | `loop/runner.py` | hand-set (GATE §3) |

### Measurement settings (JS3)

| Number | Where | Origin |
|---|---|---|
| audit sample 30 / 10 / 10, seed 20261124 | `reports/audit_sample.py` | hand-set (brief minimum 30; the rest my choice) |
| held-out 20, seed 20261125, pool of 147 | `reports/heldout_sample.py` | hand-set (I chose fresh labels only) |
| 95% Clopper–Pearson | `reports/audit_report.py` `ALPHA` | hand-set |

## 2. One change at a time, on held-out labels

**Held-out set:** 20 postings drawn from the 147 that reach the JD checks (pass rules 1a, 1b and 2). Excluded: the 50 audit samples and the 20 JS1-labeled postings. The sample was committed before I labeled it (`de5824c`), and my labels before any run (`66d2c73`): 6 relevant, 14 not_relevant. With 20 postings, one posting is 5 points.

### E1 — object changed: the filter file (FILTER.md v1 → v2, rule 4 only)

| | matches my 20 labels |
|---|---|
| rule v1 | 12 / 20 |
| rule v2 | 13 / 20 |

Data: `reports/f5/e1_rule.heldout.json` (script `reports/f5_experiment.py e1`, no Claude call).

**This +1 is not a clean held-out result.** The only posting where v1 and v2 differ is H11, "Software Engineer, Developer Productivity" ("Have 5+ years of experience in engineering, including 3+ years…"). It is one of the 7 B2 postings Claude showed me while I decided on B2, and the held-out pool did not exclude those 7. That was Claude's mistake in drawing the sample. On the other 19 postings, v1 and v2 give identical verdicts (12 / 19 each). So on unseen postings, v2 did not move the score. What it fixes (new-grad ceilings, totals hidden behind smaller numbers) did not come up in them.

The 7 misses that remain under both versions come from the filter's word-level limits, not from rule 4:
- **H02, H10, H17, H19** are cut at rule 3 ("0 found") although I would apply. I read the backend, API and tooling fit; no résumé keyword appears as a word.
- **H04, H18** are kept although they require Terraform/Go/Ansible/Puppet/Ruby or "two years of production Go". Rule 3 passes on any one shared word.
- **H01 is a new false friend, found only by the held-out set.** Rule 5 cut it on "without sponsorship", but the sentence is Cloudflare's export-control boilerplate: "…authorization to receive software or technology controlled under these U.S. export laws **without sponsorship for an export license**." It is about an export license, not a work visa. All 8 rule-5 cuts in the 2,123 postings are this same sentence (`audit/all_verdicts.json`, result `found: without sponsorship`), and none of them was in the 50-posting audit sample. In the held-out set it hits H01, H06 and H16. For H06 and H16 I said not_relevant for other reasons, so the cut was right by accident. Fixed in FILTER v2.1 (Isaac, D10): the phrase became "work without sponsorship" + "without visa sponsorship". Measured: relevant 59 → 67, audit 45 → 45 of 50, **held-out 13 → 12 of 20** (H01 fixed; H06 and H16, cut right by accident, are now kept). The rule's reason is now true, but its score is lower. Since H01 was read to find this, the held-out number after the fix is not an unseen measurement (FILTER.md §5 v2.1).

### E2 — object changed: the Claude judge prompt (v2 → v3, one line)

Only line 25 differs (`diff prompts/claude_judge.v2.md prompts/claude_judge.v3.md`):
- v2: "Is the experience the posting requires within `years_experience + years_stretch`?"
- v3: "Does the job seeker have at least half of the experience the posting requires? Take the largest number of years the posting asks for as the requirement… If the posting sets an upper limit below `years_experience`… they are too experienced for it."

Everything else is the same: model `claude-sonnet-5-5` via `claude -p`, profile, résumé, validator, the 20 postings. Each prompt ran once on the held-out set, on 2026-11-25, 20 calls each, 0 rejected answers. v3 was committed before either run (`66d2c73`).

| | matches my 20 labels |
|---|---|
| prompt v2 | 13 / 20 |
| prompt v3 | 13 / 20 |

**v2 and v3 gave the same verdict on all 20 postings.** The change moved the wording of Claude's reasons, but no verdict. v3's reasons now use the ratio, e.g. H08: "requires 5+ years, but the job seeker has about 2 years, below the half (2.5) needed". On these 20, every posting Claude cut for years was out of reach under both readings (5+, 6+, 7+, 9+ years). **Decision (Isaac, D10): v3 is adopted for consistency, not for its score.** On held-out it did no better and no worse. I adopted it so that Claude and the rule judge years the same way (FILTER v2 rule 4), in the ratio terms I actually think in. Why it could not score better on Aarav: Claude under v2 already read "5+ years, including 3+…" as 5 (H11's v2 reason), so "largest number" was a fix the rule needed, not Claude. And for 2 years, "at least half" and "≤ 2 + 2" draw the same line. The only postings where v3 could differ are new-grad ceilings, and those are 3 in all 2,123, none in the held-out set. No extra run was made for this decision. The agent's default prompt is now v3 (`pipeline.py`), replacing v1, which had stayed the default since JS1 although JS1 measured v2 better. The profile field `years_stretch` is not renamed: v3 doesn't need it renamed, and the rule gives the same line for Aarav.

Both prompts miss the same 7 (H03, H04, H06, H12, H15, H16, H18). All 7 are Claude saying relevant where I said not_relevant. That is v2's "relevant unless clearly a bad fit" paragraph, the change JS1 chose, being more lenient than I am on postings outside Aarav's backend core.

Data: `reports/f5/e2_claude_judge.v2.heldout.json`, `…v3.heldout.json` (every verdict and justification), `.raw.jsonl` (every reply as received, with session id and token usage). Console logs: `evidence/js3/f5_e2_v2_run.txt`, `f5_e2_v3_run.txt`. The raw replies carry no cost field, so cost is not reported.

### What the two runs show together

| | rule v2 | Claude (v2 or v3) |
|---|---|---|
| matches my labels | 13 / 20 | 13 / 20 |
| right where the other is wrong | H03, H06, H12, H15, H16 | H01, H02, H10, H17, H19 |

They score the same, but they make **different** mistakes. The rule cuts postings I would apply to when no résumé word appears, or on the export-license false friend (H01). Claude keeps postings I would skip because it leans toward relevant. One score of 13/20 hides two opposite kinds of error.

**Limits:** 20 postings, so one posting is 5 points, and a 1-posting difference is not evidence of anything. One run per prompt: JS1's sampling report found no verdict variation over 4 fresh tries on 5 postings, but that was not repeated here.

## 3. What persistence is not proof of

The agent's behavior can change between sessions without anything having learned:
- **What persists here is files, not the model.** `claude-sonnet-5-5` is the same in every run, and nothing in this project trains or updates it. Between sessions only these carry over: `state/` (posting ids already seen), `prompts/`, the profile, `data/`, `FILTER.md` and the code. When a verdict changes from one day to the next, the first question is which of these files changed, and git answers it.
- **A different answer in a new session is not a lesson learned.** E2 is the example: the reasons changed wording because the prompt text changed. The model did not "understand the ratio" between runs. Remove line 25 and the old wording comes back.
- **A stable answer is not a correct answer.** JS1's sampling got the same verdict 4 of 4 times on 5 postings, and one of those stable verdicts was against my label (8072257). In E2, the 7 shared misses are just as consistent, and just as wrong.
- **A Claude Code session that "remembers" this project** does so through files it reads at start (CLAUDE.md, memory files, task logs). Those are context, not training. Deleting them would remove the "memory".
- **A newer score on new labels is not the same test.** JS1's held-out (9/10 for v2) and this held-out (13/20) are different postings labeled at different times. The numbers can't be compared as "Claude got worse".
