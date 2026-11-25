# FINISHED-WRONG-ANSWER.md — a clean `finished` run that is still wrong

**Date:** 2026-11-10 (UTC). Run against the loop as of commit `dff8673`,
before removal detection existed (see "After removal detection" at the end).

## Why this is a different failure from `badslug-gitlab-typo`

`badslug-gitlab-typo` is a loud failure. The board 404s, the loop reports it
as `FAILED` with the HTTP error, and nothing is hidden
(`logs/10_deliberate_board_failure_live.txt`).

This one is quiet. Every step of the run succeeds, and the report says
something that is true on its own terms. The answer is still wrong, and
nothing inside the loop can tell.

## 1. The seeded fixture (constructed — NOT a real Stripe response)

File: `evidence/stripe_SEEDED_empty_20261110T000450Z.json`. "SEEDED" is in
the name, and the content labels itself:

```json
{
  "_SEEDED_NOTICE": "CONSTRUCTED TEST FIXTURE - NOT a real Stripe or Greenhouse response. Written by hand at 20261110T000450Z for FINISHED-WRONG-ANSWER.md. It simulates an ATS endpoint returning 200 OK with a well-formed but empty jobs list because of a transient upstream problem (rate limiting, a misconfigured query, a partial outage), while the board really has open roles. The real Stripe board returned 771 postings at 2026-11-09T23:23:00Z (evidence/stripe_20261109T232300Z.json, logs/07_first_real_run_baseline.txt).",
  "jobs": [],
  "meta": {"total": 0}
}
```

The fixture is valid Greenhouse JSON: an object with a `jobs` list and a
`meta.total`. The loop's parser accepts it as a board with zero postings.
That is correct under GATE.md's 2026-11-09 amendment: "`{"jobs": []}` is a
valid board with zero postings: `ok`, not `failed`."

`.gitignore` keeps raw responses out of the repo, but files named
`*_SEEDED_*.json` are allowed through, so this fixture is committed. The
README says so.

## 2. The loop's own report: clean, boring, `finished`

JS2's loop CLI has no `--from-file`. JS1's watch had one, but here a replay
into scratch state would need a command-line override of the write root,
and GATE.md's permission policy doesn't allow that. So the replay is a
separate script, `tools/replay_from_file.py`. It:

- copies the **real** `state/stripe_seen.json` (771 seen ids) into a fresh
  temp scratch root;
- calls the unmodified `agent.loop.run()` there, with a fetch function that
  returns the fixture's bytes for Stripe's URL;
- prints `agent.loop.format_report()` unchanged;
- hashes the real state file before and after.

Real output (`logs/15_finished_wrong_answer_seeded_replay.txt`):

```
========================================================================
SEEDED REPLAY - constructed input, NOT live board data
board:        stripe
replayed:     evidence/stripe_SEEDED_empty_20261110T000450Z.json  (575 bytes, sha256 981899822f761f87)
state copied: state/stripe_seen.json -> <scratch>/state/stripe_seen.json
scratch root: /var/folders/c2/hk_k8pq11y9f6pghcbc55m6c0000gn/T/js2_replay_mo5i8s9s
========================================================================
----- loop's own report (agent.loop.format_report, unmodified) -----
JS2 loop run 2026-11-10T00:05:28+00:00  EXIT: finished
  requests 1/15  elapsed 0.002s/120s  board limit 5
  stripe               ok           0 postings in response, 0 new  (1 request(s))
  run log: logs/run_20261110T000528Z.json
----- end of loop's own report -----
note: paths in the loop's report (evidence, run log) are inside the scratch root, not the project; the scratch root is deleted below
real state/stripe_seen.json unchanged: True
# exit code: 0
```

Every part of the loop's report is true:

- the exit is `finished`;
- the board is `ok`;
- there were 0 postings in the response;
- 0 of them are new.

Nothing in it is marked as a problem. The `SEEDED` banner comes from the
replay script, not from the loop: the loop has no idea its input was
constructed. The real state file was not touched.

The total is technically on screen ("0 postings in response"). The loop
prints it, but it never compares that total to anything. The real state file
even records the previous count (`"postings_in_response": 771` in its
`runs` history), and nothing reads it back. A reader skimming for "new"
sees a quiet day.

## 3. The independent check that catches it

`tools/count_drift_check.py` is standalone:

- It uses the standard library only and imports nothing from `agent/`.
  `grep -rn count_drift agent/` finds nothing, so it is not part of the
  loop's reporting path.
- It reads two saved responses straight from disk and compares their total
  posting counts.

Before is the real Stripe response from the first real run; after is the
seeded fixture.

Real output (`logs/16_independent_count_check.txt`):

```
independent count check (standalone; not part of the loop)
before:
  evidence/stripe_20261109T232300Z.json
    shape=greenhouse  postings=771  meta.total=771  sha256=b67667ba1220abb7
after:
  evidence/stripe_SEEDED_empty_20261110T000450Z.json  [SEEDED - constructed, NOT live data]
    shape=greenhouse  postings=0  meta.total=0  sha256=981899822f761f87

change: 771 -> 0  (100% drop)
SUSPICIOUS: this board's total posting count dropped from 771 to 0 between runs. Investigate by hand (re-fetch, check the board's public page) before trusting the loop's '0 new' result for this run.
# exit code: 1
```

As a control, the same check on the two **real** consecutive Stripe
responses (`23:23:00Z` and `23:23:13Z`, byte-identical) prints
`771 -> 771 (0% drop)`, `OK`, exit 0. So the alarm is not set off by just
any pair of files.

The "before" file sits in `evidence/`, which is not committed. Its count
is still on record in committed files: `logs/07_first_real_run_baseline.txt`
(`stripe ... BASELINE: 771 postings`) and `logs/run_20261109T232300Z.json`.

## 4. The gap this proves

**The loop's repeat rule tracks only new-vs-seen ids. It has no way to tell
"this board genuinely has nothing new" from "this board silently broke and
returned nothing."**

Both cases produce the same result:

- a well-formed response;
- no id that isn't already in `seen_ids`;
- status `ok`, "0 new", exit `finished`.

The error policy can't help either. It catches only HTTP errors, timeouts,
and malformed bodies, and this response is none of those.

A 200 OK with an empty list is the most plausible way a real ATS fails
quietly. When it happens, the run looks the same as a quiet day.

Only something outside the repeat rule catches it. Here that is a
comparison of total counts across runs, done by a separate script; a human
looking at the numbers would also catch it. The loop has the data it would
need (its own state records the previous count) but never uses it.

Not changed by this demonstration: `agent/` and GATE.md are untouched. Two
things were added: the replay and check scripts in `tools/`, and the
`.gitignore` exception for SEEDED fixtures.

## After removal detection

This document describes the loop as of `dff8673`. The removal-detection
change in REVIEW-PACKET.md changes what this replay prints. Every id from the
previous fetch is now reported as "removed", so an empty response no longer
looks like a quiet day. REVIEW-PACKET.md shows the re-run. Removal detection
still does not classify the run as suspicious: the exit stays `finished`
and the board stays `ok`. The count-drift check stays independent.
