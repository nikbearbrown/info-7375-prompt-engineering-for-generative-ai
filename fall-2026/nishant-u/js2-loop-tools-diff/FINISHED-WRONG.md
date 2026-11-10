# A finished wrong answer — JS2 demo run 2026-11-10-1

> **DRAFT by Claude Code for Nishant to edit.** Every quote below is copied from files saved by the run
> and the check. Nothing here is constructed or seeded: this was a live run.

## The run

- **Command:** `python -m agent2.loop --profile demo --out out/demo` (live; fresh state in `out/demo/state/`)
- **Run id:** `2026-11-10-1`, folder `out/demo/runs/2026-11-10-1/`
- **Time:** started 2026-11-10T17:42:37+00:00 (12:42:37 ET)
- **Plan:** the demo profile from GATE.md (amendment 1), boards 1–4, no deliberately failing board

## What the controller said

The loop's printed line:

```text
2026-11-10-1: exit finished; 4 requests, 0.672 s; report in out/demo/runs/2026-11-10-1/report.md
```

`report.json`, line 11:

```json
  "exit": "finished",
```

`report.json`, lines 57–66, the Greenhouse Poshmark board:

```json
      "system": "greenhouse",
      "board": "poshmark",
      "company": "poshmark",
      "url": "https://boards-api.greenhouse.io/v1/boards/poshmark/jobs?content=true",
      "status": "parsed",
      "reason": null,
      "http_status": 200,
      "postings": 0,
      "new_ids": [],
      "baseline": true
```

`report.md`, line 13:

```text
- `greenhouse:poshmark` — parsed, HTTP 200, 0 postings, baseline (ids saved; none reported as new)
```

`trace.jsonl`, line 4:

```json
{"step": 4, "action": "fetch", "system": "greenhouse", "board": "poshmark", "host": "boards-api.greenhouse.io", "path": "/v1/boards/poshmark/jobs?content=true", "http_status": 200, "bytes": 30, "sha256": "09aefc0c2d96e9c065aab057f04eaa352d63f19114f01783cfa12c890427f7f8", "decision": "parsed: 0 postings", "requests_used": 4, "boards_attempted": 4, "seconds_used": 0.672}
```

By the gate's own definition this is a correct controller status. Every planned board was attempted
within budget, and each one returned a parsed response. The agent treats Greenhouse Poshmark as a clean
board with zero postings: no failure, no warning, and an exit of `finished`.

## Why the answer is wrong

Greenhouse returned this raw body, saved verbatim as `raw/04-greenhouse-poshmark.body`
(30 bytes, sha256 `09aefc0c2d96e9c065aab057f04eaa352d63f19114f01783cfa12c890427f7f8`, fetched
2026-11-10T17:42:37+00:00):

```json
{"jobs":[],"meta":{"total":0}}
```

In the same run, Poshmark's Ashby board (`raw/03-ashby-poshmark.body`, 275869 bytes, sha256
`bb80ddb8e53fce7340cac26e439495dc2d3c10ea8ed902b4d10de2fc680e8d2e`) listed 22 postings. The first three
titles were "Software Engineer II, Cloud Platform", "Staff Software Engineer, Web" and
"Senior Software Engineer II, Machine Learning".

So "Poshmark: 0 postings" is not a fact about Poshmark's hiring. The 200-with-empty-list response is the
same shape Lectern's `ATS.md` describes for HubSpot's wrong slug: a valid empty board, not an error. My
hypothesis is that Poshmark's postings are on Ashby and the Greenhouse board is left over. I have not
verified that.

## The independent check that caught it

`python -m agent2.check out/demo/runs/2026-11-10-1` reads only `raw/*.body` and their sidecars. It never
reads `report.json` or `trace.jsonl`, and it counts postings with its own JSON reading, not
`agent2.providers`. The two flags from its full output (saved as `out/demo/check-2026-11-10-1.json`):

```json
  "verdict": "flags raised",
  "flags": [
    {
      "kind": "zero-postings",
      "board": "greenhouse:poshmark"
    },
    {
      "kind": "cross-system",
      "company": "poshmark",
      "counts": {
        "ashby": 22,
        "greenhouse": 0
      }
    }
  ],
```

It also confirmed `sha256_ok: true` for all four bodies, so it judged the bytes the agent received.

## What this shows and does not show

- **Shows:** a run can end `finished`, with an exit that is accurate at the controller layer, while
  the result it carries is contradicted at the evidence layer. The contradiction was found by the
  check, not by the agent's report.
- **This run was a baseline.** The state was fresh, so the report says "baseline (ids saved; none
  reported as new)", not "0 new". The state now records `greenhouse:poshmark` as a seen board with no
  ids. A second demo run against `out/demo/state/` would report it as "0 new". That run has not been
  done.
- **Does not show:** why Greenhouse returns an empty Poshmark board, or that Ashby's 22 is the complete
  picture. The check's cross-system rule is a threshold I set in GATE.md (0 on one system, at least 1 on
  another). It would miss a board that is stale but not empty, and a company that is on only one system.

_Nishant: edit, then sign or withhold._
