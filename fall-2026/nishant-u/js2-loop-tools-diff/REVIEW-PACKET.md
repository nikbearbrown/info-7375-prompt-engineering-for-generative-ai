# Review packet — Job-Search Agent 2 (Chapter 6)

> **DRAFT by Claude Code for Nishant to edit.** Defect and Reproduction are filled in from saved files.
> Every later section is empty until the patch exists and has been reviewed.

## Defect

A board that returns HTTP 200 with an empty `jobs` list is treated as a clean result:

- The board's status is `parsed`, and its `new_ids` is `[]`.
- If the board was seen before, `report.md` says "0 postings, 0 new", the same words it uses for a board
  with postings and nothing new.
- If the board was never seen, it is reported as a baseline and recorded in the state as a seen board.
  The next run then reports it as "0 new".
- If every other board parsed, the run's exit is `finished`.

The rule broken is GATE.md's amendment "2026-11-10, before the review-packet patch". An empty board's
status must be `unverified-empty`, it must never be reported as "0 new", its (zero) IDs must not be
merged into state, and the run's exit must be `incomplete`.

Why it matters: on 2026-11-10 Greenhouse `poshmark` returned `{"jobs":[],"meta":{"total":0}}`, while
Poshmark's Ashby board listed 22 postings in the same run. "0 new" for Poshmark on Greenhouse reads as
"nothing new at Poshmark", and the raw responses do not support that (FINISHED-WRONG.md).

The fault is in `agent2/loop.py`, in `Loop._do_board`: any HTTP 200 body that parses becomes
`status="parsed"` whatever its length. `exit_status` and `render_markdown` then treat it like any other
parsed board. That location comes from reading the source. The behaviour below is what was observed.

## Reproduction

**Live, run `2026-11-10-2`** (second demo run, against the state run `2026-11-10-1` wrote). Started
2026-11-10T17:46:28+00:00.

```bash
python -m agent2.loop --profile demo --out out/demo
```

Printed:

```text
2026-11-10-2: exit finished; 4 requests, 0.672 s; report in out/demo/runs/2026-11-10-2/report.md
outcome check (separate): python -m agent2.check out/demo/runs/2026-11-10-2
```

`out/demo/runs/2026-11-10-2/report.json`, line 11 and lines 61–66 (Greenhouse poshmark):

```json
  "exit": "finished",
```

```json
      "status": "parsed",
      "reason": null,
      "http_status": 200,
      "postings": 0,
      "new_ids": [],
      "baseline": false
```

`report.md`, line 13:

```text
- `greenhouse:poshmark` — parsed, HTTP 200, 0 postings, 0 new
```

Raw body `raw/04-greenhouse-poshmark.body`, 30 bytes, sha256
`09aefc0c2d96e9c065aab057f04eaa352d63f19114f01783cfa12c890427f7f8`:

```json
{"jobs":[],"meta":{"total":0}}
```

The independent check (`out/demo/check-2026-11-10-2.json`) flagged `zero-postings greenhouse:poshmark`
and `cross-system poshmark {"ashby": 22, "greenhouse": 0}`.

**Run `2026-11-10-1`**, the first demo run on fresh state, showed the never-seen form. Its `report.md`
said "`greenhouse:poshmark` — parsed, HTTP 200, 0 postings, baseline (ids saved; none reported as new)",
and the state it wrote lists `greenhouse:poshmark` among the seen boards.

**Offline, before the patch:** the regression test `tests/test_js2_review.py` (below) reproduces both
forms with fakes. Before any patch, on the current code (commit `c050acd` plus this test), it observed:

| Case | exit | status | new_ids | "0 new" in report.md | poshmark in state (before → after) |
|---|---|---|---|---|---|
| seen | `finished` | `parsed` | `[]` | yes: "0 postings, 0 new" | seen → seen |
| fresh | `finished` | `parsed` | `[]` | no: "baseline (ids saved; none reported as new)" | not seen → **seen** |

## Allowed-file list for the patch

- `agent2/loop.py`
- `tests/test_js2_review.py` (the new regression test, written before the patch)

Nothing else changes unless this list is widened here, dated, with the reason.

## Regression test

## Diff

## Diff read as behavior

## Scope check

## Commands I ran myself

## Decision

## What this test would still miss
