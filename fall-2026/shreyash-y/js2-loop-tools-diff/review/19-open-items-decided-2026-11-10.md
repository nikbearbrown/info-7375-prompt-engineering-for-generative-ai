# Three open items, settled by Shreyash after reading the saved ads

## My review of the remaining open items, November 10, 2026

*Shreyash's words, typed into the session on 2026-11-10. This replaces a shorter decision paragraph on `Dev` given earlier the same day (in commit `5ed5159`). The last sentence of the `Dev` paragraph was replaced later that evening, after the regrade, also in Shreyash's words. Claude Code did not change them.*

**1. Klaviyo — Posting 7809608003**

I checked the posting against my original label and found a mistake in my manual review. The job description mentions Python, but I could not find a second skill that matched my rule. The posting also requires 12+ years of experience.

My original hand-label missed the skills condition. After comparing the description with the rule, I decided the rule was correct and my manual label needed to be corrected. I kept this distinction clear rather than changing working code to match an incorrect label.

**2. Linear — Two Experience Requirements**

I checked the two Linear postings referenced in `review/08`. The Solutions Engineer, APAC posting explicitly requires 8+ years of relevant experience, while the Account Executive, Enterprise posting requires 7+ years in a quota-carrying sales role.

I decided that both are genuine experience requirements, not optional preferences. This helped me confirm that the parser should evaluate the actual requirement text instead of relying only on section headings.

**3. Palantir — `Dev` Department**

I decided that `Dev` should count as an engineering department for the three Palantir software engineering internships because their titles and responsibilities clearly involve software development.

However, I would not automatically treat `Dev` as engineering for every company using Lever. Different companies may use the same department label differently.

Even if I accept `Dev` as engineering for these Palantir postings, they still fail my location condition because they are based in New York or Denver rather than Boston or an accepted remote location.

For now, I documented this interpretation without changing the implementation. I would need additional evidence before introducing a broader department-mapping rule.

**What I learned**

These checks showed me that my manual judgments also need verification. Not every mismatch means the code is wrong. Sometimes the rule is correct, and the mistake is in my original label or interpretation. I kept these decisions separate from code changes so the review record shows exactly what I concluded and what remains unresolved.

## The findings that led to it (written first)

*Shreyash's words, typed into the session on 2026-11-10 after reading the saved ads, which a read-only helper printed (the skills found in 7809608003, the two Linear requirement lines, and the Palantir intern departments). Claude Code added only this heading and note. No code was changed: the `Dev` decision is recorded first, as it says, and is not implemented in this submission.*

| Item | My finding | Proposed decision |
|---|---|---|
| Klaviyo 7809608003 | The saved ad mentions Python but not a second skill from the rule's matching list. It also requires 12+ years of experience. | The original hand-label for condition 4 appears incorrect. |
| Linear — Solutions Engineer, APAC | The saved ad explicitly states 8+ years in Solutions Engineering, Pre-Sales, or a similar role. | Confirm 8+ years as a mandatory requirement. |
| Linear — Account Executive, Enterprise | The saved ad explicitly requires 7+ years in a quota-carrying sales role, alongside 3+ years selling to enterprises. | Confirm 7+ years as a mandatory requirement. |

The first item explains the discrepancy between review/16 and review/18: the rule's skills failure appears justified, while the original hand-label omitted that failure.

For Palantir Dev, my recommendation is yes, treat it as an engineering department, but only through a documented, provider-specific interpretation. The saved jobs are explicitly Software Engineer internships, and their responsibilities concern software development. However, the raw department value Dev remains ambiguous on its own, so I would not globally equate every Dev department with engineering.

Changing this interpretation would remove the department failure for those postings, but they would still fail the Boston/remote location rule. I reviewed the Palantir Dev posting myself and recorded my interpretation of the job requirements. I kept this as a manual review rather than claiming I had written or executed a test for this posting.
