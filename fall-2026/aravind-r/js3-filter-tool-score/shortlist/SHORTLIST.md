# Source-grounded shortlist (Phase 3)

**Filter:** v1.1.0-e (tag `js3-filter-final`, run `runs/filter/v1.1.0-e`).

**Shortlist** = keep ∪ cannot_tell (FILTER.md §5.2): 7 postings, all of them audit rows.

**Held-out:** v1.1.0-e keeps or marks cannot_tell **0** of the 20 held-out postings (count only), so
no held-out posting is on this list (FILTER.md §4 amendment, `97252450`).

| audit_id | posting | title | v1.1.0-e decision |
|---|---|---|---|
| A005 | gh-stripe:8186541 | Product Manager, Connected Account Onboarding Experiences | keep |
| A010 | gh-stripe:8204227 | Product Manager - Developer Experience, Bridge | keep |
| A020 | gh-stripe:7586413 | Product Manager, Terminal Developer Experiences | keep |
| A025 | gh-stripe:7983856 | Product Manager, Treasury for Platforms | keep |
| A014 | gh-airbnb:8303742 | Product Manager, Trips | cannot_tell |
| A022 | gh-stripe:8195440 | Product Manager, Connect Growth & Monetization | cannot_tell |
| A042 | gh-stripe:8223723 | Product Manager - Issuance, Bridge | cannot_tell |

## 1. How the claims were obtained (a deviation)

- **Intended:** one tool-less `claude -p` call per posting. All 7 failed with no reply because of
  the spend limit (2026-11-26 00:03 UTC; `runs/claude/justify.v1-v1.1.0-e/failed/`, `3caf2978`).
- **Used:** the manual route (FILTER.md §4 deviation).
  - The 7 rendered prompts are byte-identical to the failed calls (`manual/prompts/`).
  - Aravind pasted each one into **claude.ai, web, incognito chat**. The model shown in the selector
    was **Claude Opus 5.5** (self-reported). The replies were obtained on **2026-11-25**.
  - The raw replies (`manual/responses/`) were imported by `tools/import-manual.mjs` through the
    same validator. Records: `runs/claude/justify.v1-v1.1.0-e/A*.json`, with `manual_paste: true` and
    the SHA-256 of each prompt and reply.
- **Filing error.** Two replies were first saved under the wrong filenames. Aravind caught it and
  renamed them without editing the content (FRICTIONAL.md). The importer now rejects a reply whose
  `posting_id` doesn't match its file.
- **Result:** all 7 replies were valid JSON, with 54 claims. Every non-null quote is an exact
  substring of the posting body (37 quotes; 17 claims abstained with `quote: null`).

## 2. The claim table

- `shortlist/claims-justify.v1-v1.1.0-e.csv`: Claude's proposals.
- `shortlist/claims-confirmed-justify.v1-v1.1.0-e.csv`: Aravind's confirmed labels, built by
  `tools/confirm-claims.mjs` from `shortlist/my-labels.json`. Every confirmed supported or
  contradicted label was re-checked against an exact quote.

| | supported | contradicted | insufficient |
|---|---|---|---|
| Claude proposed | 35 | 0 | 19 (17 abstentions) |
| **Aravind confirmed** | **37** | **6** | **11** |

**Aravind's labels differ from Claude's on 8 of 54 claims.** The other 46 take Claude's proposed label.

| Claims | Claude | Aravind | Span Aravind cites |
|---|---|---|---|
| A005.5, A010.6, A020.5, A022.5, A025.5, A042.6: "The posting does not state a work location or remote option in its text." | insufficient (abstain) | **contradicted** | the board location field, e.g. "San Francisco, Seattle" (A020), "San Francisco Or New York" (A010, A042). The field counts as posting text under the FILTER.md §2.1 amendment, made **after** seeing these replies. |
| A010.4, A042.4: "The posting states that its preferred qualifications, the section where the 6–10+ / 5+ years line appears, are a bonus rather than a requirement." | insufficient | **supported** | "Preferred Qualifications" (the heading directly above the years line), together with Claude's quote "The preferred qualifications are a bonus, not a requirement." |

**Per posting (confirmed):**

| Posting | claims | supported | contradicted | insufficient | judgment | abstained |
|---|---|---|---|---|---|---|
| A005 | 8 | 6 | 1 | 1 | 5 | 2 |
| A010 | 8 | 5 | 1 | 2 | 6 | 3 |
| A020 | 8 | 6 | 1 | 1 | 6 | 2 |
| A025 | 7 | 5 | 1 | 1 | 5 | 2 |
| A014 | 7 | 4 | 0 | 3 | 5 | 3 |
| A022 | 8 | 6 | 1 | 1 | 6 | 2 |
| A042 | 8 | 5 | 1 | 2 | 6 | 3 |

**Judgments.** 39 of the 54 claims are marked `judgment`, not `quoted`.
- The domain-fit claims are inferences, not entailments. Example, A020.8: "The role's surface
  includes iOS and Android client SDKs, which touches the job seeker's mobile domain", quoting "the
  client SDKs (JavaScript, iOS, Android, React Native, .NET, and Java)".
- They are labeled supported **only as JUDGMENT**: the quote supports the fact the inference starts
  from, not the inference.
- The same goes for the "within her stretch maximum" claims (A005.4, A020.4, A025.4), which compare a
  quoted number with the persona.

## 3. Relevance is not entailment

**Main case: the filter made the entailment error, and the justification didn't (A010, A042).**

- **What the filter did:** under v1.1.0-e it reads E from A010's years line, "6–10+ years of product
  management experience, …". That line sits under the heading "Preferred Qualifications", so the
  filter treats a preferred qualification as a requirement. A042 has the same structure ("5+ years in
  product management or a related role, …"); the filter doesn't read that line only because it lacks
  the word "experience" (FILTER.md §5.4).
- **The claim "The role requires 6+ / 5+ years"** matches the words, but the posting's own text
  contradicts it: "We're looking for someone who meets the minimum requirements to be considered for
  the role. If you meet these requirements, you are encouraged to apply. The preferred qualifications
  are a bonus, not a requirement."
- **Claude avoided this claim.**
  - It wrote "lists 6–10+ / 5+ years … as a qualification" (A010.3, A042.3: supported).
  - It claimed that the section is a bonus (A010.4, A042.4: supported by Aravind with the heading).
  - It abstained on minimum years (A010.5, A042.5: "The posting does not state a minimum required
    number of years of experience").
- **So relevance and entailment came apart at the filter.** The years line is relevant to
  "experience fit", but it does not entail a requirement.

**The reverse: entailed, but not relevant (A005.7).**

- The claim "The employer describes itself as a financial infrastructure platform." is entailed by its
  quote, "Stripe is a financial infrastructure platform for businesses." It is labeled supported.
- But the quote is Stripe's company boilerplate, which appears across Stripe postings. It says
  something true about Stripe and nothing about this role.
- A supported claim is not therefore evidence for relevance. This is the same mechanism as the
  boilerplate "payments" known limit (159 reworded Stripe intros; RESULTS.md).

**Secondary: A037 (from the audit; not on the shortlist because v1.1.0-e rejects it).**

- The claim "This is a core-tier PM role" is supported by the title, "Product Manager, Strategic Apps",
  which the filter scores as core (T = 1).
- The body contradicts it: "We’re looking for a Staff Product Manager to set the strategy and lead
  execution for Strategic Apps." That level is adjacent in the filter's own tiers.

## 4. The abstention rule and its limits

**The filter's rule** (FILTER.md §1.3, §2.3) answers `cannot_tell` only when an unknown component
could flip the decision (lo < 0.80 ≤ hi), or when the title or text is missing.

| Case | What happened | What it shows |
|---|---|---|
| **(a) Confidently wrong: A010 in `bdc146c8`** (v1.1.0-a) | "6–10+ years …" was read as 10+, so E = 0 and lo = hi = 0.75: **reject**, no abstention. | A value the rule extracted wrongly is treated as known. Fixed in v1.1.0-d, but the mechanism remains. |
| **(b) Abstained, but the value was stated: A022** (v1.1.0-e) | "More than three years of product management experience" is under "Minimum requirements". "three" is spelled out, so no years were parsed: E unknown, lo 0.75, hi 1.0, **cannot_tell**. | The posting states the requirement. Claude read it (A022.3, A022.4: supported). The abstention comes from the parser. |
| **(c) Abstained correctly: A014** (v1.1.0-e) | No role description and no years in the text (FILTER.md §5.4): E unknown, lo 0.65, hi 0.9, **cannot_tell**. Aravind's recheck: cannot_tell. Claude: A014.4, A014.5 abstain. | Here "cannot tell" is right: the posting really doesn't say. |
| **(d) Claude abstained though the evidence was in a field it was given: location, 6 Stripe replies** | The prompt's POSTING block includes `"location"` (e.g. "San Francisco, Seattle"), but Claude wrote "The posting does not state a work location … in its text" (6 claims). | The *justification's* abstention rule has the same limit as the filter's: it abstained on information it held but read as out of scope. The prompt said "the posting's text", and Claude took that to mean the body. Aravind's label: contradicted (§2). |

- **(b) against (c):** both produce the same signal (E unknown, lo < 0.80 ≤ hi). The filter's rule
  can't tell **"not stated"** (A014) from **"stated but unreadable"** (A022).
- **(d):** a third failure: **"stated in a structured field, but treated as not stated."**
- **A042** is a further parser variant: its years are stated, but not in a sentence containing
  "experience", so they are never read.
