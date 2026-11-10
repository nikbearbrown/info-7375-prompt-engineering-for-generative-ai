# Blind check of the multi-part case studies (2026-11-09)

**What was done.** An AI reader (a fresh Claude subagent) was given only the student pages of the six cases, with no keys and no other files, and asked to mark all 60 statements true or false, say how confident it was, flag any statement that could reasonably be judged either way, and list problems.

**Result.**
- Its 60 answers matched the author's keys on all 60 statements.
- It flagged 5 statements as ambiguous or low confidence and noted 4 more technicalities. All nine were fixed in the text, listed below.

**Caveat.** The reader is the same kind of model that wrote the cases, so agreement shows the statements are clear and consistent, not that the keys are right: shared mistakes would agree too. A TA or instructor read is still needed before any use.

| Case, statement | What the reader flagged | Fix |
|---|---|---|
| 1 J | "cannot be taken back" is an outside-world claim; "worth its cost" is a judgment | Reworded: a paid refund is hard to undo, so requiring approval before large refunds fits the risk |
| 2 G | The case never said R7 came back through the MCP search tool | The run record now says the pipeline calls the MCP search tool and that R7 is among the five passages it returns |
| 2 J | R7 was not in run 1's citations, so "the support includes R7" was inferred | Run 1 now cites both R12-c3 and R7-c1 |
| 4 I | Compound: the "name an owner" half does not follow from the case | Reduced to the part the case supports (the 10% versus 4.5% gap) |
| 4 J | The sign-off said "300 held-out applications" while the evaluation gave 40 past openings | Sign-off note now says "Tested on held-out past applications. Approved." |
| 5 I | True only with a technicality (the script checks the sum, not the extraction) | Reworded to "a stronger check on the sum" |
| 5 J | "exact" was vague | Reworded: asking for tests first does not mean the totals no longer need checking |
| 6 A | "tells the model where to stop" is a technicality | Reworded: a stop sequence ends generation when that text appears |
| 6 H | "come from the passages and not from learning" was absolute | Reworded: correct answers do not show the bot has learned the course |

The ten statements per case, their parts and the true/false balance are unchanged (30 of 60 true).
