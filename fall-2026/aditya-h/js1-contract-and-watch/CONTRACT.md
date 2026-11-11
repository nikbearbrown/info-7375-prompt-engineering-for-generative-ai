# CONTRACT — Job-Search Agent 1

**Author:** Aditya Hasija
**Written:** 2026-10-31, before any code for this assignment was generated.
**Contract version:** v1 (rule id `title-us-v1`)

**Provenance:**
- **Decisions:** Aditya made every decision in this contract in the Claude Code chat on 2026-10-31: the board, the persona, the title families, no seniority exclusion, title-only matching, the US-location rule, the wrong versions, and the choice of failure sentence.
- **Wording:** Claude Code turned those answers into this text.
- **Board checks:** at Aditya's request, Claude Code checked two points against the live Stripe board on 2026-10-31. All 21 postings with `location.name` = "N/A" had an `offices[]` value. Matching "product manager" in the posting body would have flagged 101 postings instead of 37, pulling in Android Engineer and Customer Success Manager roles.
- **TA-style review:** at Aditya's request, Claude Code also reviewed the draft as a TA would. It tightened ambiguities a TA could not resolve by hand (how a phrase matches, missing fields, fetch errors, a corrupt state file, résumé validation, a seeded-run fallback) and added a second worked example. These were clarifications; none changes a decision above.
- **Approval:** Aditya approved this text in chat ("Approved") on 2026-10-31 at about 22:38 EDT, before any code was written.

## In

- **Board:** one Greenhouse board, `stripe`. It is fetched from `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` (public, no login, one request per run).
- **Résumé:** one JSON file in the shape of `search/examples/<persona>/resume.example.json`. The demo persona is the fictional **Maya Sehgal**. The résumé is **valid** only if it has:
  - `personal.name`, `personal.location`, `personal.email` and `personal.phone`, all non-empty strings;
  - a non-empty `experience[]` list in which every item has a non-empty `title` and `company`;
  - a `skills` object.

  An invalid résumé stops the run before any fetch.
- **State:** a local JSON state file holding `seen_ids` (every posting id seen so far), `last_run` (an ISO timestamp), and `board`.
  - If the file is missing, the run is a **baseline**.
  - If the file exists but is unreadable or malformed, the run **stops with an error**. It is never silently treated as a baseline.
- **Needs:** Python 3 (standard library only), network access to the one allow-listed host, and the `claude` CLI for the Claude judge only. The Claude judge receives the résumé fields and one posting's fields as text and has no tools. The rule judge runs fully offline.

## Out

**New** means the posting's `id` is not in `seen_ids`.
- A posting whose `updated_at` changed but whose `id` did not is **not** new.
- Ids that disappear from the board stay in `seen_ids`. If such an id comes back, it is not reported as new.

For each new posting, the agent returns two verdicts, kept separate and labeled:
1. **Rule verdict (a record):** `relevant` or `not_relevant`, computed by *The rule* below. Anyone can recompute it by hand from the saved raw response.
2. **Claude verdict (a judgment):** `relevant`, `not_relevant`, or `invalid`, from Claude under a fixed prompt contract. It is always labeled "Claude judgment (model, date)". It is never merged into the rule verdict and never presented as a fact. When the two verdicts disagree, both are shown and the disagreement is flagged, not resolved.

Each verdict carries a **justification** that names:
- at least one **résumé field** with its value (e.g. `experience[0].title = "AI Product Manager"`, `personal.location = "Boston, MA"`), and
- at least one **posting field** with its value (e.g. `title = "Product Manager, Global Payouts"`, `offices[0].name = "US"`).

**Claude output format.** Claude must return exactly one JSON object with these keys, and nothing else:
```json
{"posting_id": 123, "verdict": "relevant | not_relevant", "resume_fields": ["experience[0].title"], "posting_fields": ["title"], "reason": "..."}
```
A validator rejects any reply that:
- is not valid JSON, or has missing or extra keys;
- uses a verdict other than `relevant` or `not_relevant`;
- has a `posting_id` different from the posting asked about;
- has an empty `resume_fields` or `posting_fields`;
- cites a field path that does not resolve to a value in the résumé or the posting;
- has an empty `reason`.

A rejected reply is recorded as `invalid` along with the raw reply text. It is never coerced or repaired into a verdict.

**Every run** writes two outputs:
- a JSON run record for programs to read: board, run time, contract/rule version, postings fetched, new, relevant (per judge), skipped, the raw response path, and the state file path;
- a Markdown report for people to read, listing each new posting with both verdicts and their justifications.

**First run (baseline):** records every posting id, reports **0 new**, and produces no verdicts.

**No new postings:** reports 0 new and makes no Claude calls.

**Second run:** if the second calendar day shows no change on the board, a second run against an earlier saved raw response will also be shown, labeled **SEEDED** wherever it appears.

## Refuses

The agent will not:
1. **Fetch a host that is not allow-listed.** The allow-list is exactly `boards-api.greenhouse.io` over `https`. Any other URL raises an error before a request is made.
2. **Show a real résumé on screen or on GitHub.** The agent refuses to run unless every email in the résumé ends in `@example.com` and every phone number contains `555`. Reports show only the fields a justification cites, never the whole résumé. My real résumé stays on my machine and is never committed.
3. **Present a model's judgment as a fact.** Claude's verdict is always labeled as a judgment. Invalid Claude replies are shown as `invalid`.
4. **Update the state file from a bad fetch.** If the fetch fails (an HTTP error, a timeout, a body that is not JSON, or no `jobs` list), the run stops, saves what it received as evidence, and leaves the state file unchanged. A response with zero jobs when the state already holds ids is treated as suspect: the run reports it and does not overwrite `seen_ids`.
5. **Apply, message or log in.** It never applies to jobs, emails or messages anyone, or logs in anywhere.
6. **Call a posting "new" by any test other than id.** A posting is reported as new only if its `id` is absent from the state file.
7. **Invent postings.** Every reported posting must exist in the raw response saved for that run.

## The rule

Both checks are always evaluated, and both results appear in the justification. A new posting is **relevant** if and only if **both** pass; otherwise it is **not_relevant**.

**Phrase matching** (used in both checks): a phrase matches if it appears in the text, case-insensitive, and is not immediately preceded or followed by a letter. Under this definition "US" matches in "US-Remote" and "Remote-US", but not in "Business".

**Check 1 — Title family.** Lowercase the posting's `title` and collapse repeated whitespace. It passes if any of these phrases matches:
`product manager`, `product analyst`, `product strategy`, `product operations`, `product owner`.
- **Every seniority level counts.** New Grad, Senior, Staff and Senior Staff are all accepted. My reasoning is that New Grad PM roles often take people with 1–3 years of experience, and some companies take a "Senior PM" with about 3 years.
- **Only the title decides.** The posting body (`content`) never makes a posting relevant. Abbreviations such as "PM" do not match.
- **Phrases, not single words.** "Product Marketing Manager" and "Engineering Manager, Accounting Products" do **not** match.
- **Missing or empty title:** Check 1 fails with the reason "title missing".
- **Résumé basis:** Maya's `experience[].title` values ("AI Product Manager", "Product Manager, Payment Platform") support the product-manager family. Maya's `skills` (SQL, Power BI, funnel analytics) support product analyst and product operations. These title families are my choice for this persona.

**Check 2 — US location.** Maya's `personal.location` is "Boston, MA" (US), and Maya is open to remote work in the US. The check passes if either of these holds:
- (a) any `offices[].name` is exactly `US` or starts with `US-` (case-sensitive, as Greenhouse returns them); or
- (b) one of these markers matches in `location.name`: `US`, `USA`, `United States`, `Remote-US`, `US-Remote`, `US Remote`, `San Francisco`, `SF`, `New York`, `New-York`, `NYC`, `NY`, `Seattle`, `SEA`, `Chicago`, `Atlanta`, `Boston`.

Other location cases:
- A posting listing both US and non-US places (e.g. "New York, Toronto") passes.
- "Remote" without a country is not a US marker on its own.
- If `location.name` is "N/A" or empty, only (a) can pass. If neither (a) nor (b) passes, Check 2 fails with the reason "location not US / unknown".

**Not part of the rule:** visa sponsorship (Stripe postings rarely state it), salary, and skills overlap. Any `skills` values from the résumé that appear in the posting body are listed in the justification as context only and do not change the verdict.

**Hand-prediction examples** (both postings were on the Stripe board on 2026-10-31):
- "Product Manager, Ecosystem Risk"; `location.name` "Toronto"; `offices` ["Canada Locations"]. Check 1 passes ("product manager"). Check 2 fails: no office is `US`/`US-…`, and there is no US marker. Verdict: `not_relevant`.
- "Staff Product Manager, Connect"; `location.name` "N/A"; `offices` ["US"]. Check 1 passes ("product manager"; seniority ignored). Check 2 passes via (a), since `offices[0].name = "US"`. Verdict: `relevant`.

## Wrong versions

My tests must catch these three plausible-but-wrong implementations:

1. **Labels paired with the wrong postings.**
   - *What it does:* verdicts are computed correctly but attached by list position, so they drift onto other postings when the order changes or a posting is skipped.
   - *Why it looks right:* every posting still has a verdict and the counts are right.
   - *Test:* judge a fixture with known per-id labels, reverse the input order, and judge it again. Every verdict must match its expected label by `id` both times. A Claude reply whose `posting_id` doesn't match the posting asked about must be rejected.
2. **Justification that cites nothing.**
   - *What it does:* the verdict is right, but the justification is empty, generic ("good fit"), or names fields that don't exist.
   - *Why it looks right:* the verdict itself is correct.
   - *Test:* every rule justification must name at least one résumé field and one posting field, and each must resolve to its real value. The Claude validator must reject replies with empty field lists, made-up field paths, or an empty reason.
3. **Substring false positive.**
   - *What it does:* matches single words or loose substrings ("product" and "manager" anywhere, or "US" inside another word).
   - *Why it looks right:* every real PM posting still matches.
   - *Test:* fixed cases with expected verdicts:
     - "Product Marketing Manager" (US office) → not_relevant
     - "Engineering Manager, Accounting Products" (US office) → not_relevant
     - "Staff Product Manager, Billing" (`US` office) → relevant
     - "Product Manager: New Grad Accelerator" (`US-SF-HQ` office) → relevant
     - a PM title with `location.name` "Business Park, Dublin" and an `Ireland Locations` office → not_relevant

## What a failure looks like

- 2026-10-31: This agent has failed if the second run reports an already-seen Stripe posting id as new, or if any rule verdict differs from the verdict I get by applying the written rule by hand.

*(Sentence drafted by Claude Code as one of four options; chosen by Aditya on 2026-10-31 before any code ran.)*
