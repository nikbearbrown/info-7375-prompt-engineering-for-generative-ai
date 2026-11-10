# Review packet — Ashby board names with capitals and spaces

Arundhati K · 2026-11-10 · the change I asked Claude Code to make, reviewed on evidence.

Sections 1–4 are facts and Claude Code's reading, labelled as such. **Sections 5–7 are mine.**

## 1. The defect, reproduced first (commit `772af22`, before any patch)

The board-name rule I carried over from JS1 (`^[a-z0-9-]{1,64}$`) rejects real Ashby board names that
contain capitals or spaces. Lectern's `ATS.md` documents one: `Jasper AI`.

Live check (Claude Code ran it, 2026-11-10 ~16:37 EST, curl, public GET, nothing saved):

| URL | HTTP | postings |
|---|---|---|
| `https://api.ashbyhq.com/posting-api/job-board/Jasper%20AI` | 200 | 7 |
| `https://api.ashbyhq.com/posting-api/job-board/jasper-ai` | 404 | — |
| `https://api.ashbyhq.com/posting-api/job-board/jasperai` | 404 | — |

So there is no lowercase spelling that works around it. And because names are checked in the config step,
one such board makes the **whole run** exit `error` with 0 requests sent: the other boards go unwatched.

`review/reproduce_defect.py` shows it offline (log: `review/01-before-patch.txt`):

```text
url_for('ashby', 'Jasper AI') -> ValueError: board name must match ^[a-z0-9-]{1,64}$: 'Jasper AI'
run with Stripe + Notion + Jasper AI -> exit='error' ... requests sent=0
DEFECT PRESENT
```

## 2. The test, written before the patch (commit `772af22`)

`tests/test_providers.py`, 5 tests. Before the patch: 2 errors (`test_name_with_space_and_capitals_is_encoded`,
`test_encoded_url_still_passes_policy`), 3 pass. The 3 passing ones guard what the fix must *not* break:
a loosened rule must still refuse `../x`, `a/b`, `..`, `a?b=1`, `a#b`, `a%2Fb`, `a\b`, empty, 65 characters,
and a newline; Greenhouse names stay strict.

## 3. The diff (`review/patch.diff`), read as a change in behaviour (Claude Code's reading)

| input | before | after |
|---|---|---|
| Ashby `Jasper AI` | refused → whole run `error` | `…/job-board/Jasper%20AI`, fetched |
| Ashby `notion` | `…/notion` | same |
| Ashby `../x`, `a/b`, `a%2Fb`, `.` | refused | still refused (must start with letter/digit; no `/ ? # % \`) |
| Ashby `a..` or `a ` (trailing space) | refused | **now accepted** (one path segment, encoded `a..`, `a%20`) |
| Greenhouse `stripe` | `…/boards/stripe/jobs` | same |
| Greenhouse `stripe` + newline | **accepted**, URL `…/boards/stripe\n/jobs` (`$` matches before a final newline) | refused (`fullmatch`) |
| non-string name | `TypeError` | `ValueError` → exit `error: bad config` |

## 4. Scope (facts for my decision)

- Files changed: only `jsagent2/providers.py` (+14 −6). No test was edited to pass.
- Asked for: accept Ashby names with capitals/spaces, safely. Also changed: the Greenhouse check now uses
  `fullmatch`, so a trailing newline is refused. That is stricter, but **it is not Ashby**, and
  `test_greenhouse_rule_unchanged` says "unchanged", which is not exactly true.
- Not changed (still GATE §1): a bad board name still makes the whole run `error`.
- `BOARD_SLUG` changed from one regex to a dict. Nothing else imports it (`grep -rn BOARD_SLUG`).
- The same newline bug is still in my JS1 code (`../js1-contract-and-watch/jsagent/fetch.py`), untouched.

## 5. Commands I ran myself

2026-11-10, ~16:40–16:43 EST, in my own macOS terminal, with the patch applied but not committed.
Full output, unchanged: [review/02-my-commands.txt](02-my-commands.txt).

| command | what it showed |
|---|---|
| `python3 review/reproduce_defect.py` | `Jasper%20AI` URL; run with Stripe + Notion + Jasper AI → `exit='finished'`, 3 requests; `DEFECT FIXED` |
| `python3 -m unittest discover -s tests -t . -v` | `Ran 43 tests … OK`, including the 5 in `tests/test_providers.py` |
| `git diff -- jsagent2/providers.py` | the diff (cut off by the pager; full diff in `review/patch.diff`) |
| `python3 run.py --approve-state-write` | live run with the patch: exit `incomplete`, 775 / 143 / 155, 404 handled, state written (`evidence/run-live-2-approved/`) |

Not run by me: the live `Jasper AI` fetch through the agent's own transport (4th command offered). The only
live check of `Jasper AI` is Claude Code's curl in section 1.

## 6. My decision: accept / revise / reject

**Decision: accept** (my reply in the Claude Code session, 2026-11-10 ~16:45 EST: "accept").

Evidence it rests on: the reproduction flips from `DEFECT PRESENT` (`01-before-patch.txt`, before the patch)
to `DEFECT FIXED` (`02-my-commands.txt`, my run); the 2 failing tests pass and the 3 guard tests (path
escape, Greenhouse) still pass; 38 earlier tests unchanged and green; my live run with the patch behaves
the same on the real boards.

Accepted as is, including what section 4 lists: the Greenhouse `fullmatch` tightening (outside the Ashby
scope) and the test name `test_greenhouse_rule_unchanged`, which is no longer exactly true.

Because (my words):

## 7. One case my test would still miss

<!-- A real case that tests/test_providers.py does not cover and the patch could get wrong. -->
