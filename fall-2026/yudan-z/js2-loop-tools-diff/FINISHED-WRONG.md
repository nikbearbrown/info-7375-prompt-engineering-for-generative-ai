# A finished wrong answer, and the independent check that caught it

## Executive summary

A run can end cleanly and still be wrong. On 2026-11-09 the agent read Ramp on the wrong applicant-tracking system and reported exit `finished`, with Ramp at 1 posting. A separate check, which does not trust the agent's report, counted Ramp's postings on all three systems and flagged the board: Ashby lists 176. This is a **real** run against the live APIs, not a seeded one.

## The mistake

`config/boards-wrong-ats.json` lists Ramp under Greenhouse, which is an easy guess to make. Greenhouse does not answer "no such board" for `ramp`: it returns HTTP 200 with one posting, "Copy of Chief Legal Officer" in Dublin, apparently a leftover. Nothing in the response looks broken.

## The agent's own report: finished, and wrong

`python -m agent.cli --workdir runs/wrong-ats --boards config/boards-wrong-ats.json` → `runs/wrong-ats/terminal-agent.txt`

```
  · greenhouse/pinterest: ok, 167 postings, 0 new (baseline)
  · greenhouse/ramp: ok, 1 postings, 0 new (baseline)
  · lever/palantir: ok, 304 postings, 0 new (baseline)
✓ run 20261109T211154Z: exit finished (code 0) · requests 3/12 · 0.525 s
process exit code: 0
```

By GATE's own rules this exit is correct: every board was fetched, saved and compared. The answer is still wrong, because I would have been watching an empty Ramp for months.

## The independent check

`python check/crosscheck.py runs/wrong-ats/run-20261109T211154Z.json` → `runs/wrong-ats/terminal-crosscheck.txt`

- `check/crosscheck.py` imports nothing from `agent/`, and has its own fetch code.
- It asks all three systems for each board name, and flags a board whose count is under 10% of what the company lists elsewhere.

```
  ok   pinterest: agent read greenhouse = 167 postings; greenhouse = 167, ashby = HTTP 404, lever = HTTP 404
  FLAG ramp: agent read greenhouse = 1 postings; greenhouse = 1, ashby = 176, lever = HTTP 404
  ok   palantir: agent read lever = 304 postings; greenhouse = HTTP 404, ashby = HTTP 404, lever = 304
1 board(s) flagged: the run finished, but its answer for these boards is wrong
process exit code: 1
```

## What this check cannot catch

- **A board name that exists on no other system.** For example, Lectern's notes say HubSpot's real Greenhouse board is `hubspotjobs`, while `hubspot` returns an empty board. My check compares one name across three systems, so it would not catch the wrong name on the right system.
- **The difference between the count the check reads and the count the agent keeps.** Ashby's raw response for Ramp had 176 postings, and the agent kept 172, because it drops postings marked `isListed: false`. This difference is expected, but the check does not explain it.
