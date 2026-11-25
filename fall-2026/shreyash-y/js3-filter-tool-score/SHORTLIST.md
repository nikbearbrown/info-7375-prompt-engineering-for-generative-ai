# The source-grounded shortlist (Chapter 7)

*Drafted by Claude Code on 2026-11-25 from `results/shortlist-v1.{json,md}` (the code's labels, every
claim of every kept posting) and `results/claims-claude/` (Claude's independent labels). The
decisions in section 4 are Shreyash's.*

- **What was kept.** Filter v1 kept **5** of the 789 postings, all Klaviyo, all Boston. **4** are
  still open. `klaviyo:7855793003` closed after 2026-11-10, so it is labeled but not shortlisted.
- **The claims.** Each kept posting's justification is **nine claims**: role, department, location,
  skills, experience, seniority, full-time, paid, relocation. Six are must-haves under the evidence
  rules (answer 11): role, location, experience and the three exclusion claims.
- **Who labeled them.**
  - The code labels every claim (`js3/claims.py`). A label is *supported* only with an exact quote
    from the posting that states the claim.
  - Claude (opus, `claude -p`, no tools) labeled the same 45 claims without seeing the code's
    labels, and gave a quote for each label (`js3/claim_judge.py`, 2026-11-25 17:33–17:34 EST; the first run, without Alex's profile, was at 17:31–17:32).
  - Every quote from both was checked against the posting (wrong version 4): **0 not found**.
- **Agreement.** The two labelers agree on **42 of 45** claims. The 3 disagreements are in section 4.

## 1. Every claim, labeled

`supp` supported · `insu` insufficient · `cont` contradicted · `*` follow-up B (experience not stated:
kept, does not make the agent abstain) · `C:` Claude's label where it differs from the code's

| Posting | role | dept | location | skills | experience | seniority | full-time | paid | relocation | Agent's answer |
|---|---|---|---|---|---|---|---|---|---|---|
| Senior Software Engineer - Growth `7696724003` | supp | supp | supp | insu | insu* | supp / C:cont | insu | supp | supp | **I cannot tell** |
| Software Engineer II (Mobile Developer - Android/Kotlin) - Remote `7792539003` | supp | supp | supp | insu | supp | supp | insu | supp | supp | **I cannot tell** |
| Software Engineer II, Test Frameworks & Tooling `7855793003` (closed) | supp | supp | supp | supp | supp | supp | insu | supp | supp | **I cannot tell** |
| Software Engineer, Conversational Products & Agent Workflows `8041054003` | supp | supp | supp | supp | supp | supp | insu | supp | supp | **I cannot tell** |
| Software Engineer II - Flows Experience `8199437003` | supp | supp | supp | insu / C:supp | insu* | supp / C:insu | insu | supp | supp | **I cannot tell** |

The quotes behind every cell are in `results/shortlist-v1.md` (code) and `results/claims-claude/`
(Claude).

## 2. Relevance is not entailment: the Android/Kotlin posting

**`klaviyo:7792539003`, Software Engineer II (Mobile Developer - Android/Kotlin) - Remote, Boston.**

- **The filter kept it**, and Rule 4 says it "names 3 of Alex's skills ['Python', 'TypeScript',
  'React']". The words are really there. These are the three quotes Rule 4 found:
  - "comfortable with webviews and location services, and open to picking up new technologies
    (Python, React, AWS) as the team's surface area grows."
  - "Technologies We Use (not exhaustive) iOS (Swift) Android (Kotlin) React Native Flutter React,
    TypeScript, Redux Python, Django …"
  - "We maintain native and wrapper SDKs across iOS, Android, React Native, Expo, and Flutter."
- **None of them states the claim the justification makes**, that the job asks for Alex's skills.
  - The first quote says you should be willing to learn Python and React, which is the opposite of
    requiring them.
  - The second is a company-wide technology list.
  - The third is about SDKs, and "React Native" is not React.
- **What the ad does require:** "Android-first — 1-3 years of professional Android development
  experience, ideally including Kotlin; this is your core strength and primary focus." Kotlin and
  Android are not among Alex's ten skills.
- **So the posting matches the filter's words but does not support the claim.** The code labels it
  *insufficient*, because the skills sit in a tech list or come with "picking up". Claude labels it
  *insufficient* on its own ("Python, React and TypeScript appear only as technologies the team uses
  or ones to pick up, not as requirements"). Claude said the same thing in tool session 1
  (TOOLSERVER.md).
- **The same gap, more quietly:** in the Growth and Flows postings, Alex's skills appear in a
  "Technologies we use (not exhaustive)" list. Whether a tech list counts is disagreement 2 in
  section 4.

## 3. The abstention rule, and a counterexample that exposes its limits

**The rule, as FILTER.md answer 11 and follow-up B set it.** The agent says "I cannot tell" when a
must-have claim (role, location, experience, exclusions) is insufficient or has quotes both ways, or
the posting text is empty. "Experience not stated" is the one exception.

**Counterexample: it abstains on a posting a reader can see is fine.**

- **The posting:** Senior Software Engineer - Growth (`7696724003`), in Boston, in Engineering, with
  "Base Pay Range For US Locations: $148,000 — $222,000 USD".
- **What happens:** the agent answers **I cannot tell**. The must-have claim "It is a full-time,
  permanent job" has no quote: the word "full-time" appears **0 times** in all five kept postings,
  and Greenhouse gives no employment-type field. So the rule abstains on **all five** kept postings,
  and nothing reaches Alex.
- **The limit:** the rule cannot tell *not said because it is obvious* from *not said because it is
  unknown*. A claim that something is absent (not part-time, not contract) has no sentence to quote,
  so a quote-based rule treats it as missing evidence every time.
  - Shreyash made exactly this exception for experience in follow-up B: "Just because the company does
    not mention experience does not mean Alex is not eligible."
  - It was not made for the exclusion claims.

**The opposite limit, on the same shortlist.** The rule abstains only on *missing* evidence, never on
evidence that is present but misleading.

- The Android posting's skills claim (section 2) is not a must-have.
- Had Klaviyo written "full-time" anywhere, the agent would have sent Alex an Android/Kotlin job, and
  every must-have would have shown as "supported".
- A quote that exists is not a quote that entails.

**Measured, not adopted.** Exempting "full-time not stated" the way follow-up B exempts experience
would turn the 4 open postings into "reaches Alex", including the Android one. That is a change to the
evidence rules, so it is Shreyash's call (section 4).

## 4. Shreyash's decisions

| # | Posting, claim | Code | Claude, with its quote | Shreyash's label and why |
|---|---|---|---|---|
| 1 | Growth `7696724003`, "It is not a Director, Staff, Principal, Manager or Lead role." | supported: the title has none of the five words | **contradicted**: "You will serve as a technical leader and liaison". "The posting describes the role as a technical leadership position, so it is effectively a lead role." | *(Shreyash)* |
| 2 | Flows `8199437003`, "It asks for at least 2 of Alex's skills." | insufficient: only in the intro and the "Technologies we use" list, not under a requirements heading | **supported**: "React, TypeScript, JavaScript Python, Django, Celery". The intro also says "from the React canvas down to the Python services and APIs underneath". | *(Shreyash)* |
| 3 | Flows `8199437003`, the seniority claim | supported | **insufficient**: the posting asks the hire to act "as a technical leader" and "never explicitly says the role is not a lead role" | *(Shreyash)* |
| 4 | The evidence rules: should "full-time not stated" be an exception like follow-up B? | — | — | *(Shreyash)* |

**Claude disagreed with itself.** On the Growth posting, Claude labeled a "Technologies we use (not
exhaustive)" list *insufficient* for skills. On Flows, it labeled the same kind of list *supported*.

**An error of Claude Code's, kept as evidence.** The first Claude labeling run
(`results/claims-claude-run1-no-profile/`) was given the posting and the claims but not Alex's profile.
Claude then said a claim about "Alex's skills" could not be checked ("it does not say which skills Alex
has"), which was right. The second run added Alex's public profile (no contact details).
