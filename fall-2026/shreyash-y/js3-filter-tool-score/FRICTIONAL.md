# FRICTIONAL — Job-Search Agent 3

There are two parts, kept apart on purpose. **Part 1 is Shreyash's.** Part 2 is the log Claude Code
kept while building and running, where "I" means Claude Code.

## Part 1 — Shreyash

### What Shreyash did, from the session record

*Listed by Claude Code from the session and the commits. These are things Shreyash said or did; nothing
here says what he thought.*

- **2026-11-25, 16:58 and 17:05.** Wrote FILTER.md v1: 13 answers, then a reason for each rule and the
  decisions A–C, where three of his answers pulled against each other. Committed alone, before any code
  (`5e6a7703`, `3163fdb5`).
- **17:53–18:04.** Labeled 70 postings in the chat, with a reason for each.
  - Asked for the full ad three times (11, 20 and, earlier, the requirements of 8).
  - Changed 6 answers:
    - 8, 11 and 20 after seeing more of the ad;
    - 31 after Claude Code asked him to judge it as if it were open;
    - 39 and 49 after the double-check he asked for, in which Claude Code described how the rules read
      them.

    His first answers for 39 and 49 never reached the frozen file; `labels/hand-verdicts-provenance.md`
    records them.
- **About 18:07.** Decided the v1.1 changes from their measurements: adopted 4 and rejected 2
  (`61e0d4c0`). In the same message he labeled the three disputed claims and wrote both trust decisions;
  those first appear in `0e31a4c3` (18:16).
- **18:21.** Signed the sign-off in the session, without changing it ("sign shreyash yadav 26th november 2026"); at 18:28 corrected the date ("sorry its 25th november").
- **About 18:49–18:52.** After the independent reviews:
  - wrote the How sentences for the sign-off and longer trust decisions;
  - chose "I labeled the 70 postings myself" over his first draft ("I reviewed the suggested labels");
  - signed the updated sign-off.
- **By 18:28, and at 18:30.** Ran the full test suite and the hand-verdict hash check himself. The first command, which Claude Code gave him, hid the test result line, and the corrected one showed 218 tests OK (`evidence/commands-run-by-shreyash-2026-11-25.txt`).

### In my own words

*Shreyash's words, typed into the session on 2026-11-25. Claude Code changed formatting only.*

*These entries were written at the end of the work: pasted at about 18:07 EST, first committed in
`b89adefd` (18:19). The evidence line after each one is Claude Code's.*

**2026-11-25 — Checking job labels**

I expected the filter to work well because I had already defined the rules in JS2. During the labeling process, posting 8 was shown with an incomplete requirements section because the tool missed a curly apostrophe. After seeing the full description, the answer changed from yes to no because the job required 7+ years of experience. This showed me how missing information can change a decision.

*Evidence: `labels/hand-verdicts-provenance.md` (item 8); `tests/test_js3_sections_apostrophe.py`; commits `85e78b65` and `97517e88`.*

**2026-11-25 — Reviewing filter mistakes**

The audit showed three interesting cases: Recommendations, Android and Product Engineer. I would accept adding Product Engineer and counting MySQL and PostgreSQL as SQL. I would reject reducing the minimum skills to one and removing all skills from technology lists because those changes could create other mistakes.

*Evidence: AUDIT.md section 5; FILTER.md "Version 1.1" (`61e0d4c0`); `results/whatif-v1.json`; `tests/test_js3_filter_v11.py`.*

**2026-11-25 — Checking evidence and tool access**

I compared the results from the code and Claude. I would disagree with Claude on the technical leader wording because being a technical leader does not automatically make someone a Lead Engineer. I would also limit the use of chrome-devtools-mcp because it accessed more information than the agent needed. One thing that is still unclear is how to tell whether a skill is central to the job or just mentioned in the posting without missing suitable jobs.

*Evidence: SHORTLIST.md section 4; TOOLSERVER.md section 3; `transcripts/other-server/`.*

## Part 2 — Claude Code's log

*Written by Claude Code from the session, the commits and the saved outputs. "I" is Claude Code. All
times are EST on 2026-11-25.*

- **16:50 — Reading before building.**
  - **Tried:** I read the brief, JS1's contract, and JS2's gate, rule and runs.
  - **What happened:** the course repository's copy of the brief says JS3 was due **2026-11-23**. I
    told Shreyash to check Canvas for the late window.
  - **What I did:** I stopped before writing any code, because the brief grades FILTER.md as written
    before the build, and the JS1 TA asked that the reasoning be visibly Shreyash's.
- **16:58–17:05 — FILTER.md.**
  - **What happened:** Shreyash's answers left six rules without a reason, and three of them pulled
    against each other:
    - answer 6a ("I cannot tell") against JS2's "reject hybrid jobs with a Remote tag";
    - answer 8 ("not mentioned passes") against the evidence rule;
    - internships out "because Alex is looking for full-time jobs", which leaves part-time open.
  - **What I did:** I asked once, in a fill-in form. His answers A–C settled all three.
- **17:06 — Live run.**
  - **What happened:** the JS2 loop ran as JS2 left it: 637 postings, the 404 board failed by design,
    and whoop came back empty. Because this folder's `runs/` was new, the run was a baseline and
    reported "0 new" everywhere.
  - **What I did:** I computed "new since JS2" myself from the corpus instead: 98 new, 152 closed.
- **17:14–17:20 — The filter, tests first.** The tests failed on import, then the code passed all 57
  on its first run.
  - **Surprise:** filter v1 gives the **same verdict as JS2's rule on all 789 postings**.
    Shreyash's new answers (Palantir `Dev`, internships, "I cannot tell") changed the *reasons* on
    hundreds of postings, but not one verdict, because location and title reject them anyway. I had
    expected at least the `Dev` decision to move something.
- **17:20 — False friends, measured.** I looked for them before any label existed.
  - "react quickly" counted as React in 2 Palantir ads.
  - "remote position… reside in: Dallas, TX" was read as the tag and the ad disagreeing ("cannot tell")
    in 36 ads, 35 Oscar and 1 Palantir. I first described all 36 as Oscar "Dallas, Texas"; the cities
    and states vary.
  - The kept Android job's skills appear only in "open to picking up new technologies (Python, React,
    AWS)" and a tech list.
- **17:23–17:26 — The tool server.**
  - **Not test-first:** I wrote the MCP server before its tests. The tests came after (15), so they
    check the code I wrote rather than a contract I wrote first.
  - **What the real client did that I did not expect:** Claude Code probed `server/discover` with
    protocol `2026-07-28`, then asked for `2025-11-25`. My server answered "Method not found", then
    offered `2025-06-18`, and the client accepted. The transcript shows it, and a test now pins the
    downgrade.
- **17:26 — chrome-devtools-mcp.** A helper read its source (no code run) and found usage statistics
  and update checks on by default. I turned both off for the one page load. Even so, the page contacted
  at least 51 hosts and showed the "Submit application" form. That made the trust question concrete.
  (I first wrote "51 hosts". The independent review found I had counted only the first 200 of 231
  requests, and that I had said "9" read-only tools where the server declares 8.)
- **17:27–17:39 — Claude conditions, before any label.**
  - **Pre-registration:** all six conditions were committed before running (`a9e5d445`). The seventh,
    B3, was committed before it ran and before any label (`186d6af6`).
  - **Results:**
    - No condition moved a verdict.
    - With FILTER.md in context, Claude applied Shreyash's `Dev` decision: all 9 held-out Palantir
      `Dev` postings stopped failing the department rule, and 12 postings changed their reasons in all.
    - Offered the tool, it never called it.
  - **What I fixed:** my "made-up quote" check flagged 6 quotes.
    - 5 were punctuation: a comma inside the closing quote, curly quotes turned straight.
    - 1 was my extractor misreading the text between two quotes.
    - I added a normalized check and classified all 6 by hand.
- **17:31 — My mistake: missing context.** My first independent-labeling prompt to Claude left out
  Alex's profile. Claude said a claim about "Alex's skills" could not be checked, which was right. I
  kept that run as evidence and reran it with the profile.
- **17:40 — My mistake: an estimated time.**
  - **What happened:** I wrote B3's time as "17:50" from an estimate. The records say 17:38. CP09's end
    time had the same problem.
  - **What I did:** I corrected the comment and the documents, and amended three commit messages before
    anything was pushed:
    - CP09: its call times;
    - CP11: B3's time;
    - CP15: the label time range.

    Amending changed only those three commits' hashes. No pushed history was rewritten.
  - **What I take from it:** read times from the records, never from memory.
- **17:53–18:04 — Labeling, in the chat.** Shreyash answered posting 1 in the chat instead of the
  terminal tool, so I switched to chat batches. That introduced three problems of mine:
  - **The excerpt was cut.** My first batch cut each requirements section at 380 characters.
  - **The apostrophe bug.** Posting 8's requirements heading, "What We’re Looking For:", has a curly
    apostrophe my section reader did not know, so the excerpt showed only its "Nice to have" part.
    Shreyash's note ("No experience requirement is shown") gave it away.
    - I wrote a failing test, then the fix (`85e78b65`, `97517e88`).
    - The fix changed no filter result.
    - He changed his answer after seeing the full section.
  - **A missing instruction.** The chat batches left out "judge it as if it were open", and his only
    reason for posting 31 was "The job is closed". I asked him to judge it as if open.
  - **A non-blind answer.** To answer his own double-check question, I told him how Rule 4 reads
    posting 31. That answer is marked `not_blind` in the file.
- **18:09–18:12 — v1.1, and my wrong number.**
  - **What happened:** I had written "36 location results go from cannot tell to fail" for A4, before
    running it. Run, it changed 12.
  - **Why:** of the other 24, 21 write the state as a code ("Dallas, TX"), 2 write "reside:" without
    "in", and 1 (Palantir) is not a residence line. I first wrote "24 … and 2", which sums to 38. The
    review caught that too.
  - **What I did:** two test-first fixes brought it to 35 of 36, and FILTER.md carries a dated
    correction. Shreyash's decision did not depend on the number, since 0 verdicts change either way,
    but the number was in front of him when he decided.
- **18:33–18:57 — Two independent reviews, and what I fixed.**
  - **The reviews:** a grader (estimated 82/100) and a number check, both Claude Code helpers. They
    read the files and reran every script on a copy; all 14 result files regenerated byte for byte.
  - **What they found, all checked and fixed:**
    - The first answers for 39 and 49 never reached the record (`labels/hand-verdicts-provenance.md`).
    - The held-out set was spent by rejecting A3, so v1.1's 24 of 24 is not an untouched result.
    - My server crashed on a non-object `params`, and its folder check let `transcripts-evil/` through:
      the same bug class as JS2's `runs-evil`. I fixed both test-first (`85187c4b`, `bd093fef`).
    - "No plugin or memory" overstated what the transcripts show.
    - FILTER-NOTES' timing line was wrong.
    - Several counts and descriptions were wrong: 9 read-only tools instead of 8, "51" stated as a
      total, "36 … Dallas, Texas", must-haves "six" instead of seven, and P's cost.
  - **What I take from it:** I stated some numbers before running them (36, 9, 51) and described
    records more broadly than they are. A reader who recomputes from the files caught what my own
    re-reading did not.
- **Still unresolved:**
  - The held-out set is too easy to separate most changes: everything scores 24 of 24 except A3.
  - Only one person labeled.
  - The tool server still scores with v1.
  - The Android job is a known false positive, and I don't know a rule that removes it without also
    losing jobs Shreyash wants.
  - That last point is the same question Shreyash left open: how to tell a central skill from a
    mentioned one.
