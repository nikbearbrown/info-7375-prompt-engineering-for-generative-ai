# Sign-off: Job-Search Agent 3

**Status: approved by Ashwin on 2026-11-25** (in chat). Ashwin supplied this wording; Codex helped draft it. The signature covers the limited checks described, not full rubric completion. The driver's-seat table below is still Claude Code's draft; Ashwin has **not** approved it.

```text
Sign-off — Job-Search Agent 3
Checked:      I ran the supplied test suite at b616bc09: 55 tests passed, exit 0, on Python 3.9.6.
              This verifies that the supplied tests passed, not that every requirement is complete.
How:          I ran Claude's tests myself. I did not independently author those tests.
              The saved output is drafting/checks-run-by-ashwin.txt.
Not checked:  - The required hand-judged posting audit remains 0/47.
              - None of the 90 claim labels is an independent human judgment.
              - The original 30-posting evaluation is potentially contaminated.
              - The level-II and forward-deployed exclusions were not independently audited.
              - Current job availability and Supriya's clearance or work-authorization eligibility
                were not verified.
Not claiming: Full rubric completion, validated filter accuracy, an uncontaminated improvement from
              v1.1, suitability of every KEEP, or model training. The Mission Manager change corrects
              a demonstrated keyword mismatch; it does not establish better overall accuracy.
Signed or withheld: Signed: Ashwin Thankachan, November 25, 2026.
                    This signs the limited checks described, not full rubric completion.
```

## Facts Ashwin can check, with the test or file for each

| Property | Test or evidence |
|---|---|
| FILTER.md came before the code | `git log --follow FILTER.md`: `a3a7a2af` contains no filter code |
| Each wrong version W1–W8 is caught | `python3 -m tests.test_wrong_versions`, `tests/test_claims.py::test_w7_negated_quote` |
| The tool refuses all 30 held-out keys and unknown keys | `tests/test_tool_and_audit.py`, `evaluations/own-server/client-probe-2026-11-25.jsonl` |
| The server has no network or process code, and no transcript outside the folder | `tests/test_mcp_server.py` |
| v1.1 changes one object, and only 2 development decisions | `tests/test_v11_mission_manager.py` |
| The audit selection is reproducible and excludes held-out keys | `tests/test_tool_and_audit.py::Audit` |
| Claude Code's later run: 56 tests pass on Python 3.9.6 and 3.12.15 at `4943de33` (the 56th, added in `bf491431`, checks the server disclosure). Ashwin did not run the 56th | `python3 -m unittest`, and the same with `/opt/homebrew/bin/python3.12` |
| Ashwin ran the 55 tests personally on 3.9.6 at `b616bc09`: OK, exit 0 | `drafting/checks-run-by-ashwin.txt` |

## Candidate "Not checked" items, from the record

- **The hand-judged reject audit: 0 of 47.** The verdicts are AI-assisted, inferred from the held-out labels.
- **Human claim labels: none.** All 90 are Codex AI-assisted; 29 of them were made from excerpts only.
- **Clean held-out performance.** The 30-posting set is potentially contaminated.
- **The level-II and forward-deployed exclusions.** FILTER.md section 10 promised an audit; their 7 postings were
  never judged.
- **The v0 (JS1 rule) comparison.** FILTER.md names it, but it was not re-run.
- **Whether any job is still open.** The snapshot is from 2026-11-09.
- **The choices in `drafting/IMPLEMENTATION-NOTES.md`** (I1–I9), including `Munich, DE` being read as Delaware.

## Driver's seat (Claude Code's draft; not approved by Ashwin)

| Task | Claude should | Ashwin should | Why |
|---|---|---|---|
| Collect and score postings | Run the filter, keep records, compute counts and intervals | Approve the rules first, and decide what to change | The rules encode Supriya's preferences, and only the person can own those |
| Write claims about a posting | Quote the posting, abstain when it is silent | Label each claim S / C / I | Matching words is not support; that call needs a reader |
| Judge whether a posting is worth Supriya's time | Show the evidence: duties, years, location, clearance | **Make the judgment** | Fit, eligibility and willingness are the job seeker's facts and decisions, not the posting's |
| Run and evaluate tools | Probe them, record transcripts, compare declared and actual | Decide what to trust and with what access | Trust is an authorization, and only the person can grant it |
| Report results | Draft, recompute, and flag contamination | Sign or withhold | The signature says the person checked it |
