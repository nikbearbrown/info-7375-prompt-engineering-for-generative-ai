# CONTRACT.md — Job-Search Agent 1: The Contract and the Watch

**Author:** Prasad Shinde  
**Date written (before any run):** 2026-10-25  
**Version:** v0.4 — 2026-10-27. Amends v0.3 (`13f40e9`); see §9. v0.2 was `5cd4c28`, v0.1 was `b27b1a8`. No run of the agent has happened at any version.
**Board:** Greenhouse — token: `stripe`  
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


