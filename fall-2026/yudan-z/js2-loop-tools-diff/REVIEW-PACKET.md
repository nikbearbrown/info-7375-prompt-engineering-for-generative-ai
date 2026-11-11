# Review packet — R3 and US states written in full

## Executive summary

I asked Claude Code to fix one real defect in my rule and reviewed its change on evidence before accepting it.
- **The defect:** R3 ("the job is in the US") read only two-letter state codes. Databricks writes `San Francisco, California`, so **364 of 1,561 real postings** from run 1 failed R3 although they are in the US.
- **What I did:** I predicted the expected answers, the tests were written from them and failed first, and I read Claude Code's diff as a change in behaviour on all 1,561 real postings.
- **Decision: revise, then accept.** The first patch silently left out Georgia, which still missed 6 real US postings, and its docstring announced a contract revision I had not approved. After one revision, R3 changed from fail to pass on all 364 postings and from pass to fail on none. No final verdict changed on this day's data.

All files are in `review/`, numbered in the order they were made on 2026-11-09.

## 1. The defect, reproduced before any change

`python review/reproduce_r3.py` on run 1's saved responses → `review/01-reproduce-before.txt`:

```
rule.py R3 on 1561 real postings from 3 systems
  ashby: 0 of 172 fail R3 although the location names a US state in full
  greenhouse: 364 of 1085 fail R3 although the location names a US state in full
  lever: 0 of 304 fail R3 although the location names a US state in full
```

Examples include `Bellevue, Washington; Mountain View, California; San Francisco, California` on Databricks posting 7586263002, "Associate Product Manager, New Grad (2027 Start)".

## 2. My predictions, and the test written before the patch

Before any patch, I decided what each location should give. Commit `20799aa` holds the test, and `review/02-test-before-patch.txt` shows it failing on the old code (4 of 8 tests failed).

| Location | My prediction | Why |
|---|---|---|
| `San Francisco, California`, `New York City, New York` | pass | US city with its state |
| `Washington, D.C.` | pass | the US capital |
| `Remote - California` | pass | remote, but tied to a US state (bare `Remote` still fails, as in JS1) |
| `California; New York` | pass | a state name alone is still a US location |
| `Tbilisi, Georgia` | fail | the country Georgia |
| `Toronto, Canada`, `London, United Kingdom`, `Bengaluru, India` | fail | not the US |
| `San Francisco, CA` pass · `Toronto, ON, CA` fail · `Remote` fail | unchanged | JS1 behaviour kept |
| `Indianapolis Avenue, London, United Kingdom` | fail | a state name inside another word must not count |

## 3. The change Claude Code made

The prompt is in `review/03-prompt-to-claude-code.txt`. It ran in a separate Claude Code session (`claude -p`, Read/Edit/Grep/Glob only; no shell, no network), and its full log is in `review/03-claude-code-session.jsonl`. The diff is in `review/04-diff.txt`: a list of full state names plus one line in `_segment_is_us`.

## 4. The diff read as a change in behaviour

`review/compare_behaviour.py` runs the rule before the change (a frozen copy, `review/rule_before_r3.py`, so no git is needed) and the patched rule on every real posting and lists every location whose R3 result changed. The output is in `review/05-behaviour-change.txt`.

- **R3 changed on 358 postings, all fail → pass.** Every location in the list is in the US. Claude read all 88 distinct locations; the list is in the file so anyone can check it.
- **Not fixed:** 6 postings. `review/06-reproduce-after.txt` shows that `Atlanta, Georgia` and `Remote - Georgia` still fail, because the patch had **left Georgia out entirely** to make `Tbilisi, Georgia` fail. The diff says so only in a code comment.
- **No final verdict changed.** Every affected posting already fails another check, such as the title (R1) or seniority (R2). The fix matters for future postings, not for this day's results.

## 5. Scope

| Question | Finding |
|---|---|
| Files touched | `agent/rule.py` only. No test was edited, and nothing outside R3 changed. |
| Beyond the request | The docstring said "Revision 2026-11-09", a contract change I had not approved. That is out of scope: a revision is my decision, written in `CONTRACT.md`. |
| Hidden trade-off | Georgia was dropped to satisfy the Tbilisi test, so US Georgia postings were still failing. |

## 6. My decision: revise, then accept

- **Revise (2026-11-09).** First, two more tests (`test_georgia_the_us_state`, commit `db56c1e`) failed on the first patch (`review/09-tests-before-revision.txt`). Then the same Claude Code session got the revision prompt (`review/10-revision-prompt.txt`): keep Georgia, read it as the country only next to a city of the country Georgia, and remove the "Revision" wording. The new diff is in `review/11-diff-after-revision.txt`.
- **Evidence after the revision:**
  - R3 changed on **364** postings, all fail → pass, with **0** pass → fail (`review/12-behaviour-change-after-revision.txt`).
  - No posting naming a US state in full still fails (`review/13-reproduce-after-revision.txt`).
- **Commands I ran myself**, in my own PowerShell on 2026-11-09:
  - `git diff agent/rule.py`, read on screen;
  - the full test suite, 86 tests OK (`review/07-yudan-ran-tests.txt`);
  - the behaviour comparison (`review/08-yudan-ran-compare.txt`: "R3 changed on 364; final verdict changed on 0").
- **Accepted** in commit `59e9c5c`, with a dated revision in `CONTRACT.md`.

## 7. A case my tests would still miss

A city of the country Georgia that is not in the four-city list, such as `Gori, Georgia`, is read as the US state and passes R3. My tests check `Tbilisi, Georgia` only. Other misses of the same kind: a US location written with neither a state nor a country (`Remote`, a city alone like `Seattle`), which still fails as it did in JS1.
