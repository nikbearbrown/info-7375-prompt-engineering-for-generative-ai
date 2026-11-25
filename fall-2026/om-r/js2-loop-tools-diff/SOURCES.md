# SOURCES.md: what I used, what I wrote, what Claude contributed

## Starting sources

- **Assignment:** "Job-Search Agent 2 — The Loop, the Tools, and the Diff"
  (INFO 7375, Chapters 4–6): the agent loop and its exits, tools and
  permissions, and Claude Code with evidence-based diff review.
- **Job-Search Agent 1** (`fall-2026/om-r/js1-contract-and-watch/`). JS2
  builds directly on it and reuses:
  - **the allow-list pattern** from JS1's `agent/fetch.py`: `check_url`
    (HTTPS only, host on an allow-list), plus a redirect handler that
    re-checks every redirect target. In JS2 it moved into
    `agent/permissions.py` and was extended with `api.lever.co`, a
    userinfo/port check, and write-path containment.
  - **the state-tracking approach** from JS1's `agent/watch.py`:
    - a first run is a baseline that records every id and reports none as
      new;
    - later runs report only ids not in the board's seen-state;
    - state is written atomically.

    In JS2 this became per-board state files (`state/<board>_seen.json`),
    and later gained `last_fetch_ids` for removal detection.
  - **the test-first discipline:** wrong-version tests written before the
    code, shown failing against deliberately wrong stubs, with the
    implementation picked by an environment variable (`JS1_IMPL` became
    `JS2_IMPL`).
  - **the conventions** of numbered `logs/` files and `SEEDED` labels for
    constructed input.
- **Data:** three public job-board APIs, fetched 2026-11-09 and 2026-11-10.
  Raw responses are saved in `evidence/`; they are not committed, but their
  counts are in `logs/`.
  - Greenhouse, `gitlab`:
    `boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true`
  - Greenhouse, `stripe`:
    `boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`
  - Lever, `palantir`: `api.lever.co/v0/postings/palantir?mode=json`
    (paginated)
- **Libraries:** the Python 3.11 standard library only.

## Toolchain

Python 3.11 (tested on 3.11.15), standard library only (`urllib`,
`unittest`, `json`, `pathlib`, and the others listed in README.md). There
are no third-party dependencies and no `requirements.txt`; this was checked
by parsing every import in `agent/`, `tests/` and `tools/`. JS1's Anthropic
SDK is not used, because JS2 has no judgment step. This is the same
toolchain stated in README.md and GATE.md.

## What I wrote and decided

- **GATE.md, in full, before any code existed:**
  - the four exits;
  - the three budgets;
  - the repeat rule;
  - the error policy;
  - the permission policy;
  - the two wrong versions;
  - the dated failure definition.
- **The resolutions of the seven open questions** Claude flagged after the
  first implementation pass (GATE.md, 2026-11-09 amendment):
  1. Any budget hit is `budget-exhausted`; `incomplete` is only for boards
     refused without `--approve-new-board`.
  2. The `error` exit means every *attempted* board failed.
  3. `interrupted` is a defined per-board status: partial data is
     discarded and state is unchanged.
  4. Retries count against the request budget.
  5. An empty body is `failed`; `{"jobs": []}` is a valid board with zero
     postings.
  6. Initialize git and commit in small, ordered commits, not pushed.
  7. Remove `api.anthropic.com` from the allow-list until judgment code
     exists.
- **Other design and scope decisions:**
  - the git identity: the course email from JS1, with all commits
    rewritten before anything was pushed;
  - keeping `evidence/` and `state/` out of the repo while keeping
    `logs/run_*.json` as the run record;
  - the permission boundary cases to test;
  - the finished-wrong-answer scenario (a SEEDED 200 OK with an empty
    list, caught only by an independent count comparison);
  - choosing removal detection as the reviewed non-trivial change, and
    requiring test-first steps and a scope review;
  - which FRICTIONAL.md items to close, and how.
- **The decision to ACCEPT the removal-detection patch**, with a GATE.md
  amendment as a required follow-up. I set the amendment's content
  (REVIEW-PACKET.md, Step 6; GATE.md, "Amendment 2026-11-10").
- **My own verification** (REVIEW-PACKET.md, Step 5):
  - running the full suite;
  - running the replay and the count-drift check;
  - reading `git diff 8bb6a17 d3e2e8a`;
  - finding the tool-invocation bug by running the command myself, and
    re-running it after the fix.
- **The sign-off** (`SIGNOFF.md`) and the "Om did" and "Why that part
  stayed mine" entries in the driver's-seat table.

## What Claude contributed

**Claude Code** (Anthropic's CLI, model `claude-opus-5-5`) acted as a coding
and drafting assistant throughout:

- **All code:**
  - `agent/`: `loop.py`, `permissions.py`, `fetch.py`, `boards.py`;
  - `tests/`: all 46 tests and the `fakes.py` fixtures;
  - `tools/`: `replay_from_file.py`, `count_drift_check.py`,
    `weak_patch_check.py`.
- **The deliberately wrong code:** the two wrong-version stubs
  (`agent/wrong_stub_budget.py`, `agent/wrong_stub_failed_board.py`), the
  permission mutation check (`tests/mutation_check.py`), and the
  wrong-patch check (`tools/weak_patch_check.py`).
- **The SEEDED fixtures:** the empty Stripe response and the gitlab
  minus-one response, each labeled in its filename and content.
- **The runs it executed itself:**
  - every test run in `logs/`;
  - the live baseline and rerun (2026-11-09);
  - the live deliberate 404;
  - the replays;
  - the fresh-clone reproduction of every README command (2026-11-10).
- **Drafts I directed and corrected:**
  - FINISHED-WRONG-ANSWER.md;
  - REVIEW-PACKET.md, steps 1–4 and 7, plus its step 6 recommendation as
    the patch's author. Steps 5 and 6 are my own text;
  - the GATE.md amendments, written from my decisions;
  - README.md and this file, apart from the sign-off and the
    driver's-seat entries;
  - the sign-off and driver's-seat skeletons.
- **FRICTIONAL.md entries**, written from my account and checked against
  the record. That check corrected four inaccuracies in my original list
  and removed two statements Claude had not actually observed.
- **The git identity rewrite.** It rewrote all commits to the course
  identity and verified the result. It also caught that its own first
  search of the history was broken (it had searched only commit objects),
  then logged both the broken and the corrected search (FRICTIONAL.md,
  entry 4; `logs/14_identity_rewrite_evidence.txt`).
- **The git history:** commits authored as me, at my direction.

## Outside AI tools

None. I did not use ChatGPT or any other AI tool outside Claude Code
anywhere in this build. That is unlike JS1, where:

- ChatGPT helped with the wording of the sign-off;
- the Sampling Report labels were composed in a separate claude.ai chat
  (JS1 SOURCES.md).

No file in this repository mentions or credits an outside AI tool: a
`git grep` for ChatGPT, OpenAI, Gemini and Copilot finds nothing.
