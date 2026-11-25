# Sign-off

## 1. What I checked and how

- **Labels before code:**
  - I hand-labeled 90 postings (`dev`: 6 keep / 39 reject; `heldout`: 5 keep / 40 reject) by reading each posting in full.
  - The completed label sheets were committed alone (`215f29a`) before `agent/filter.py` existed (`342075a`).
  - Claude cross-checked the experience requirements cited in my reasons against the raw text: all 29 `dev` year counts matched, and one held-out guess (`affirm:8032173003`) contradicted its posting, which I corrected before committing.
- **Spec before code:**
  - `FILTER.md` v1.0 was committed alone (`0041401`) prior to any filter implementation.
  - Two Day 1 survey claims in `v1.0` turned out to be false: `"SWE II asks 5+ years"` (it asks for `1.5+` years) and `"91 postings share a title"` (`173` postings share a board and title across `82` groups; `91` is the number of extra copies).
  - Both were corrected as documentation-only versions (`v1.1` and `v1.3`), leaving `v1.0` untouched as written.
- **Tests before code, three times:**
  - The filter tests (`3beb6f0`), shortlist tests (`f89aef7`), and MCP server tests (`8458710`) were each committed alone and verified failing before implementation.
  - All 57 tests now pass (`python3 -m unittest discover -s tests -t .`).
  - `python3 -m tests.wrong_versions` patches each wrong version (`W1`–`W5`) into the filter in memory and confirms each one causes its corresponding test class to fail.
- **Reject audit by hand:** For the `v1.0` filter run, I judged 53 postings myself:
  - `30` random rejects: `0` should have been kept (`95%` Wilson interval `0–11.4%`, a sample estimate for this run's `378` rejects);
  - all `22` kept postings: `11` genuine fits;
  - `9` close calls (`0.40–0.60`, adding 1 extra rejected posting beyond the 22 kept).
- **Single rule change measured on `dev`, then once on `heldout`:**
  - `dev`: false positives dropped from `6` to `0`.
  - `heldout`, evaluated once (`bdf8998`): false positives dropped from `5` to `4`.
  - Recall remained unchanged on both splits (`6/6` on `dev`, `5/5` on `heldout`; `score/report.md`).
- **The MCP server, verified by running it:**
  - `15` passing tests (12 initial + 3 added for schema validation in `e273c8e`);
  - a scripted raw-protocol transcript (`evidence/mcp/scripted-transcript.jsonl`);
  - one live Claude Code session (`Nov 24, 06:03 UTC`, `3ee665a`) alongside the server's own JSONL call log;
  - an adversarial probe that caught the missing runtime schema validation, fixed tests-first in `e273c8e`.

## 2. What I did not check

1. **Postings outside three boards on one day:** Only `robinhood`, `affirm`, and `wealthfront` collected on Nov 23, 2026 were tested; nothing here measures how the filter performs on other companies or later dates.
2. **Whether the `heldout` result generalizes:** `heldout` contains only 5 true keeps, the rule change shifted 1 posting, and `heldout` was not strictly untouched because some of its rows appeared in `audit/filter-v1.0/kept.csv` before `v1.2` was chosen (`score/report.md`).
3. **Every `"I cannot tell"` branch on live postings:** None of the 400 collected postings had empty body text, an empty location, or an unrecognized location, so those paths are verified only on unit-test fixtures.
4. **Experience requirements strictly between 2 and 3 years (such as `"2.5+ years"`):** No posting in this collection asks for a fractional requirement between 2 and 3 years, so the `N ≥ 3` boundary in `v1.2` is untested on real data in that gap.
5. **The official Filesystem MCP server at runtime:** Evaluated statically from its GitHub README and source code (`v2.4.0`) without downloading or executing it locally.
6. **Site terms of service:** Reused the public, read-only board endpoints from JS2 without reviewing each company's terms of use.

## 3. What I am not claiming

- The `50%` kept precision (`11/22`) is a count for this single 400-posting run, and the `0/30` reject result is a sample estimate (`0–11.4%`) for this run's rejects; neither is a general rate across job boards.
- The shortlist's claim classifications are not an independently validated classifier; its `"track record"` / `"proven ability"` contradiction cue was written after reading those postings in the audit.
- The scoring weights (`0.50`, `0.30`, `−0.40`, `0.20`, `0.10`) were hand-authored rather than tuned by optimization, and only one rule (`R2` at `N ≥ 3`) was modified once.

## 4. Driver's seat: why the system stays mine

| Part | What Claude did | What I did | Decision I made, and its evidence | Why it stays mine |
| :--- | :--- | :--- | :--- | :--- |
| **What counts as a good posting** | Built the stratified sampler and reading aids; checked cited years against posting text | Hand-labeled 90 postings and judged 53 audit postings by reading them in full | Kept `SWE II` roles asking `1.5+` years; rejected `3`-year roles, mobile-only roles, and mid-level `2+`-year roles (`labels/`, `audit/`) | Deciding whether a role fits Sam is a human hiring judgment, not something keyword counts settle |
| **The rules** | Drafted `FILTER.md` and `agent/filter.py`; proposed the `N ≥ 3` penalty | Approved `v1.0` untouched; approved `v1.2`; required `v1.0` to stay unedited | `v1.2` (`6dc9c6a`), chosen from `dev` and the audit before running `heldout` | Any rule change shifts which jobs Sam sees; I own that precision-recall trade-off |
| **Held-out evaluation** | Ran `agent/evaluate.py` once when instructed | Decided when `heldout` was ready to spend | Evaluated `v1.0` vs. `v1.2` once immediately after locking `v1.2` (`bdf8998`) | Spending the held-out split is an irreversible experimental choice |
| **The MCP server's reach** | Built a read-only stdio server; registered it locally when approved | Approved registration and the runtime schema-validation fix | Zero write tools; log writes confined strictly inside `out/` (`test_log_must_stay_in_folder`) | What an agent is allowed to read or touch is set by me, not by the server |
| **What is honest to claim** | Flagged the leaks (`heldout` seen in audit, post-hoc shortlist cues, client miscount, two false survey facts) | Reviewed every discrepancy, rewrote the write-ups (`README`, `FRICTIONAL`, `CASES`, `EVALUATIONS`, `report`, `PERSISTENCE`, `SOURCES`, this sign-off) in my own words, and kept uncorrected artifacts intact | Documented all caveats explicitly in `README.md` (`4d0c744`), `score/report.md`, and `shortlist/CASES.md` (`17f1a98`) | I am the one signing off on what this repository claims |

## 5. Sign-off

- **Status:** Signed
- **Operator:** Atharva C.
- **Date:** 2026-11-24
