# Claude Code's response, Nov 9, 2026

Claude Code (Opus 5.5) changed one file, `agent/skills.py` (+27 / −1 lines). The diff is in `02-patch-20261109.diff`. This is Claude's own account of the change, saved as it was given; the review of it is in REVIEW_PACKET.md.

## What Claude said it changed
- Added `AMBIGUOUS_SKILLS`: for skills whose names are also English words (React, Go), the any-case whole-word match is replaced by:
  - React: `React` capitalized, or `reactjs` / `react.js` in any case.
  - Go: `Go` capitalized and not followed by a hyphen, or `golang` in any case.
- Added `_found()`, which uses those patterns for React/Go and the old `_word()` match for every other skill.
- `match_skills()` now calls `_found()` instead of `_word()` directly.

## What Claude said it did not change
- `tests/test_skills.py` and every other test file.
- Matching for all other skills (Python, Java, SQL, TypeScript…) goes through the same `_word()` as before.

## What Claude ran
- `python3 -m unittest tests.test_skills`: 6 tests, OK (previously 7 failures).
- `python3 -m unittest discover -s tests -t .`: 35 tests, OK.
- `python3 -m agent.reproduce_skills evidence/run-20261109-041358Z/raw/03-wealthfront-a1.json`: the Director of PM and Product Designer postings no longer match; Network, DevOps and Frontend still do.

## What Claude flagged for the reviewer
1. The module docstring at the top of `skills.py` still says the defect is "carried over on purpose". The patch did not update it, so it is now stale.
2. Known misses the patch does not handle: "Go build something…" (capital Go starting a sentence) still matches as accepted in the tests; "Go-based services" no longer matches because of the hyphen rule; "REACT" in all capitals no longer matches.
3. The prompt says "Golang" currently passes. It did not: "Golang" was one of the 7 failures in the red run. The patch adds it as new behavior.
