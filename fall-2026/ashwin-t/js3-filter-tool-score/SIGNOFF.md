# Sign-off: Job-Search Agent 3

**Status: approved by Ashwin on 2026-11-25** (in chat). Ashwin supplied this wording; Codex helped draft it. The signature covers the limited checks described, not full rubric completion. The driver's-seat table below was drafted by Claude Code and approved by Ashwin on 2026-11-25 with the recorded changes.

```text
Sign-off — Job-Search Agent 3
Checked:      I ran the supplied test suite at b616bc09: 55 tests passed, exit 0, on Python 3.9.6.
              This verifies that the supplied tests passed, not that every requirement is complete.
How:          I ran Claude's tests myself. I did not independently author those tests.
              The saved output is drafting/checks-run-by-ashwin.txt.
Not checked:  - An independent blind posting audit was not performed; the later 47 personal reviews followed AI suggestions and disclosed results.
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

## Addendum, 2026-11-25 (evening)

Drafted by Claude Code and approved by Ashwin in chat on 2026-11-25. Ashwin's signature above stays on the
original wording; this addendum adds later checks and gaps.

```text
Checked (with Claude's help):
              Claude Code ran the full suite, now 87 tests, on Python 3.9.6 and 3.12.15; I did not rerun it.
              tests/test_recompute_v10.py (15 tests, written by a Claude subagent without importing
              jobfilter/filter.py) re-derives every v1.0 title gate, topic group, score and decision from
              FILTER.md and filters/v1.0.json. It agrees on all 775 development postings. FILTER.md section 4
              also requires an eligible location: 4 postings reach 7 only with non-US locations and are
              correctly REJECT.
Checked by hand (added after the hand check, later that evening):
              I labeled a blind sample of 15 claims (10 of 15 agree with Codex), and applied the written
              rule to two postings: both decisions match the code; my scores (7 and 5) are one below the
              code's (8 and 6), recorded as given (audit/BLIND-EXTRA.md).
Not checked:  - The other 75 claims have only Codex labels.
              - My 20 blind verdicts came from a 4-option form; 6 were corrected after review.
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

- **Blind audit independence.** Ashwin subsequently confirmed personal review of all 47 required sample rows after exposure to AI suggestions and results.
- **Human claim labels: none.** All 90 are Codex AI-assisted; 29 of them were made from excerpts only.
- **Clean held-out performance.** The 30-posting set is potentially contaminated.
- **The level-II and forward-deployed exclusions.** FILTER.md section 10 promised an audit; their 7 postings were
  never judged.
- **The v0 (JS1 rule) comparison.** FILTER.md names it, but it was not re-run.
- **Whether any job is still open.** The snapshot is from 2026-11-09.
- **The choices in `drafting/IMPLEMENTATION-NOTES.md`** (I1–I9). Ashwin reviewed them after signing, retrospectively. Two disagreements remain unresolved defects: I5 (structured remote fields are not scored) and I7 (`Munich, DE` is read as Delaware). I8 is accepted only as a limitation.

## Driver's seat: intended division of responsibility

Claude Code drafted this table. Ashwin approved it on 2026-11-25 with two changes: this label, and the wording of the
last row.

**What actually happened:** the claim labels were AI-assisted (Codex). The audit verdicts began as Codex suggestions; Ashwin subsequently confirmed personal review of all 47 required sample postings, retaining their verdicts. The review was not blind. The table describes the intended split, not what was done in this assignment.

| Task | Claude should | Ashwin should | Why |
|---|---|---|---|
| Collect and score postings | Run the filter, keep records, compute counts and intervals | Approve the rules first, and decide what to change | The rules encode Supriya's preferences, and only the person can own those |
| Write claims about a posting | Quote the posting, abstain when it is silent | Label each claim S / C / I | Matching words is not support; that call needs a reader |
| Judge whether a posting is worth Supriya's time | Show the evidence: duties, years, location, clearance | **Make the judgment** | Fit, eligibility and willingness are the job seeker's facts and decisions, not the posting's |
| Run and evaluate tools | Probe them, record transcripts, compare declared and actual | Decide what to trust and with what access | Trust is an authorization, and only the person can grant it |
| Report results | Draft, recompute, and flag contamination | Sign or withhold | The signature identifies exactly what the person checked and what remains unverified |

## Post-signature review confirmation (2026-11-25)

Ashwin explicitly confirmed the 30 random-reject verdicts and then all 17 closest-call/kept verdicts in chat.
The hand sheet records those personal judgments with prior AI exposure and review timing. The earlier signature
continues to cover its stated test run; these later confirmations do not claim a new personal test run.
