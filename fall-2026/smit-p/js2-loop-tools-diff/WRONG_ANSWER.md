# A finished wrong answer, and the independent check that caught it

**Every run on this page is SEEDED.** They replay responses from files instead of calling the
network. The Lever, Ashby, and baseline Figma bodies are the real responses saved by live run
`2026-11-08T00-43-54Z`. The empty Figma body (`fixtures/vanish/figma-empty-SEEDED.json`) is
hand-written. It shows what an outage, a half-finished ATS migration, or a board being rebuilt
would look like: a valid `200` with `{"jobs": [], "meta": {"total": 0}}`. Runs were made on
2026-11-08 at commit `45480d2` (loop v1) and `1b7f999` (patched).

## The wrong answer (loop v1)

Run 1 replays the real responses and sets the baseline. Run 2 is identical except that Figma
returns an empty board.

```text
$ python3 run_agent.py --boards fixtures/vanish/boards.json --replay fixtures/vanish/scenario-2-figma-empty.json --run-id seeded-vanish-2
run seeded-vanish-2  [SEEDED (replayed saved responses, not a live run)]  requests=3  elapsed=0.02s
  figma                  greenhouse ok                         count=0  new=0
  spotify                lever      ok                         count=85  new=0
  linear                 ashby      ok                         count=32  new=0
exit: finished (code 0)
```

The run ended cleanly with exit code 0, every board `ok`, and nothing new. Read as a report, it
says "I checked all three boards and nothing changed." For Figma that is false. The agent
can't tell "Figma has no openings" from "Figma's board is broken," so it should not claim
either one.

v1 did worse than give one wrong answer. It also replaced Figma's 145-posting baseline with an
empty one, so the next good response looked like a hiring spree:

```text
$ python3 run_agent.py --boards fixtures/vanish/boards.json --replay fixtures/vanish/scenario-1-baseline.json --run-id seeded-vanish-3
run seeded-vanish-3  [SEEDED (replayed saved responses, not a live run)]  requests=3  elapsed=0.02s
  figma                  greenhouse ok                         count=145  new=145
      + 5426468004  Account Executive, Enterprise
      + 5579204004  Account Executive, Enterprise (Bengaluru, India)
      ...
```

## The independent check

`verify_run.py` is not the agent grading itself. It imports nothing from `agent/`, never reads
the agent's state files, and trusts only the raw bytes saved for each run. For every board the
agent called `ok`, it recounts postings from the raw file with its own parsing and compares the
count with the same board's raw file from the most recent earlier run of the same kind.

```text
$ python3 verify_run.py seeded-vanish-2
PASS  hosts                               3 requests, off-list: none
PASS  request count                       trace has 3, summary says 3
PASS  seeded label                        replayed responses must be labeled
PASS  figma: recount from raw             agent 0, recount 0
PASS  figma: greenhouse meta.total        meta.total 0, jobs 0
FAIL  figma: empty after non-empty        145 postings in seeded-vanish-1, 0 now, yet reported as status ok
PASS  spotify: recount from raw           agent 85, recount 85
PASS  spotify: compared with earlier raw  85 in seeded-vanish-1, 85 now
PASS  linear: recount from raw            agent 32, recount 32
PASS  linear: compared with earlier raw   32 in seeded-vanish-1, 32 now
FAIL  exit status earned                  finished requires every board ok and nothing suspicious
verify seeded-vanish-2: agent said 'finished'; independent check FAILED (2)
```

The recount and Greenhouse's own `meta.total` both **pass**. The agent counted the empty
response correctly, so a check that only re-derives the agent's number from the same response
can't catch this. The failure appears only when the check compares against evidence from
outside the current response, here the earlier raw file.

## After the fix

The fix is the subject of [REVIEW_PACKET.md](REVIEW_PACKET.md). The same seeded scenario on
the patched loop:

```text
run seeded-vanishfix-3  [SEEDED (replayed saved responses, not a live run)]  requests=3  elapsed=0.01s
  figma                  greenhouse suspect:empty_after_nonempty count=null
  spotify                lever      ok                         count=85  new=0
  linear                 ashby      ok                         count=32  new=0
  NEEDS HUMAN: figma: suspect:empty_after_nonempty (0 postings now, 145 in the baseline)
exit: incomplete (code 2)
...
verify seeded-vanishfix-3: agent said 'incomplete'; independent check passed
```

When Figma comes back, nothing old is reported as new, because the baseline survived
(`evidence/review-5-figma-restored.txt`):

```text
run seeded-vanishfix-4  [SEEDED (replayed saved responses, not a live run)]  requests=3  elapsed=0.02s
  figma                  greenhouse ok                         count=145  new=0
```

## To reproduce

Run ids must be new, so use fresh suffixes. The v1 behavior needs the v1 code:

```bash
git checkout 337cf1b -- agent/loop.py
python3 run_agent.py --boards fixtures/vanish/boards.json --replay fixtures/vanish/scenario-1-baseline.json --run-id seeded-repro-1
python3 run_agent.py --boards fixtures/vanish/boards.json --replay fixtures/vanish/scenario-2-figma-empty.json --run-id seeded-repro-2
python3 verify_run.py seeded-repro-2
git checkout HEAD -- agent/loop.py
```

## What the check does not catch

A board that drops from 145 to 3 is not flagged, because only an exact drop to zero is.
A partial response from a struggling server would pass as a real shrink.
