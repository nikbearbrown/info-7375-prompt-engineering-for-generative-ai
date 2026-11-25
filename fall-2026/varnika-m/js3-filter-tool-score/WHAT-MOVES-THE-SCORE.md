# What moves the score

## 1. Every number in the scorer, and where it came from

"Fitted" would mean chosen to agree with my labels. **No number in v1 was fitted.** v1.1's two changes were found on my audit labels (FILTER.md, Versions).

| Object | Value | Origin |
|---|---|---|
| R1 role phrases | 8 phrases ("Software Engineer" … "Cloud Engineer") | **inherited**: from Claude's discarded JS1 contract draft, which I kept (JS1 `SOURCES.md`) |
| R2 seniority words | 11 words (Senior … Internship) | **inherited**, the same way |
| R2 graduation date (v1.1 B) | "must be graduating" in Dec 2026 or later | **hand-set**, then **found on my audit labels** (item 32) |
| R3 location test | "United States", or a state code or DC after a comma | **inherited** from JS1 (Claude's review suggested the method; the wording is mine) |
| R3 "D.C." (v1.1 A) | accepted after a comma | **found on my audit labels** (items 53, 54) |
| R4 years limit | 3 | **inherited** from JS1. The number came from Claude's discarded draft; the reason (29 months against 36) is mine. |
| R4 phrase patterns | "N+", "at least N", "N–M" (counts as M) | **inherited**: my JS1 choice among options Claude offered |
| R5 skills | 15 terms | **inherited** from the persona's résumé (the Reallocation Engine example) |
| R5 minimum | 2 different skills | **inherited** from Claude's discarded JS1 draft |
| Score | the number of rules passed, 0–5, equal weights | **hand-set** in FILTER.md v1 (drafted by Claude Code, kept by me) |
| Keep threshold | 5 of 5 | **inherited** from JS1 ("all five rules") |
| Close call | 4 of 5 | **hand-set** in FILTER.md v1 |
| Ranking | the number of *different* skills matched | **hand-set** in FILTER.md v1 |
| Evidence cue words (C2 "new grad"…, C5 "you have", "a plus"…) | word lists in `js3/claims.py` | **hand-set** by Claude Code from FILTER.md section 2 |
| Abstention | "I cannot tell" if C1, C3 or C4 is insufficient | **hand-set**: my decision D2 |
| Audit sizes and seed | 30 / 8 / 8 / 16, seed `20261125` | **hand-set** in FILTER.md v1 (30 is the assignment's minimum) |
| Claude prompt `baseline-v1` | `prompts/baseline-v1.txt` (SHA-256 `058a0742…`) | **inherited** from JS1, written by Claude Code |
| Claude prompt `revision-v1` | `prompts/revision-v1.txt` (`187efea5…`): adds "judge only must-haves" | **inherited** from JS1. I chose the change in JS1, and Claude Code wrote it. |
| Claude model and session | `claude-opus-5-5`, fresh `claude -p`, no tools, empty folder, no settings | **inherited** from JS1 `claude_judge.py` |

## 2. One change at a time, on the held-out labels

**The held-out set:** 16 postings drawn at random from scores 3–5. My labels for them were used **only** here.
- 2 of the 16 are fits by my labels (items 6 and 58).
- With so few fits, **one** disagreement moves agreement by more than 6 points.
- Each set-up was asked once. Run-to-run variation was not measured.

**The baseline:** filter v1, and Claude with `baseline-v1` on the whole posting.

| # | Object changed | The change | Agreement with my 16 labels | Fits found / kept but not fit / fits missed | Decision |
|---|---|---|---|---|---|
| — | — | filter v1 | **16/16** | 2 / 0 / 0 | baseline |
| M1 | **the filter file** | R4 counts must-have years only | 16/16 | 2 / 0 / 0 | **rejected**: no measured effect. It moved one posting (43, my N) from reject to close call. |
| M2 | **a setting** | keep at 4 of 5 | **10/16** | 2 / **6** / 0 | **rejected**: 6 wrong keeps |
| — | — | Claude, `baseline-v1`, whole posting | **16/16** | 2 / 0 / 0 | baseline |
| M3 | **the prompt** | `revision-v1` (judge only must-haves) | **14/16** | 1 / 1 / 1 | **not adopted** (below) |
| M4 | **the context** | Claude sees only the title, the location and the requirement lines | 16/16 | 2 / 0 / 0 | no change in answers, with less text |
| — | the filter file | v1.1 (A: D.C.; B: graduation date) | 16/16 | 2 / 0 / 0 | **adopted**, on the audit evidence. Held-out cannot show its effect: no held-out posting is in D.C. or asks for a future graduation. |

**What M3 changed** (`measure/replies/`, asked 2026-11-25 between 15:53:53 and 15:54:37 UTC):
- **Item 55, Palantir Mixed Reality Developer, my N.** `baseline-v1` said NOT_MATCH. `revision-v1` said **MATCH**: *"The posting's 'What We Require' asks for a CS bachelor's or equivalent experience, 2+ years programming in languages such as Java or Python, and ability to obtain a clearance…"*. Judging only must-haves, it dropped Unity and Unreal.
- **Item 58, Palantir Software Engineer, New Grad - Defense, my Y.** `baseline-v1` said MATCH. `revision-v1` said **NOT_MATCH**, reasoning that *"the posting requires an active US securit[y clearance]"*. The posting says "*Active US Security clearance **or eligibility and willingness to obtain** a US Security clearance*", so it misread its must-have.

The same one-sentence change made Claude both more lenient (55) and stricter (58), each time disagreeing with me. On 16 postings this cannot show which prompt is better in general. It does show that a prompt change can move verdicts in **both directions at once**.

**The tool list** (its description) is the fifth object. It was **not** changed in a measured way. The description's version string went from v1 to v1.1 with the filter. The clarification TOOL-SERVER.md calls for was not made.

## 3. What persistence is not proof of

**A behavior that changes, or stays the same, across sessions does not mean anything was trained.** Here is where that applies in this assignment:

- Every Claude judgment ran in a **fresh session**: `claude -p --no-session-persistence --tools "" --setting-sources ""`, in an empty temporary folder. No reply saw another reply or my labels.
  - When `revision-v1` answered differently from `baseline-v1`, the difference came from **the prompt text**, which is the only thing that differed. Claude learned nothing between the two.
  - When M4 gave the same answers as the baseline, that does not show Claude "remembered" its earlier verdicts.
- The tool server answered with v1 in session 1 and answers with v1.1 now. **It changed because `js3/filter.py` and FILTER.md changed**, files I can diff (`git diff 48488ab3 ac25be53`). The model did not change.
- The agent "remembers" seen postings across runs (JS1–JS2 state files) and its rules across assignments (FILTER.md, `rule.py`). **That is files on disk**, not learning. Delete the files and the memory is gone. Change them and the behavior changes, with no model involved.
- Claude agreeing 16/16 with my labels in the baseline does not mean it learned my rule. It never saw my labels, and with 2 fits in 16, an "always NOT_MATCH" answer would already have scored 14/16.
