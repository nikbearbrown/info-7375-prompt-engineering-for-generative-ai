# Three open items, settled by Shreyash after reading the saved ads

## Decided (Shreyash, 2026-11-10)

*Shreyash's words, typed into the session on 2026-11-10 as the decision on `Dev`, after the table and notes below. Claude Code did not change them.*

I decided that `Dev` should count as an engineering department for these Palantir postings because their titles and responsibilities clearly describe software engineering work. However, I would only apply this interpretation to Palantir rather than treating `Dev` as engineering on every Lever board.

This interpretation would remove the department failure for the three internships, but the postings would still fail my location condition because they are in New York or Denver. I documented this decision without changing the implementation, since I have not tested the same interpretation across other Lever boards.

## The findings that led to it (written first)

*Shreyash's words, typed into the session on 2026-11-10 after reading the saved ads, which a read-only helper printed (the skills found in 7809608003, the two Linear requirement lines, and the Palantir intern departments). Claude Code added only this heading and note. No code was changed: the `Dev` decision is recorded first, as it says, and is not implemented in this submission.*

| Item | My finding | Proposed decision |
|---|---|---|
| Klaviyo 7809608003 | The saved ad mentions Python but not a second skill from the rule's matching list. It also requires 12+ years of experience. | The original hand-label for condition 4 appears incorrect. |
| Linear — Solutions Engineer, APAC | The saved ad explicitly states 8+ years in Solutions Engineering, Pre-Sales, or a similar role. | Confirm 8+ years as a mandatory requirement. |
| Linear — Account Executive, Enterprise | The saved ad explicitly requires 7+ years in a quota-carrying sales role, alongside 3+ years selling to enterprises. | Confirm 7+ years as a mandatory requirement. |

The first item explains the discrepancy between review/16 and review/18: the rule's skills failure appears justified, while the original hand-label omitted that failure.

For Palantir Dev, my recommendation is yes, treat it as an engineering department, but only through a documented, provider-specific interpretation. The saved jobs are explicitly Software Engineer internships, and their responsibilities concern software development. However, the raw department value Dev remains ambiguous on its own, so I would not globally equate every Dev department with engineering.

Changing this interpretation would remove the department failure for those postings, but they would still fail the Boston/remote location rule. You should record the decision before changing any code.
