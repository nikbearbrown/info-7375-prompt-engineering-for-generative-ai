# Sources

## What I started from

**My own Job-Search Agent 2**, in this repository at
[`fall-2026/weiting-w/js2-loop-tools-diff`](../js2-loop-tools-diff/), commit
`1fb701b3`. Not the Reallocation Engine, not Lectern.

The three layers divide like this:

- **JS1** wrote a contract and one rule, R-v2, and watched one board.
- **JS2** made it a bounded loop over four boards and three applicant-tracking
  systems, under a permission policy enforced in code, and fixed R-v2's remote
  false positive to produce R-v3.
- **JS3** reads the postings. JS2 captured 452 of them live on
  2026-11-11T00:18Z and R-v3 judged every one on title, department and
  location alone — it never opened a description. This layer does, and decides
  what reaches me and on what evidence.

## What came from JS2, file by file

`inherited/` holds the carried-over code. Verified with `diff`, not from
memory.

| file | from | changed how |
|---|---|---|
| `inherited/rule.py` | `js2/agent/rule.py` | **import lines only** |
| `inherited/fieldpath.py` | `js2/agent/fieldpath.py` | **import lines only** |
| `inherited/resume.py` | `js2/agent/resume.py` | **import lines only** |
| `inherited/errors.py` | `js2/agent/errors.py` | **import lines only** |
| `inherited/providers/*` | `js2/agent/providers/*` | **import lines only** |
| `data/resume.persona.json` | `js2/data/` | **byte-identical**, sha256 `b70768bb…f95896` |

They are **not** byte-identical, and the difference is named rather than
glossed: JS2's modules import each other with package-relative imports
(`from .fieldpath import whole_word`), which do not resolve from this package,
so each such line was rewritten to an absolute `inherited.` import. No logic,
no constant, no word list, no weight, no docstring was touched.

`tests/test_inherited_is_unchanged.py` holds that claim against the bytes: when
the JS2 folder is a sibling it compares every file line by line and requires
every differing line to be an import statement. It skips when the sibling is
absent, and that skip is in README.md's sign-off as the one case where a copy
could drift unnoticed.

**The corpus is read in place**, from `../js2-loop-tools-diff/evidence/raw/`.
It is not copied into this folder: 4.5 MB of the same bytes twice in one
repository is worse than a relative path, and a TA cloning the repository gets
both folders.

## What is new in JS3

`FILTER.md`, `jobfilter/` (corpus, score, gates, evidence, pipeline, cli),
`toolserver/`, `tools/`, `prompts/`, the reports, and the tests.

## What Claude contributed, and what it did not

Claude (Opus 5) wrote all of it, in one Cowork session on **2026-11-23**:
`FILTER.md`, every module, every test, the tool server, both evaluations and
every report, including this file. The code in this submission was not typed
by me and I am not going to imply otherwise.

What that leaves me responsible for is narrower, and it is the part this
assignment is testing:

- **The 48 hand labels.** The reject audit rests on them, they are blind by
  construction — `audit/audit-form.html` shows no score, no bucket and no
  gate, and shuffles the order with a recorded seed — and nobody else could
  produce them. `audit/labels-weiting.json` is mine.
- **The decision to build layer 3 on my own JS2** rather than start from the
  Reallocation Engine or Lectern.
- **Accepting three amendments** (A1, A2, A3) after reading what each one
  predicted and what it measured, and **declining a fourth**: `MIN_WALL_YEARS`
  stays at 3 even though P-v3 read "Minimum 1 year" as disqualifying, because
  the audit should settle that and not me on the last evening.
- **What the sign-off claims and what it refuses to claim**, including keeping
  every item in its "Not checked" list.

### Three things Claude found against its own work, unasked

Recorded because "what you accepted, modified, or rejected from Claude" is a
scored line and because they are the reason this submission's numbers moved:

1. **F-v1 as frozen scored nothing** — 0 of 452 postings reached the scorer.
   Claude ran it, reported the empty result, and traced it to an inherited
   gate that was testing which applicant-tracking system a company bought
   (A1).
2. **Three signal words were false friends** — `infrastructure` firing on
   177/177 of one board from a boilerplate sentence, `go` wrong 46 times in 55,
   and the new-graduate bonus landing on a sales job (A2).
3. **The top-scoring shortlist entry required five years** and the experience
   rule could not read the phrasing, nor the number `3+` (A3).

I did not ask for any of these. The third one deleted the best-looking result
in the submission.

## External sources

- **The corpus**: four public applicant-tracking endpoints, read by JS2 with
  one unauthenticated GET each on 2026-11-11 — `boards-api.greenhouse.io`
  (`reddit`), `api.lever.co` (`spotify`), `api.ashbyhq.com` (`ramp`, `linear`).
  JS3 makes **no network request at all** and reads only the saved bytes.
- **`@modelcontextprotocol/server-filesystem` version 2.4.0**, installed from
  the public npm registry on 2026-11-23 and run with `npx`. The second tool
  server evaluated in `reports/tool-evaluation.md`. Its
  `repository.url` is `git+https://github.com/modelcontextprotocol/servers.git`
  and its license field reads "SEE LICENSE IN LICENSE". I evaluated the code
  npm installed, not a web page about it.
- **The Model Context Protocol message shape** — `initialize`, `tools/list`,
  `tools/call`, `notifications/initialized`, JSON-RPC 2.0 over stdio.
  `toolserver/server.py` implements it by hand; it links against no SDK and
  copies no code.

## Dependencies

Python 3, standard library only, for everything in `jobfilter/`, `toolserver/`,
`tools/` and `inherited/`. `pytest` for the tests, in `requirements-dev.txt`.
Node and npm are needed only to reproduce the second tool-server evaluation,
and nothing in this folder depends on them.
