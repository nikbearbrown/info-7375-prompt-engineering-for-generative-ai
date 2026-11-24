# FRICTIONAL — SponsorSQL final project

This account draws on the dated Claude draft and memory aid kept in `INFO-7375/final-project-notes/`, with claims checked against saved project files and commits. I don't count a review, gate choice, or signature as done unless a file records it.

## 2026-11-21 — Rules and answer key before the build

Claude prepared the pre-mortem, contract, and answer key for ten development questions before the agent code was committed. The pre-mortem identified title matching as a likely failure: a substring search could count “Metadata Analyst” as “Data Analyst.” A separate Python script calculated the key, and `evals/FREEZE.md` recorded its SHA-256 hash.

I looked over the preparation files on November 21. I didn't record which key rows I checked, and I didn't recount all ten answers independently. I recorded my agreement with the pre-mortem and contract later, in `SIGNOFF.md` on November 23.

**Trace:** `da6b416a`; `pre-mortem.md`; `CONTRACT.md`; `evals/FREEZE.md`.

## 2026-11-21 — First agent and its limits

Claude built SponsorSQL with Python's standard library and SQLite. Its loop observes, decides, acts, records, and stops, with at most two attempts and a ten-second query limit. The database opens read-only, and SQLite's authorizer restricts reads to the permitted table. The approval screen has a SHA-256 fingerprint, so a decision can be tied to the view shown.

After review fixes, 43 tests passed on Python 3.9 and 3.14. In the November 21 build environment, the Claude command line reported “Not logged in.” The evaluated SQL therefore came from separate Claude sessions, saved as received and replayed through the agent. Those runs demonstrate the replay path, not a live model call inside the loop. I didn't run the tests myself at this stage.

**Trace:** `ed4a2e1f`; `tests/`; `evidence.md`.

## 2026-11-21 — Held-out questions frozen

Five held-out questions and their key were saved before either question set received a model proposal. Both keys have hashes in `evals/FREEZE.md`, and the evaluator checks those hashes before scoring. This protected the saved keys from silent edits; five questions remain a small sample.

**Trace:** `dfbbb739`; `evals/FREEZE.md`.

## 2026-11-21 — First development score: 4/10

Contract v1's recorded replies passed four of ten development questions. D4, D5, D6, and D9 exposed the predicted title problem: substring matching counted near matches and missed punctuation variants even though the SQL ran. D3 exhausted the ten-second budget, so the loop stopped instead of returning a number. D8 kept a trailing-space title in a separate group.

A query can execute successfully while answering the wrong question. The independent key, rather than a successful SQL run, exposed the title-count errors.

**Trace:** `b65b7256`; `evals/FAILURE-LOG.md`; `evals/results/dev-round1-contract-v1.json`.

## 2026-11-21 — Revised contract: 9/10

Claude's v2 contract specified `title_has()` for whole-word title matching, trimmed labels, a `[blank]` group, and a rule limiting answers to the title classes named in a question. A no-join rule addressed the slow query. The second development run reached 9/10.

D8 still missed. Four source titles end in tabs or a non-breaking space. Python `strip()` in the key removes those characters, while SQLite `TRIM()` in the proposed SQL does not. That is a definition mismatch. The contract was not changed again after this score, so the held-out run used the frozen v2. V2 was scored before I reviewed it. I reviewed it on November 23 and accepted it, as recorded in `SIGNOFF.md`.

**Trace:** `710368ed`; `evals/PROMPT-CONTRACT-v2.md`; `evals/FAILURE-LOG.md`.

## 2026-11-21 — Held-out score: 5/5

The five held-out replies passed on their first and only scoring. H3 also exposed a misleading warning: a median wage was labelled as a `count`, so the system compared the wage value with the number of supporting rows and displayed `MISMATCH`. The answer passed the key, but the warning was wrong.

The five questions were written alongside the contract, and later review found that development hints appeared in the prompts. The 5/5 result supports these five recorded questions; it cannot establish accuracy on arbitrary requests or new files.

**Trace:** `53fbca0b`; `evals/FAILURE-LOG.md`; `evals/results/`.

## 2026-11-21 — Failure cases and a controlled reproduction

Ten deliberate cases exercised deletion, a hidden second statement, an off-limits table, a runaway query, contact details, a visa prediction, malformed replies, clarification, a stale approval, and an answer inconsistent with its rows. All ten behaved as predicted. The source table still contained 437,496 rows after the checks.

The controlled failure replayed the title-matching bug from October. The independent key caught it, and `title_has()` was the recovery. This was a reproduction of a known failure, not a prediction of a previously unseen one.

**Trace:** `c09ab7da`; `evidence/failures.log`; `evals/results/failures-after-review.json`.

## 2026-11-21 — Separate review and fixes

A separate Claude reviewer, without the build conversation, reported 18 findings. The project judged all 18 genuine. Nine prompted code changes, some partial: quote-aware text checks, removal of `printf`, a time limit capped by remaining budget, protection against gate-view spoofing, `stopped_error` records for crashes, and stricter score comparisons. The other nine were documented, including owner-review timing, development hints in prompts, the limited held-out set, and the controlled failure's status as a replication.

The saved replies were scored again with the stricter comparators. The numbers remained 4/10, 9/10, and 5/5. I haven't written my own judgment of each finding or ranked what to fix next.

**Trace:** `a8cbf96d`; `c314f474`; `audit-note.md`; `evidence/independent-review-2026-11-21.md`; `evidence/rescore-after-review.log`.

## 2026-11-23 — Boston answer and approval screen

A run on the real database displayed 40 certified H-1B Data Analyst cases with a recorded Boston, MA worksite. The view included SQL, matching rows, the source checksum, an answer fingerprint, and the approve/refuse/defer prompt. The SQL was a recorded Claude reply replayed by the agent. That saved view didn't record a decision.

That evening, an AI-assisted check reran the 43 tests, compared D2 and H1 with their matching rows, and got 40 for Boston with an Excel `COUNTIFS` formula. A live call couldn't reach the gate because the `claude` executable wasn't installed. A replay was deferred during that check; that wasn't my decision.

Then I repeated the checks myself. I ran the tests and saw 43 pass. I compared D2 and H1 with their matching rows. I recounted Boston in the workbook with my own `COUNTIFS` formula and got 40, matching SponsorSQL. I reviewed contract v2 against v1 and accepted it, and I settled the Q4 and Q6 definitions. At the gate, I ran D2 with the recorded reply, looked at the SQL and the 40 matching rows, and approved the answer: run `20261124T031329Z-4d8997` stopped `approved_and_exported`. I signed `SIGNOFF.md` with the decision **narrow**.

**Trace:** `c983068a`; `evidence/gate-view-D2-2026-11-23.txt`; `evidence/assisted-checks-2026-11-23.md`; `evidence/owner-gate-approve-2026-11-23.json`; `SIGNOFF.md`.

## 2026-11-23 — First film and script revision

Claude assembled a 3:27 film in the requested order: executive summary, introduction, methods, and evaluation. It used the local Brutalist toolkit and a synthetic voice. Figures on screen came from saved output and were re-typeset and labelled. The toolkit gates passed, but frame inspection found problems they missed, including clipped animation endings, arrows starting inside boxes, small captions, and misplaced check marks. Those visuals were corrected.

I then requested script changes for B00, B01, B05, B08, and B09: remove the spoken H-1B definition while retaining its caption, add “blindly,” explain the permission rule in simpler language, and make the two question sets and scores clearer. For B11, Claude pointed out that the proposed claim that v2 was scored after owner review conflicted with the records; I chose wording that said scoring came first and review came later. For B12, I selected “Written by Atharva Hambir with Claude” after Claude objected to a credit line that reversed drafting and review. The synthetic voice was disclosed in `film/README.md` rather than spoken in the film.

Rebuilding revealed missing spaces in small text, such as “invisibletabs”; rendering the text larger and scaling it down fixed the display. The 5/5 bar in B09 was moved earlier, and an empty-looking interval in the outro was addressed. The second film ran 3:56. My review and acceptance of v2 are now recorded in `SIGNOFF.md`, so that line is supported.

**Trace:** `c983068a`; `2515ca54`; `film/README.md`; `film/beat_sheet.json`.

## 2026-11-23 — Full film check and later cuts

The next pass inspected every beat at four moments, compared visual cues with narration, checked the revised lines against project files, and measured the audio for gaps and clipping. B05's SQL definition was kept on screen longer. B08 changed “straight from the file” to “from the data,” because the key scripts read the database produced by the loader. Pronunciation was not verified, and the quiet export, measured at −24.7 LUFS, was left as it was.

I subsequently removed “never just because the model says it's done” from B04. The beat was re-rendered, gates reran clean, and the film was exported at 3:54. The final export runs 3:51. I haven't recorded here whether I watched the final export all the way through.

**Trace:** `7cfd0779`; `a6a9c490`; `cc572ed8`; `film/README.md`; `film/FACTCHECK.md`.

## Still open

- Run a question through the live Claude CLI. It wasn't installed, so the live path is still untested.
- Finish recording the stranger run in `STRANGER-RUN.md`: part A names Aditya, but the rest is blank.
- Upload the film and record its link when that has actually happened.
