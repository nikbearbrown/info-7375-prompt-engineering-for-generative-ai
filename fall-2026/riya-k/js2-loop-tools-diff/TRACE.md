# The trace: one real run, the deliberate failure, and the finished-wrong-answer

Every run writes three files: `report-<run_id>.json` (machine-readable), `report-<run_id>.md` (readable),
and `trace/<run_id>.jsonl` (every observation in order: each policy decision, request, response, retry wait,
board result, budget stop, and the exit). Raw responses are in `raw/`, exactly as the boards sent them.

## 1. The real run: live, day 1 (run by me, 2026-11-09 20:32 UTC)

Command: `python3 -m jsagent.loop run --label live-day1`
Files: `runs/report-20261109T203203Z-live-day1.{json,md}`, `runs/trace/20261109T203203Z-live-day1.jsonl` (53 events),
`runs/raw/*-live-day1-a1.json`.

| board | status | HTTP | attempts | postings | new |
|---|---|---|---|---|---|
| greenhouse:databricks | ok | 200 | 1 | 918 | **80** (since my JS1 run on 2026-11-01) |
| greenhouse:anthropic | ok | 200 | 1 | 676 | baseline |
| ashby:openai | ok | 200 | 1 | 812 | baseline |
| ashby:notion | ok | 200 | 1 | 153 | baseline |
| ashby:notarealco-js2 | **failed** | 404 | 1 | **null** | — |
| smartrecruiters:hubspot | **suspect_empty** | 200 | 1 | 0 | — |

**Exit: `incomplete`**: "2 board(s) failed or flagged; escalated to Riya". Budget used: 6/6 boards, 6/10 requests, 4.03/60 s.

### The deliberate failure, as the trace recorded it

```text
{"t": 3.464, "kind": "request",  "url": ".../posting-api/job-board/notarealco-js2", "n": 5, "attempt": 1}
{"t": 3.548, "kind": "response", "url": ".../posting-api/job-board/notarealco-js2", "status": 404, "bytes": 9}
{"t": 3.549, "kind": "board_result", "board": "ashby:notarealco-js2", "attempts": 1, "http_status": 404,
 "postings": null, "status": "failed", "reason": "HTTP 404 (4xx: not retried)"}
```

GATE.md's error policy was followed: a 4xx is not retried (one attempt), the count is `null` (not 0), the other boards
were still read, and the run ended `incomplete` with the board listed under "Escalated to Riya". The 9-byte body
(`Not Found`) is saved in `runs/raw/ashby-notarealco-js2-20261109T203203Z-live-day1-a1.json`.

The empty-board trap was also caught by the agent itself: SmartRecruiters `hubspot` returned HTTP 200 with
`{"totalFound":0,"content":[]}` (52 bytes), and the loop marked it `suspect_empty` instead of reporting "no new jobs".
It was not baselined (no state file was written for it), so a later real board would not have every posting hidden as "seen".

Note: this trace was written before commit `8286907`, so its policy entries have no `t` and show absolute paths.
I left it as it ran.

## 2. The finished-wrong-answer (DEMONSTRATION, run by me, 2026-11-09 20:57 UTC, live)

Command: `python3 -m jsagent.loop run --config demo/naive.json --out runs/demo-naive --no-empty-guard`
The `--no-empty-guard` flag turns on GATE.md wrong version 1 on purpose. It exists only for this demonstration.

```text
- Exit: finished (all boards read)
- Label: live-naive · empty guard OFF (naive demonstration mode)
| greenhouse:anthropic    | ok | 200 | 1 | 676 | baseline |
| smartrecruiters:hubspot | ok | 200 | 1 | 0   | baseline |
agent exit code: 0
```

The run ended cleanly and is **wrong**: it says HubSpot was read fine and has no postings.

### The independent check that caught it (not the agent's own report)

Command: `python3 tools/independent_check.py runs/demo-naive/report-20261109T205704Z-live-naive.json --config demo/naive.json`

```text
  [agrees] recount greenhouse:anthropic: 676 postings in raw
  [agrees] recount smartrecruiters:hubspot: 0 postings in raw (totalFound 0)
  [CONTRADICTED] second_source smartrecruiters:hubspot: report says 0; greenhouse:hubspotjobs has 126 postings (HTTP 200)
  [CONTRADICTED] exit smartrecruiters:hubspot: report says finished, but these boards have 0 or no postings
VERDICT: CONTRADICTED  (1 request(s))
check exit code: 1
```

Why this check is independent: it is a separate program; it reads only the saved report and raw files and
does its own JSON counting (it does not import the loop or the adapters, only the allow-list/path policy); and it asks a
**different source** (HubSpot's real board on a different system). Note that the recount **agreed** with the wrong report.
A count can be correct and the answer still wrong. Only the second source showed that.
Its own output: `runs/demo-naive/checks/` (raw second-source response included).

## 3. The `finished` exit (SEEDED, run by Claude Code in my session, 2026-11-09 20:53 UTC, offline)

Command: `python3 -m jsagent.loop run --config demo/good4.json --out runs/seeded --fixtures runs/raw --fixture-tag 20261109T203203Z-live-day1 --label seeded-good4`

It replayed the four real boards' day-1 raw responses (no network) → **Exit: `finished`**, 4/6 boards, 4/10 requests.
This is labeled **seeded**: the responses are real, but they were replayed, not fetched again.

## 4. Live, day 2 (run by me, 2026-11-10 19:45 UTC, the TA's "two real calendar days")

Command: `python3 -m jsagent.loop run --label live-day2` (same `boards.json`, same `runs/` state as day 1, 23 h 13 min later).
Files: `runs/report-20261110T194501Z-live-day2.{json,md}`, `runs/trace/20261110T194501Z-live-day2.jsonl`,
`runs/raw/*-live-day2-a1.json`. The day-1 watch run was judged before amendments 3 and 4; this one was judged after them.

| board | status | HTTP | attempts | postings | new since day 1 | gone since day 1 |
|---|---|---|---|---|---|---|
| greenhouse:databricks | ok | 200 | 1 | 914 | **10** | 14 |
| greenhouse:anthropic | ok | 200 | 1 | 677 | **12** | 11 |
| ashby:openai | ok | 200 | 1 | 830 | **26** | 8 |
| ashby:notion | ok | 200 | 1 | 155 | **3** | 1 |
| ashby:notarealco-js2 | **failed** | 404 | 1 | **null** | — | — |
| smartrecruiters:hubspot | **suspect_empty** | 200 | 1 | 0 | — | — |

**Exit: `incomplete`** (the same two planted boards, escalated). Budget used: 6/6 boards, 6/10 requests, **41.20/60 s**.

**Checked after the run (by recount, not by the agent; done by Claude Code in my session, 2026-11-10):** the "new" and
"gone" columns were recomputed by diffing the ids in the day-1 and day-2 raw files directly; all four "new" counts match the report. The report's
`removed_since_last` for Databricks is 77, not 14, because its state also holds JS1 ids (state only grows, GATE.md), so no
approval was needed. `tools/independent_check.py --offline` on this report: every recount agrees, "no contradiction found".

**What the rule said about the 51 new postings:** 1 relevant: Databricks 8933544002 "Applied AI Architect" (United
States; title word AI; Python, SQL, AWS). Notion `ea6f01b1-…` "Product Design Intern (Summer 2027)" is the first live
posting excluded by both new amendments at once: "title has intern word(s) ['Intern']; employmentType 'Intern' is not
full-time". It was not on any board on day 1, so this is the rule meeting a posting it was not written against.

**What day 2 showed that day 1 did not: the time budget nearly mattered.** On day 1 the whole run took 4.03 s. On day 2
the Databricks response alone took **34.07 s** (request at t=0.001, response at t=34.067, 9.96 MB):

```text
{"t": 0.001, "kind": "request",  "url": ".../boards/databricks/jobs?content=true", "n": 1, "attempt": 1}
{"t": 34.067, "kind": "response", "url": ".../boards/databricks/jobs?content=true", "status": 200, "bytes": 9963648}
```

That is longer than `REQUEST_TIMEOUT = 20 s`, which did not fire, because urllib's timeout applies to each socket read and
not to the whole download (the case listed in SIGNOFF "Not checked" 6). The other five boards fit in the remaining 26 s.
If the slow board had been later in the list, the 60 s budget could have stopped the run as `budget_exhausted` with
boards listed under `never_ran`, which is the behavior GATE.md asks for, but one I have only seen in tests.
