# A finished wrong answer, and the independent check that catches it

**Everything here is a labeled SEEDED REPLAY plus a deliberately wrong version. No network was used.**

## The input (`seeded/finished-wrong-answer/`, built by `build.py`)

| Board | Body | Provenance |
|---|---|---|
| `greenhouse/klaviyo` | 3 postings | real slice of the live response collected 2026-11-09T20:21:52Z |
| `ashby/supabase` | 2 postings | real slice of the same live run |
| `greenhouse/hubspotjobs` | `{"jobs": [], "meta": {"total": 0}}` | **hand-made**; the real board had 126 postings then |

The seeded state says a previous run saw those klaviyo and supabase ids and 5 real hubspotjobs ids.
No live empty board was available: Lectern recorded `hubspot` as an empty 200 on 2026-09-26, but it
returned 404 on 2026-11-08 (`drafting/GATE-QUESTIONS.md`), so GATE.md chose a seeded replay.

## What ran (2026-11-09, `python3 -m wrong_versions.demo_finished_wrong`, output in `demo-console.txt`)

| Run | Code | Status | What it said about hubspotjobs |
|---|---|---|---|
| `runs/2026-11-09T20-23-30Z-seeded-WRONG-VERSION-w01` | wrong version **w01** (GATE.md wrong version 1: an empty response is treated as a normal observation) | **FINISHED, exit 0** | observed, 0 postings, **0 new** |
| `runs/2026-11-09T20-23-30Z-seeded-real-code` | the real loop | incomplete, exit 1 | `empty-needs-review`: "not 'no new jobs'" |

The wrong run ended cleanly. Its own report has no error, no attention section, exit 0. That is the
finished wrong answer: an empty board reported as "no new jobs".

## The independent check (`independent_check.py`)

It imports nothing from `jobloop`. It re-reads each saved raw file, re-hashes it, recounts postings with its
own counter (`len(jobs)` or `len(list)`), and compares that with the report's claims and the trace.

```text
$ python3 independent_check.py runs/2026-11-09T20-23-30Z-seeded-WRONG-VERSION-w01      (exit 1)
FAIL: 3 violation(s); the run's own report is not trustworthy:
  [C4] greenhouse/hubspotjobs: reported as observed, but the saved evidence is HTTP 200 with 0 postings
  [C6] greenhouse/hubspotjobs: reported as 0 new postings ('no new jobs') without a nonempty raw listing
  [C5] run: the run says FINISHED, but at least one board lacks a nonempty HTTP 200 raw listing

$ python3 independent_check.py runs/2026-11-09T20-23-30Z-seeded-real-code              (exit 0)
PASS: no invariant violations found. This does not prove the rule verdicts are right.
```

Saved as `check-wrong-version.txt` and `check-real-code.txt`.

**What the check cannot catch:** a raw file that is itself wrong (a server really returning a stale or
truncated board), and any wrong rule verdict. It checks that claims match evidence, not that evidence is true.

**Honesty note:** a first version of these two demo runs, made minutes earlier, printed a misleading state
line for seeded runs. Claude Code deleted those two uncommitted runs, fixed the wording (`a11a167`) and
re-ran; the committed runs are the re-run.
