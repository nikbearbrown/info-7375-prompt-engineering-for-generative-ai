# FRICTIONAL.md: JS3

Each quote is my answer, typed in chat with Claude Code on 2026-11-24 and copied here exactly, typos included. Claude
asked the questions (in italics). The **Trace** lines under each entry were added by Claude: only what changed, the
commit and the file. They are not my words. My reasons for individual labels are in `audit/hand-reasons.json`, verbatim.

## 1. Reading 78 postings was too slow

*While labeling the 78 cards, what was hard, and why did you ask for the years and requirements boxes?*

"it was not easy for me to go through all the JDs and read each and everything so i wantd you to give it to me short to save my time"

**Trace:** yellow "Years of experience" box and blue "Requirements" box added to every card, copied from the posting;
same sample and card order (commit `9adef86`, `tools/make_sheets.py`).

## 2. The years box missed "8 or more years" (card #41)

*On card #41 the yellow box said "No years mentioned", but you saw "8 or more years". How did you notice?*

"even though no years were mentioned , i was reading the short description you gave in the blue box and the first point itself had 8 or more years"

*After the yellow box got that one wrong, did you trust it less for the remaining cards?*

"yes i started reading th eblue box description more carefully"

**Trace:** box pattern fixed (commit `c1007a5`). The filter's own years check had the same hole; fixed as candidate c2,
included in v1.1 (`FILTER.md` §6, commit `810ee17`). Still not caught: "Extensive years" (`SHORTLIST.md` §3,
counterexample 3).

## 3. I judged some cards as myself, not as Arya

*On #19 and #45 you first judged the job against your own background, not Arya's. Then you chose to judge everything
as Arya. What did you learn from that?*

"that the labels should be for arya not me , i was considering that she inherited all my ex but that wasnt the case"

**Trace:** chosen in chat, "A, keep 19 as not". #19 correction withdrawn; #45 corrected to Not
(`audit/hand-label-corrections.json`, commit `0d21d78`).

## 4. What I accepted, changed or rejected from Claude

*What did you accept, change or reject from Claude today?*

"i accepted the weights, added G5, kept 78 labels because that how i would be accurate"

**Trace:** weights and threshold 6 in `FILTER.md` v1 (commit `27646b2`); G5 added in the same commit after Claude's
"Sales Engineer scores 7" example; 78 labels kept when Claude offered 52; v1.1 = all four candidates, chosen on dev
labels (commit `810ee17`).

## 5. Unresolved: "always not" and my own worry while labeling

*What's still unresolved, or what bothers you about the result?*

"yes i was scared that if i select not alsways then it would beat the filter and it would be of ni use]"

*While you were labeling, did that worry make you pick "Show" on any card where your honest answer was "Not"?*

"yes a  couple of times i did think about that"

**Trace:** on the blind held-out labels, "always not" = 16/20, filter v1.1 = 15/20 (`out/score-table.md`,
`SCORE.md` §2). 8 of 10 blind Shows were later changed in chat (`AUDIT.md` §2, "A bias I admit").
