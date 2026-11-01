# Prompt experiment (Chapter 2)

## Setup (all dated)

| Step | When (UTC) | Who |
|---|---|---|
| 20 real Klaviyo postings picked by a fixed seed (12 engineering + 8 other; 10 dev / 10 held-out) | 2026-10-25 ~23:05 | `select_postings.py` (Claude Code's procedure) |
| Labeling rule written, before any label | 2026-10-26 16:53 | Omkar's choices: `LABELING-RULE.md` |
| 20 hand labels | 2026-10-27 ~17:00 | **Omkar**, one click per posting in chat (11 relevant / 9 not). Asked whether to revisit 5 labels that conflict with his own rule, he chose "Keep as they are" |
| Baseline prompt on dev | 2026-10-27 ~17:02 | Claude Code ran it |
| The one change, chosen by Omkar: **"Add my labeling rule"** (the definition block is the *only* difference; see `diff prompts/baseline.txt prompts/revision.txt`) | 2026-10-27 ~17:04 | Omkar chose; Claude wrote the block from LABELING-RULE.md |
| Revision on dev | 2026-10-27 ~17:05 | Claude Code |
| **Lock**: sha256 of both prompts + labels (`lock.json`) | 2026-10-27 17:06:27 | Claude Code |
| Both prompts on held-out (first time anyone saw Claude's held-out verdicts) | 2026-10-27 ~17:07 | Claude Code |

Pass = Claude's verdict equals Omkar's hand label. A rejected output would count as a fail; none were rejected (40/40 valid).

## Results

| prompt | split | n | valid | pass | pass rate | rule = hand |
|---|---|---:|---:|---:|---:|---:|
| baseline | dev | 10 | 10 | 4 | 4/10 = 40% | 6/10 |
| baseline | heldout | 10 | 10 | 6 | 6/10 = 60% | 7/10 |
| revision | dev | 10 | 10 | 4 | 4/10 = 40% | 6/10 |
| revision | heldout | 10 | 10 | 6 | 6/10 = 60% | 7/10 |

"rule = hand" is how often the agent's **written rule** (the record) matched Omkar's labels on the same postings.

## What it shows, and how little (draft by Claude Code)

- **The one change changed no verdict.** All 20 postings got the same verdict from both prompts. It did change the *reasons*. For example, on the Denver architect posting the baseline counted "Denver vs Boston" against it; the revision dropped location and cited role type and years instead. The change moved the justification, not the decision.
- **Claude said relevant once in 40 calls**: Software Engineer II – Recommendations (2+ years), under both prompts. Omkar labelled it relevant too.
- **Every miss has the same shape.** Omkar said relevant, Claude said not_relevant, and the posting is senior, lead, staff or principal, or asks for 4–10+ years. Claude's verdicts match Omkar's *written* rule ("about 3 years or fewer") more closely than his labels do. So the 40–60% pass rate measures the gap between his labels and his rule as much as Claude's quality.
- **Dev 40% vs held-out 60%** is a difference of 2 postings out of 10. With 10 cases, one posting is 10 points. This gap is noise-sized and supports no claim that either prompt "generalises".
- **The written rule matched the hand labels better than Claude did** (6/10 and 7/10), because it also has no seniority gate. It agreed with Claude on 17 of 20.
- **Not shown:** whether a different single change (for example "senior titles are fine", which is closer to how Omkar labelled) would move verdicts; behaviour on a board with more junior roles; any other model.
