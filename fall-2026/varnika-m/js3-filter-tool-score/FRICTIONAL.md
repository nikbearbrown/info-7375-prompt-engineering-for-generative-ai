# FRICTIONAL — Job-Search Agent 3

My log of what I tried, what happened, what I checked or changed, and what I accepted, changed or rejected from Claude. Claude Code drafted the factual lines from the session, the commits and the saved files. **The "What I learned" lines are mine.** I wrote them from the angles Claude Code listed for each entry (it listed angles, not sentences), and it pasted them in word for word.

### 2026-11-25 — Due today, and the filter written first
- **What I tried:** JS3 was due the same day. I asked Claude Code which recommendation to take for each FILTER.md decision.
- **What happened:**
  - Claude Code built FILTER.md v1 on my own JS1 rules and reasons.
  - It recommended D1: keep JS1's "count every years phrase", and test "must-haves only" as a measured change.
  - It recommended D2 ("I cannot tell" when there is no evidence) and D3 (keep my "at most 1 of 30" pass line).
  - I replied "ok as you say" and then "ok" to the draft, which was committed before any code (`48488ab3`).
- **What I checked, changed, or learned:**
  - **What I learned:** When I wrote the filter rules before looking at the results, I learned that setting the rules first makes it harder to change them just to get a better result.
  - **Still unresolved:** The decisions are mine, but all three were Claude's recommendations, which I accepted without changing them.
- **From Claude, accepted / changed / rejected:** Accepted D1–D3 and the draft unchanged.
- **Trace:** `48488ab3`; FILTER.md header and Versions.

### 2026-11-25 — Labeling: asking Claude to do it, and deciding myself
- **What I tried:** I asked Claude Code to do the labeling, twice, and once to do my corrections.
- **What happened:**
  - Claude Code declined each time, because the labels are the hand judgment the audit is about. It offered three honest options, and **I chose to label all 62 myself**.
  - It made a shorter quick view and explained my rule in simple steps.
  - I asked whether "3+ years" is Y or N, and what to do about clearance. My first thought was that he is an immigrant. Claude Code pointed out that his résumé says nothing about citizenship, and that it must not be decided from his name. I chose the "status unknown" rule before any label (`c1dd36e5`).
  - In batch 1, I wrote "Y/N not sure" for five items because no years were given, and "needs an active clearance" for four items whose postings say "or willing to obtain". Claude Code suggested a label for each of the nine from my written rules, and I confirmed all of them.
  - For items 21–62, Claude Code asked how my second batch was made, because its wording was different. I answered that I decided each one myself.
- **What I checked, changed, or learned:**
  - **What I learned:** When I was unsure about the clearance requirements, I learned that missing information does not mean someone is ineligible. I should use "status unknown" instead of making assumptions about a person.
  - **Still unresolved:** 9 of my 62 labels are confirmed suggestions, not labels I wrote first. My reason for item 17 ("Requires 3+ years (Aarav has 29 months)") contradicts my own "3+ years" decision. The label stands on the other must-have I cited.
- **From Claude, accepted / changed / rejected:** Accepted the two labeling decisions and the nine suggestions. I changed my first idea about his status.
- **Trace:** `c1dd36e5`, `c7007363`; `audit/labels-raw.md`; `audit/LABELING-DECISIONS.md`.

### 2026-11-25 — The audit passed my line and found a bug
- **What I tried:** Comparing my 62 labels with the filter.
- **What happened:**
  - 0 of 30 random rejects fit Aarav, so my pass line is met.
  - 2 of 8 close calls fit (items 53 and 54). Both failed only R3, because "Washington, D.C." has dots and JS1's rule only knew "DC". 64 postings have "D.C.", and v1 failed every one of them on R3.
  - 1 of 8 kept postings did not fit: "must be graduating in December 2026", and he finished in May 2026.
  - I decided v1.1: add "D.C." and the graduation-date rule; record "Platform Engineer" as a false friend without a rule; reject must-haves-only years (no measured effect), keep-at-4 (6 wrong keeps) and grouping by title.
- **What I checked, changed, or learned:**
  - **What I learned:** When the audit passed but still found the Washington, D.C. formatting bug, I learned that passing the main test does not mean the filter is completely correct. Small formatting issues can silently reject good jobs.
  - **Still unresolved:** 0 of 30 still allows up to about 9.5% of the rejects to fit. A and B were found on my audit labels, and the held-out set has no posting that could test them.
- **From Claude, accepted / changed / rejected:** Accepted all six recommendations.
- **Trace:** AUDIT.md; FILTER.md v1.1; `ac25be53`.

### 2026-11-25 — My tool server, used by Claude, and someone else's server
- **What I tried:** Offering my filter to Claude through a tool server written from scratch, and having Claude Code use it.
- **What happened:**
  - Claude Code 2.1.283 connected and listed the one tool. It called it twice: once on a real posting, and once on an id that does not exist, which came back as an error.
  - In its reply, Claude said my tool's output contradicts itself: `outcome: keep` next to `answer: I cannot tell`. Both are by design, but the output does not explain them.
  - The reference `fetch` server's description tells the model it "now" has internet access, and does not mention any of its refusals.
- **What I checked, changed, or learned:**
  - **What I learned:** When Claude's tool output looked contradictory, I learned that a tool's response can be technically correct but still confusing. I need to check what the tool actually does instead of trusting how it describes itself.
  - **Still unresolved:** The description fix for my tool is not made. The `fetch` server was only read, not run, and six of its helper modules were not read at all. I did not read its source myself.
- **From Claude, accepted / changed / rejected:** Accepted both trust decisions as drafted.
- **Trace:** TOOL-SERVER.md; `transcripts/claude-code-session-1.server.jsonl`.

### 2026-11-25 — One change at a time
- **What I tried:** Measuring each change against my 16 held-out labels.
- **What happened:**
  - Keep-at-4 made 6 wrong keeps.
  - The "must-haves only" prompt changed two verdicts, both away from my labels: one more lenient (Mixed Reality Developer) and one stricter. On the stricter one, it read "or eligibility and willingness to obtain" as requiring an active clearance.
  - Everything else agreed 16/16. With only 2 fits among the 16, that agreement says little.
- **What I checked, changed, or learned:**
  - **What I learned:** When one extra sentence in the prompt changed Claude's decisions in opposite directions, I learned that even a small prompt change can affect results unpredictably. Next time, I will change one thing at a time and compare the results carefully.
  - **Still unresolved:** Each set-up was asked once, so run-to-run variation is unknown.
- **From Claude, accepted / changed / rejected:** Accepted the decisions not to adopt M2 or M3.
- **Trace:** WHAT-MOVES-THE-SCORE.md; `measure/scores.json`; `measure/replies/`.
