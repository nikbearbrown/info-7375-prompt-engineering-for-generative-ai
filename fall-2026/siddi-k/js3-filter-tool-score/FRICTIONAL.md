# FRICTIONAL.md

Written by Siddi Kommuri and pasted in chat on 2026-11-25 at about 22:38 ET. Claude saved it verbatim, except for one phrase in Entry 2 that Siddi approved changing at about 22:43 ET: "using the filter" became "on the blind sheet, which did not show the filter's verdicts". The entry topics follow a list of possible episodes Claude suggested when Siddi asked for a brief; the entries and their wording are Siddi's.

### Entry 1 — Nov 25 · FILTER draft

I accepted Claude's FILTER.md draft because it gave me a starting point instead of having to design every filtering question from scratch. The three open questions forced me to make decisions about the experience cap and location requirements, particularly 2 versus 4 years and anywhere in the USA versus the JS1 city list. I accepted the draft, but those choices also mean the filter isn't necessarily identical to my original labeling rule. Claude contributed the draft and surfaced the choices; I made the decisions. I understand that the written filter defines what the judge evaluates, and inconsistencies with the labels can affect the experiment. **Evidence:** `4e62099c`

### Entry 2 — Nov 25 · Labeling 62 postings

I labeled 62 postings on the blind sheet, which did not show the filter's verdicts, but I don't have a reliable time estimate for how long the labeling took. Some non-US and sales postings were marked relevant, which means I was not applying a strict location and job-function standard consistently with the earlier criteria. I need to be honest about whether those decisions reflected my actual interpretation or whether I moved too quickly through the labels. Claude helped organize the workflow, but the labels were my decisions. Stripe posting `7392697` changed from not relevant in October to relevant, and I need to understand what changed in my interpretation rather than pretend the two labels are consistent. **Evidence:** `4d633be9`

### Entry 3 — Nov 25 · Keeping the labels

I decided to keep the existing labels instead of relabeling them after the audit. The audit result of 18 out of 30 made me less confident that my labels were consistent, but changing them now would also change the ground truth after seeing the audit. I chose to preserve the original labels, although that means accepting that the dataset has noise and disagreements. Claude contributed the audit findings; I chose not to modify the labels. I understand that the 18/30 result is a warning about label quality, not proof that either the judge or my labels are correct. **Evidence:** `labels/DECISION.md`

### Entry 4 — Nov 25 · FILTER v1.1 versus v1.2

I adopted v1.1 and rejected v1.2. I kept the version I was comfortable using rather than accepting a further proposed change without sufficient reason. I also kept the budget at 30 even though Claude's earlier estimate of approximately 30 was wrong, because I wanted the limit to remain an explicit decision rather than something changed automatically. Claude proposed the versions and recommendations, but I made the final choices. I understand that filter changes should be deliberate and documented, especially when the labels are already fixed. **Evidence:** `FILTER.md` §E

### Entry 5 — Nov 25 · Security Engineer and unresolved evaluation

The Security Engineer case showed me that an agent can support its reasoning with claims and still reach the wrong answer. I don't want to confuse a convincing explanation with a correct verdict. I still don't fully understand why none of the Claude variants changed their verdicts or how much confidence I should place in the reported 41–77% interval. Claude provided the analyses, but the result does not establish that the variants are reliable. I would want to inspect the disagreements and understand the evaluation before treating the filter as validated. **Evidence:** `FILTER.md` §E; `labels/DECISION.md`

---

## Reference: events Claude can point to (Claude's list, not Siddi's account; times ET, 2026-11-25)

| Time | Event | Evidence |
|---|---|---|
| ~21:50 | Siddi chose "Claude drafts, I edit" for FILTER.md and a 30-request budget | chat; FILTER.md header |
| 21:59 | Siddi answered the three open questions (anywhere in the USA; years cap 4; keep 30, though Claude's "~30" was really 31) and approved the rest | `4e62099c` |
| 22:00 | The collection ended `budget-exhausted`. Canva had grown to 29 postings, so 2 had no text. | `40f9ea3e` |
| 22:03 | Filter v1 kept only 8 of 975. Claude found that G4 reads "Chicago", "SF, NYC" and the like as not US. | `2ffbb8f9`; AUDIT.md |
| 22:07 | The real Claude CLI session probed the 2026-07-28 `server/discover` before falling back to `initialize` | `evidence/mcp/2026-11-26T03-06-55Z/` |
| 22:12 | The shortlist showed the Security Engineer: supported claims, wrong answer | SHORTLIST.md |
| 22:18 | The first course-server session failed (the tap's folder bug) and Claude said it would not guess. Re-run worked. | `evidence/other-server/` |
| 22:21 | Five Claude variants: identical verdicts on all held-out postings | `6dcc3edd` |
| 22:25 | Siddi's 62 blind labels: 39 relevant, 25 of which conflict with LABELING.md; Stripe 7392697 flipped from Oct 31 | `4d633be9` |
| ~22:28 | Siddi kept the labels as-is, adopted v1.1 and rejected v1.2 | `labels/DECISION.md`, FILTER.md §E |
