# CONTRACT.md — Job-Search Agent 1: The Contract and the Watch (amended for JS2 in v0.5)

**Author:** Prasad Shinde  
**Date written (before any run):** 2026-10-25  
**Version:** v0.8 — 2026-11-07. Amends v0.7 (JS2-CP5b-v0.7); see §9 and the v0.5 to v0.8 sections at the end of this file. v0.5 amended v0.4 (`bff5356`) for JS2. v0.4 was 2026-10-27; v0.3 was `13f40e9`, v0.2 was `5cd4c28`, v0.1 was `b27b1a8`.  
**Pointer:** the v0.5 section at the end of this file supersedes §1 items 1, 3, 4 and 7, §3 item 1, and §6's Claude judge for JS2. It also changes §1 item 5 (no replies are collected in JS2), the `state.json` path in §1 item 6, and §2's other outputs, and it adds Ashby's fields to §2 and §4. Everything else in §§1–8 stands as v0.4 left it.  
**Board:** five boards, per GATE.md §0 (and v0.5, item 1): Greenhouse — tokens `stripe`, `duolingo`, `robinhood`; Ashby — names `notion`, `js2nosuchboard`  
**Language / toolchain:** Python 3.11 or newer (3.11 is the floor because CI checks 3.11), standard library only, tests with `unittest`. On my machine: Python 3.13.17, run as `python3.13` (the Mac's default `python3` is 3.9.6, which is too old). Test command: `python3.13 -m unittest discover -s tests -v`. No `pip install` is required or permitted for v1.

## Changelog

- **2026-10-25 — v0.1.** First draft, committed and pushed as `b27b1a8`
  before any code or run. Written by me.
- **2026-10-25 — v0.2.** Claude
  (Claude.ai, in my course Project chat) reviewed v0.1 and listed issues.
  I made the decisions and applied the changes step by step in my editor,
  chose claude's help to refind the wordings. I ran the checks myself: downloaded the
  Stripe board, recorded its size and SHA-256, counted the fields, checked
  the URL without `?content=true`, and looked at Stripe's location
  spellings before fixing the persona. Main changes: [board `stripe` and
  the one fetch URL; the `id` rule; Claude runs outside the agent with
  saved replies; one `field=value` per line in Claude's format; the
  validator checks citations; the cleanup order; named matching quirks;
  sections 8 and 9.]
- **2026-10-26 — v0.3.** Writing the CP2 expected-outcome tables
  (rule cases, watch cases, refusal cases, validator cases) turned up
  three gaps in the contract: no skills minimum, no rule for an
  existing but empty state.json, and a phone rule that did not say
  whether an area code may come before the 555. Claude pointed out a
  fourth: the required-fields rule had been deleted during the v0.2
  edits. Decisions: the skills minimum is 2, so a persona with exactly
  two skills runs; an existing state.json that is an empty list is not
  a baseline, so every id in the response is new; a phone counts as a
  555 number when 555 is the exchange, so 617-555-0142 runs. Main
  changes: [required-fields rule restored; skills minimum set to 2;
  empty-but-existing state.json is not a baseline; phone rule
  clarified to the 555 exchange.]
- **2026-10-27 — v0.4.** During CP3, Claude Code raised three
  points: §1.3 still listed Alex's old locations while the rule cases
  used the final list; the working draft named board `vercel` and no
  commit, while my changelog and the CP2 tables say board `stripe`
  and v0.1 committed as `b27b1a8`; and the changelog wording for v0.1
  and v0.2 was still open. My decisions: the board is `stripe` and
  v0.1 stands as committed at `b27b1a8`, so changes from here are
  amendments, not drafting fixes; §1.3 follows the final locations,
  ["New York", "NYC", "Remote"]; the changelog keeps my own wording
  for v0.1 and v0.2. I reviewed the rest of the points and accepted
  them. Main changes: [§1.3 locations updated to the final list.]
- **2026-11-06 — v0.5.** Written before any JS2 code. Claude
  (Claude.ai) reviewed two drafts; after the second review it typed
  the fixes into the file at my request. I made every decision and
  ran the evidence checks myself on the 2026-11-05 snapshot. Main
  changes: [five boards and the two fetch URL forms; the allow-list
  grows to two hosts; state keyed by (board, id), the board key
  being the ATS plus the name, in state/state.json; Ashby's fields
  mapped into §2 and §4 — descriptionPlain for C3 with §4 step 4
  only, location plus secondaries joined for C2, jobUrl for
  absolute_url; where a run writes, with a failed board's response
  saved; a 10 s timeout; the Claude judge is not run in JS2; seven
  new known consequences, each pinned by a test.]
- **2026-11-06 — v0.6.** Written after CP5a (the permission layer)
  and before CP5b (the loop). While building CP5a, Claude Code
  stopped on four rule conflicts and made eleven smaller decisions
  on its own; I decided the four, and reviewed and accepted the
  eleven (v0.6, D1–D11). Claude (Claude.ai) typed this entry and the
  v0.6 section at my request; the decisions are mine. Main changes:
  [state is a new file per run, written safely; nothing outside the
  JS2 folder, and nothing in the two reference folders, is ever
  written, even with approval; fetch checks the URL form and that the
  board is configured; D1–D11 accepted; two known limits recorded.]
- **2026-11-06 — v0.7.** Written after CP5b (the loop) and before
  run 1. While building CP5b, Claude Code stopped on five open
  points, which I decided, and made twenty smaller decisions on its
  own, which I reviewed and accepted (v0.7, E1–E20). Claude
  (Claude.ai) typed this entry and the v0.7 section at my request;
  the decisions are mine. Main changes: [evidence saved per attempt;
  unlisted statuses fail with no retry, 429 included; a retry stopped
  by a budget is "not completed"; a duplicate board is an invalid
  config; "judge code unchanged" means agent/replies.py, and rule.py
  gets Ashby's step-4-only path; a first run with zero jobs saves
  nothing; seeded runs; E1–E20 accepted; three known limits recorded.]
- **2026-11-07 — v0.8.** Written after CP8 (the reviewed W5 change)
  and before run 2. Records what run 2 relies on: the honest
  User-Agent (JS2-CP5c), GATE.md v0.3's empty-board rule (JS2-CP8a to
  CP8c) and the version labels. No new decisions: each was decided and
  committed earlier, and this entry records them. Claude (Claude.ai)
  typed this entry and the v0.8 section at my request; the decisions
  are mine. Main changes: [an honest identity on every request; an
  empty board with saved ids is a failure, its line per W5; labels to
  GATE v0.3 and CONTRACT v0.8; two known limits.]

> This contract was written before I asked Claude to implement anything.
> Implementation must match this document. If implementation and contract
> disagree, the contract is wrong or the code is wrong — I will note which
> I changed, when, and why in FRICTIONAL.md. I will not
> silently edit this contract after a run to make the results look correct.

---

## 1. In — What the agent takes in

1. **Board and the one fetch URL (one board only)**
   - The board is Greenhouse, token `stripe`, read from `config.json`.
   - The agent fetches exactly one URL:
     `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`
     There is no other URL form. `?content=true` is required, because
     without it the jobs have no `content` field (see the evidence note below).
   - URLs inside the response, such as each posting's `absolute_url`, are
     data to copy into the output, never URLs to fetch.
   - The token identifies *one* company board. The agent does not discover
     other boards, search Greenhouse, or follow links to other companies.
        - **Evidence note (my own checks, 2026-10-25, before any code):**
     - Downloaded with `curl` at 21:44 local time (Boston) and saved as
       `evidence/stripe_jobs_content_true_2026-10-25.json`:
       5,585,090 bytes, SHA-256
       `de04ad85474172a2b7124b92943265efa8a9aff0644793f96af90a927e17d055`.
     - In that file: 719 jobs; all 719 have a `content` field; none has a
       `description` field; in all 719, `content` is HTML-escaped (it
       contains `&lt;` instead of `<`); the raw file text contains
       `\u0026lt;`; each `id` is a JSON number (example: `8172510`);
       35 titles contain "product manager" (case-insensitive).
     - The same URL without `?content=true`, checked the same evening and
       not saved: 719 jobs, 0 with a `content` field.

2. **Résumé as JSON (fictional persona only)**
   - A local file path to a résumé in JSON, e.g. `resume_persona.json`.
   - **Required fields.** If any field is missing, empty, or below its
     minimum, the agent stops with an error and produces no verdicts:
     `name`, `email`, `phone` (not empty); `target_titles` (at least 1);
     `skills` (at least 2, because C3 needs 2 distinct skills);
     `locations` (at least 1); `max_years_required` (a whole number).
   - **Final persona (invented, not me), fixed before any run:**
     - `name`: `"Alex Rivera"`
     - `email`: `"alex.rivera@example.com"`
     - `phone`: `"555-0142"`
     - `target_titles`: `["Associate Product Manager", "Product Manager", "Product Analyst"]`
     - `skills`: `["Python", "SQL", "A/B testing", "roadmapping", "user research"]`
     - `locations`: `["New York", "NYC", "Remote"]`
     - `max_years_required`: `3`
   - The locations were chosen after looking at how Stripe writes
     locations in the 2026-10-25 evidence file, before any labeling or run.

3. **State file and the `id` rule**
   - A local JSON file, `state.json`, containing the list of posting ids
     seen on previous runs. If it does not exist, that run is the baseline
     (see §2). If it exists, even as an empty list `[]`, the run is not a
     baseline: every id not in it is new. The agent writes `state.json`
     only after a run finishes successfully, so a failed run can never
     leave behind an empty file.
   - In the board response, each `id` is a JSON number (see the evidence
     note in item 1). The agent converts each `id` to a string once, as
     soon as it reads the response (`str(id)`), and uses only that string
     form from then on.
   - `state.json` stores ids as a JSON list of strings, and "new" is
     decided by comparing strings to strings only. Comparing a numeric id
     to a stored string id would make every posting look new. That is a
     contract violation, and a test must cover it.

4. **Config file**
   - `config.json`, containing: `board_token` (`"stripe"`), `allow_list`
     (exactly `["boards-api.greenhouse.io"]`), `resume_path`,
     `state_path`, `evidence_dir`, and `claude_outputs_dir`.
   - Before every fetch, the agent checks that the URL's host is in
     `allow_list`. If it is not, the agent refuses (§3) and fetches nothing.

5. **Saved Claude replies (Claude runs outside the agent — see §6)**
   - The agent never calls Claude. I run Claude myself, one posting per
     fresh Incognito chat, and save each reply.
   - Each reply is saved as plain text, exactly as Claude returned it,
     in `claude_outputs/<posting_id>.txt` — one file per new posting.
   - `claude_outputs/metadata.json` records, for each `posting_id`: the
     file name, the date the reply was collected, the model shown in the
     chat, and the prompt version used. A reply without a metadata entry
     is not read.
   - A new posting with no saved reply gets `claude_verdict: "rejected"`
     (§2). It is kept in the report, never dropped.
   - The extra replies for the sampling report and the prompt experiment
     are stored separately under `experiments/`, with the same kind of
     metadata. The agent does not read them.     

6. **Every file the agent reads — a closed list**
   - the persona résumé (`resume_path` in `config.json`)
   - `state.json`
   - `config.json`
   - `claude_outputs/metadata.json` and the `.txt` files it lists
   - for a seeded run only: a saved earlier board response from
     `evidence/`, and the run report must say `seeded`, not `live`
   - Nothing else: not `experiments/`, no real résumé, no API keys or
     credentials, no other local files.

7. **What it needs to run**
   - Network access to the allow-listed host only (see §3), for a live
     run. A seeded run needs no network.
   - Read access to the résumé JSON and the state file.
   - Write access to: the raw-evidence directory, the updated state file,
     and the run report. No other writes, no sending, no applying.

## 2. Out — What it returns

For **each new posting only** — a posting whose `id` was not in the state
file at the start of the run — the agent returns one record with:

- `posting_id` (string — the `str(id)` form of the numeric board id;
  see §1, the state-file item)
- `title` (string, copied exactly)
- `absolute_url` (string, copied exactly)
- `location.name` (string, copied exactly, or `"not stated"` if absent)
- `rule_verdict`: `"relevant"` or `"not_relevant"` — from §4, recomputable
- `rule_justification`: an object that **must** name both sides:
  - `resume_fields`: a list of `{"field": ..., "value": ...}` entries for
    every résumé value a condition was compared against, e.g.
    `{"field": "skills", "value": "Python"}`
  - `posting_fields`: a list of `{"field": ..., "matched": ...}` entries —
    the field name plus the matched term only, never the whole
    `content`, e.g. `{"field": "title", "matched": "Product Manager"}`
  - `conditions`: for **each** of C1, C2 and C3 (all three, always):
    `true` / `false`, the résumé values compared, and the posting
    field's actual value. **A `not_relevant` record must cite every
    failing condition, not just the first.** Citing only one, or none,
    is a W2 failure (§5).
- `claude_verdict`: exactly one of `"relevant"`, `"not_relevant"`, or
  `"rejected"` — **labeled in every output as `judgment (Claude)`, never
  as a fact or as the rule verdict.** A posting with no saved reply, or
  with a reply that fails validation (§6), gets `"rejected"`. The record
  is kept, never dropped, so the rule and Claude always cover the same
  new postings.
- `claude_justification`: for `"relevant"` / `"not_relevant"`, Claude's
  validated reply; for `"rejected"`, the reply text exactly as saved (or
  a note that none was saved) plus the list of reasons it failed
  validation. A reply is never repaired silently.

Other outputs for a run:
- The raw board response, saved unchanged as evidence, with fetch date/time
  and URL in the filename or a sidecar note.
- An updated state file containing all ids seen up to and including this run.
- A run summary: `total_fetched`, `new_count`, the list of new ids, and
  whether the run was `live` or `seeded`.
- **Baseline rule:** On the first run (empty state), the agent saves all
  ids and reports **0 postings as new**. It does not judge the baseline set.

If there are no new postings, the agent returns an empty new-postings list
and says so. It does not re-judge old postings to fill the report.

## 3. Refuses — What it will not do

The agent **will not**:

1. Fetch any host not on the allow-list. Allow-list for v1 is exactly:
   - `boards-api.greenhouse.io`
   Any other host — including a redirect to another host, a link inside a
   posting (such as its `absolute_url`), or a board on Ashby / Lever /
   SmartRecruiters — is refused and logged, not followed.
2. Show a real résumé on screen, in logs, in tests, or on GitHub. Only the
   fictional persona résumé may be printed, committed, or screenshotted.
   The agent refuses to run unless the résumé email ends in
   `@example.com` and the phone contains `555-01` followed by two digits
   (the range reserved for fiction), with or without an area code
   before it — e.g. `555-0142` or `617-555-0142`.
3. Present a model's judgment as a fact. Claude verdicts are always labeled
   `judgment (Claude)`. Only the rule verdict in §4 is a record that anyone
   can recompute from the saved raw response and the persona résumé.
4. Apply to a job, send email or messages, create accounts, or contact an
   employer or a person named in a posting.
5. Infer facts not in the posting or the résumé — e.g. salary, visa
   sponsorship, whether a company is "good," or whether the persona would
   "like" the job — and use an inferred fact in a verdict.
6. Store credentials, cookies, or API keys, or read any file outside the
   closed list in §1, item 6.
7. Call Claude or any other model. The agent holds no API key and has no
   model endpoint on its allow-list. Claude runs outside the agent (§6);
   the agent only reads the saved replies (§1, item 5).   

A refusal is an output: the agent stops or skips that item, logs the reason,
and does not produce a substitute verdict.

## 4. The Rule — How relevance is judged

A TA must be able to predict the rule verdict by hand from the saved raw
response and `resume_persona.json` alone, without running code or asking a model.

**Cleanup of `content`, in this exact order** (facts from the evidence
note in §1, item 1):
1. Parse the response as JSON. This turns the raw `\u0026lt;` into `&lt;`.
2. HTML-unescape the text (Python's `html.unescape`), so `&lt;p&gt;`
   becomes `<p>`. Before this step there are no real tags to remove.
3. Remove tags: replace every `<...>` tag with a space.
4. Collapse every run of whitespace into a single space.

For `title` and `location.name`: trim spaces at both ends and collapse
inner whitespace.

**Matching:** all matching is case-insensitive plain substring on the
cleaned text — no whole-word rule, no synonyms, no stemming, no model
interpretation. `APM` does not count as `Product Manager` unless `APM` is
listed in `target_titles`.

A posting is **`relevant` if and only if ALL three conditions are true**.
All three are always checked, even after one fails, so the justification
(§2) can cite every condition:

- **C1 — Title:** `posting.title` contains at least one string from
  `resume.target_titles`.
- **C2 — Location:** cleaned `posting.location.name` contains at least
  one string from `resume.locations`, **or** it is exactly `remote`
  (case-insensitive, so `Remote` and `REMOTE` count too) and some
  `resume.locations` entry starts with `remote` (also case-insensitive).
- **C3 — Skills:** the cleaned `content` (steps 1–4 above) contains at
  least **2 distinct** strings from `resume.skills`. The same skill
  counted twice counts once. If `content` is missing, C3 is `false`.
  There is no other source for C3.

Otherwise — if any of C1, C2, or C3 is false — the posting is
**`not_relevant`**.

Notes for hand-checking:
- If a field is missing, that condition is `false`. Missing data is not
  guessed.
- The rule does not use Claude, scores, approval counts, posting date,
  company size, or any field not listed above.
- `max_years_required` is recorded in the résumé for later assignments;
  it is **not** part of the v1 rule, specifically so a TA does not have to
  parse experience requirements from free text by hand. If I add it later,
  that is an amendment (§9), not a silent edit.

- **Known, accepted consequences of plain substring matching** — each
  one must be pinned by a test:
  - `SQL` matches inside `NoSQL` (a false positive).
  - `Senior Product Manager`, `Staff Product Manager` and
    `Lead Product Manager` all contain `Product Manager`, so they pass C1.
    The rule has no seniority filter, even though the persona's
    `max_years_required` is 3.
  - `roadmap` does not match `roadmapping`, and `APM` does not match
    `Product Manager` (false negatives).

**Worked example (invented, for hand-checking — not a real posting),
using the persona in §1:**
- Résumé: `target_titles` includes `"Product Manager"`, `locations`
  includes `"Remote"`, `skills` includes `"Python"`
  and `"SQL"`.
- Posting: `title = "Product Manager, Payments"`,
  `location.name = "Remote"`, cleaned `content`
  contains "Python" and "SQL".
- C1 true, C2 true, C3 true (2 skills) → `relevant`. The justification
  must list exactly those résumé values and posting fields, in the §2
  format.

## 5. Wrong Versions — Plausible-but-wrong implementations tests must catch

Tests written from this section must fail on these versions and pass on
the correct one. These are not bugs in general — they are specific wrong
implementations of *this* contract.

- **W1 — Mismatched pairing (labels paired with the wrong postings)**
  The code computes verdicts correctly for a set of postings, but attaches
  each verdict / justification to a different `posting_id` (e.g. by sorting
  verdicts and postings independently, or by zipping two lists in different
  orders). Output looks plausible — every posting has a verdict — but the
  verdict for posting A is actually the verdict for posting B.   
  The same wrong version applies to Claude's saved replies if they are
  matched to postings by file order instead of by `posting_id`.
  *Test that must catch it:* Two postings with opposite hand labels and
  distinct ids/titles; assert each id carries its own hand-computed verdict
  and cites its own title. Reordering the input must not change which
  verdict belongs to which id.

- **W2 — Justification that cites nothing (or cites what is not there)**
  The code returns the correct `relevant` / `not_relevant` label, but the
  justification is empty, generic ("matches the résumé"), or cites a skill /
  title / location that is not in the résumé or not in that posting.
  Under this contract, a right label with a wrong justification is a failure.  
  and a `not_relevant` record cites all three conditions, with every
  failing one marked.
  *Test that must catch it:* For every record, assert every term in
  `rule_justification.resume_fields` is present in the résumé file and every
  term in `rule_justification.posting_fields` is present (case-insensitive)
  in that posting's saved fields; assert a relevant record cites at least
  1 target title and at least 2 skills.

- **Pinned tests (not wrong versions, but tests that must exist):**
  - ids: a numeric `id` from the board and the same id stored as a
    string in `state.json` must count as already seen, not new (§1).
  - matching quirks from §4: `SQL` inside `NoSQL` counts; `Senior`,
    `Staff` and `Lead Product Manager` pass C1; `roadmap` does not match
    `roadmapping`; `APM` does not match `Product Manager`; `New York`
    does not match `New-York`.
  - validator (§6): `POSTING_FIELD: location.name=SF, SEA, NYC` is one
    value, `SF, SEA, NYC`; `RESUME_FIELD: skills=Python, SQL` is one
    value that is not a résumé skill, so the reply is `rejected`;
    `RESUME_FIELD: skills=New York` cites a real résumé value under the
    wrong field, so the reply is `rejected`.

## 6. Two Judges — Rule vs. Claude

- **Rule judge (a record):** Implements §4 exactly. Deterministic. Anyone
  with the raw response + résumé can recompute it by hand or by re-running
  the function. Disagreement with the hand label means the code or the
  hand label is wrong — investigate, do not average them away.
- **Claude judge (a judgment), run outside the agent:** I run Claude
  myself, one posting per fresh Incognito chat (so no memory or earlier
  conversation affects the answer), and save each reply as in §1,
  item 5. The agent only reads and validates the saved replies.
  - **What Claude is asked:** to apply §4 — C1, C2, C3, with the same
    cleanup and substring matching — and nothing else. Claude is not
    asked whether the job is worth the persona's time. A verdict based on
    anything outside §4 breaks the prompt contract.
  - **Fixed output format** — one `field=value` pair per line, never
    comma-separated, because real values contain commas (Stripe titles
    like `Product Manager, Payments`, locations like `SF, SEA, NYC`):
  ```
  VERDICT: relevant | not_relevant
  RESUME_FIELD: <field>=<value used>
  POSTING_FIELD: <field>=<matched term in this posting>
  REASON: <one sentence naming a match or a failed condition>
  ```
    Exactly one `VERDICT` line first, then one or more `RESUME_FIELD`
    lines and one or more `POSTING_FIELD` lines (repeat the line for each
    value), then exactly one `REASON` line last. Each `*_FIELD` line is
    split at its **first** `=` only, so a value may contain commas.
    Allowed `POSTING_FIELD` names: `title`, `location.name`, `content`.

  - **Validator (in the agent)** checks each saved reply, in this order:
    1. **Format:** exactly the lines above, in that order; `VERDICT` is
       `relevant` or `not_relevant`; every `*_FIELD` line has a field
       name, an `=`, and a non-empty value; no extra lines.
    2. **Citations exist:** each `RESUME_FIELD` value is in the résumé
       *under that field* (for example, `skills=Python` passes, but
       `skills=New York` fails, because New York is a location). Each
       `POSTING_FIELD` value is in that posting's named field, after
       the §4 cleanup.
  - A reply that fails either check gets `claude_verdict: "rejected"`,
    with the reasons listed. It is never repaired silently, and no
    free-form reply is presented as a verdict.
  - **Expect rejections:** Claude.ai often wraps answers in Markdown or
    adds a sentence before them. Those replies are correctly rejected.
    How many were rejected, and why, is a real result to report in the
    sampling report and the prompt experiment, not something to hide.

The two verdicts are reported side by side and never merged into one score.

## 7. What a Failure Looks Like

**Dated sentence, written before any run:**

> On 2026-10-25, before running anything, I will call this a failure if,
> on the run I submit, the agent reports an already-seen posting as new,
> or labels a posting `relevant` whose justification does not cite a
> target-title match from the résumé and that title in the posting itself.

Other failures are possible; this is the minimum I commit to checking first.

## 8. Hand-Labeling — the Rule Is §4

- My hand labels apply **§4 by hand**: the same C1–C3, the same cleanup,
  the same substring matching, and no broader judgment about whether a
  job is worth applying to. Hand labels, the rule and Claude are only
  comparable because all three use the same rule.
- Because of this, my hand labels should always match the rule's
  verdict. Where they don't, either the code or my labeling is wrong.
  The prompt experiment therefore measures whether Claude follows this
  contract, not whether a job is worth the persona's time.
- The labeling *procedure* (label without looking at Claude's or the
  code's output; label the development set first; don't look at the
  held-out set until the end) goes in `experiments/labeling_protocol.md`.
  That file points to §4, adds no criteria, and is committed before any
  labeling begins.

## 9. Amendments — No Silent Edits After v0.2

- v0.2 is locked when it is committed. After that, any change to a value,
  rule, format or toolchain is an amendment, recorded in the table below
  with a version bump (v0.3, v0.4, …), and noted in FRICTIONAL.md.

| Date | Section | Old → New | Reason | Tests re-run |
|---|---|---|---|---|
| 2026-10-26 | §1 résumé item | required-fields rule missing (deleted during v0.2 edits) → restored; `skills` at least 2 | refusal cases P05–P07 depend on it | none yet (no code exists) |
| 2026-10-26 | §1 state item | "created empty … baseline" → an existing empty `state.json` is not a baseline; state written only after a successful run | watch case S07 | none yet (no code exists) |
| 2026-10-26 | §3 item 3 | "a `555-` number" → contains `555-01` plus two digits, area code allowed | refusal case P04 | none yet (no code exists) |
| 2026-10-27 | §1, §2, §3, §6 | unspecified → the 12 CP3 decisions listed below the table | found unclear while implementing v0.3 | yes: 5/5 tests pass on 2026-10-27, after the decisions were coded |
| 2026-11-06 | §1 item 1 | one board (Greenhouse `stripe`), one fetch URL → five boards (GATE.md §0) and two fetch URL forms, Greenhouse and Ashby (v0.5, item 1) | JS2 watches several boards on two ATSs; the loop is what JS2 builds | none yet, since no JS2 code has changed; 45/45 on the copied JS1 code (CP3) |
| 2026-11-06 | §3 item 1 (and §1 item 4) | allow-list exactly `boards-api.greenhouse.io`, an Ashby board refused → `boards-api.greenhouse.io` and `api.ashbyhq.com`, exact match, https only (v0.5, item 2) | Ashby boards cannot be fetched under the JS1 list; the refusal rule itself is unchanged | none yet, since no JS2 code has changed; 45/45 on the copied JS1 code (CP3) |
| 2026-11-06 | §1 item 3 | `state.json` holds one board's ids as a list of strings → `state/state.json`, one section per board, board key = ATS plus name (`greenhouse:stripe`), ids keyed by (board, id) (v0.5, item 4) | five boards share one state file, and an id is only unique inside its board (GATE.md §3) | none yet, since no JS2 code has changed; 45/45 on the copied JS1 code (CP3) |
| 2026-11-06 | §2, §4 | posting fields are Greenhouse's (`content`, `location.name`, `absolute_url`) → Ashby's fields mapped in v0.5, item 3: `descriptionPlain` for C3 (§4 step 4 only), `location` plus secondaries joined for C2, `jobUrl` for `absolute_url` | Ashby's response shape differs from Greenhouse's; the rule in §4 does not change | none yet, since no JS2 code has changed; 45/45 on the copied JS1 code (CP3) |
| 2026-11-06 | §1 item 7, §2 | writes are the raw-evidence directory, the state file and the run report → state to `state/state.json`, raw responses to `evidence/` (a failed board's response is saved too, with its status in the sidecar note; a timeout gets a sidecar note only), reports to `output/`; never `evidence/gate_probes/` or `evidence/snapshots/` (v0.5, item 5) | the JS2 folder layout (GATE.md §5); a failed board leaves evidence, not silence | none yet, since no JS2 code has changed; 45/45 on the copied JS1 code (CP3) |
| 2026-11-06 | §6 (and §1 item 5) | I run Claude on each new posting and save each reply → in JS2 the Claude judge is not run and no replies are collected; every new posting's Claude line is "rejected — no saved reply (judge not run in JS2)" (v0.5, item 7) | JS2 is graded on the loop, not the judge (GATE.md §1); JS1's code and verdict meanings are unchanged | none yet, since no JS2 code has changed; 45/45 on the copied JS1 code (CP3) |
| 2026-11-06 | §1 item 7 (fetch) | no timeout stated in the contract (JS1's code used 30 s) → 10 s per request, one retry, then the board is failed (v0.5, item 6) | GATE.md §4 sets the timeout; the contract now states it too | none yet, since no JS2 code has changed; 45/45 on the copied JS1 code (CP3) |
| 2026-11-06 | §4 known consequences, §5 pinned tests | JS1's quirks only → seven more, each pinned by a test (v0.5, item 8) | two ATSs and five boards bring new edge cases, seen in the 2026-11-02 probes and the 2026-11-05 snapshot | none yet, since no JS2 code has changed; 45/45 on the copied JS1 code (CP3) |
| 2026-11-06 | v0.5 item 4 (§1 item 3) | one state file, `state/state.json`, updated each run → a new file per run, `state/state_<UTC>.json`; the newest by name is read; written to a temporary file first, then moved into place (v0.6, items 1–2) | updating one file each run is an overwrite, which GATE.md §5 puts behind approval; a new file per run needs no exception, and each run's state becomes evidence | 64/64 after JS2-CP5a; state itself is built in CP5b |
| 2026-11-06 | v0.5 items 1, 2, 5 (with GATE.md §5) | URL form and board not checked; approval's reach not bounded → fetch checks the URL form and that the board is configured for that host; no approval opens a write outside the JS2 folder or into `evidence/gate_probes/` or `evidence/snapshots/` (v0.6, item 3) | Claude Code's four questions in CP5a, and my answers | 64/64 (JS2-CP5a) |
| 2026-11-06 | §1–§5, implementation details | unspecified → D1–D11, decided by Claude Code in CP5a and accepted by me (v0.6, item 4) | found unsettled while building the permission layer | 64/64 (JS2-CP5a) |
| 2026-11-06 | §4 timeout, §5 | not stated → two known limits recorded (v0.6, item 5) | found on review of CP5a | none: recorded, not tested |
| 2026-11-06 | v0.5 item 5 | one evidence file per board per run → one file per attempt, with a sidecar; a timeout attempt gets a sidecar only (v0.7, item 1) | a retried board can get two responses with a status, and every one is evidence | 106/106 (JS2-CP5b) |
| 2026-11-06 | GATE.md §4 table, extended here | statuses other than 200, 3xx, 404 and 5xx unspecified → failed — HTTP <status>, no retry, 429 and 204 included (v0.7, item 2) | Claude Code's question in CP5b | 106/106 (JS2-CP5b) |
| 2026-11-06 | GATE.md §1–§2 | a retry stopped by a budget unspecified → the board is "not completed", not a §4 failure (v0.7, item 3) | Claude Code's question in CP5b | 106/106 (JS2-CP5b) |
| 2026-11-06 | §1 item 4 (config) | a board listed twice unspecified → invalid config, error before any fetch (v0.7, item 4) | Claude Code's question in CP5b | 106/106 (JS2-CP5b) |
| 2026-11-06 | v0.5 items 3 and 7, §4 | "judge code unchanged" read as covering rule.py → it means agent/replies.py; rule.py gets Ashby's step-4-only path (v0.7, item 5) | v0.5 item 3 and item 7 conflicted as worded | 106/106 (JS2-CP5b) |
| 2026-11-06 | §1 item 3, §2 baseline rule | a first run with zero jobs saved an empty list (JS1) → saves nothing, so the next run is a baseline (v0.7, item 6) | on a board never seen, an empty first answer is more likely a problem than a truth | 106/106 (JS2-CP5b) |
| 2026-11-06 | §1–§6, implementation details | unspecified → E1–E20, decided by Claude Code in CP5b and accepted by me; seeded runs, my decision (v0.7, items 7–8) | found unsettled while building the loop | 106/106 (JS2-CP5b) |
| 2026-11-06 | §2 outputs | not stated → three known limits recorded (v0.7, item 9) | found on review of CP5b | none: recorded, not tested |
| 2026-11-07 | §1 item 7 (fetch) | Python's default User-Agent → an honest project identity on every request (v0.8, item 1) | Ashby's Cloudflare refused Python's default with 403, error 1010; found by my smoke run, fixed test-first | 108/108 (JS2-CP5c) |
| 2026-11-07 | §4, v0.7 item 6 and E16 | zero jobs on a board with saved ids was ok → "failed — empty board", its line in W5's wording (GATE.md v0.3; v0.8, item 2) | the CP7 demo; the W5 test failed first (JS2-CP8b); the patch was reviewed and accepted (JS2-CP8c) | 109/109 (JS2-CP8c) |
| 2026-11-07 | §2 outputs | the report labeled gate v0.2 and contract v0.6 → gate v0.3 and contract v0.8, from JS2-CP8e (v0.8, item 3) | run 1's report carried a stale label | the suite, after JS2-CP8e |
| 2026-11-07 | §4 | not stated → two more known limits recorded (v0.8, item 4) | found on review of JS2-CP8c | none: recorded, not tested |

### v0.4 — decisions made during CP3 (2026-10-27)

Claude Code found these points unclear while implementing v0.3. For
items 1–6 it stopped and asked, and I chose. Items 7–12 it decided and
reported, and I reviewed and accepted them. Each is marked in the code
with a dated comment.

1. §6: a saved reply may end with exactly one final line break; anything
   else extra (including `\r`) is rejected.
2. §6: `RESUME_FIELD` may cite only `target_titles`, `locations` or
   `skills`, and the value must equal one entry exactly (case-sensitive).
3. §1/§2: the run report is written where `--report` says (default
   `run_report.json` next to `config.json`); `config.json` is unchanged.
4. §1 replies item: `metadata.json` is an object keyed by `posting_id`,
   each entry with `file` (`<posting_id>.txt`), `collected`, `model`,
   `prompt_version`.
5. §2: C3's condition entry records whether `content` was present and
   which skills were found — never the content text.
6. §1 résumé item: blank list entries are refused, and the `skills`
   minimum counts distinct skills.
7. §6: `POSTING_FIELD` values are matched like §4 — case-insensitive
   plain substring, after cleanup.
8. §2: a seeded run updates `state.json` but saves no new evidence,
   because nothing is fetched.
9. §3 item 1: every redirect is refused, even to the same host.
10. §3 item 3: the `@example.com` check is case-sensitive.
11. §1 state item: if an id appears twice in one response, only the
    first posting is judged.
12. §2: each condition's compared value is the cleaned value; the
    record's `title` and `location.name` stay raw copies.

---

## v0.5 — 2026-11-06 (JS2)
Amends v0.4 (JS1, bff5356) for JS2. Exits, budgets, repeats, errors and
permissions live in GATE.md v0.2; this contract does not repeat them.

1. Boards (§1 item 1): the five boards in GATE.md §0 — Greenhouse: stripe,
   duolingo, robinhood (watched); Ashby: notion (watched), js2nosuchboard
   (fails on purpose). The loop reads the board list from the config; no
   board is wired into the code.
   Fetch URLs, exactly:
   - Greenhouse: https://boards-api.greenhouse.io/v1/boards/<token>/jobs?content=true
   - Ashby: https://api.ashbyhq.com/posting-api/job-board/<name>?includeCompensation=true
     (pattern from Lectern, collect.py:52)
2. Allow-list (§1 item 4, §3 item 1): exact match, https only —
   boards-api.greenhouse.io and api.ashbyhq.com. The rule is GATE.md §5's:
   the whole host, lowercased; no subdomains, no suffix or prefix matches,
   no userinfo, no non-default port, no http. Anything else is refused
   before a request is sent.
3. Ashby fields (§2, §4):
   - id → id. Ashby ids are UUID strings already, so JS1's string
     comparison applies with no conversion at the boundary.
   - title → title.
   - location.name → location, with secondaryLocations[].location joined
     after it. Trimming: each part — the main location and each
     secondary — is trimmed, then the parts are joined with "; ", so the
     C2 input reads like Greenhouse's own strings, e.g. "San Francisco,
     California; New York, New York". isRemote: not used, because in
     evidence/snapshots/notion_2026-11-05T194458Z.json, 87 of 150
     postings are isRemote: true, and 86 of those are workplaceType:
     "Hybrid"; 0 of 150 location strings, secondaries included, contain
     "remote". So the flag does not mean remote, and C2 reads only text.
     workplaceType: not used either, with the same reason: §4 checks
     text.
   - content (C3) → descriptionPlain. Cleanup: only §4 step 4 — collapse
     every run of whitespace into a single space — so a skill that wraps
     onto a new line still matches. §4 steps 2 and 3 (unescape, remove
     tags) are not applied: they exist for Greenhouse's escaped HTML. In
     the posting checked on 2026-11-05, descriptionPlain was plain text
     with line breaks and no tags, while descriptionHtml carried real
     tags; that is why descriptionHtml is not the C3 input. With the
     cleanup cut down to step 4, a TA can still check C3 by hand.
   - absolute_url → jobUrl.
4. State (§1 item 3): seen ids are keyed by (board, id), as GATE.md §3
   says, and the board key is the ATS plus the name: greenhouse:stripe,
   greenhouse:duolingo, greenhouse:robinhood, ashby:notion,
   ashby:js2nosuchboard. File: state/state.json in this folder — one
   file, one section per board key. It starts empty in JS2: each board's
   first run is its baseline, and JS1's state.json is not read, copied,
   or written.
5. Where a run writes: state → state/state.json; raw responses →
   evidence/, one file per board per run, named for the board and the
   UTC time; reports → output/. A failed board's response is saved too:
   any response that has a status — including the 404 body from
   js2nosuchboard — is saved in evidence/ with its status in the sidecar
   note. A timeout has no body, so it gets a sidecar note only. Never:
   evidence/gate_probes/ or evidence/snapshots/ — both are read-only
   reference, and a run never writes there (GATE.md §5).
6. Timeout: 10 s per request (GATE.md §4). A request with no answer in
   10 s is a timeout: one retry, then the board is failed — timeout after
   2 attempts. The 60 s run budget is GATE.md §2.
7. The judge in JS2: JS1's judge code, unchanged, and no new replies. The
   rule judge runs on every new posting, as in JS1. The Claude judge is
   not run: every new posting's Claude line reads "rejected — no saved
   reply (judge not run in JS2)", JS1's verdict for a missing reply. JS2
   reports no Claude verdicts and claims none (GATE.md §1).
8. New known consequences, each pinned by a test:
   - C2 can pass on a secondary location alone: main location
     "San Francisco, California", secondary "New York, New York" → C2
     true, because the secondaries are joined into the C2 input. Pinned
     by a constructed Ashby case: main fails, secondary matches, expect
     C2 true.
   - isRemote alone never passes C2: isRemote true, location
     "San Francisco, California", no secondaries → C2 false, because the
     boolean adds no text. Pinned by a constructed Ashby case.
   - The one workplaceType: "Remote" posting fails C2, because its
     location text never says Remote. That is a known false negative,
     accepted: C2 reads location text only. Pinned by a constructed
     Ashby case: workplaceType "Remote", location a city, expect C2
     false.
   - "Remote - California" passes C2 by substring, as seen on Duolingo.
     Pinned by a constructed Greenhouse case: location "Remote -
     California", expect C2 true.
   - A skill split across a line break in descriptionPlain still matches
     after whitespace is collapsed (§4 step 4 turns the break into a
     space before C3 runs). Pinned by a constructed Ashby case: expect
     the skill found.
   - The same id string on two boards is two postings: seen is
     (board, id), so neither copy is dropped as already seen. Pinned by
     the W4 test in GATE.md §6.
   - On Ashby, the status is checked before the body is read: a 404 body
     is plain text with no jobs in it, and it is reported as failed —
     not found (404), never as an empty board. Pinned by a constructed
     plain-text 404 response, and by every js2nosuchboard run.

## v0.6 — 2026-11-06 (JS2, between CP5a and CP5b)
Amends v0.5. Written after the permission layer (JS2-CP5a) was built and
before the loop (CP5b).

1. State (replaces the file layout in v0.5 item 4): each run writes a new
   file, state/state_<UTC>.json, with the UTC time written like
   2026-11-06T201500Z. A state file is never overwritten. The next run
   reads the newest one by name; leftover temporary files are ignored. If
   state/ holds no state file, every board's run is a baseline. If the
   newest state file cannot be read or parsed, the run ends as error
   (GATE.md §1) and writes no new state. The (board, id) key and the board
   keys of v0.5 item 4 are unchanged.
2. Safe state writes: the new state file is written to a temporary file in
   state/ first, then moved into place, so a crash can never leave a
   half-written newest file.
3. Permission answers (Claude Code's questions in CP5a; my decisions):
   - Nothing that resolves outside the JS2 folder is ever written, even
     with --approve. GATE.md §5's "inside this folder only" wins over the
     approval clause, which covers writes outside the working subfolders
     but inside the folder.
   - evidence/gate_probes/ and evidence/snapshots/ are never written, even
     with --approve.
   - Fetch checks the URL form of v0.5 item 1, and that the board in the
     URL is configured for that host. Either failure is refused under its
     own named rule.
4. Claude Code's decisions in CP5a, reviewed and accepted by me:
   - D1. A board name is letters, digits, "_" and "-" only, so no "..",
     "/" or encoded character can reach the server's path.
   - D2. An explicit :443 is allowed, since it is the default port.
   - D3. A URL with spaces, control characters or non-ASCII characters is
     refused.
   - D4. An --approve path is relative to the project folder and compared
     resolved, so ./config.json counts as config.json.
   - D5. Protected names (GATE.md, the two read-only folders, config.json,
     CONTRACT.md) are compared ignoring case, because the Mac's disk
     ignores case: a write to gate.md is refused.
   - D6. GATE.md is also protected through a hard link.
   - D7. The writable folders are matched exactly, case-sensitive, so
     case can only make the policy stricter, never looser.
   - D8. A refusal lists every approval condition the write broke.
   - D9. A write that names a folder instead of a file is refused.
   - D10. The tool layer creates missing parent folders below a path the
     check has already allowed.
   - D11. The host in each configured board is lowercased, as in GATE.md
     §5; the board name is compared exactly, as the config writes it, so
     Stripe is refused when the config lists stripe.
5. Known limits, recorded and not tested:
   - The 10 s timeout limits each wait on the socket, not the whole
     request: a server that sends one byte every 9 s never times out. The
     60 s run budget (GATE.md §2) is checked between requests, not during
     one.
   - The read-only folders are not protected through a hard link the way
     GATE.md is: if output/x were a hard link to a snapshot file and an
     overwrite of output/x were approved, the snapshot would change.

## v0.7 — 2026-11-06 (JS2, between CP5b and run 1)
Amends v0.6. Written after the loop (JS2-CP5b) was built and before run 1.

1. Evidence per attempt (replaces "one file per board per run" in v0.5
   item 5): every response with a status is saved, one file per attempt,
   named <ats>_<name>_<UTC>_a<N>.json, with a sidecar note
   <same name>.sidecar.json giving the status, URL and UTC time. A timeout
   attempt has no body, so it gets a sidecar only. A seeded board saves no
   evidence, as in JS1 (v0.4 decision 8).
2. Statuses GATE.md §4's table does not list (extends it): any status
   other than 200, 3xx, 404 or 5xx — 400, 403, 410, 429 and 204 included —
   is "failed — HTTP <status>", with no retry. The body is saved and never
   read as jobs, and the run continues. 429 is not retried: a quick second
   request ignores what the server just asked, and waiting for its
   Retry-After could break the 60 s budget.
3. A retry stopped by a budget (GATE.md §1–§2): the board's line reads
   "not completed — <reason> on attempt 1; retry not started: <budget>
   exhausted". It is not a §4 failure, because §4's second attempt never
   happened. The board's ids are unchanged, and the run's exit is
   budget-exhausted, naming the budget and this board.
4. A board listed twice in the config is an invalid config: the run ends as
   error (GATE.md §1) before any fetch. The repeat rule (GATE.md §3) is
   still built and tested at the loop level.
5. "JS1's judge code, unchanged" (GATE.md §1, v0.5 item 7) means the Claude
   judge, agent/replies.py. The rule, agent/rule.py, takes the input v0.5
   item 3 asks for: a posting marked as Ashby gets §4 step 4 only on
   descriptionPlain; a Greenhouse posting goes through JS1's code
   unchanged, and every JS1 rule test is unchanged. Pinned by
   test_ashby_content_gets_step_4_only.
6. Zero jobs on a board's first run: nothing is saved for that board, so
   its next run is a baseline again. On a board never seen, an empty first
   answer is more likely a problem than a truth, and saving an empty
   section would turn every later posting into "new". This differs from
   JS1, which saved an empty list; JS1's S07 rule (an existing empty
   section is not a baseline) is unchanged.
7. Claude Code's decisions in CP5b, reviewed and accepted by me:
   - E1. The config has exactly six keys: boards, allow_list,
     resume_path, state_dir, evidence_dir, output_dir. Any other key is
     an invalid config, so budgets can never live in the config.
   - E2. An allow_list other than the two hosts is refused.
   - E3. The boards in config.json follow GATE.md §0's order.
   - E4. A persona that fails §3 item 2 ends the run as refused.
   - E5. A refused run writes nothing; its report is only printed and
     returned.
   - E6. An error before the loop (config, persona, state) writes a
     report but no state; an invalid config's report goes to output/.
   - E7. Before any fetch: every board URL is checked against the policy,
     the persona path as a read, and the state, evidence and output
     folders for writing a new file; seed files are read.
   - E8. A board with no section in the state file is at its baseline; a
     section that exists, even an empty one, is not.
   - E9. The state file is an object of board key → ids; sections for
     boards no longer configured are carried over.
   - E10. Write order: state to a temporary file, then the report, then
     the move into place. If the report cannot be written, the state stays
     a temporary file, and the next run re-reports those postings instead
     of losing them. The move checks that the target does not exist, then
     renames. Temporary files are never deleted: there is no delete tool.
   - E11. Two runs started in the same second collide on their file
     names; the write is refused and the run ends as incomplete.
   - E12. The clock starts when the run starts. The request and time
     budgets are checked before each attempt. A seeded board uses no
     request, but counts as a board and is under the time budget.
   - E13. After two attempts, the failure reason comes from the last
     attempt: "timeout after 2 attempts", or "5xx / connection error after
     2 attempts".
   - E14. An unexpected shape is: a Greenhouse id that is neither a
     number nor a non-empty string; an Ashby id that is not a non-empty
     string; or a body that is not JSON or has no jobs list. Every other
     field is optional.
   - E15. An Ashby location part that is not a string, or is empty after
     trimming, is dropped.
   - E16. Board lines read: "ok — N jobs, M new" (with "(baseline)" on a
     first run); "failed — <reason>; attempts: n", with no job or id
     fields; "not completed — …"; "not attempted".
   - E17. Each new posting carries claude_verdict "rejected" and
     claude_line, the exact sentence of v0.5 item 7.
   - E18. Exit codes: 0 finished (with or without failures), 1 error,
     2 refused, 3 incomplete, 4 budget-exhausted.
   - E19. The tool layer gains list_dir (checked as a read), move (target
     checked as a write, never overwriting) and the GATE.md §3 write-repeat
     ledger; the policy gains a public resolve(), with no rule changes.
   - E20. Every direct network and file call in the loop goes through the
     tool layer. The persona is read through it; persona.py's own reader
     and replies.py are not used by the loop. The JS1 helpers in tools/
     still write directly; they are outside the agent.
8. Seeded runs (my decision): --seed <board_key>=<path under evidence/>,
   repeatable, with the path relative to the project folder. A seeded
   board reads that file as a 200 response body; unseeded boards are
   fetched live; the report marks each board live or seeded. A seed
   outside evidence/ is refused; a seed for a board that is not configured
   is an error.
9. Known limits, recorded and not tested:
   - If the state move fails after the report is written, the report on
     disk still says the state was written; only the printed and returned
     report records state_error.
   - Between the check that the target does not exist and the rename there
     is a small race window. It is harmless for a single run at a time.
   - The JS1 helpers in tools/ write files directly, outside the policy.
     The agent never calls them.
     
## v0.8 — 2026-11-07 (JS2, after CP8, before run 2)
Amends v0.7. Written after the W5 patch (JS2-CP8c) and before run 2.

1. An identity on every request (JS2-CP5c): every request carries
   User-Agent: js2-loop-tools-diff/0.7 (INFO 7375 course project).
   On 2026-11-06 a smoke run found api.ashbyhq.com, which sits behind
   Cloudflare, answering Python's default "Python-urllib/3.13" with 403,
   error 1010, for every board. curl confirmed it, and an honest project
   identity gets 200 for notion and 404 for js2nosuchboard. The agent
   names itself and imitates no browser or other client; if an honest
   identity were refused, the refusal would be accepted and recorded, not
   evaded. It is not a config key (v0.7 E1). Lectern does the same
   (collect.py:42). The "0.7" names the agent build that introduced it; it
   is an identity, not this contract's version, and it does not change
   with each amendment.
2. An empty board with saved ids (GATE.md v0.3 §4, W5) is adopted: a 200
   with zero jobs on a board whose saved state holds at least one id is
   "failed — empty board: 0 jobs, N ids saved before", with no retry, the
   saved ids unchanged and a live response saved as evidence. The line
   follows W5's exact wording, without the "; attempts: n" suffix of
   v0.7 E16's other failed lines; the attempts count is in the line's
   attempts field. The "0 jobs" is part of the failure reason, not the
   board's value: the line carries no jobs_fetched field, so GATE.md §4's
   "never 0 jobs" holds.
3. Version labels: from JS2-CP8e on, the agent and its report name
   GATE.md v0.3 and CONTRACT.md v0.8. Run 1's report (2026-11-07T00:06:11Z)
   is labeled contract v0.6 although the contract was v0.7 at the time;
   v0.7 recorded decisions the code already implemented, so run 1 behaved
   as v0.7 says. Run 1's report is not edited.
4. Known limits, added:
   - A board whose saved section exists but is empty, [], and which
     returns zero jobs is ok under GATE.md v0.3, since it holds no ids.
     That is correct, but no test pins it.
   - A partial drop, such as 59 jobs falling to 3, is not caught (GATE.md
     v0.3 changelog).
