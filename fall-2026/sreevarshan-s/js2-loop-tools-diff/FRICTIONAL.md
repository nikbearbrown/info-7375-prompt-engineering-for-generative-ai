# Frictional — Sreevarshan Sathiyamurthy, 2026-11-06

Things that went wrong or were harder than expected, as they happened.

1. **The wrong-answer demo wrote three files directly into output/ during development.** Claude Code saw them as untracked files after a commit, assumed its tests had leaked them, and moved the whole output/ folder aside without checking first. The folder also held my live-run evidence. Claude Code restored it and confirmed that the four committed live-run files (commit 13e4b94) were unchanged (Claude Code's note in its reply, 2026-11-06). The three files came from a manual demo run, not the tests; I later committed them as evidence (commit 9e02c5a).

2. **The review-packet test needed three fixes before it would run:** `self.output` instead of `self.output_dir`, the full `BoardFetchError` arguments (`board, status_code, retriable, kind, message`), and `write_trace=False`. As first written it stopped with an AttributeError instead of failing on the defect. After the fixes it failed for the intended reason (`2 != 1`). The test was still written and committed before the patch (8624b8f before 31149a6).

3. **The timeout review-packet candidate was rejected.** Claude Code found that the timeout already existed: `REQUEST_TIMEOUT = 15` is passed to every `urlopen` call, and the loop caps each request at the time left in the 90-second run budget. A "failing" test for a missing timeout would have passed, so I picked a different defect.

4. **The repeat-rule gap I described cannot actually happen.** REVIEW_PACKET.md describes a missed case: a retriable failure whose retry is skipped by the budget, then a third appearance of the same board. In the current loop a retry is skipped only when the request or time limit is reached, and the same limits are checked before the next board, so the run stops as budget-exhausted first. Claude Code caught this after the document was committed.

5. **BOUNDARY_TESTS.md was committed twice** because `git commit --allow-empty` ran before the append. Commit 26fb887 changes no files; the results are in 59142a6.
