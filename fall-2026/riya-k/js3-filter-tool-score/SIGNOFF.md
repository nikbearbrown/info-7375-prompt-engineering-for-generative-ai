# Sign-off: Job-Search Agent 3

**Checked: which properties, by which of my own tests**

| Property | Test / check | How |
|---|---|---|
| Whole-word matching ("AI" not in "maintain", "SQL" not in "NoSQL") (W1) | `tests/test_filter.py::W1SubstringMatching` | test written before running v1 on the corpus |
| Gates beat the score (a London or Staff posting with score 11 is rejected) (W2) | `W2ScoreWithoutGates` | same |
| No keep without a ROLE word in the title (W3) | `W3TitleBlind` | same; the G5 gate itself came from a worked example in chat |
| Labels frozen before measurement (W4) | `tests/test_heldout.py`; `audit/hand-labels.sha256` committed in `fe8f7e5` before any comparison | by a test + commit order |
| Each wrong version is actually caught | `tools/check_wrong_versions.py`: W1, W2, W3, W4a, W4b planted into temp copies, all CAUGHT | by mutation |
| `filters/filter-v1.json` = the FILTER.md table | `FilterFileMatchesDocument` | by a test |
| Abstention A1–A3 and evidence labels (years, location, absent skill ≠ contradiction) | `Abstention`, `Evidence` | by tests |
| v1.1 rules (G6, years pattern, US cities, `agents` cut) | `V11` | tests written **after** the v1.1 code, by Claude |
| Every shortlist quote occurs verbatim in its posting | `tools/make_shortlist.py` check: 0/285 (v1), 0/242 (v1.1) mismatches | by recomputation |
| The tool server: protocol shapes, one read-only tool, refuses extra arguments / unknown tools / writes outside `transcripts/` | `tests/test_mcp_server.py` (12 tests); real transcripts s1, s2 | by tests + real Claude Code sessions |
| The filter's errors on real postings | 78 blind hand labels; reasons and 11 corrections in my words | **by hand**: me |
| The years box on the label sheet missed "8 or more years" | card #41 | **by hand**: I found it |

**How:** by hand (all 78 labels, the reasons, the corrections, every rule and threshold decision); by tests and a
mutation check (Claude wrote the code and the tests; the W1–W3 tests and the FILTER.md decisions existed before the
corpus run); by recomputation (shortlist quotes; Claude's spot-check of the C4 quotes); with Claude's help (Claude
drafted the weights I accepted, wrote all the code, ran every Claude session, and suggested the questions that led to
my corrections).

**Not checked:**
1. What v1.1 throws away. It rejects about 290 more postings than v1, and I didn't draw a new random-reject sample.
2. Whether any scorer finds good jobs. My held-out set has 3 blind Shows (1 after corrections), too few to measure.
   "Always say not" beats every scorer on blind held-out labels.
3. The "N years" pattern: the 80-character "experience" window and the "smallest number" rule. Claude wrote them,
   and §3 of `SHORTLIST.md` shows one case ("3+ … and 8+") where they're wrong. I didn't review the pattern on more postings.
4. Most claim labels in the 46-posting v1.1 shortlist. Only the examples in `SHORTLIST.md` were read by hand.
5. Whether Claude Code would really send its working folder as a root to the filesystem server (I only probed it with
   my own client).
6. Whether the postings are still open. The corpus is from 2026-11-10.

**Not claiming:**
- That the filter, or Claude, is accurate on all postings. Every number is from samples of 58 and 20, with intervals.
- That anything was trained. All behavior changes are file edits (`SCORE.md` §3).
- That my corrected labels are blind. They were made after seeing the filter's verdicts.
- That a `kept` posting is worth applying to.

**Signed or withheld:** ____________ (name, date)

---

## Driver's seat

| Claude should | I should | Why |
|---|---|---|
| run the filter on every posting, every time, the same way | write and version the filter (FILTER.md), and decide every change to it | the rule is my judgment, written down; Claude applying it is just arithmetic |
| quote the posting for every claim, and say "I cannot tell" when the text doesn't say | read the posting before I believe a claim | the quote shows the words are there; only reading shows they mean what the claim says (#32 "Remote", #48 "evaluation") |
| point out where my labels and my reasons disagree | decide whether to change a label, and say so in the record | a label I changed because Claude asked is no longer blind; only I can say what I meant |
| score, sort and shortlist | decide that a posting is worth my time | "worth my time" depends on things no posting text says: what I want next, what I'd turn down, how much one application costs me this week. A filter can only rule postings out; it can't want a job |
| run as a read-only tool, never apply, email or log in | do every outward action myself | an application goes out under my name |
