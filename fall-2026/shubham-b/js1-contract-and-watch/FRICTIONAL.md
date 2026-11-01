# FRICTIONAL.md — Where the Build Pushed Back

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
