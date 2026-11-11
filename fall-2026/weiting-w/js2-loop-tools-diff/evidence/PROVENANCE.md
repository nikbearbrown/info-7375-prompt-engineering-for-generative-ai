# Provenance of every file under `evidence/`

One rule: **a reader must be able to tell, for any byte in this directory,
whether a job board sent it.** Three origins, three directories, and nothing
shares a directory with something of a different origin.

| directory | origin | can it be cited as evidence about a real board? |
|---|---|---|
| `evidence/raw/` | live HTTP responses, captured by `agent.loop` | **yes** |
| `evidence/fixtures/` | a live response captured by JS1, carried over | **yes**, for 2026-10-31 |
| `evidence/seeded/` | constructed by hand, or replays of the above | **no** |
| `evidence/runs/`, `evidence/state/` | written by the loop about its own runs | they describe runs, not boards |

`tools/crosscheck.py` reads `--raw-dir`, which defaults to `evidence/raw/`.
Pointing it at `evidence/seeded/` is how the finished-wrong-answer
demonstration is run, and the `--raw-dir` argument appears in that report's
transcript so it cannot be mistaken for a run against real data.

---

## `evidence/fixtures/` — carried over from JS1

### `js1-greenhouse-reddit-20261031.json`
- **sha256** `8871e1bb5de49c071f3b661a7d59e5fc879b29c187dd0a90409521aa479b86d5`
- **A real HTTP response.** `GET https://boards-api.greenhouse.io/v1/boards/reddit/jobs`,
  HTTP 200, 163 postings, captured **2026-10-31T02:25:28Z** by Weiting on her
  own Mac during JS1, as `evidence/raw/20261031T022528Z-reddit.json` in
  `fall-2026/weiting-w/js1-contract-and-watch/`. Byte-identical to that file;
  the sha256 above is the one JS1 recorded.
- Renamed on the way in, to say in the filename which board, which day, and
  that it came from JS1. Not re-fetched, not edited, not reformatted.
- **What it is used for.** The R-v2 → R-v3 baseline
  (`tests/test_rule_carried_over.py`), the G4 defect reproduction
  (`tests/test_review_g4_location.py`), and the "previous count" side of the
  wrong-answer demonstration.

### `js1-rv2-verdicts.json`
- **sha256** `e1854d5020a65b14064a39cb60e91fcb2817b80755651698dede7fd864af88e2`
- **Computed, not captured.** 163 verdicts produced by running **JS1's own
  committed `jobagent.rule`** (R-v2) over the response above, by
  `tools/make_rv2_baseline.py` on 2026-11-09.
- Its own `provenance` block records the JS1 rule version, the JS1 path, and
  the source sha256. `test_the_baseline_is_the_one_js1_committed` re-hashes the
  response and refuses to run if the two disagree, so this file cannot be
  silently paired with different bytes.
- Tally: `{G1_title_block: 143, relevant: 11, G2_discipline: 8, G3_job_family: 1}`.

## `evidence/seeded/` — nothing here came from a board

Everything in this directory is **SEEDED**, and `reports/wrong-answer.md` says
so in its first paragraph. Both runs below used `--replay-from`; no request was
made to any host.

### `replay-wrong-answer/greenhouse-reddit.json`
- **sha256** `dfa9e6f090a401734b450fba0fe63593ee6d527102b8f5e2b73b9531c388d89d`
- **CONSTRUCTED BY HAND** on 2026-11-09. HTTP-200-shaped, valid JSON, correct
  schema, `"jobs": []`. It carries its own `_seeded` field saying in its own
  bytes that `boards-api.greenhouse.io` never sent it, so the label survives
  being copied out of this repository.

### `replay-real/greenhouse-reddit.json`
- **sha256** `8871e1bb5de49c071f3b661a7d59e5fc879b29c187dd0a90409521aa479b86d5`
- A **copy of the real JS1 capture**, renamed to the filename
  `loop.replay_fetcher` looks for. Same sha256 as the fixture, so it is the
  same bytes and can be checked to be. Real bytes, replayed — not a live fetch,
  which is why the run report records `mode=replay:evidence/seeded/replay-real`.

### `wrong-answer/20261109T220101Z-greenhouse-reddit.json`
- sha256 `8871e...86d5` — written by run 1 of the demonstration. 163 postings.
  Identical bytes to the real capture, because run 1 replayed it.

### `wrong-answer/20261109T220103Z-greenhouse-reddit.json`
- sha256 `dfa9e...d89d` — written by run 2. The empty response. **This is the
  file the loop called `finished` on.**

### `runs/`, `state/`
- Written by the two demonstration runs: two run reports, two JSONL traces, one
  state file. Each run report records `mode`, so a replay can never be read as
  a live fetch, and the `label` field of each says `SEEDED run 1 of 2` /
  `SEEDED run 2 of 2`.
- `state/seen.json` is the file whose `last_count` went 163 → 0 without
  complaint. It is kept precisely because it is wrong;
  `reports/wrong-answer.md` §4 explains it.

## `evidence/raw/`, `evidence/runs/`, `evidence/state/` — the live run

The live multi-board run of **2026-11-11T00:18Z** (2026-11-10, 7:18pm ET): four
real HTTP 200 responses, the run report, the trace, and the state file.

**Fetched by Weiting, on her own Mac, in her own Terminal.** The cloud container
this repository was built in cannot reach any of the three applicant-tracking
hosts — every CONNECT is refused 403 by the egress proxy — and neither can the
Linux VM that bridges to her machine, where `curl` returns status `000` for all
four boards. Only her own Terminal has a route out, which is also how JS1's
capture was made. The full terminal output is in `README.md` under "What I ran
myself".

| file | board | postings | sha256 |
|---|---|---|---|
| `raw/20261111T001811Z-greenhouse-reddit.json` | `greenhouse:reddit` | 157 | `f9e53e5f788db378e247d4ff7f0844b63c4cb070de21dd5b3ca2ba2abb607615` |
| `raw/20261111T001812Z-lever-spotify.json` | `lever:spotify` | 85 | `8303a53fde8c3ec9f000464ea0b04326d0ac50bf7f9a4f687db95418f52035de` |
| `raw/20261111T001812Z-ashby-ramp.json` | `ashby:ramp` | 177 | `f35232d7d376223a043da726cb878931965773d6ed50f1097944b82d432ddcf5` |
| `raw/20261111T001812Z-ashby-linear.json` | `ashby:linear` | 33 | `ac2e34215a8b41df85b357494c444e8df2505cc8d762cfd6951d7f9bd2e3d35a` |

452 postings, one GET per board, no authentication.

**There is no fifth file, and that is the point.** The plan contains five
boards. `greenhouse:js2-no-such-board-9f3a` answered 404, was classified
`permanent`, was not retried, and wrote nothing — a board that was never
observed has no response to save and no count to report. `runs/run-20261111T001812Z.json`
records it as `postings_seen: null`, not `0`; reporting it as `0` is wrong
version W1.

- `runs/run-20261111T001812Z.json` — the run report. `mode: live`, exit status
  `incomplete`, `complete: false`.
- `runs/trace-20261111T001811Z.jsonl` — five observations, one per board
  attempt, written as they happened. The exit status is derived from these, not
  asserted (GATE.md §1 E2).
- `state/seen.json` — 452 ids, namespaced `provider:id`. First run, so every
  posting was recorded as seen and none was reported as new.

**Note on the code version.** An earlier live run at 00:12Z used a copy of the
code taken before this repository's last three commits. Its files are **not**
here; the run was repeated from a clean copy of the submitted code and this is
that second run, so the code in this repository is the code that produced these
bytes. `README.md` records both runs.

## What is deliberately not here

- **No real résumé.** `data/resume.persona.json` is a fictional persona.
  `*.real.json` is unreadable by the agent in code, not by convention
  (`agent/policy.py`, boundary case 16), so the real résumé cannot be read even
  by accident.
- **No credentials, no tokens, no cookies.** The agent authenticates to
  nothing; every endpoint is a public job board read with an unauthenticated
  GET.
- **No caches.** `__pycache__/` and `.pytest_cache/` are in `.gitignore`.
- **No contacts, tracker, or conversation transcripts.**

## Checking this file

```
find evidence -name '*.json' -type f | sort | xargs sha256sum
```

Every sha256 quoted above is reproducible from the committed bytes with that
command. If one differs, this file is wrong and should be trusted less than the
bytes.
