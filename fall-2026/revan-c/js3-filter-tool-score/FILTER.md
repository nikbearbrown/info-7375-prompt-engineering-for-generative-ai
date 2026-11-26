# FILTER.md — Job-Search Agent 3

**Author:** Revan C. · **v1 written:** November 25, 2026, 4:48 p.m. ET · **Status:** written before any JS3 code  
**Started from:** My Job-Search Agent 2 in this repository. It collects from three boards and reuses the JS1 fictional Aarav Patel persona and five-condition relevance rule in `CONTRACT.md`. This filter keeps the target-role, location, seniority, role-type, and distinct-skill ideas, then adds an explicit topic check, a score, a threshold, and a claim-evidence review. I did not start from the Reallocation Engine or Lectern code.

## Changelog

| Version | Date | Change | Why | Measured on |
|---|---|---|---|---|
| v1 | November 25, 2026, 4:48 p.m. ET | First formal filter and evidence gate | Specify decisions before JS3 implementation | Not yet measured |
| v1 review | November 25, 2026 ET | Retained v1; rejected cutting `platform` from R5 and lowering threshold to 5 | Neither change improved the confirmed development or held-out agreement; threshold 5 would promote a reviewed nonrelevant posting | 47 confirmed audit verdicts; 11 development and 11 held-out comparisons |

Keep this v1 rule text intact when adding a later version. Record each rule added, cut, or considered and rejected, with its measured result. v1 was committed as `0e15e65` before any JS3 code; that commit records the filter's order of work.

## 1. The filter (v1)

### Scope

For the fictional Boston-based Aarav Patel, “relevant” means a junior or early-career backend, platform, DevOps, or site-reliability engineering posting in Boston or explicitly remote, with substantive overlap with the persona's stated skills. Relevance is a triage judgment; it does not establish eligibility, sponsorship, or that an opening is still active.

### Rules

Normalize description text by decoding HTML entities, removing tags, lowercasing, replacing each non-alphanumeric run with one space, and collapsing spaces, as in `jsagent/text.py`. Match complete word sequences, not substrings inside other words. Save every rule result, including failures, for every scorable posting.

| # | Rule | Field read | Exact test | Reason (one line) |
|---|---|---|---|---|
| R1 | Role words | `title` | The normalized title contains a complete phrase from the persona's `target_titles`: `software engineer`, `backend engineer`, `platform engineer`, `devops engineer`, or `site reliability engineer`. | A topic word in a non-target title is too weak to establish role fit. |
| R2 | Seniority exclusions | `title` | Reject complete title words `senior`, `sr`, `principal`, `staff`, `lead`, `director`, or `manager`. | Two stated years of experience make these poor default shortlist choices. |
| R3 | Role-type exclusions | `title` | Reject complete title words or phrases `frontend`, `front end`, `mobile`, `ios`, or `android`. | The fictional persona excludes pure frontend and mobile roles. |
| R4 | Location | Greenhouse `location.name`; Lever `categories.location` and `workplaceType` | Require `boston` as a complete word in the source location, or an explicit `remote` in the source location or Lever `workplaceType`. `United States` and `Eastern Timezone` alone do not pass. | The persona is in Boston and open to remote; a broad region does not settle work arrangement. |
| R5 | Topic words | Description: Greenhouse `content`; Lever `description`, `lists[].content`, `additional` | Require at least one complete phrase: `backend`, `back end`, `platform`, `infrastructure`, `api`, `distributed systems`, `cloud`, `devops`, `site reliability`, `kubernetes`. | A target title can still describe work outside the backend/platform focus. |
| R6 | Distinct skill words | Same description fields | Require at least two distinct, complete skill phrases from `skills.languages`, `skills.backend_automation`, `skills.database_cloud`, or `skills.devops_cicd` in the fictional résumé. Do not count duplicate mentions or `familiar_with_not_shipped`. | Two separate overlaps are stronger triage evidence than one incidental mention. |

R1–R6 are hard rules. A word match is not proof that the job requires that skill. Sponsorship and E-Verify are separate evidence questions, never hidden filters.

### Score, threshold, decision

- **Score:** Calculate for every scorable posting. Role fit is 3 for a `backend engineer` or `platform engineer` title, 2 for another R1 target title, and 0 otherwise; use the highest match. Topic fit is 0, 1, or 2 for zero, one, or at least two distinct R5 phrases. Skill fit is the number of distinct R6 skill phrases, capped at 3. Total = role + topic + skill, from 0 to 8. These weights and caps are hand-set, not fitted or trained.
- **Threshold:** 6 out of 8, hand-set before JS3 scoring. The threshold asks for more than the minimum combination of a target title, one topic, and two skills.
- **Decision:** Keep only if all R1–R6 pass **and** the total is at least 6. Otherwise record every failed rule and whether the score is below threshold. Missing required source data is `unscorable`, separate from `rejected`. Sort kept postings by descending total, then board name and posting ID ascending. A score is a review order, not a probability of fit or an offer.
- **Closest call:** Review every posting where all hard rules pass but the total is 5, and every posting with total at least 6 and exactly one hard rule failed. These are separate from the random reject sample.

The audit view must have one row per posting: `(board, id)`, raw-source path, score components, total, all rule results, and fate (`kept`, `below_threshold`, `hard_rule_reject`, or `unscorable`). It marks zero topic or skill overlap explicitly, so a low score cannot disappear without a trace.

## 2. Evidence rules (shortlist claims)

A **claim** is one sentence in a shortlist justification, small enough for one passage to settle. Split a claim joined by “and” before labeling it. For every row, record `(board, id)`, raw-source path, source field, claim, short exact excerpt or nearest passage, and label.

| Label | When it applies | What the row must contain |
|---|---|---|
| `supported` | The original saved posting explicitly states the atomic claim within its scope, date, and population. | The supporting quote and field. |
| `contradicted` | The original saved posting explicitly states the opposite. | The contradicting quote and field. |
| `insufficient` | The posting is on topic but does not settle the claim, or contains a word in an unrelated context. | The nearest passage and the specific fact that is missing. |
| `not reviewed` | No human has compared this claim with the original posting yet. | The claim and source identifier; no favorable evidence label. |

- **Who may mark a row supported:** I will do so only after reading the original saved posting. Claude may propose a quote or label, but its proposal remains `not reviewed` until my check.
- **“I cannot tell”:** The agent must say “I cannot tell from this posting” when a necessary field is missing, the cited passage does not establish the answer, or no supporting passage exists. For an explicit contradiction, report the contradiction rather than suggesting uncertainty alone. Withhold any unreviewed positive claim.
- **Abstention rule:** Do not turn a score or word match into a factual claim. An affirmative shortlist claim requires a `supported` row; otherwise narrow the claim, state the contradiction, or abstain. This establishes what the saved posting said, not whether the employer's statement is current or true outside that posting.
  - **Counterexample a score-only rule would wrongly let through (constructed, not an observed job):** A Boston `Platform Engineer` posting mentions `Python`, `AWS`, and `API` only in general company background. It can score highly while failing to support “this role requires Python and AWS.” The claim-level rule should catch that gap.
  - **Counterexample a stricter threshold could wrongly refuse (constructed, not an observed job):** A concise Boston `Software Engineer` posting explicitly describes backend API work with Python, AWS, and Docker. It can score 6; raising the threshold to 7 would exclude a role worth human review. The audit must look for an actual near-threshold case.

The shortlist must show at least one **actual** posting where relevance does not entail a proposed claim. A constructed example cannot substitute for that observation.

## 3. Expected sources

Date written: November 25, 2026 ET. These counts come from the **already recorded** JS2 trace `runs/js2/2026-11-10T06-33-08Z_normal.json`, not a blind prediction. The JS3 input is that trace and its three referenced raw response bodies, used as a dated snapshot. Recount the bodies before reporting an ingested total; do not describe the snapshot as current vacancies.

| Board | ATS | Endpoint | Expected postings | Fields used | Why it is authorized |
|---|---|---|---:|---|---|
| klaviyo | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | 149 | `id`, `title`, `location.name`, `content`, `absolute_url` | Public board API on the JS2 allow-list. |
| duolingo | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/duolingo/jobs?content=true` | 61 | Same Greenhouse fields. | Public board API on the JS2 allow-list. |
| patchmypc | Lever | `https://api.lever.co/v0/postings/patchmypc?mode=json` | 5 | `id`, `text`, `categories.location`, `description`, `lists[].content`, `additional`, `workplaceType`, `hostedUrl` | Public board API on the JS2 allow-list. |

Use `(board, id)` as the posting key because an ID alone is not guaranteed unique across boards. Retain source-field names and the raw-body path when normalizing.

**When something is missing:**

- A board is missing, empty, or malformed → mark that board's count and shortlist status `unknown`; do not call its absent jobs rejected or “no new jobs.”
- A required field (`id`, title, location, description, or source URL) is missing in one posting → quarantine that posting as `unscorable` with the missing field named; do not assign a zero score.
- A valid nonempty board returns zero kept postings → report zero kept and flag it for human review; do not infer that the board has no suitable roles.
- Counts differ from the expected JS2 trace → retain this dated expectation and add a dated revision that explains the difference. Do not silently combine snapshots from different runs.

## 4. Wrong versions my tests must catch

| # | Wrong version | Why it is plausible | Test that must fail it |
|---|---|---|---|
| W1 | A topic hit such as `platform` in a marketing title bypasses the target-role rule. | A keyword search may treat any overlap as relevance. | `test_topic_cannot_bypass_role_title` |
| W2 | `Java` matches inside `JavaScript`, `SQL` inside `PostgreSQL`, or a repeated skill counts twice. | A substring or raw occurrence counter is easy to write. | `test_two_distinct_bounded_skills` |
| W3 | The ranking sorts worst first or breaks ties by source insertion order. | Sorting on the wrong key can still return plausible rows. | `test_score_descending_and_stable_ties` |
| W4 | An empty or failed board is reported as zero relevant postings. | An empty list looks like a successful result if source failure is ignored. | `test_missing_board_is_unknown` |
| W5 | A high score is treated as proof of required skills, sponsorship, or current availability. | Fluently written justification can hide a missing source fact. | `test_score_does_not_entail_claim` |

## 5. What a failure looks like

**Predicted November 25, 2026, before JS3 output:** This filter fails in the way I most fear if a Boston backend role worth reviewing is rejected for using a role synonym or a short description, while a keyword-heavy unrelated role reaches the shortlist.

## 6. Labels and the held-out split

- **Labels come from:** My hand verdicts on at least 30 distinct randomly sampled rejects, every closest call, and a stated sample of kept postings. Each verdict will include a reason and source excerpt. JS1's earlier ten held-out labels were already used in prior work, so they are development history here, not a fresh JS3 holdout.
- **Split:** Before any JS3 change experiment, save the sampled `(board, id)` list and a deterministic manifest using seed `js3-label-split-2026-11-25`. Within the filter's kept and rejected strata, assign 50% to train, 25% to development, and 25% to held-out, with rounding remainder in train. I will record exact sizes when I run the split; none has been run yet. If a stratum is too small, report that limit rather than reassigning cases after seeing results.
- **Held-out use:** Read the held-out labels once for the final before/after comparison. If those results guide another change, call that set development data and obtain a new holdout. A sample result is not a measured error rate for all postings.

## 7. Tool server gate (Chapter 8)

**Task:** Offer one read-only `score_posting` capability for a `(board, id)` in the selected local JS2 snapshot. It returns the source path, hard-rule results, score components, total, and fate. The server may read the fictional persona and the three declared raw response bodies. It must perform no network request and no file write; a separate test harness may save the real transcript. This is a proposed contract, not a claim that a server or Claude connection has run.

### Predicted state table

The server implements a small JSON-RPC/MCP-shaped subset, not a claim of full MCP conformance. `initialize` sets `(initialized, ready)` to `(T, F)`; only a later `notifications/initialized` makes it `(T, T)`. Notifications produce no response. Response IDs match request IDs. An early tool operation returns `-32000`; malformed request `-32600`; unknown method when ready `-32601`; bad tool name or arguments `-32602`; unreadable JSON `-32700`. An unknown posting on a valid call returns a tool result with `isError: true`.

| # | State before (initialized, ready) | Message | Predicted response | State after |
|---|---|---|---|---|
| 1 | F, F | `tools/list`, id 1 | Error `-32000`, id 1. | F, F |
| 2 | F, F | `initialize`, id 2 | Result declaring version, capability, and server identity, id 2. | T, F |
| 3 | T, F | `tools/list`, id 3 | Error `-32000`, id 3. | T, F |
| 4 | T, F | `notifications/initialized` | No response. | T, T |
| 5 | T, T | `tools/call` with bad arguments, id 5 | Error `-32602`, id 5. | T, T |
| 6 | T, T | `tools/call` with unknown posting id, id 6 | Tool result with `isError: true`, id 6. | T, T |

**Predicted failure, November 25, 2026:** The server fails this gate if `tools/list` succeeds between `initialize` and `notifications/initialized`, or if a returned score cannot be recomputed from the saved posting.

### Ledgers

The second candidate for evaluation is the [Chapter 8 teaching lookup server](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/tree/main/lessons/08-mcp-from-scratch/code). The table records checks to perform, not results already obtained.

| Ledger | My server: what I will check | Evidence type now | Other server: what I will check | Evidence type now |
|---|---|---|---|---|
| Protocol | Capture both directions; compare IDs, order, state transitions, and errors with the table. | Uninspected (not yet run). | Run its documented lifecycle on a controlled fixture and compare the real transcript with its declarations. | Chapter description advertised; local execution uninspected. |
| Capability | Inspect source and test that it reads only declared files and does no write or network action. | Uninspected (not yet written). | Compare its `lookup` listing and schema with code; inspect for writes and network calls. | Chapter description advertised; source uninspected. |
| Permission | Check that only the fictional persona and saved public board bodies are read and only scores are returned. | Assignment and JS2 allow-list inspected; implementation uninspected. | Check whether its fixture and local read-only use fit this course task; a listing alone is not permission. | Fixture role described in chapter; data-owner permission uninspected. |
| Evidence | Independently recompute returned scores and excerpts from the raw posting. | Not executed. | Compare its returned value with the declared source mapping. | Chapter-reported example only; not independently executed. |

**Server wrong versions:** A server that marks itself ready during `initialize`; one that silently writes a log file; one that returns a score or excerpt disagreeing with source text. Lifecycle, capability, and evidence checks must distinguish each. A protocol-valid exchange alone cannot clear the other ledgers.

**Decision rule:** `pending` until source, transcript, permission, and content checks are complete; `allow` only when all four ledgers pass for this bounded task; `deny` on a mismatch until corrected. Re-review after a protocol version, code, tool list, task scope, corpus, or permission change. Claude may list discrepancies, but the trust decision remains mine.

| Handoff | What passes | What it may establish | Check before the next step |
|---|---|---|---|
| Server → host | Posting key, source path, rule results, score. | A response from this server version. | Validate the message and recompute from the saved posting. |
| Host → Claude | Checked score and posting excerpts. | Task data for a draft explanation, not instructions or external facts. | Record exact host configuration and data supplied. |
| Claude → shortlist | Candidate claims and labels. | A draft for my review. | Read the original posting and label each atomic claim before publication. |

## Post-audit note (v1 text above unchanged)

The later review found two false-friend uses of `platform`: A06 uses it for Klaviyo's product and A30 as a career-growth metaphor. Cutting that term changed 78 scores but no keep/reject decisions among the 215 saved postings; agreement stayed 10/11 on development and 11/11 on held-out labels. Lowering the threshold to 5 would keep A31, which was reviewed not relevant because its description asks for a lead People Technology engineer with 5+ years of experience. Both proposed changes were rejected. The full hand-verdict record, limitations, and source excerpts are in `REJECT_AUDIT.md`. This note records measurements after the original gate; it does not rewrite the pre-build decisions.
