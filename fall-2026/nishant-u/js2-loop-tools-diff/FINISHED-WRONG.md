# A finished wrong answer — JS2 demo run 2026-11-10-2

> **DRAFT by Claude Code for Nishant to edit.** Every quote below is copied from files saved by the runs
> and the check. Nothing here is constructed or seeded: both runs were live.

## The runs

| Run | Command | Started (UTC) | State | Role here |
|---|---|---|---|---|
| `2026-11-10-1` | `python -m agent2.loop --profile demo --out out/demo` | 2026-11-10T17:42:37+00:00 | fresh `out/demo/state/` | context: the baseline |
| `2026-11-10-2` | the same command, run again | 2026-11-10T17:46:28+00:00 (12:46:28 ET) | the state run 1 wrote | **the main example** |

Both use the demo profile from GATE.md (amendment 1): boards 1–4, with no deliberately failing board.

**Run 1, for context.** The state was fresh, so every board was a baseline. Its `report.md` said
"`greenhouse:poshmark` — parsed, HTTP 200, 0 postings, baseline (ids saved; none reported as new)". It
also recorded `greenhouse:poshmark` in the state as a board already seen, with no ids. That set up run 2
to report it as "0 new".

## What the controller said (run 2)

The loop's printed line:

```text
2026-11-10-2: exit finished; 4 requests, 0.672 s; report in out/demo/runs/2026-11-10-2/report.md
```

`out/demo/runs/2026-11-10-2/report.json`, line 11:

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
      "baseline": false
```

`report.md`, lines 3, 5, 12 and 13:

```text
- Exit (controller status): **finished**
- Used: 4/10 requests, 4/5 boards, 0.672/60 s
- `ashby:poshmark` — parsed, HTTP 200, 22 postings, 0 new
- `greenhouse:poshmark` — parsed, HTTP 200, 0 postings, 0 new
```

`trace.jsonl`, line 4:

```json
{"step": 4, "action": "fetch", "system": "greenhouse", "board": "poshmark", "host": "boards-api.greenhouse.io", "path": "/v1/boards/poshmark/jobs?content=true", "http_status": 200, "bytes": 30, "sha256": "09aefc0c2d96e9c065aab057f04eaa352d63f19114f01783cfa12c890427f7f8", "decision": "parsed: 0 postings", "requests_used": 4, "boards_attempted": 4, "seconds_used": 0.672}
```

By the gate as written before the review-packet amendment, this is a correct controller status. Every
planned board was attempted within budget, and each one returned a parsed response. The report puts
"0 new" for an empty board beside "0 new" for a board with 22 postings, and nothing in it tells them
apart.

## Why the answer is wrong

Greenhouse returned this raw body, saved verbatim as `raw/04-greenhouse-poshmark.body` (30 bytes, sha256
`09aefc0c2d96e9c065aab057f04eaa352d63f19114f01783cfa12c890427f7f8`, fetched 2026-11-10T17:46:29+00:00).
The bytes and hash are identical to run 1's:

```json
{"jobs":[],"meta":{"total":0}}
```

In the same run, Poshmark's Ashby board (`raw/03-ashby-poshmark.body`, sha256
`bb80ddb8e53fce7340cac26e439495dc2d3c10ea8ed902b4d10de2fc680e8d2e`, also identical to run 1) listed 22
postings.

"Poshmark on Greenhouse: 0 new" reads as "nothing new at Poshmark", and the record does not support
that. A 200 with an empty list is the same shape Lectern's `ATS.md` describes for HubSpot's wrong slug:
a valid empty board, not an error. My hypothesis is that Poshmark's postings are on Ashby and the
Greenhouse board is left over. I have not verified that.

## The independent check that caught it

`python -m agent2.check out/demo/runs/2026-11-10-2` reads only `raw/*.body` and their sidecars. It never
reads `report.json` or `trace.jsonl`, and it counts postings with its own JSON reading, not
`agent2.providers`. The verdict and flags from its full output (saved as
`out/demo/check-2026-11-10-2.json`):

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

It also confirmed `sha256_ok: true` for all four bodies, so it judged the bytes the agent received. Run 1's
check (`out/demo/check-2026-11-10-1.json`) raised the same two flags.

## What this shows and does not show

- **Shows:** a run can end `finished`, accurate at the controller layer, and report "0 new" for a board
  whose raw response contradicts what that phrase suggests. The contradiction was found by a check that
  reads the raw responses, not by the agent's report.
- **Does not show:** why Greenhouse returns an empty Poshmark board, or that Ashby's 22 is the complete
  picture. The cross-system rule is a threshold I set in GATE.md (0 on one system, at least 1 on
  another). It would miss a board that is stale but not empty, and a company that is on only one system.
- **Next:** the review packet (`REVIEW-PACKET.md`) changes the loop so that an empty board becomes
  `unverified-empty` and the run ends `incomplete`.

_Nishant: edit, then sign or withhold._

After the patch (commit cd15d19), the same live demo ended incomplete, with Greenhouse poshmark marked unverified-empty (out/demo-postpatch/runs/2026-11-10-1).
