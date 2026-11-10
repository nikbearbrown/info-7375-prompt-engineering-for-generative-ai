# FRICTIONAL — Job-Search Agent 2

There are two parts, kept apart on purpose. **Part 1 is Shreyash's.** Part 2 is the log Claude Code kept while building and running, where "I" means Claude Code.

## Part 1 — Shreyash

### What I did, from the session record

*Listed by Claude Code from the session. These are things Shreyash said or did; nothing here says what Shreyash thought.*

- **2026-11-09.** Wrote GATE.md: the boards, the four exits, budgets of 6 boards, 12 requests and 120 s, the repeat rule, the error policy, the permission policy, five wrong versions, and the review-packet plan. Committed alone as `9fbab0d`.
- **2026-11-09.** Ran three commands on patch revision 1 and decided to revise it, although all 84 tests passed (`review/04`, `review/05`).
- **2026-11-09.** Ran three commands on revision 3 and accepted it with named limitations (`review/17`, `review/18`). Corrected the decision the same evening when it named the wrong posting.

### In my own words

*Shreyash's words, typed into the session on 2026-11-09 (a second version replacing the first). Claude Code did not change them.*

- **2026-11-09:**
  - **What I tried and expected:**
    I tried building a loop that checks six job boards and handles failures without giving incorrect results. I expected it to report the actual status of each board and not claim success when something was missing.
  - **What surprised me, or what I checked:**
    I was surprised that revision 1 passed all 84 tests but still had 16 cases where perks were treated as requirements. I also checked the finished-wrong demo and saw that the agent could report success even when it missed most of the postings.
  - **What I accepted, changed, or rejected from Claude:**
    I decided the boards, budgets, and error-handling rules for the loop. I sent revision 1 back for revision because the behavior was still wrong, and later accepted revision 3 with its known limitations documented.
  - **What I still don't understand, and my next step:**
    I'm still not fully sure how the rule should decide between a remote tag and the actual location requirements in a job description. My next step is to improve those checks and test whether the loop can detect incomplete responses from Ashby and Lever.

### Added 2026-11-10

*Three more entries in Shreyash's words, typed into the session on 2026-11-10 after reading the review files and the saved ads. Claude Code did not change them.*

#### 2026-11-10 — Reading the revisions

**Evidence:** `review/03`, `review/10`, `review/15`

**What I reviewed:**

I compared the findings from all three revisions to understand why the results were changing. In revision 1, the parser treated "based on country requirements" in the benefits section as a requirements heading. Because of this, 16 Linear postings incorrectly treated a paid-time-off benefit after four years as a job requirement.

Revision 2 fixed that issue, but the comparison showed around 37 dropped experience-requirement entries. The parser was treating later requirements as optional after encountering words like "preferred" in an earlier bullet. I also saw that some headings, such as "What We Require," were not handled correctly.

**My decision:**

I sent revision 1 back for revision even though all 84 tests passed. Revision 2 was also not sufficient because fixing one problem introduced or exposed other incorrect interpretations. I accepted revision 3 because it evaluated experience phrases within their own sentences, stopped quoting the perk, and passed the recorded checks without changing the overall job verdicts.

**What remains unresolved:**

The parser can still misinterpret conflicting location information. For example, an Oscar posting has a "Remote (Arizona)" office tag but allows applicants residing anywhere in the United States. The tests do not fully cover these conflicts.

#### 2026-11-10 — Correcting my review decision

**Evidence:** Commits `b7daf41` and `3a48610`, `review/18`

**Why my earlier decision needed correction:**

After my initial acceptance decision for revision 3, I corrected a mistake in the example I used to explain a remaining limitation. I had referred to the wrong posting when discussing the conflict between a remote-office tag and the actual location requirement.

The relevant example was Oscar's "Physician Reviewer – Utilization Management" posting. Its office tag says "Remote (Arizona)," while its description says applicants must reside in the United States.

**What I changed:**

I corrected the posting reference in my review decision while keeping the overall decision to accept revision 3. I also kept the location issue documented as an unresolved limitation instead of claiming that the rule handled every remote posting correctly.

**What I learned:**

Even when the overall decision is reasonable, the evidence used to support it must be accurate. A wrong example can make a review less trustworthy. This showed me why I need to check the actual posting details and not rely only on the summary generated by Claude.

#### 2026-11-10 — Interpreting run 3

**Evidence:** Run 3 trace, `TRACE.md`, and saved Palantir responses

**What I checked:**

Run 3 found six new postings: two from Oscar, one from Linear, and three from Palantir. All six were classified as Not Relevant.

The three Palantir postings were software engineering internships: two Connectivity Platform and Product postings in New York and Denver, and one Data Connectors posting in New York.

These were interesting because they failed only two conditions: department and location. The department returned by Lever was `Dev`, which was not included in my engineering-department allow-list.

**My decision on `Dev`:**

I think `Dev` should count as an engineering department for these Palantir postings because their titles and responsibilities clearly involve software engineering. However, I would not automatically treat `Dev` as engineering for every company without checking what that department label means.

Even with that interpretation, these three postings would remain Not Relevant under my current location rule because they are in New York or Denver rather than Boston or an accepted remote location.

**My remaining concern:**

Different Lever boards may use `Dev` differently. I still need to test whether a company-specific department mapping is safer than adding `Dev` to the general engineering allow-list. I am documenting this decision without claiming the implementation has been changed.

## Part 2 — Claude Code's process log ("I" = Claude Code)

**2026-11-09 19:19, the gate first.**
- I committed Shreyash's GATE.md alone. I had added a "Budget decisions" table, which is more than formatting, so I labeled it as mine and amended the still-local commit, so that the note "formatting only" stays true.
- I wrote GATE-NOTES.md for the two choices the gate leaves open:
  - an empty board makes the run `incomplete`;
  - every run writes new files, so a normal run never needs overwrite approval.

**19:22, tests before code.**
- I wrote 20 boundary cases with predictions, the loop tests and the five wrong versions as code, and froze the test files by sha256. All three new modules failed to import.

**19:24, a green run I did not trust.**
- All 69 tests passed on the first run, so I broke the code six ways in a scratch copy. Five breaks were caught.
- Deleting the "never write through a symlink" line left everything green. Boundary row 11 is caught by the real-path check, not by that line, so the line is untested defence in depth. It is recorded, not hidden.

**19:25, live run 1.**
- Six boards on three systems. The deliberate 404 was tried once and recorded as `failed`, with no count. WHOOP's `[]` became `empty`. The exit was `incomplete`, 6/12 requests, 3.4 s.

**19:25, the finished wrong answer.**
- I cut Oscar's saved response to 20 jobs (seeded) and the agent said `finished`.
- My check then crashed, because its command line assumed `runs/<id>` and the seeded run is nested. Its "exit 1" was a crash, not a catch. I fixed the folder lookup and re-ran only the check, which then flagged `meta.total 199` and "179 of 199 disappeared".

**19:26–19:45, the review packet.**
- **Reproduce first:** real postings copied from JS1, and a test that failed on v1, 10 of 15.
- **Rev 1** passed 84/84. Reading its behavior diff on 685 postings, I found 16 Linear jobs failing on a perk ("Paid month off after 4 years…"), because "(based on country requirements)" looked like a heading. My first guess at the cause changed nothing, which showed it was wrong.
- **Shreyash ran the commands and chose to revise.** I wrote a regression test from the 16 postings; it failed on rev 1.
- **Rev 2** fixed the perk. My regression test then failed on 2 of the 16, and the ads showed it was my test that was wrong: they state real requirements ("8+ years in a Solutions Engineering…"). I corrected it with each requirement quoted and recorded why (`review/08`).
- **Rev 2's dropped failures.** Listing every condition rev 2 stopped failing showed about 37 real requirements dropped. Rev 1 had dropped 20 Palantir ones as well, which I missed because I only sampled its diff.
- **Reading those ads** showed 3 of the "drops" were right: "Preferred skills: 4+ years". The other 14 were mandatory.
- **Rev 3** reads each "N years" phrase in its own sentence. It needed two more fixes before its tests passed: "CPA preferred What We Require:" read as a preferred heading, and a Lever requirement list running into "Hybrid schedule:".
- **Rev 3's result:** 93/93 with no test edited, 0 verdict changes, every dropped and new failure read. Shreyash accepted it.

**20:17, live run 2.**
- Shreyash asked for it straight away, about 50 minutes after run 1. It came out `incomplete` with 0 new on every working board, and all six responses were byte-identical to run 1's.
- A quiet run is a real result, but it means a real new posting was never judged inside the loop.

**2026-11-10 15:47, live run 3.**
- A day later, there were 6 real new postings: 2 Oscar, 1 Linear, 3 Palantir. All were judged in the loop by rev 3, and all came out Not Relevant. The recount from the raw files matched.
- The closest calls were Palantir's software engineering intern postings, failing only on the department label `Dev` and on location. The contract's department list does not settle whether `Dev` is engineering.

**2026-11-10, after a review of the submission.**
- The review asked for a test that only the no-symlink line can pass. I wrote boundary row 21 and its prediction, and committed them before running (`2b8ed44`): a symlink inside runs/ to a not-yet-existing file inside runs/.
- It passes on the real code. With the line deleted, it is now the one failing test, so the mutation-check gap from 2026-11-09 is closed.
- The review also asked that the Physician Reviewer case stay disclosed. The README now has a "Known limitations" section listing it with the other open questions.

**What is unresolved.**
- The Physician Reviewer case: a state-tagged office beats an ad that says "reside in the United States".
- The location-vs-offices question.
- The check cannot catch a partial Ashby or Lever response.
- A real timeout or redirect never happened, so those paths were only tested with constructed inputs.
- Whether a Lever department label like `Dev` should count as an engineering department.
