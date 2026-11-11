# FRICTIONAL — Job-Search Agent 2

My log of what I tried, what happened, what I checked or changed, and what I accepted, changed or rejected from Claude. Claude Code drafted the factual lines from the session, the commits and the saved files. **The "What I learned" lines are mine.** I wrote them and gave them to Claude Code, which pasted them in word for word.

### 2026-11-10 — Who writes GATE.md?
- **What I tried:** I asked Claude Code to complete the whole assignment. When it asked who should write GATE.md, I asked what the assignment requires.
- **What happened:** Claude Code pointed to Step 1 ("Before Claude Code touches the code, write GATE.md"). It explained that the grading scores the content, and that Claude's help is allowed if SOURCES.md records it. It drafted GATE.md, and I replied "ok" to keep it as drafted. It was committed before any code (`040be50`, 14:45 local time).
- **What I checked, changed, or learned:**
  - **What I learned:** I learned that setting limits is not enough. I also need to explain why I chose those limits and what should happen when something goes wrong.
  - **Still unresolved:** Every number in GATE.md (5 boards, 8 requests, 120 s, 2 retries, 2 s and 4 s) is Claude's choice, not one I derived. Two findings (8b, 8c) show GATE.md itself has holes, and I have not written a decision about them.
- **From Claude, accepted / changed / rejected:** Accepted the draft unchanged.
- **Trace:** `040be50`; GATE.md header; SOURCES.md row "GATE.md".

### 2026-11-10 — A boundary test that passed for the wrong reason
- **What I tried:** Running the wrong-version tests, which swap in each plausible-but-wrong check and expect a boundary test to fail on it.
- **What happened:** W3 (not resolving `..`) was **not** caught. Boundary test B14 wrote to `jobs/../config/boards.json`, a file that exists, so the "written once" rule refused it before the `..` check mattered. B14 passed on the wrong version too.
- **What I checked, changed, or learned:**
  - Claude Code added a second case, to a file that does not exist (`jobs/../config/new.json`), and B14 now catches W3. Nothing in the test was removed.
  - **What I learned:** I learned that a test can pass without checking the problem I wanted it to check. I need to make sure the test actually catches the wrong version.
- **From Claude, accepted / changed / rejected:** Accepted the strengthened test.
- **Trace:** `322da65` (commit message); POLICY.md row B14; `tests/test_wrong_versions.py::test_w3_unresolved_dot_dot_is_caught`.

### 2026-11-10 — 80 new Anthropic ids, but not all of them new jobs
- **What I tried:** Starting the Anthropic board from JS1's state (675 ids from 2026-10-31), so the first JS2 run was a real watch over 10 days.
- **What happened:** Live run 1 reported 677 postings, 80 new and 78 gone. `check_run.py` recomputed the 80 from JS1's saved bytes and they matched. But 9 of the 80 have a `first_published` date before 2026-10-31, so they were not on JS1's board, yet they are not new postings either.
- **What I checked, changed, or learned:**
  - **What I learned:** I learned that comparing job IDs is not always enough to know which jobs are really new. I also need to check the saved responses and dates.
  - **Still unresolved:** Why those 9 were missing on 2026-10-31.
- **From Claude, accepted / changed / rejected:** Accepted the import and the run. Claude Code ran run 1.
- **Trace:** `762801a`, `af625cb`; `jobs/runs/2026-11-10T212848Z.md`.

### 2026-11-10 — The review packet: my test run, then my decision
- **What I tried:** Claude Code found that the real network code ignored its timeout on a slow body, and committed a test before any patch (`8ddfec0`). I ran it myself.
- **What happened:**
  - Before the patch: 1 FAIL, "still reading after 6 s with timeout=1.0".
  - After the patch (`91bfbda`) I ran the suite (96 OK) and `git diff`.
  - My first paste ended at `(END)`: the diff had opened in a pager, so my live run had not started yet. I pressed `q` and it ran.
  - I asked Claude Code what it thought. It recommended REVISE, because the patch silently falls back if Python's private `._sock` attribute is missing.
  - I decided REVISE in my own words, and the guard test was added (`764c262`).
- **What I checked, changed, or learned:**
  - **What I learned:** I learned that a fix can solve one problem but still have another weakness. That is why I asked for an extra test for the missing `_sock` attribute.
  - **Still unresolved:** Slow **headers** still held a 1-second request for 21 s. I have not written whether I accept the revised patch (REVIEW-PACKET.md section 6, last line).
- **From Claude, accepted / changed / rejected:** Accepted the defect and the test. Asked for a revision of the patch. My decision followed Claude's suggestion, which I asked for.
- **Trace:** `8ddfec0` → `91bfbda` → `764c262`; [review/2-before-patch-varnika-run.txt](review/2-before-patch-varnika-run.txt), [review/6-after-patch-varnika-run.txt](review/6-after-patch-varnika-run.txt); REVIEW-PACKET.md section 6.

### 2026-11-10 — My live run 2 exposed a bug in a fix
- **What I tried:** Live run 2, on the patched code, partly to test HTTPS, which the review test did not cover.
- **What happened:**
  - All three real boards were `ok` over HTTPS.
  - But Anthropic showed `gone 78`, while its response was byte-identical to run 1's, so the right number is 0.
  - Claude Code's earlier fix for review finding 7 fell back to "every id ever seen" when a state file had no `last_ids`.
  - `check_run.py` said SUPPORTED at first, because it did not check `gone`. After a `gone_recomputed` check was added, it said NOT SUPPORTED: "loop 78 gone, recomputed 0".
  - The record was not edited.
- **What I checked, changed, or learned:**
  - **What I learned:** I learned that the agent's result should not be trusted without checking it separately. The agent reported 78 jobs as gone, but the independent check showed that the correct number was 0.
  - **Still unresolved:** `check_run.py` checks only what it was written to check. It missed this until a check was added.
- **From Claude, accepted / changed / rejected:** Accepted the tests (`9a2179e`) and the fix (`c47736c`). Live run 3 showed `gone 0`.
- **Trace:** `3bd3518`, `9a2179e`, `c47736c`, `02e3655`; REVIEW-FINDINGS.md row 7b.

### 2026-11-10 — A second Claude reviewing the first Claude's code
- **What I tried:** I did not ask for this. Claude Code started a separate reviewer on its own initiative.
- **What happened:**
  - The reviewer reported 8 findings. Two were security-relevant: an environment proxy would have been used, with its credentials. Two were budget holes: a NaN budget switched the seconds limit off, and the check never used the seconds budget.
  - Each finding became a test that failed before it was fixed. 7 are fixed. 8b and 8c are left for me as GATE.md decisions.
- **What I checked, changed, or learned:**
  - **What I learned:** I learned that another review can find problems that the first review missed. But I still need to understand the findings and make the final decisions myself.
  - **Still unresolved:** 8b and 8c. And a reviewer that is also Claude may share the first Claude's blind spots.
- **From Claude, accepted / changed / rejected:** Accepted the fixes. Rejected nothing.
- **Trace:** `7e09390` → `9ab582c`; `3e48c6c` → `f51b6c8`; REVIEW-FINDINGS.md.

### 2026-11-10 — My two decisions at the end: the time budget and my username
- **What I tried:**
  - I wrote a time-budget decision for GATE.md: an invalid or unreliable time budget must stop the run, and the independent check must enforce the same time budget as the agent.
  - I also asked for my macOS username to be removed from the saved files.
- **What happened:**
  - Claude Code checked the code against my decision before changing it. A NaN budget flag was already refused, but **a clock giving NaN let a run end `finished` with no time limit**.
  - The checker allowed 5 s past the budget for each request, and it accepted a total time of NaN.
  - The tests failed first (`304b599`, 5 of 6), then were fixed (`71491b1`). My decision is under GATE.md Decisions, November 10, 2026.
  - For my username: the folder path was replaced with `<js2-folder>` in 8 files. The code was changed first, so future runs write relative paths (`4afa0b8` → `c10af62`, then `263953b`). Every check verdict stayed the same.
- **What I checked, changed, or learned:**
  - **Still unresolved:** The earlier commits still contain the unredacted files, because the git history was not rewritten, so that the commit ids cited in this folder stay valid.
  - The 5 s allowance for work after the last request is Claude Code's choice. I have not written a decision about it.
- **From Claude, accepted / changed / rejected:** Accepted the tests and changes.
- **Trace:** `304b599`, `71491b1`, `f5abb31`, `4afa0b8`, `c10af62`, `263953b`; GATE.md Decisions; SOURCES.md "Redaction".
