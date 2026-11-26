# Source-grounded shortlist (Phase 3)

**Filter:** v1.1.0-e (tag `js3-filter-final`, run `runs/filter/v1.1.0-e`).

**Shortlist** = keep ∪ cannot_tell (FILTER.md §5.2): 7 postings, all of them audit rows.

| audit_id | posting | title | v1.1.0-e decision |
|---|---|---|---|
| A005 | gh-stripe:8186541 | Product Manager, Connected Account Onboarding Experiences | keep |
| A010 | gh-stripe:8204227 | Product Manager - Developer Experience, Bridge | keep |
| A020 | gh-stripe:7586413 | Product Manager, Terminal Developer Experiences | keep |
| A025 | gh-stripe:7983856 | Product Manager, Treasury for Platforms | keep |
| A014 | gh-airbnb:8303742 | Product Manager, Trips | cannot_tell |
| A022 | gh-stripe:8195440 | Product Manager, Connect Growth & Monetization | cannot_tell |
| A042 | gh-stripe:8223723 | Product Manager - Issuance, Bridge | cannot_tell |

Held-out: v1.1.0-e keeps or marks cannot_tell **0** of the 20 held-out postings (count only), so
no held-out posting is on this shortlist (FILTER.md §4 amendment, `97252450`).

## 1. Claims (pending: no Claude reply yet)

- **Prompt:** `prompts/justify.v1.md`, committed before any call (`59d8fc69`).
- **Runner:** `tools/justify-shortlist.mjs`. One tool-less `claude -p` per posting: `--tools ""`,
  `--strict-mcp-config`, `--no-session-persistence`, from an empty temp folder. Requested model:
  `claude-sonnet-5-5`.
- **First attempt, 2026-11-26 00:03 UTC (2026-11-25, 19:03 ET): all 7 calls failed with no reply.**
  - The CLI returned: "You've hit your individual spend limit · run /usage-credits to ask your
    admin for a higher limit". Exit code 1; 0 tokens; no model reported.
  - The records are kept in `runs/claude/justify.v1-v1.1.0-e/failed/` (`3caf2978`).
  - Not a single claim exists yet. Nothing below is a Claude response.

When the calls succeed, `shortlist/claims-justify.v1-v1.1.0-e.csv` holds one row per claim, with:
- the quote and its mechanical check (`exact` / `not a substring` / `none`)
- Claude's proposed label and the labels the quote allows (FILTER.md §2)
- an empty `my_label`, which Aravind confirms

## 2. Relevance is not entailment (Aravind's cases; quotes are verbatim from the posting text)

**Primary: A042** (A010 has the same structure).

- **The claim** a reader, or a keyword filter, would build: "The role requires 5+ years of product
  management experience."
- **Words that match:** "5+ years in product management or a related role, with a proven record of
  delivering impactful products." It sits under the heading "Preferred Qualifications".
- **What the posting says about that heading:** "We're looking for someone who meets the minimum
  requirements to be considered for the role. If you meet these requirements, you are encouraged to
  apply. The preferred qualifications are a bonus, not a requirement."
- **Label: contradicted.** The second quote entails that the 5+ years are *not* a requirement. The
  years line is relevant to the claim (same words, same topic) but does not entail it.
- **A010 is the same:** "6–10+ years of product management experience, …" also sits under
  "Preferred Qualifications", with the same "bonus, not a requirement" sentence.
- **The filter makes this exact mistake for A010:** v1.1.0-e reads E from that preferred line
  (FILTER.md §5.4, "years under a Preferred heading are read as required").

**Secondary: A037** (not on the shortlist: v1.1.0-e rejects it; cited from the audit).

- **The claim:** "This is a core-tier PM role." It is supported by the title "Product Manager,
  Strategic Apps", which the filter scores as core (T = 1).
- **The body:** "We’re looking for a Staff Product Manager to set the strategy and lead execution
  for Strategic Apps." and "8+ years of relevant product-management, engineering, or equivalent
  experience, …"
- **Label against the full posting: contradicted.** The title words are relevant, but the body says
  the level is Staff, which is adjacent in the filter's own tiers.

## 3. The abstention rule and its limits

**The rule** (FILTER.md §1.3, §2.3) answers `cannot_tell` only when an unknown component could flip
the decision (lo < 0.80 ≤ hi), or when the title or text is missing.

| Case | What happened | What it shows |
|---|---|---|
| **(a) Confidently wrong: A010 in `bdc146c8`** (v1.1.0-a) | "6–10+ years …" was read as 10+, so E = 0, lo = hi = 0.75, and the result was **reject**. No abstention. | The rule abstains only on values it knows are missing. A value it extracted wrongly is treated as known, so the answer is confident and wrong. Fixed in v1.1.0-d (A010 is now keep), but the mechanism stays: any misread is invisible to the rule. |
| **(b) Abstained, but the value was stated: A022** (v1.1.0-e) | "More than three years of product management experience" is under "Minimum requirements". "three" is spelled out, so the years pattern finds nothing: E unknown, lo 0.75, hi 1.0, **cannot_tell**. | The posting *does* state the requirement (3 years: E would be 1.0, so keep). The abstention comes from the parser, not the posting. |
| **(c) Abstained correctly: A014** (v1.1.0-e) | The normalized text has Airbnb's intro and pay boilerplate but no role description and no years (FILTER.md §5.4: 1 of 203 Airbnb postings). E unknown, lo 0.65, hi 0.9, **cannot_tell**. Aravind's recheck: cannot_tell. | Here "cannot tell" is right: the posting really does not say. |

**(b) against (c):** both produce exactly the same signal (E unknown, lo < 0.80 ≤ hi). The rule
cannot tell **"not stated"** (A014) from **"stated but unreadable"** (A022). Telling them apart would
need a second check, for example "a requirements heading exists, but no years were parsed under it".
That check was not built (the filter is frozen).

A042 is a fourth variant: the years are stated ("5+ years in product management …") but not in a
sentence containing "experience", so they are not read. It also abstains, for a parser reason.
