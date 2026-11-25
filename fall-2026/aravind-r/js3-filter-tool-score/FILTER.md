# FILTER — Job-Search Agent 3

**Version 1.0.0 — 2026-11-25. Written before any filter or scorer code.**

This is the gate. The filter is this document: the machine-readable block in §6 is what the
code loads (`src/spec.mjs`). No weight, word, or threshold lives anywhere else. To change the
filter: edit this file, bump the version, and log the change in §9 with a before/after
measurement.

Persona: Maya Sehgal, fictional (`persona/persona-prefs.json`, inherited from JS1/JS2):
- `years_pm`: 2
- locations: San Francisco, Los Angeles, San Jose, Remote
- needs sponsorship
- domains: payments, fintech, data, e-commerce, mobile

**Tags.**
- **[DECIDED 2026-11-25]**: a decision Aravind made at Checkpoint 0.
- **[DECIDED 2026-11-25, hand-set]**: drafted by Claude Code and accepted by Aravind at
  Checkpoint 1 as hand-set v1 values. None of them was fitted on labels.
- **[SUGGESTED]**: a note that is not yet a rule.

**What was looked at before drafting.**
- Corpus-level term and field counts over all 1,064 postings in the snapshot. No labels and
  no per-posting verdicts.
- The 36 Stripe titles containing "Product Manager".
- At Aravind's request, a throwaway count of keep / reject / cannot_tell under this exact
  rule, before any code was committed (§5.1).
- No label sheet existed yet. Where a count shaped a rule, it is quoted next to the rule.

---

## 1. What makes a posting relevant

A posting is worth Maya's time when it is:
- a product-management role
- that she can do at her level (2 years as a PM)
- in a place she can work
- from an employer that does not rule out sponsorship
- ideally in one of her domains.

### 1.1 Hard vetoes (score = 0; the reason is quoted) [DECIDED 2026-11-25]

| Rule | Match | Reasoning |
|---|---|---|
| V1 Sponsorship | If `needs_sponsorship` is true: the text contains any of `unable to sponsor`, `not able to sponsor`, `will not sponsor`, `does not sponsor`, `cannot sponsor`, `without sponsorship`, `sponsorship is not available` | Maya cannot take a job that refuses sponsorship, however well it scores otherwise. Phrase list inherited from JS1 Gate 5. |
| V2 Citizenship / clearance | The text contains any of `security clearance`, `u.s. citizen`, `us citizenship`, `citizenship is required` | A requirement she cannot meet. Phrase list inherited from JS1 Gate 6. |

A veto records `{rule, phrase, quote}`. The quote is the sentence of the normalized text that
contains the phrase.

### 1.2 Weighted components, each a value in [0, 1] [DECIDED 2026-11-25, hand-set]

#### Title tier (T)

Take the title up to the first `,`, ` - `, `(`, or `:`. Trim it and collapse whitespace.

| Tier | Value | Titles (exact match on the prefix, case-insensitive) | Reasoning |
|---|---|---|---|
| core | 1.0 | Product Manager, Senior Product Manager, Sr. Product Manager, AI Product Manager, Technical Product Manager, Web3 Product Manager, Technical Program Manager, Senior Technical Program Manager | The JS1 Gate 1 list: titles at Maya's level, already accepted. |
| adjacent | 0.5 | Staff Product Manager, Senior Staff Product Manager, Principal Product Manager, Group Product Manager, Lead Product Manager, Product Lead, Program Manager, Product Owner, Product Operations Manager | PM-family roles that JS1 failed outright. They get partial credit so that a strong one can surface, and the audit can show whether that is wrong. |
| none | 0.0 | everything else | Role words are what make a posting a PM job. Topic words alone must never be enough (W4). |

- **Junior override.** T = 0 if the title contains `Associate`, `APM`, `Intern`, or
  `New Grad` as a whole word.
  - Reasoning: "Product Manager: New Grad Accelerator" is in the Stripe snapshot, and it is
    below Maya's level.
  - Inherited from JS1 Gate 2, including its whole-word revision ("Intern" matched
    "International" in 8 JS1 titles).
- **`:` is a cut character** so that "Product Manager: New Grad Accelerator" has the prefix
  "Product Manager". The junior override still sets T to 0.

#### Experience fit (E)

Take the first `N+ years`, `N-M years`, or `N or more years` phrase in a sentence that contains
`experience`, and use its lower bound N. This extraction is inherited from JS1 Gate 3.

| Case | E | Reasoning |
|---|---|---|
| N ≤ years_pm + 1 (= 3) | 1.0 | Within reach. The +1 slack is the inherited JS1 ceiling. |
| N = years_pm + 2 (= 4) | 0.5 | A stretch, not a no. New in JS3. |
| N ≥ years_pm + 3 | 0.0 | Out of reach. |
| any range with upper bound ≤ 2 (e.g. "0–2 years") | 0.0 | Junior. Inherited from JS1 Gate 2. |
| no phrase found | **unknown** | The posting does not say. That is neither a match nor a miss (§2.3). |

#### Topic words (P)

Count the distinct `topic.terms` that appear as whole words (case-insensitive) in the title,
department, or text. P = min(1, distinct / 2).

- The terms are Maya's `domains` plus the spelling variant `ecommerce`.
  - Reasoning: in JS1, domains were only a citation. Here they help rank PM roles, but they can
    never lift a non-PM title over the threshold.
- Distinct terms only, capped at 2. Repeating a word must not raise the score (W3).
- **[SUGGESTED] note: near-universal words carry almost no signal.**
  - The counts: `payments` appears in 746 of 776 Stripe postings, `data` in 402 of 776, and
    `training` (not a topic term) in 172 of 203 Airbnb postings.
  - A term that appears in nearly every posting from a board can't separate that board's
    postings. As written, `payments` adds almost nothing on Stripe. Most likely it comes from
    company boilerplate, not from the role.
  - **No rule change in v1.** The reject audit decides. Aravind names a false friend only from
    a posting judged by hand, never from these counts.

#### Location (L)

| Case | L | Reasoning |
|---|---|---|
| A `locations` entry is a case-insensitive substring of `location`, or an alias appears as a whole word | 1.0 | She can work there. |
| no match | 0.0 | Not a place on her list. |
| `location` missing or empty | **unknown** | The posting does not say (§2.3). |

- **Aliases.**
  - `SF` and `Bay Area` mean San Francisco; `LA` means Los Angeles.
  - The snapshot has locations such as "SF, SEA, NY, Remote-US". The JS1 substring rule did
    not read those as San Francisco; they matched only through "Remote".
- **Audit target: `Remote` matching outside the US.** `Remote` also matches "EMEA, or Remote"
  and "Remote (East Coast)". It stays as written for v1. Whether remote work outside the US
  counts for Maya is a question for the audit.

### 1.3 Score and decision [DECIDED 2026-11-25; numbers hand-set]

```
score = wT·T + wP·P + wE·E + wL·L          (all weights hand-set v1, sum = 1)
```

- **Veto** → score 0, decision `reject`, reason quoted.
- Otherwise compute **lo** (unknown components set to 0) and **hi** (unknown components set to
  1):
  - hi < threshold → `reject`
  - lo ≥ threshold → `keep`
  - otherwise → `cannot_tell`: the decision depends on something the posting does not state.
- **The displayed score** sets each unknown to its `impute` value (E 0.5, L 0). It is used only
  for ordering and never decides anything.
- **Ranking:** `keep` by score, highest first; then `cannot_tell`; then `reject`. Ties break by
  `board`, then `id`, ascending.
- **Near-threshold band** for the audit: |score − threshold| ≤ 0.10.
- **Rounding:** lo, hi, and score are rounded to 6 decimals before comparing, so that
  0.4 + 0.25 + 0.15 does not fall to 0.79999… (W7).

**Why these numbers (hand-set v1):** wT 0.40, wL 0.25, wE 0.25, wP 0.10, threshold 0.80.
- **Title is necessary.** With T = 0 the maximum is 0.60, below 0.80 (W4).
- **Location and experience can't be bought back with title + topic** (W13):
  - core, L = 0, E = 1, P = 1 → 0.75 → reject
  - core, L = 1, E = 0, P = 1 → 0.75 → reject
  - core, L = 1, E = 0.5, P = 0 → 0.775 → reject
  - core, L = 1, E = 0.5, P = 0.5 → 0.825 → keep
  - core, L = 1, E = 1 → 0.90 or more → keep
- **Unknown experience** with core + L = 1: lo ≤ 0.75 and hi ≥ 0.90, so the result is always
  `cannot_tell`.
- **Threshold changed from 0.70 to 0.80** (Aravind, Checkpoint 1, before commit).
  - At 0.70, a core-PM posting with location = 0 or experience = 0 scored 0.75 and passed.
  - That would have silently loosened JS1's location and experience-ceiling gates.
  - The origin stays hand-set v1.

---

## 2. Evidence rules (for the shortlist) [DECIDED 2026-11-25, hand-set]

Every claim in a shortlist justification is labeled against **the posting's own normalized
text** (§3) and nothing else.

### 2.1 Labels

| Label | When |
|---|---|
| **supported** | A quoted span is an exact substring of the normalized text, and the span alone entails the claim. A reader given only the span would agree. |
| **contradicted** | An exact quoted span entails that the claim is false. Example: the claim "fits her experience" against the span "8+ years of product management experience". |
| **insufficient** | Any of: no exact span; the span is only on topic (shares words, does not entail); or the claim is about something a posting cannot establish, such as whether Maya would enjoy it, team quality, the company's reputation, or whether she would be hired. |

- **Mechanical precondition.** A quote that is not an exact substring cannot support or
  contradict anything, so the claim is `insufficient` (W10).
- The code checks substrings. Aravind confirms entailment by hand.
- Labels proposed by the code or by Claude stay proposals until Aravind confirms them.

**Relevance is not entailment.** A posting can match the filter's words (e.g. "payments")
without supporting a claim built on them (e.g. "the role works on payments"). Boilerplate about
the company is not a statement about the role.

### 2.2 Labels attach to claims, not to postings

- One shortlisted posting can carry supported, contradicted, and insufficient claims at once.
- A contradicted claim about a decisive component (title, experience, location, or a veto) is
  a filter error, and it goes into the audit.

### 2.3 When the agent must say "I cannot tell"

1. When the decision depends on an unknown component: `lo < threshold ≤ hi` (§1.3).
2. When the title is missing, or the normalized text is under **200 characters**.
   - Nothing is scored except vetoes, which still apply if their phrase is present.
3. **For a claim**, when the posting does not state the fact the claim needs.
   - The claim is `insufficient`, and the justification says "the posting does not say".
   - It must never fill the gap from outside knowledge about the company.

`cannot_tell` is reported as its own count. It is never folded into `reject` or `keep`.

---

## 3. Expected sources and fields [DECIDED 2026-11-25; mappings hand-set]

- **Data:** the frozen JS2 snapshot `data/raw/20261110T225032086Z-post-patch-2/`, fetched
  2026-11-10. `data/MANIFEST.json` holds the SHA-256 of each file.
- **Nothing is fetched for JS3.** The JS2 allow-list (`boards-api.greenhouse.io`,
  `api.lever.co`) is unchanged and unused.

| Board | System | Expected | Raw count (JS2 trace) |
|---|---|---|---|
| gh-stripe | Greenhouse | `{jobs: [...]}` | 776 |
| gh-airbnb | Greenhouse | `{jobs: [...]}` | 203 |
| lv-spotify | Lever | bare array | 85 |
| gh-broken | Greenhouse | **unavailable** (404 body) | none |

### 3.1 Normalized schema

Each posting is normalized to exactly `{id, board, title, location, department, text, url}`.

| Field | Greenhouse | Lever |
|---|---|---|
| id | `String(id)` | `id` (a UUID string) |
| board | the board id | the board id |
| title | `title`, trimmed | `text`, trimmed |
| location | `location.name` | `categories.allLocations` joined with `"; "` if non-empty, else `categories.location` |
| department | `departments[].name` joined with `"; "` | `categories.department` |
| text | `content`, HTML decoded and tags stripped (JS2 `src/text.mjs`, inherited) | `descriptionPlain` + each list's `text` and stripped `content` + `additionalPlain`, separated by newlines |
| url | `absolute_url` | `hostedUrl` |

- `applyUrl` is **never** stored, logged, or returned by the tool [DECIDED 2026-11-25].
- The normalized object has exactly these seven keys (W9).

### 3.2 When something is missing

| Missing | Behavior |
|---|---|
| raw file absent, not JSON, or the wrong shape (e.g. the 404 body for gh-broken) | Board `unavailable` with a reason. Counts are `null`, never `0`. Reported as "board not seen", never "0 relevant" (W6). |
| `id` null or absent | Posting skipped and counted in `skipped.null_id`, with a warning. The run continues [DECIDED 2026-11-25]. JS2 ended the whole run with exit 12 (§8). |
| duplicate `id` within one board | Board `unavailable: malformed`. Inherited from JS2 (`42c9bc52`). |
| `title` missing or empty | `cannot_tell` (§2.3 item 2). |
| `location` missing or empty | L unknown. `cannot_tell` only if L could flip the decision. |
| `department` missing | Topic words come from title and text only. No penalty. |
| text missing or under 200 characters | `cannot_tell` (§2.3 item 2). Vetoes are still checked. |
| `url` missing | Still scored. `url: null` is flagged in the shortlist as "no link". |

Corpus check (2026-11-25, counts only): all three real boards have 0 missing locations, 0
missing departments, 0 texts under 200 characters, and 0 null ids. So only synthetic test
fixtures exercise the missing-field rules, and the tests say so.

---

## 4. Claude in the scorer [DECIDED 2026-11-25]

### How it is called

- `claude -p` runs **only** from `src/judge.mjs`, which only the scorer module calls.
- It runs only as `--tools '' --no-session-persistence`, from a fresh, empty temporary folder.
- Every response is saved under `runs/claude/` with:
  - UTC time
  - requested model and the models reported
  - session id
  - prompt file and prompt SHA-256
- The MCP server makes no network calls. It never imports `src/judge.mjs` or
  `node:child_process` (W12).

### What Claude decides: nothing numeric (Option A)

- The score and the keep / reject / cannot_tell decision are fully deterministic (§1.3).
- Claude only writes the shortlist justification: atomic claims, each with a quoted span
  (`prompts/justify.v1.md`). The claims are labeled under §2, and the output is labeled
  JUDGMENT.
- Rejected: Option B, where Claude would judge the `cannot_tell` postings. It would let a
  JUDGMENT change a decision.

### Phase 5 uses two metrics, both on held-out labels only

| Change to | Measured on |
|---|---|
| the filter file (§6) | held-out **relevance** labels (Aravind's `my_label`) |
| the prompt or the context given to Claude | held-out **claim** labels: the share of claims supported, contradicted, insufficient, or with a non-verbatim quote |

Under Option A, a prompt or context change cannot move relevance precision or recall.

---

## 5. Wrong versions (each must make at least one test fail) [DECIDED 2026-11-25, hand-set]

| # | Plausible-but-wrong version | Why someone would write it | Test |
|---|---|---|---|
| W1 | Substring matching instead of whole words, for title, topic, and alias terms | `text.includes(term)` | `data` must not match "database"; `Intern` must not match "International"; `LA` must not match "Lagos" |
| W2 | A veto treated as a negative weight | "just subtract a lot" | A no-sponsorship posting with T = E = L = P = 1 scores exactly 0 and is rejected, with the phrase quoted |
| W3 | Topic score counts occurrences | "more mentions = more relevant" | "payments" ×20 gives the same P as ×1; two distinct terms beat one repeated |
| W4 | Weights that let topic + location + experience carry a non-PM title | tuning on keyword-rich postings | Under the §6 spec, max score with T = 0 < threshold; a perfect non-PM fixture is rejected |
| W5 | A missing field treated as a match, or an imputed value deciding | defaulting to "fits" | Missing location that could flip the decision → `cannot_tell`, not `keep`; the displayed score never decides |
| W6 | An unavailable board reported as 0 postings or 0 relevant | `jobs ?? []` | The gh-broken 404 body → `unavailable` with null counts |
| W7 | `>` instead of `≥` at the threshold | off-by-one | A score exactly at the threshold is `keep` |
| W8 | Ranking that is unstable, or mixes `cannot_tell` or vetoed postings in with the kept ones | sorting by score alone | Order is keep (score descending) → cannot_tell → reject; ties by board, then id |
| W9 | The normalizer leaks `applyUrl` or extra keys, or crashes on a null id | spreading the raw object | Exactly 7 keys; a null id is skipped and counted, not thrown |
| W10 | A non-verbatim quote counted as support | trusting a paraphrase | A non-substring quote can only be `insufficient` |
| W11 | Weights or terms hard-coded instead of read from this file | convenience | Behavior follows the spec object; no §6 number appears in `src/filter.mjs` |
| W12 | The judge reachable from the tool server, or `child_process` imported elsewhere | reuse | Only `src/judge.mjs` imports `node:child_process`; Phase 4 adds the server's import-graph check |
| W13 | A posting that fully fails location or fully fails experience still passes on title + topic | weights tuned so a strong title "wins" | Exact cases: core+L0+E1+P1 → reject; core+L1+E0+P1 → reject; core+L1+E0.5+P0 → reject; core+L1+E0.5+P0.5 → keep |

### 5.1 Known limit: the v1 rule on the snapshot (counts only, no labels)

**How it was produced.** A throwaway script that is not committed, run on 2026-11-25 before any
filter code was written, at Aravind's request. It follows this document with threshold 0.80.
The committed implementation re-counts in Phase 2, and any difference is recorded in §9.

| Board | Postings | keep | cannot_tell | reject (of which veto) | Title T > 0 | Experience unknown (all titles) |
|---|---|---|---|---|---|---|
| gh-stripe | 776 | 0 | 2 | 774 (0) | 53 | 149 |
| gh-airbnb | 203 | 0 | 1 | 202 (0) | 7 | 34 |
| lv-spotify | 85 | 0 | 0 | 85 (0) | 11 | 44 |
| **total** | **1,064** | **0** | **3** | **1,061 (0)** | **71** | **227** |

**What this shows.**
- **cannot_tell did not flood.** There were 3 of 1,064, and all 3 were cannot_tell because
  experience was unknown.
  - Most postings with unknown experience are rejected anyway, because hi < 0.80 whenever
    T = 0 (max 0.60) or L = 0.
- **The v1 shortlist is empty.**
  - Of the 71 postings with T > 0, 54 state an experience requirement that sets E = 0
    (N ≥ 5, or a junior range).
  - 14 have unknown experience, and 11 of those also have L = 0.
  - That leaves 2 with E = 0.5 and 1 with E = 1, all three with L = 0.
- **This is not a rate**, and it doesn't say whether the 3 cannot_tell or the 1,061 rejects
  are right. Only the audit can.
- **Counterexample for Phase 3.**
  - The abstention rule abstains only when an unknown *could* flip the decision.
  - A posting whose experience requirement is stated in a form the regex misses ("five
    years", "a few years") is treated as unknown or misread, and then confidently decided.
  - Also, the rule never abstains on a stated value that it extracted wrongly.

### 5.2 Shortlist definition [DECIDED 2026-11-25, written before any audit verdict]

- **shortlist = keep ∪ cannot_tell.**
  - A `cannot_tell` posting reaches Aravind for a human decision. It is not dropped.
- **Phase 3 runs on this set.** Under v1.0.0 it is the 3 `cannot_tell` postings (§5.1).
  - If v1.1 changes the set, Phase 3 uses v1.1, and the Phase 3 document says which version
    it used.
- **No rule change may be made in order to grow the shortlist.**
- **Every v1.1 change must cite the audit rows** (`audit_id`) that motivated it, in §9.

**Amendment, 2026-11-25** (after `e0d80ff0`, before any audit verdict) [DECIDED 2026-11-25]:
- **Evidence for v1.1** is audit rows **or** a committed measurement artifact.
- **Changes that can only remove postings from the shortlist** (veto additions) may cite
  `e0d80ff0` (`audit/sponsor-visa-hits.md`).
- **Changes that can add postings to the shortlist** still require audit rows.
- **Planned for v1.1, not applied.** It is held until all audit verdicts are in, so that the
  audit measures v1.0.0.
  - Add exactly the two missed phrasings from `e0d80ff0` to `vetoes.sponsorship`:
    - `no visa/relocation support` (gh-airbnb:8299386)
    - `unable to provide … visa sponsorship` (lv-spotify:a3c9129a-…). This one is a bounded
      pattern: "unable to provide", then a few words, then "visa sponsorship".
  - A test must show the pattern does **not** match "executive sponsor", "financial sponsor",
    event sponsorship, or "Visa and Mastercard".
  - Expected effect: 0 decisions change (both postings already score 0). The CHANGELOG records
    the counts before and after.
  - **Rejected alternative:** a broad `sponsor` / `visa` match. In `e0d80ff0`, 29 of the 31
    distinct matching lines were false friends (executive or financial sponsors, event
    sponsorship, Visa the card network).

---

## 6. The filter spec (the code loads this block) [DECIDED 2026-11-25, hand-set v1]

Reason line for `threshold` 0.80: at 0.70, a core-PM posting with location = 0 or
experience = 0 scored 0.75 and passed, silently loosening JS1's location and experience-ceiling
gates (Aravind, Checkpoint 1). Origin: hand-set v1.

```json filter-spec
{
  "version": "1.0.0",
  "title": {
    "cut_chars": [",", " - ", "(", ":"],
    "tiers": {
      "core": { "value": 1.0, "titles": ["Product Manager", "Senior Product Manager", "Sr. Product Manager", "AI Product Manager", "Technical Product Manager", "Web3 Product Manager", "Technical Program Manager", "Senior Technical Program Manager"] },
      "adjacent": { "value": 0.5, "titles": ["Staff Product Manager", "Senior Staff Product Manager", "Principal Product Manager", "Group Product Manager", "Lead Product Manager", "Product Lead", "Program Manager", "Product Owner", "Product Operations Manager"] }
    },
    "junior_terms": ["Associate", "APM", "Intern", "New Grad"]
  },
  "topic": { "terms": ["payments", "fintech", "data", "e-commerce", "ecommerce", "mobile"], "saturate_at": 2 },
  "experience": { "slack": 1, "stretch": 2, "stretch_value": 0.5, "junior_upper_max": 2, "impute": 0.5 },
  "location": { "aliases": { "sf": "San Francisco", "bay area": "San Francisco", "la": "Los Angeles" }, "impute": 0.0 },
  "vetoes": {
    "sponsorship": ["unable to sponsor", "not able to sponsor", "will not sponsor", "does not sponsor", "cannot sponsor", "without sponsorship", "sponsorship is not available"],
    "citizenship": ["security clearance", "u.s. citizen", "us citizenship", "citizenship is required"]
  },
  "weights": { "title": 0.40, "location": 0.25, "experience": 0.25, "topic": 0.10 },
  "threshold": 0.80,
  "near_band": 0.10,
  "min_text_chars": 200
}
```

---

## 7. Labels and held-out [DECIDED 2026-11-25]

- JS1's 20 hand labels (2026-10-31) are inherited context only. They are not the eval set.
- **The new sheet:** about 40 postings, seeded (seed recorded), stratified into dev 20 and
  held-out 20.
  - Each half has at least 5 likely positives, drawn from postings with PM or product titles.
  - **The sample is enriched**, so precision and recall on it are not population rates.
- **Held-out is frozen first.** Its ids and a SHA-256 are written to a file and committed
  before any rule change. Held-out results are never shown during tuning.
- **The Phase 2 audit sample is separate from both.** If audit findings drive a rule change,
  that counts as dev use, and the changelog says so.

## 8. Decisions (dated)

- **2026-11-25 — Claude re-enabled in the scorer only.**
  - This reverses JS2 GATE.md's 2026-11-10 decision: "Disable the JS1 external judge in JS2
    because its CLI subprocess bypasses the network policy".
  - Reason: Chapter 9 needs a Claude prompt as a measurable object in the scorer.
  - The risk JS2 named, an unpoliced subprocess, is limited but not removed. The call is
    tool-less, keeps no session, runs in an empty temporary folder, and is reachable only from
    `src/judge.mjs`.
  - The `claude` CLI still makes its own network call to Anthropic. That host is outside the
    agent's allow-list, and the call is accepted as the price of a Claude judgment.
  - JS2's WV12 is untouched: JS3 does not modify JS2, and JS3 has no `loop.mjs`.
- **2026-11-25 — Null raw id: skip and count.** For JS3's normalizer, this replaces JS2's
  run-ending `error` (exit 12).
- **2026-11-25 — Frozen snapshot, no fetch.** The data is from 2026-11-10.
- **2026-11-25 — Option A for Claude** (§4).
- **2026-11-25 — Threshold 0.80** (§6 reason line).

## 9. CHANGELOG

| Version | Date | Change | Why | Measured before → after (set: dev/audit) |
|---|---|---|---|---|
| 1.0.0 | 2026-11-25 | First committed version. The draft had threshold 0.70; it was set to 0.80 at Checkpoint 1, before commit, and W13 was added. | §6 reason line | No labels yet. Counts only (§5.1): keep 0 / cannot_tell 3 / reject 1,061 at 0.80 |
