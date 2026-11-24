# SIGNOFF.md

> **DRAFT by Claude (Nov 24, 2026). Not signed.** Each line says what the record shows was checked. Before signing, I must re-check, cut or rewrite every line in my own words. Anything I did not personally do comes out.

## 1. What I checked and how

- **Labels before code.**
  - I hand-labeled 90 postings (dev 6 keep / 39 reject, held-out 5 / 40) by reading each one in full.
  - The labels were committed alone (`215f29a`), before `agent/filter.py` existed (`342075a`).
  - Claude checked the years I cited against the text: all 29 dev year counts matched, and one held-out guess was wrong, which I corrected before committing.
- **Spec before code.**
  - FILTER.md v1.0 was committed alone (`0041401`).
  - Two survey facts in it turned out false: "SWE II asks 5+ years" (it is 1.5+) and "91 postings share a title" (it is 173; 91 is the number of extra copies).
  - Both were corrected as documentation versions (v1.1, v1.3), with v1.0 left as written.
- **Tests before code, three times.**
  - The filter tests (`3beb6f0`), shortlist tests (`f89aef7`) and MCP tests (`8458710`) were each committed alone and seen failing.
  - Now 57 pass (`python3 -m unittest discover -s tests -t .`).
  - `python3 -m tests.wrong_versions` patches each wrong version W1–W5 into the filter, and each one makes its test fail.
- **Reject audit by hand.** For the v1.0 filter I judged 53 postings myself:
  - 30 random rejects: 0 should have been kept (95% Wilson interval 0–11.4%, a sample estimate for this run);
  - all 22 kept postings: 11 right;
  - 9 close calls.
- **The rule change was measured where it was chosen, then once on held-out.**
  - Dev: false positives 6 → 0.
  - Held-out, run once: 5 → 4.
  - Recall was unchanged on both (`score/report.md`).
- **The MCP server, by running it:**
  - 15 tests;
  - a scripted raw transcript;
  - one real Claude Code session (Nov 24, 06:03 UTC) with the server's own log;
  - a probe that found the schema bug, fixed with tests first (`e273c8e`).

## 2. What I did not check

1. **Postings outside three boards on one day.** That's robinhood, affirm and wealthfront on Nov 23, 2026. Nothing says how the filter does on other companies or other days.
2. **Whether the held-out result generalizes.** Held-out has 5 keeps, and the change moved 1 posting. It was also not fully untouched (`score/report.md`).
3. **Every "I cannot tell" path on real data.** No posting in this run has empty text, an empty location or an unknown location, so those paths are tested only on fixtures.
4. **Years between 2 and 3** (for example "2.5+ years"). No posting in this run asks for that, so the v1.2 boundary is untested on real data.
5. **The Filesystem MCP server at runtime.** I evaluated it from its source and README only.
6. **The sites' terms of use.** I used the public, read-only APIs from JS2, but I did not read each company's terms.

## 3. What I am not claiming

- **The 50% kept precision and the 0/30 rejects are results for this run,** not rates for job postings in general.
- **The shortlist's claim labels are not a validated classifier.** Their "track record" cue was chosen after reading the postings it flags.
- **The weights (0.50, 0.30, −0.40, 0.20, 0.10) are not tuned.** They are hand-set, and only one was changed, once.

## 4. Driver's seat: why the system stays mine

| Part | What Claude did | What I did | Decision I made, and its evidence | Why it stays mine |
|---|---|---|---|---|
| What counts as a good posting | Built the sample and the reading aids; checked cited years against the text | Labeled 90 and judged 53 postings by reading them | Kept SWE II roles asking 1.5+ years; rejected 3+ year and mobile-only roles, and mid-level 2+ year roles (`labels/`, `audit/`) | Whether a role fits Sam is a hiring judgment, not something the text decides |
| The rules | Drafted FILTER.md and the code; proposed the N ≥ 3 change | Approved v1.0 as written; approved running v1.2; required v1.0 to stay unedited | v1.2 (`6dc9c6a`), measured on dev before held-out | A rule change moves which jobs Sam sees; I own that trade |
| Held-out | Ran it when I asked, once | Decided when to spend it | Ran it right after v1.2, not before (`bdf8998`) | Using it up is a one-time choice |
| The MCP server's reach | Wrote a read-only server; registered it at local scope when I said yes | Approved registration; approved the schema fix | No write tool; the log stays inside `out/` (`test_log_must_stay_in_folder`) | What an agent may touch is set by me, not by the agent |
| What is honest to claim | Flagged the leaks (held-out seen in audit, cues chosen after the fact, the client's miscount, two false survey facts) | TODO: decide what goes in the README | TODO | I am the one signing |

## 5. Sign-off

- **Status:** NOT SIGNED (draft)
- **Operator:** TODO
- **Date:** TODO
