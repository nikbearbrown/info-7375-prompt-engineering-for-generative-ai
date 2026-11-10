# SOURCES — Job-Search Agent 2

Yash Saraf · INFO 7375 · 2026-11-10

## What I used

| Tool or source | Version / date | Licence | Used for |
|---|---|---|---|
| **My JS1 project**, `fall-2026/yash-s/js1-contract-and-watch/` | commit `73260d2` | mine | **Copied unchanged:** `persona/priya-nair.resume.example.json` (sha256 `a4fdbc96…`) and my JS1 final state, which became `state/greenhouse-databricks.state.json` before the first JS2 run (924 ids, sha256 `7265577c…`). `record.py` is the RECORD rule extracted word for word from JS1's `judge.py`. **Ideas carried over, re-implemented:** the host allow-list, refusing redirects, saving raw responses before parsing, create-only evidence (the JS1 overwrite fix), atomic state writes, and the persona check. |
| **Lectern**, the instructor's collector, `fall-2026/nik-bear-brown/lectern/` | course repo, pulled 2026-11-09 | per the course repo | **The Ashby URL and fields** from `collect.py`: `posting-api/job-board/{slug}?includeCompensation=true`, and `id`, `title`, `descriptionHtml` / `descriptionPlain`, `location`, `secondaryLocations` and `jobUrl`. One line in `providers.py`, combining `location` with `secondaryLocations`, closely follows Lectern's `normalise()`. **Board names** `anthropic` and `openai` came from its `sources.json`. |
| **Greenhouse Job Board API**, public, no login | fetched 2026-11-10T02:51Z | Databricks' and Anthropic's public postings | `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true` for `databricks`, `anthropic` and the misspelled `databricks-misspelled` (which returned 404). The raw responses are saved unmodified in `runs/`. |
| **Ashby Posting API**, public, no login | fetched 2026-11-10T02:51Z | OpenAI's public postings | `https://api.ashbyhq.com/posting-api/job-board/openai?includeCompensation=true`, saved unmodified in `runs/` |
| **Python** | 3.13.5 (Anaconda, my runs) and 3.9.6 (macOS system, Claude's runs) | PSF | All code and tests; standard library only |
| **Claude Code** | Claude Opus 5.5, 2026-11-09 to 2026-11-10 | Anthropic terms | Writing code and drafts under my review (below). The agent itself calls no model. |

The Reallocation Engine, which the brief offers as a starting point, was not used in JS2.

## What I made

- **GATE.md:** every exit, budget, repeat rule, error rule and permission rule, written before any code (commit `e18f63c`), and my dated note changing the review-packet topic.
- **BOUNDARY-TESTS.md:** all 15 predictions, written before any code. After testing, I checked each one against its result.
- **The decisions:** the board list, the deliberate failure, starting Databricks from my JS1 state, and the budget values.
- **The runs:** I ran the live run, the seeded demonstration and the independent checks myself.
- **The review packet:**
  - I found the "new=0" defect in my live run.
  - I wrote the test assertions, which decide the correct behavior (`null` and `new=unknown`), and committed them failing before the patch (`bca5bb6`).
  - I wrote the patch request and its limits, read the diff, ran the tests and `wrong_versions.py`, and accepted the patch.
- **The writing:** FRICTIONAL.md, the sign-off, and the reasons in the driver's seat table.
- **Every git command.**

## What Claude contributed

Claude Code, in this session.

**Code, all checked by tests I ran:**
- `agent.py`, `policy.py`, `providers.py`, `independent_check.py`, `wrong_versions.py` and `tests/`;
- the 10 extra policy tests beyond my 15 cases;
- the **setup only** of `tests/test_review_failed_board_count.py` (temporary folders, replayed responses, console capture). The assertions are mine.

**The review patch:** two lines in `agent.py`, written to my request (`review/agent-patch.diff`). Claude also pointed out that the patch covers "stopped by error" as well, one step beyond my numbered list.

**Demonstration files:** the replay folder, including the **constructed** empty Anthropic response, and a rehearsal in a scratch copy before I ran the demonstration myself.

**Checks:**
- checking my live run's files (fingerprints, recounts, state growth) and finding where the "new=0" came from in the code;
- reviewing GATE.md, which pointed out two unclear rules that I then decided.

**Drafts:** README.md, this file, `review/REVIEW-PACKET.md`, `demo/README.md`, and the results section of BOUNDARY-TESTS.md, all written from the commits and saved outputs.

**Where Claude was wrong or had to correct itself:**
- Its first version of the WV1 test checked a failed board's status and the report, but **not** `new_count` or the console. That is why all 63 tests passed while my live run still printed "new=0".
- One test had an indexing bug (a `KeyError`), found and fixed when Claude first ran the suite.
- Before the tests ran, Claude found and fixed three gaps in its own code: replayed responses were not read through the policy, a configuration file could be read from any folder, and a run stopped by an error left later boards out of the summary.
- `wrong_versions.py` printed test names twice on Python 3.11 and newer. I saw this in my run, and Claude fixed the display.
- Its first draft of the review packet said that I ran the full test suite and the wrong-version check between my test and the patch. I had not. Claude corrected this before I reviewed the packet.
- I asked Claude not to run git commands. It once ran a read-only `git status` by mistake. It changed nothing.

**Other AI tools:** none.
