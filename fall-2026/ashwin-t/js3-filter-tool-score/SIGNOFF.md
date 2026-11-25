# Sign-off: Job-Search Agent 3

**This sign-off is Ashwin's to write.** Claude Code has listed facts Ashwin can check, and candidate "Not checked"
items drawn from the record. Ashwin decides which to keep, adds their own, and signs or withholds.

```text
Sign-off — Job-Search Agent 3
Checked:      (Ashwin)
How:          (Ashwin)
Not checked:  (Ashwin, at least three real items)
Not claiming: (Ashwin)
Signed or withheld: ____________ (name, date)
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
| 55 tests pass on Python 3.9.6 and 3.12.15 | `python3 -m unittest`, and the same with `/opt/homebrew/bin/python3.12` |

## Candidate "Not checked" items, from the record

- **The hand-judged reject audit: 0 of 47.** The verdicts are AI-assisted, inferred from the held-out labels.
- **Human claim labels: none.** All 90 are Codex AI-assisted; 29 of them were made from excerpts only.
- **Clean held-out performance.** The 30-posting set is potentially contaminated.
- **The level-II and forward-deployed exclusions.** FILTER.md section 10 promised an audit; their 7 postings were
  never judged.
- **The v0 (JS1 rule) comparison.** FILTER.md names it, but it was not re-run.
- **Whether any job is still open.** The snapshot is from 2026-11-09.
- **The choices in `drafting/IMPLEMENTATION-NOTES.md`** (I1–I9), including `Munich, DE` being read as Delaware.

## Driver's seat (draft for Ashwin to edit)

| Task | Claude should | Ashwin should | Why |
|---|---|---|---|
| Collect and score postings | Run the filter, keep records, compute counts and intervals | Approve the rules first, and decide what to change | The rules encode Supriya's preferences, and only the person can own those |
| Write claims about a posting | Quote the posting, abstain when it is silent | Label each claim S / C / I | Matching words is not support; that call needs a reader |
| Judge whether a posting is worth Supriya's time | Show the evidence: duties, years, location, clearance | **Make the judgment** | Fit, eligibility and willingness are the job seeker's facts and decisions, not the posting's |
| Run and evaluate tools | Probe them, record transcripts, compare declared and actual | Decide what to trust and with what access | Trust is an authorization, and only the person can grant it |
| Report results | Draft, recompute, and flag contamination | Sign or withhold | The signature says the person checked it |
