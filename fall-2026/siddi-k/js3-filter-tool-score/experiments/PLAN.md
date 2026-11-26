# What moves the score: the plan, written before any variant is scored

Written by Claude on 2026-11-26 (about 03:40 UTC, 22:40 ET on 2026-11-25), before any Claude variant ran and before Siddi's hand labels existed. It is committed before scoring so the comparisons can't be chosen after seeing results.

## The held-out set H (30 postings)

- 20 come from the blind sheet. Siddi labels them in the same sitting as the reject audit, without knowing which items they are.
  - `held_out_A`: 12 drawn by seed 7376 from titles containing data, machine learning, ml, ai, analytics, analyst or scientist.
  - `held_out_B`: 8 drawn from everything else.
  - Neither group overlaps the audit items.
- 10 are JS1's held-out Stripe postings, which Siddi labelled on 2026-10-31. They were never used in JS3. 3 of the 10 are relevant.
- **Known before scoring:** the 20 new items are mostly "AI Sales" and other non-engineering titles. Their relevant count is unknown until Siddi labels them, but it may be 0. If it is, H has about 3 relevant postings, so each one moves relevant-recall by a third. **No result on H can show a difference smaller than that.**
- **Audit labels are development data.** They (random rejects, close calls, kept) are used to find problems and to fit numbers. They are never used to score a change.

## One change at a time

Each variant differs from its baseline in exactly one object.

| Variant | Object changed | What changed | Baseline |
|---|---|---|---|
| filter v1.1 | the filter file | adds `us_place_names` (14 US city names and abbreviations, hand-set from the collection's own location strings, no labels used) | filter v1 |
| filter v1.2 | the filter file | drops Notion's blurb sentence (the false friend "ai") | filter v1 |
| B | (baseline) | JS1 `judge_v1` prompt, filter-v1 requirements text, `claude-sonnet-5-5`, no tools | |
| P | the prompt | `judge_v2`: JS1's pre-registered sentence that treats senior titles and over-cap years as not worth it | B |
| C | the context | one added candidate line with Siddi's LABELING.md answers, verbatim; instructions unchanged | B |
| T | the tool list | the `score_posting` MCP tool is available, plus one line naming the posting's board and id, which the tool needs | B |
| S | a setting | model `claude-haiku-5-5` | B |

Fitting one number happens after the audit labels exist: `keep_threshold`, fitted on the audit labels (development data only), then tested once on H. It is reported as **fitted**.

## What is measured

- On H, against Siddi's labels: agreement count, true and false positives, false negatives, true negatives, and no-answer counts. A filter "cannot tell" or an invalid Claude output counts as no answer.
- No percentages are reported without their counts.

## Decision rule (Siddi decides; this is a recommendation)

- A filter change is recommended for adoption only if it fixes at least one H error and adds none.
- A Claude change is never adopted on H alone. H is too small, and the Claude stage is not part of the filter Siddi signs.

## What persistence is not proof of

Any difference between B and a variant comes from the prompt, the context, the tools or the setting sent with that call. Every call starts in a new, empty directory with `--no-session-persistence`. No weights change, and nothing carries from one call to the next. If a behaviour looks like it "stuck" across sessions, the cause is something we sent again: a file, a prompt, a tool. It is not evidence that anything was trained.
