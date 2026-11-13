# Review packet: the years rule misses posting 19

One non-trivial change I asked Claude Code to make, reviewed the way the JS2 brief asks: the bug reproduced, my test written before the patch, the diff read as a change in behavior, whether it stayed in scope, the commands I ran myself, and my decision with the evidence. Text marked as mine is my own, sent in chat and copied word for word; Claude Code adds the facts, commands and outputs around it.

## 1. The bug

Contract v0.1, check 7, reads years of experience only in sentences that contain the word "experience". Posting 19 of my JS1 labels, OpenAI's "Software Engineer, Workload Enablement" (`9efcef02-0515-4672-bace-81329944b38b`), states its requirement without that word:

> - 5+ years in one or more of: ML systems, performance engineering, distributed systems, or HPC.

So the rule reads no years at all and calls the posting relevant for Jane Doe, who has 3. This miss was first noted in JS1 (js1/FRICTIONAL.md, Friday entry).

## 2. Reproduced (2026-11-08, 5:24 PM ET, by me)

```text
python3 tools/explain_rule.py runs/2026-10-30T093102Z/response.json 9efcef02-0515-4672-bace-81329944b38b
```

Output (as logged in MY-CHECKS.md): "Rule verdict (record): relevant" and "Check 7 (years of experience): passes. Posting descriptionPlain states no years of experience, which is not a requirement".

**What I ran and saw (mine):** Running explain_rule.py on posting 19 from the October 30 saved answer showed that the rule marked it relevant because check 7 only checks sentences containing the word "experience" and missed the actual requirement of "5+ years". Consequently, the agent failed to catch that Jane only has 3 years of experience and incorrectly let the posting pass.

**To see the bug again after the patch (a note added on 2026-11-09):** the command above now applies contract v0.2, whose check 7 reads the "5+ years" and calls the posting not relevant. `--contract 0.1`, added to the tool on 2026-11-09 with a test, shows the reading I reproduced:

```text
python3 tools/explain_rule.py --contract 0.1 runs/2026-10-30T093102Z/response.json 9efcef02-0515-4672-bace-81329944b38b
```

## 3. My prediction, before any count (2026-11-08, 5:40 PM ET)

The question: of the 95 postings my rule calls relevant on the 2026-10-30 baseline (814 postings), how many flip to not relevant once years are also read outside "experience" sentences?

**My guess (mine):** I guess 12, because while 60 total postings state years without the word "experience", most of those are already rejected by earlier checks on job title or level.

## 4. How years should be read (contract v0.2)

Measured after my guess was committed (e3ea1e2), on OpenAI's 2026-10-30 answer and on the three boards' answers from my live run 1 (2026-11-08):

| Reading | OpenAI Oct 30 (95 relevant) | OpenAI Nov 8 (91) | Verkada (5) | Palantir (9) |
|---|---:|---:|---:|---:|
| A: keep v0.1, only sentences with "experience" | 0 flip | 0 | 0 | 0 |
| B: every sentence that states years | 2 | 2 | 0 | 0 |
| C: "experience" sentences plus bullet lines | 2 | 2 | 0 | 0 |
| D: "experience" sentences plus "N years in/of/with/as/at/on" or "N years <doing>" | 2 | 2 | 0 | 0 |

The same two OpenAI postings flip under B, C and D: posting 19, and "Software Engineer, Data Infrastructure" ("- Have 4+ years in data infrastructure engineering OR"). **My guess was 12; the count is 2.** The readings differ only on postings the rule already rejects for other reasons. Of the 8 sentences that B reads and C and D do not, 6 on Verkada are real requirements (for example "2+ years productionizing modern LLMs, VLMs, or agentic systems" and "for the last 3+ years within a similar company"), and 2 are not: Palantir's "team was formed 15+ years ago" and Verkada's "5x the business over the next 3 years". C also depends on bullet marks, which Greenhouse's HTML lists lose when they become text.

**My pick (2026-11-08, multiple choice, after seeing this table): E**, every sentence that states years, except "N years ago" and "the next N years". Claude Code laid out A to E and recommended E.

## 5. My test, written before the patch

`tests/test_years_v02.py`, drafted by Claude Code from my pick E, five tests on real sentences from my saved answers:

| Test | Line or posting | Must give |
|---|---|---|
| posting 19's requirement is read | "- 5+ years in one or more of: ML systems, ..." | 5 years |
| a Greenhouse requirement without the word "experience" is read | Verkada: "2+ years productionizing modern LLMs, VLMs, or agentic systems ..." | 2 years |
| years ago is not a requirement | Palantir: "... PCL team was formed 15+ years ago ..." | nothing |
| the next N years is not a requirement | Verkada: "... help us 5x the business over the next 3 years." | nothing |
| both OpenAI postings are no longer relevant for Jane | posting 19 and "Software Engineer, Data Infrastructure" | not_relevant, decided by check 7 |

I ran it on 2026-11-08 at 5:45 PM ET, before any patch existed: `FAILED (failures=4)`. The two tests that say a wording is not a requirement passed, as they must before and after the patch.

## 6. The patch, and the diff read as a change in behavior

**The patch (Claude Code, commit `4b1a418`, after my test in `788852b`).** 8 files, 89 lines added and 18 removed (`git show --stat 4b1a418`):

| File | What changed |
|---|---|
| `job_agent/rule.py` | `years_asked` reads years in every sentence, except a number followed by "ago" or preceded by "next"; `judge`, `check_years` and `years_asked` take a contract version, and "0.1" keeps the old reading word for word |
| `CONTRACT.md` | version 0.2: check 7's new wording, and my decision under "Where these choices come from" |
| `job_agent/__init__.py` | `CONTRACT_VERSION` 0.1 to 0.2 |
| `tests/test_rule.py` | JS1's check-7 test now runs with contract "0.1" (what it was written for); a v0.2 test beside it; v0.1's baseline counts kept, and a new test that v0.2 flips exactly 2 baseline postings |
| `tools/experiment.py`, `tools/select_postings.py` | pinned to contract "0.1", because JS1's experiment and seeded selection were made with it; their committed reports and selection are unchanged |
| `tools/rule_verdicts.py` | `--flips`: every posting whose verdict differs between v0.1 and v0.2 |
| `tools/mutants.py` | 3 planted mistakes for the new reading: 61 of 61 caught |

Measured on the 2026-10-30 baseline after the patch: 95 relevant become 93, and check 7 decides 50 postings instead of 48. The two flips are posting 19 and "Software Engineer, Data Infrastructure". My test passes, and so do all 202 tests on Python 3.12 and 3.9.

**My reading of the diff as a change in behavior (mine):** Before, check 7 only read years in sentences containing "experience." Now, it reads every sentence containing numbers and years, skipping only specific exclusions like "N years ago" or "the next N years," which means even unrelated sentences like company history are read.

## 7. Scope

**Facts:** the reading changed only inside check 7; checks 1 to 6 have no changed line. Beyond `rule.py`, the patch touched JS1's experiment and selection tools only to pin them to v0.1, and JS1's tests to say which contract each one checks. v0.2 also reads two sentences that are not requirements, and the v0.2 test pins both: "10+ years in the industry is a plus." now blocks for Jane, and "We have grown 10x in 2 years." is read as 2 years, which Jane has.

**My judgment of the scope (mine):** Yes, the change stayed strictly in check 7 with version plumbing keeping JS1 evidence tied to v0.1. I accept the risk that bonus statements like "10+ years in the industry is a plus" make the rule stricter because across all four saved answers from three boards, the change flipped only the two real requirements and caused zero false drops from bonus lines.

**The "OR" in the Data Infrastructure posting (checked after my `--flips` run):** its line ends with "OR", and the next line is the alternative: "- Have 4+ years in infrastructure engineering with a strong interest in data". Both paths ask for 4+ years, so the flip holds either way. Both lines sit under "You might thrive in this role if you:", which the rule reads as requirements in v0.1 and v0.2 alike.

## 8. Commands I ran myself

All in my own terminal on 2026-11-08 (ET), with their output logged in MY-CHECKS.md:

| When | Command | Result |
|---|---|---|
| 5:24 PM | `python3 tools/explain_rule.py runs/2026-10-30T093102Z/response.json 9efcef02-0515-4672-bace-81329944b38b` | the bug: relevant, check 7 "states no years" |
| 5:45 PM | `python3 -m unittest tests.test_years_v02` (before the patch) | FAILED (failures=4) |
| 6:00 PM | `python3 -m unittest tests.test_years_v02` (after the patch) | OK, 5 of 5 |
| 6:01 PM | `python3 tools/rule_verdicts.py runs/2026-10-30T093102Z/response.json --flips` | 2 flips: Data Infrastructure (N = 4) and Workload Enablement (N = 5), relevant to not_relevant |
| 6:02 PM | `python3 tools/mutants.py` | 61 of 61 planted mistakes caught, including the 3 for the new reading |
| 6:24 PM | `git --no-pager show 4b1a418 -- job_agent/rule.py CONTRACT.md` | the diff of check 7 and the contract, printed in full |

## 9. My decision (accept, revise or reject) and the evidence

**Mine:** Accept. My evidence is clear: the tests went from 4 of 5 failing to 5 of 5 passing after the patch, exactly two postings flipped and both were correct (including the "OR" requirement), and all 61 planted mistakes across the suite were successfully caught.

## 10. One case my test would still miss

**Mine:** A common case it still misses is when words break up the expected phrasing, such as "a minimum of 5 calendar years" or abbreviations like "5+ yrs" and "Five-plus years."

Checked by Claude Code on 2026-11-08 with `rule.years_asked`, which reads no years in "A minimum of 5 calendar years in backend.", "5+ yrs in backend." or "Five-plus years in backend.", and reads 5 in "5 or more years of backend work.", a wording the pattern lists by name.
