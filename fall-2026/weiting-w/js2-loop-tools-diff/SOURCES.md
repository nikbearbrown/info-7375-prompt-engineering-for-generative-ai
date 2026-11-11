# Sources

## Where this started

**This is layer 2 of my own JS1 agent**, not a fresh start and not a different
project. The base is
[`fall-2026/weiting-w/js1-contract-and-watch/`](../js1-contract-and-watch/) in
this same repository — my own submission, commit
`bcc40d7e96e1374a1083fd1bb8a7a0bd6431061d`. JS1 was one board, one rule, one
written contract. JS2 is several boards, a bounded loop, a permission policy in
code, and a review of a change to the rule JS1 wrote.

I did **not** start from the Reallocation Engine or from Lectern.

## What came from JS1, file by file

Verified with `diff`, not from memory. Counts are differing lines.

### Carried over unchanged

| file | note |
|---|---|
| `agent/resume.py` | byte-identical to `jobagent/resume.py`. The persona guard and the loader. |
| `agent/fieldpath.py` | identical apart from one docstring line that named JS1's model-output validator, which this package does not have (GATE.md §8 A3). `whole_word()` is the same function that makes G1 a word match rather than a substring match. |
| `data/resume.persona.json` | identical, sha256 `b70768bb94aebc565addafd3c9e835c28ac3dc2261d25bea31b059aa51f95896`. Same fictional persona, so JS1's verdicts and JS2's are about the same person. |
| `evidence/fixtures/js1-greenhouse-reddit-20261031.json` | JS1's live capture, byte-identical, sha256 `8871e1bb…b86d5`. See `evidence/PROVENANCE.md`. |

### Carried over and changed

| file | lines differing | what changed and why |
|---|---|---|
| `agent/rule.py` | 188 | The four gates, their order and their comparisons are JS1's R-v2. Two amendments on top: **A1** made the rule read a normalised `Posting` instead of a Greenhouse-shaped dict, with `provider_field` carried into every justification (a letter bump, asserted to change no verdict); **A2** fixed the G4 remote false positive (a number bump, exactly 2 of 163 verdicts move). `review/review-packet.md` is the review of A2. |
| `agent/state.py` | 83 | JS1 stored bare Greenhouse ids. JS2 namespaces them `provider:id` (`STATE_VERSION = 2`) because three systems can collide, and adds a per-board `last_count` / `last_seen_at` / `last_status`. A3 added the write-policy check. |
| `agent/errors.py` | 81 | JS1 had a handful of exceptions. JS2 has one class per error *classification*, so `GATE.md` §4's table is a property of the type rather than of a message string. |
| `agent/report.py` | — | Rewritten around a derived exit status and the four loop exits; keeps JS1's non-colliding-filename fix and its `ESCALATE:` line. |
| `agent/cli.py` | — | Rewritten for the `watch` subcommand, replay mode and the budget flags. Keeps JS1's rule that no flag may widen a limit. |

### Replaced

| JS1 | JS2 | why |
|---|---|---|
| `jobagent/allowlist.py` | `agent/policy.py` | JS1 checked a host. JS2 checks host, scheme, port, method, redirects, write confinement, read confinement, the `*.real.json` guard and the overwrite approval — the permission policy the assignment asks to be enforced in code. |
| `jobagent/fetch.py` | `agent/http.py` | Rewritten so failures are mapped to classifications by exception class. |
| `jobagent/validator.py`, `jobagent/claude_judge.py` | *(absent)* | **Not carried over.** JS2's loop calls no model, so there is no model output to validate. GATE.md §5.4 originally assumed they would be carried over and was corrected; `tests/test_no_model_and_no_environment.py` now asserts their absence. |

### New in JS2

`agent/loop.py`, `agent/trace.py`, `agent/policy.py`, `agent/providers/` (base,
greenhouse, lever, ashby), `tools/crosscheck.py`, `tools/boundary_table.py`,
`tools/make_rv2_baseline.py`, `GATE.md`, and the tests.

## What Claude contributed, and what it did not

Claude (Opus 5) was the whole of the implementation work, in a Cowork session
on 2026-11-09. It wrote `GATE.md`, every file under `agent/`, `tools/` and
`tests/`, the reports, and this file. I should not pretend otherwise: the code
in this submission was not typed by me.

What that leaves me responsible for is narrower and is the part the assignment
is actually testing, so it is worth being exact about:

- **The decision to build layer 2 on my own JS1** rather than on a fresh
  codebase, and the decision to use the G4 remote false positive — a defect JS1
  pre-registered and that I had personally labelled against — as the review
  subject.
- **The live run.** The cloud container Claude works in cannot reach any of the
  three applicant-tracking hosts (every CONNECT refused 403 by the egress
  proxy), and neither can the Linux VM that bridges to my Mac. Every real byte
  in `evidence/raw/` was fetched by me, in my own Terminal, on my own machine.
  JS1's capture was made the same way. See "What I ran myself" in `README.md`.
- **The four labels in JS1** that this submission's baseline rests on, including
  the two Ontario postings that are the defect under review — with the
  non-blindness JS1 recorded and that `review/review-packet.md` §2 repeats.
- **Accepting the review.** The decision in `review/review-packet.md` §7, and
  the decision not to fix the substring-identity defect it found the night
  before a deadline.

Claude also found and reported three things against its own work that I did not
ask it to look for, and they are in the submission rather than quietly fixed:
the G4 patch widened scope beyond the reported defect (`review-packet.md` §3),
the review's own test shares an oracle with the implementation it tests (§7),
and GATE.md §5's "there is no second path" was false when written (§8 A3). The
third one changed the code.

## External sources

- **Greenhouse job board API** — `boards-api.greenhouse.io`, public,
  unauthenticated. Board token `reddit`.
- **Lever postings API** — `api.lever.co`, public, unauthenticated. Token
  `spotify`.
- **Ashby posting API** — `api.ashbyhq.com`, public, unauthenticated. Tokens
  `ramp`, `linear`.

All read-only GETs against publicly published job boards, no authentication, no
account, no form submission, one request per board per run. Tokens were chosen
by probing candidates once each and keeping the ones that answered 200;
`config/boards.json` records which were tried and which 404'd, so the plan does
not quietly hide the misses.

No scraping library, no headless browser, no third-party aggregator, and no
endpoint that is not the board's own published API.

## Dependencies

Python 3 standard library only, for the agent and the tools. `pytest` for the
tests (`requirements-dev.txt`). Nothing else is installed or imported.
