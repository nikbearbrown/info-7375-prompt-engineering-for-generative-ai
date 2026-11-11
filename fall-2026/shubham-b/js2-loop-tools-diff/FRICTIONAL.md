# FRICTIONAL.md – Where the Build Pushed Back

## Job-Search Agent 2

**Student:** Shubham Bagwe  
**Written:** November 10, 2026  

This section records six contemporaneous episodes where the build, tools, and assumptions pushed back during Job-Search Agent 2.
### 1. Adopting GATE.md: questioning empty boards and 429 retries

**Date:** November 9, 2026  
**Trace:** `GATE.md` v1.0, `tests/meta/test_js2_wrong_versions_caught.py` (`W2`, `W3`). **Commit:** `f23fc78`.  

- **What I tried and expected:** When reviewing the initial draft of `GATE.md`, I questioned whether treating an empty board response (`EMPTY_RESPONSE`) as a hard failure was too strict for fast-churning boards, and whether HTTP 429 ("slow down") should be retried once after a short cooldown.
- **What happened:** Re-reading `CONTRACT §15` and running test `W2` reminded me that an established tech company returning zero jobs almost certainly points to an endpoint deprecation, altered JSON shape, or broken scraper token. Treating it as `OK` would silently report "0 new jobs." For 429s, retrying against an unauthenticated public scraper violates polite crawling limits (`CONTRACT §12`) and risks IP-level blocking.
- **What I decided and why:** I adopted `GATE.md` as v1.0 without relaxing the budget or retry boundaries. The 10-request budget leaves room for exactly one retry per board across the 5 planned boards ($5 \times 2 = 10$), the 2 s delay handles transient server blips, and failing fast on corrupt state or disk errors protects data integrity.
- **Still unresolved:** If a company legitimately closes all openings globally, the agent reports `EMPTY_RESPONSE` and requires manual human review, but that false-alarm cost is far better than silent failure.
- **Commit trace:** `f524c91`, `f23fc78`.

### 2. The 200-OK trap: Ramp's stale board and Ashby's UUID schema

**Date:** November 9, 2026  
**Trace:** `evidence/`, `config/watch-wrong-board.toml`, `docs/js2/FINISHED_WRONG.md`. **Commits:** `642f550`, `e8816e4`.  

- **What I tried and expected:** I expected the watch loop to verify board health through standard HTTP status codes (`200 OK`) and JSON parsing. In JS1, posting IDs were strictly validated as positive decimal integers.
- **What happened:** Two assumptions failed immediately. First, Ashby's API uses lowercase UUIDs (`00000000-0000-4000-8000-...`), causing JS1's regex validation to reject every posting. Second, probing `greenhouse/ramp` returned `HTTP 200` with exactly 1 stale posting ("Copy of Chief Legal Officer", location Dublin), while Ramp had migrated its active hiring board to Ashby (~169 jobs). The agent finished with `SUCCESS_NO_NEW` and saved the stale ID.
- **What I decided and why:** I widened `PostingId` to accept lowercase UUIDs alongside positive integers (`642f550`), mapping Ashby's fields onto Greenhouse names so the downstream classification rule remained untouched. To address the stale board issue, I introduced Amendment A2 (`min_postings` floors), making any board returning fewer jobs than its floor fail with `INVALID_RESPONSE` (`below_floor`).
- **Claude contribution — accepted, changed, or rejected:** Claude spotted the stale Ramp posting during live test runs. I rejected the assumption that `HTTP 200` implies a valid board, accepted Claude's Ashby schema mapping, and insisted on posting floors.
- **Still unresolved:** If a company moves to a third, unmonitored ATS while leaving a dummy board that still exceeds the floor, the agent cannot detect the migration automatically.
- **Commit trace:** `642f550`, `e8816e4`, `b4582e7`.

### 3. Catching Claude's pipefail mistake and commit grouping

**Date:** November 9, 2026  
**Trace:** `docs/js2/BUILD_LOG.md` (03:14 ET), commits `437946b` and `6fe3ec1`.  

- **What I tried and expected:** During the overnight automated implementation, Claude was instructed to run tests and verify they were green before committing changes.
- **What happened:** Claude ran `uv run pytest | tail -1`. Because standard bash pipes mask the exit code of the preceding command, `tail -1` exited with code 0 even though `pytest` failed. Claude committed a red test suite in commit `437946b`. Around the same time, unrelated files were lumped into the initial build commits without clean logical separation.
- **What I decided and why:** I reset the dirty commit chain (`642f550..0afcf05`) to cleanly isolate the schema widening from the fetcher logic, and enforced `set -o pipefail` in test execution scripts. A passing pipeline must reflect the test runner's actual exit status, not the reporting command's exit code.
- **Claude contribution — accepted, changed, or rejected:** I rejected Claude's commit `437946b` as broken, fixed the execution pipe with `set -o pipefail`, and re-committed the working fix in `6fe3ec1`.
- **Still unresolved:** Subagents executing shell pipelines in subshells can still mask exit codes unless `pipefail` is configured globally in every script.
- **Commit trace:** `437946b`, `6fe3ec1`, `0afcf05`.

### 4. Hand-checking career portals and setting expectations.toml

**Date:** November 10, 2026  
**Trace:** `checks/expectations.toml`, `checks/check_watch.py`. **Commits:** `e54a26d`, `32d0d8c`.  

- **What I tried and expected:** Claude left a draft comment in `checks/expectations.toml` stating "Shubham confirms each line by opening the careers page himself." I expected to do a quick visual spot check.
- **What happened:** Opening `ramp.com/careers` manually in a browser showed that all search results and links route to Ashby (`ashbyhq.com` appeared 338 times, `greenhouse` 0 times). Probing `boards-api.greenhouse.io/v1/boards/ramp/jobs` directly confirmed only the single stale Dublin job. Stripe (`stripe.com/jobs/search`) and Figma (`figma.com/careers`) both route to Greenhouse, while Linear (`linear.app/careers`) routes to Ashby.
- **What I decided and why:** I verified each company's portal by hand and set conservative posting floors roughly an order of magnitude below live numbers (Stripe: 100 vs ~768 live; Figma: 20 vs ~144 live; Ramp: 20 vs ~169 live; Linear: 5 vs ~32 live). I updated `checks/expectations.toml` with my confirmation so `checks/check_watch.py` serves as a reliable external oracle that the agent cannot tamper with.
- **Claude contribution — accepted, changed, or rejected:** I accepted Claude's initial scraper numbers as candidate baselines, but rejected treating them as authoritative until I inspected the live HTML and network requests myself.
- **Still unresolved:** If an employer redesigns their careers portal or migrates ATS systems without updating `expectations.toml`, the checker will fail until manually updated.
- **Commit trace:** `e54a26d`, `32d0d8c`.

### 5. Reviewing the A2 patch: choosing Revise over Accept

**Date:** November 10, 2026  
**Trace:** `docs/js2/review/REVIEW_PACKET.md`, commit `8259d8b`.  

- **What I tried and expected:** When reviewing the subagent's patch for GATE A2 (`8259d8b`), Claude's orchestrator recommended accepting it because all 1083 unit tests were green and it passed the live Ramp test. I expected to confirm that recommendation.
- **What happened:** Inspecting the diff revealed that `FlooredProvider.parse()` enforced the floor only on the *first* parse call (`first, self._parsed = not self._parsed, True`). This relied on an unwritten assumption that `pipeline.run_once` always parses the live response before re-parsing older saved responses for pending judgment retries (A26). In mutation `m2`, flooring every parse still passed all 76 unit tests because our tests lacked a scenario with a pending retry on an older shrunken payload.
- **What I decided and why:** I rejected Claude's recommendation to accept and chose **Revise** in `docs/js2/review/REVIEW_PACKET.md`. Relying on call order inside an adapter is an architectural smell. The floor check belongs at the loop-fetcher level before passing the body to `run_once`, rather than wrapping the provider.
- **Claude contribution — accepted, changed, or rejected:** I accepted the subagent's validation schema for `min_postings`, but rejected Claude's sign-off recommendation in favor of documenting the ordering flaw and requiring an explicit architectural revision.
- **Still unresolved:** Until the loop-fetcher refactoring lands, `FlooredProvider` remains in place, protected only by the test I wrote in episode 6.
- **Commit trace:** `affcbdd`, `8259d8b`, `docs/js2/review/REVIEW_PACKET.md`.

### 6. Writing the missing test: catching mutation m2 in test_floor.py

**Date:** November 10, 2026  
**Trace:** `tests/watch/test_floor.py` (`test_pending_retry_from_an_old_raw_below_the_floor`).  

- **What I tried and expected:** To prove the flaw identified in my review decision, I wrote a multi-run test in `tests/watch/test_floor.py` that would fail under mutation `m2` (flooring every parse) while passing on the current code.
- **What happened:** I constructed a 3-run test: Run 1 sets baseline with 3 Linear jobs. Run 2 adds ID `[3]` with 4 jobs, leaving it pending. Run 3 introduces a floor of 5 with 5 jobs (`[0, 1, 2, 4, 5]`), forcing `run_once` to parse the live response (5 jobs $\ge$ 5) and then re-parse run 2's saved raw response (4 jobs < 5) to retry pending ID `[3]`. On current code, the test passed (1096 total tests passed). When I injected mutation `m2` by changing `if first and not board.is_empty` to `if not board.is_empty`, the test failed immediately because the second parse raised `InvalidResponse("below_floor", "4 < 5")`.
- **What I decided and why:** I committed the new test to ensure that any future refactoring of `FlooredProvider` or `pipeline.run_once` cannot silently break pending retries when older raw responses fall below the active floor.
- **Claude contribution — accepted, changed, or rejected:** Claude identified mutation `m2` in `mutations.txt` but left it untested. I wrote and verified the test implementation myself, confirming both red (under mutation) and green states.
- **Still unresolved:** If a pending job's original raw response is deleted or corrupted on disk, `run_once` cannot resolve it regardless of the floor.
- **Commit trace:** `affcbdd`, `c001ae0`, `tests/watch/test_floor.py`.

## Job-Search Agent 1


**Student:** Shubham Bagwe  
**Written:** October 31, 2026

> **Retrospective note:** I wrote this file on October 31, after the fact, using `docs/BUILD_LOG.md` as the chronology. These are retrospective entries, not contemporaneous diary entries.

This log records six episodes in which my expectations, decisions, or the tools pushed back during the build. The entries distinguish my decisions from Claude's analysis and implementation. Commit references are included where the supplied record identifies them; where it does not, I say so rather than infer a hash.

## 1. Persona boundary

**Date:** October 29, 2026  
**Trace:** `docs/BUILD_LOG.md`, approximately 17:40 ET; persona fixture `persona/kiran-joshi.resume.example.json`. **Commit:** not identified in the supplied record.

- **What I tried and expected:** I considered using my own résumé as the persona and asked Claude to ghostwrite `CONTRACT.md` and this reflection in my voice. I expected that to be a quick way to get the project started.
- **What happened:** Claude refused to ghostwrite those student-owned artifacts and pointed to the assignment's fictional-persona requirement. I then drafted a fictional fixture, Kiran Joshi, using only role targets and skill categories from my `career-ops` profile.
- **What I decided and why:** I used a fictional persona rather than my real résumé so the project would respect the assignment boundary and avoid using my personal résumé as the test subject.
- **Claude contribution — accepted, changed, or rejected:** I accepted the boundary Claude identified. I changed the approach by creating the fictional fixture myself; I did not accept Claude as the author of my contract or reflection.
- **Still unresolved:** The supplied build-log excerpt does not identify the exact persona-fixture commit or document any further open persona decision.

## 2. Datadog was the wrong board

**Date:** October 29, 2026  
**Trace:** `docs/BUILD_LOG.md`, approximately 18:00–18:05 ET. **Commit:** the subsequent Stripe contract work is traced to `053fda0`; the supplied record does not identify a separate Datadog-rejection commit.

- **What I tried and expected:** I evaluated the initial Datadog recommendation against my intended title rule: `Software Engineer`, `Full-Stack`, `Backend`, or `Frontend`, excluding `Senior`, `Staff`, and `Intern`. I expected the suggested board to contain usable roles for the agent.
- **What happened:** Applying my actual title rule to 397 Datadog postings produced **0 passing postings**. Many matches from the loose initial regex were Sales Engineer roles; the software roles were Senior, Staff, or Intern.
- **What I decided and why:** I rejected Datadog and moved to Stripe. The recommendation was not useful once checked against the actual role boundary I intended to enforce.
- **Claude contribution — accepted, changed, or rejected:** I rejected the initial Datadog recommendation. Claude then probed the available boards under my title rule and surfaced Stripe; I accepted Stripe after reviewing the result (55 title-passing postings, 35 with at least two matching skills).
- **Still unresolved:** The supplied record does not establish whether another board would have been a better choice under a broader or different role definition.

## 3. Making the US-only rule hand-checkable

**Date:** October 29, 2026  
**Trace:** `docs/BUILD_LOG.md`, approximately 18:10–19:19 ET. **Commits:** `053fda0`, `c1bd530`, `7aa5d0f`.

- **What I tried and expected:** I started with a location rule that said a posting should clearly name a US city. I expected that wording to let a person consistently decide whether a posting was US-based.
- **What happened:** A posting in Bengaluru (`7543868`) passed the title and skill checks in the October 29 Stripe snapshot. My initial location wording was also ambiguous across 294 distinct `location.name` strings, including abbreviations, mixed US/non-US lists, `Toronto, CA`, and `N/A`.
- **What I decided and why:** I added a hard US-only location gate and required ambiguous or mixed locations to fail closed as `NOT_ESTABLISHED` / `NO_MATCH`. That made the rule reproducible instead of relying on an intuitive reading of a location string.
- **Claude contribution — accepted, changed, or rejected:** Claude's review also identified other contract gaps: baseline wording, missing strict JSON validation, incompatible judge/hand-label scales, punctuation handling for `C#`, plain-English false positives for `react`, `express`, and `rest`, and escaped HTML in Greenhouse content. I changed the contract to address those issues. At my direction, Claude compiled the 294 location strings into finite US and non-US signal lists for §6.4 and found `8127182` as the fewer-than-two-skills hand-check case. I accepted that extraction as implementation support, while retaining the policy decision that the location gate should be US-only.
- **Still unresolved:** The rule is based on finite signals and deliberately sends mixed or unestablished strings to `NO_MATCH`; it cannot establish the real-world work location beyond what the board's location text says.
- **Commit trace:** `053fda0`, `c1bd530`, `7aa5d0f`.

## 4. Reducing the cost of headless calls

**Date:** October 29–30, 2026  
**Trace:** `docs/BUILD_LOG.md`, approximately 17:50 ET on Oct 29 and 02:05–03:10 ET on Oct 30. **Commits:** `33ea56e` (Plan Amendment R1), `f2f3565` (integration), `b647a82..d53dabe`, `b3f3d30..7188965` (review/audit fixes).

- **What I tried and expected:** I wanted to run `claude -p` using my Claude subscription without an API key. I expected headless execution to be inexpensive and straightforward.
- **What happened:** A default call cost about `$0.17` because it loaded local plugins, hooks, and `CLAUDE.md` files. `--bare` failed with `Not logged in` because bare mode required an API key. The parallel worktree build also exposed guessed function signatures that would have caused a `TypeError`; later reviews found a fail-open child-environment denylist and a path for free-text model fields to echo résumé values.
- **What I decided and why:** I adopted a fresh empty working directory under `data/tmp/` and restricted project settings, safe mode, session persistence, and tools. The recorded calls then cost about `$0.008–$0.025` with roughly 1.6k–1.9k context tokens. I also kept the integration and safety fixes rather than accepting the initial parallel interfaces as complete.
- **Claude contribution — accepted, changed, or rejected:** I accepted the measured low-cost invocation pattern in amendment R1. I changed the integration by reconciling interfaces and removing duplicate implementations. I accepted the review findings and fixes that replaced the child-environment denylist with an explicit allowlist and added `RESUME_VALUE_ECHO` rejection for sensitive résumé content in free-text fields.
- **Still unresolved:** The `claude` subprocess can contact hosts internally that Python's `AllowListTransport` cannot inspect or restrict; that limitation is separately disclosed in the sign-off.
- **Commit trace:** `33ea56e`, `f2f3565`, `b647a82..d53dabe`, `b3f3d30..7188965`.

## 5. The v2 held-out-example exposure

**Date:** October 30–31, 2026  
**Trace:** `docs/BUILD_LOG.md`, Chapter 2 pre-freeze check. **Commits:** `c2e5599`, `ed2c64c`, `6f5dc0a`.

- **What I tried and expected:** I drafted a v2 prompt candidate and expected its examples to clarify the decision rule without contaminating the held-out evaluation.
- **What happened:** Before the prompt was frozen, Claude's pre-freeze review flagged that several examples in my draft came from held-out postings. Those examples would have exposed held-out information to the prompt.
- **What I decided and why:** I replaced the held-out-derived examples with the full `CONTRACT.md §6` lists before freezing v2. This reduced direct exposure of held-out examples and kept the prompt tied to the predeclared contract.
- **Claude contribution — accepted, changed, or rejected:** I accepted Claude's warning and the replacement approach, and directed the change. I did not treat the original draft as a valid clean held-out prompt.
- **Still unresolved:** The v2 draft had already contained held-out-derived examples before the pre-freeze correction. That exposure remains a limitation of the experiment record; the corrected frozen prompt does not erase the earlier draft exposure.
- **Commit trace:** `c2e5599`, `ed2c64c`, `6f5dc0a`.

## 6. Chapter 3: keeping I/O out of the model

**Date:** October 31, 2026  
**Trace:** `docs/BUILD_LOG.md`, Chapter 3 surface comparison. **Commit:** `8fea85b`.

- **What I tried and expected:** I compared three action surfaces and wanted to determine whether giving the model direct fetch and state-editing tools was worth the added autonomy.
- **What happened:** In surface (c), Claude fetched the board through `WebFetch` in five chunks and edited `state.json`. That cost `$0.1311` versus `$0.0234` in surface (a); a summarizing model truncated one posting mid-entry, hiding its ID, and the model then had to compare more than 700 IDs manually.
- **What I decided and why:** I chose surface (a): Python performs network fetch, SHA-256 logging, and atomic state updates; the model receives payloads on stdin with `--tools ""`. This was cheaper and kept deterministic I/O and state handling outside model judgment.
- **Claude contribution — accepted, changed, or rejected:** I rejected the higher-autonomy surface (c) as the design to ship. I accepted the evidence from the comparison and selected the constrained surface (a); the decision to keep I/O in Python remained mine.
- **Still unresolved:** The comparison covers the tested surfaces and workload; it does not establish that every future task should use the same autonomy boundary.
- **Commit trace:** `8fea85b`.
