# The source-grounded shortlist (Chapter 7)

*Drafted by Claude Code on 2026-11-25 from `results/shortlist-v1.{json,md}` (the code's labels, every
claim of every kept posting) and `results/claims-claude/` (Claude's independent labels). The
decisions in section 4 are Shreyash's.*

- **What was kept.** Filter v1 kept **5** of the 789 postings, all Klaviyo, all Boston. **4** are
  still open. `klaviyo:7855793003` closed after 2026-11-10. It is labeled like the others and appears
  in `results/shortlist-v1.*`, but as a closed posting it would not reach Alex.
- **The claims.** Each kept posting's justification is **nine claims**: role, department, location,
  skills, experience, seniority, full-time, paid, relocation. **Seven** are must-haves under the
  evidence rules (answer 11): role, location, experience, and the four exclusion claims (seniority,
  full-time, paid, relocation).
- **Who labeled them.**
  - The code labels every claim (`js3/claims.py`). A label is *supported* only with an exact quote
    from the posting that states the claim.
  - Claude (opus, `claude -p`, no tools) labeled the same 45 claims without seeing the code's
    labels. It gave an exact quote wherever it found one: 35 of its 45 labels have a quote, and the
    other 10 are "insufficient" with none (`js3/claim_judge.py`, 2026-11-25 17:33–17:34 EST; the first run, without Alex's profile, was at 17:31–17:32).
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

**Measured, then adopted.** Exempting "full-time not stated" the way follow-up B exempts experience
would turn the 4 open postings into "reaches Alex", including the Android one. That is a change to the
evidence rules, so it was Shreyash's call. He adopted it as B4 (section 4; FILTER.md v1.1).

## 4. Shreyash's decisions

*Shreyash's labels and words, pasted into the session on 2026-11-25 at about 18:07 EST; Claude Code changed formatting only.*

| # | Posting, claim | Code | Claude, with its quote | Shreyash's label and why |
|---|---|---|---|---|
| 1 | Growth `7696724003`, "It is not a Director, Staff, Principal, Manager or Lead role." | supported: the title has none of the five words | **contradicted**: "You will serve as a technical leader and liaison". "The posting describes the role as a technical leadership position, so it is effectively a lead role." | **Supported.** "I agree with the code. Being a technical leader does not mean the job title is Lead Engineer. Senior engineers can also guide other engineers." |
| 2 | Flows `8199437003`, "It asks for at least 2 of Alex's skills." | insufficient: only in the intro and the "Technologies we use" list, not under a requirements heading | **supported**: "React, TypeScript, JavaScript Python, Django, Celery". *(Claude Code's note, not Claude's label: the ad's intro also says "from the React canvas down to the Python services and APIs underneath".)* | **Insufficient.** "The ad mentions React and Python, but it does not clearly say that both are required skills. Mentioning a technology and asking for experience in it are two different things." |
| 3 | Flows `8199437003`, the seniority claim | supported | **insufficient**: the posting asks the hire to act "as a technical leader" and "never explicitly says the role is not a lead role" | **Supported.** "I agree with the code. Acting as a technical leader is a responsibility, not a Lead job title. My exclusion rule is based on the job title." |
| 4 | The evidence rules: should "full-time not stated" be an exception like follow-up B? | — | — | **Yes, make it an exception.** "If full-time is not stated, I want the job to pass this rule but mark employment type as "not stated." If the ad clearly says part-time, temporary, internship, unpaid or contract-only, reject it." (FILTER.md v1.1, B4) |

**Claude disagreed with itself.** On the Growth posting, Claude labeled a "Technologies we use (not
exhaustive)" list *insufficient* for skills. On Flows, it labeled the same kind of list *supported*.

**An error of Claude Code's, kept as evidence.** The first Claude labeling run
(`results/claims-claude-run1-no-profile/`) was given the posting and the claims but not Alex's profile.
Claude then said a claim about "Alex's skills" could not be checked ("it does not say which skills Alex
has"), which was right. The second run added Alex's public profile (no contact details).

**What the three labels settle.**

- Shreyash sided with the code on all three. So the code's labels stand on all 45 claims: the 42 where
  Claude agreed with the code, and these 3, which Shreyash settled. He did not check the other 42 one by
  one.
- So Claude's independent labels disagreed with the final labels on **3 of 45 claims**. Two of the
  three read a technical-leader *responsibility* as a Lead *role*, which Shreyash's title-based
  exclusion rule does not ask.

**One thing his labels show** (Claude Code's reading, not a decision):

- On Flows, Shreyash's *hand verdict* is yes ("Boston, engineering, React and Python"). His *claim
  label* for "asks for at least 2 of Alex's skills" is insufficient.
- Those two answers are consistent. A job can be worth Alex's time even when the posting does not
  entail one of the reasons the agent gives for it. That is relevance and entailment again, this time
  inside one person's labels.

## 5. The shortlist under filter v1.1

`results/shortlist-v1.1.{json,md}`; FILTER.md v1.1 adds A1, A2, A4 and the B4 exception.

- **7 postings kept**, 5 of them open: Growth, Android/Kotlin, Conversational Products, Flows, and
  Linear's Product Engineer.
  - Recommendations is kept too, but it is closed, as is Test Frameworks.
- **All 7 now answer "reaches Alex".** B4 removed the only must-have gap they had. Every quote was
  checked (0 not found).
  - That check shows each quote exists in its posting, not that it supports the claim. One does not.
    Linear's Product Engineer location claim is labeled *supported*, but its only quote from the ad is
    the pay range ("For US-based candidates, the expected cash compensation range…"). The ad's own
    location sentence, "This role is open to candidates based in North America.", is not used. The
    label is right for the wrong reason (AUDIT.md section 4, false friend 4).
  - Claude labeled only v1's 45 claims. The v1.1 shortlist's claims were not labeled independently.
  - For 6 of the 7, the full-time claim stays labeled *insufficient*, marked "not stated".
  - Linear's Product Engineer is *supported*: its board lists FullTime.
- **4 of the 7 reach Alex with their skills claim labeled *insufficient*:** Growth, Android/Kotlin,
  Recommendations and Flows. This happens because skills is not a must-have.
  - Measured, not proposed: if skills were a must-have, those 4 would become "I cannot tell" and 3
    would reach Alex (Test Frameworks, Conversational Products, Product Engineer). The source is
    `results/whatif-v1.json`, `_more.shortlist_v1_1`.
  - That change would also hold back Growth and Flows, which Shreyash wants. It is the same trade-off
    as A3.
- **The Android/Kotlin job still reaches Alex,** and Shreyash's hand label says it should not.
  - It stays because he rejected A3, the change that would have removed it along with two jobs he
    wants.
  - Its skills claim is still labeled insufficient, but skills is not a must-have, so the abstention
    rule does not catch it: the "opposite limit" of section 3, now live.
  - `tests/test_js3_filter_v11.py` records it as a known false positive.
