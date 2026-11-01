# FRICTIONAL — Job-Search Agent 1

Entries are from 2026-10-30 unless they say otherwise (the labels arrived on 2026-10-31), in US Eastern time (EDT, UTC-4), and are linked to commits in this folder's git history or to saved files.

The entries come in two kinds:

- **[process log]** entries record what happened in the Claude Code session. Claude Code drafted them and Aditya reviewed them.
- **[Aditya]** entries are Aditya's own account. Claude did not write them.

---

## [process log] 16:00–16:45 — Requirements, policies and data source

- **Tried / expected:** read the assignment PDF and the four linked course pages. We expected the Greenhouse public API to be enough for the whole assignment.
- **What happened:**
  - All four pages (`ai-policy.md`, `frictional.md`, `github-submission.md`, `relative-quartile.md`) were fetched and read.
  - The AI-policy **video** was not watched by Claude, because Claude cannot watch video. Whether Aditya watched it is recorded only in his own entry.
  - `github-submission.md` gives the path `fall-2025/.../assignment-XX/`, while the PDF says `fall-2026/first-name-last-initial/js1-contract-and-watch/`. **Decision:** follow the PDF.
- **Friction:** the deadline was the same day, so a "second calendar day" run was impossible. We looked for a genuine earlier response instead.
  - The Internet Archive had exactly one capture of the endpoint, dated 2026-09-22T18:19:13Z.
  - Parsing the download failed with `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8b`. The archive served the body with `Content-Encoding: gzip`, and curl had been run without `--compressed`.
  - **Response:** keep the bytes exactly as served, rename the file to `.json.gz`, and record a hash both of the gzip bytes and of the decompressed JSON. The original server ETag, preserved by the archive as `x-archive-orig-etag: W/"cf5c622455af09550354174c86b51890"`, is identical to the first 32 hex characters of our SHA-256 of the decompressed JSON (`cf5c622455af09550354174c86b51890…`). That is consistent with the body being unaltered. We infer that the ETag is a truncated SHA-256; we haven't verified it.
- **Evidence:** `evidence/snapshots/*.meta.json`, commit `710b152`.

## [process log] 16:45 — Isolating Claude CLI calls

- **Tried:** `claude -p --bare` for a context-free call.
- **What happened:** `--bare` accepts only `ANTHROPIC_API_KEY`, never the logged-in OAuth session, so it couldn't be used.
- **Response:** use the logged-in CLI with these flags: `--tools ""`, `--strict-mcp-config`, `--setting-sources ""`, `--disable-slash-commands`, `--no-session-persistence` and our own `--system-prompt`, run from an empty temp directory.
- **Probe result:** the model reported no files, tools or CLAUDE.md in its context. It did see the account email and the environment block (working directory, platform), which the CLI adds on its own.
- **Unresolved:** temperature can't be set through the CLI. Each response's `modelUsage` lists `claude-haiku-5-5` next to `claude-opus-5-5`. We take the Haiku entry to be CLI housekeeping, but we haven't verified that.

## [process log] 17:05–17:30 — Contract draft, conflict check, approval

- **What happened:** Aditya supplied the contract text at 17:05, and it was committed verbatim as `710b152`. Claude counted the rule over the 903-posting snapshot before any project code existed.
  - Only **5 of 903** postings are relevant, and 3 of the 258 new ones.
  - "databricks" appears in **903 of 903** descriptions, because it is the employer's name.
  - "spark" is not on the persona's résumé.
- **Decisions, by Aditya** (commit `22d2b42`, 17:30 EDT):
  - **Rule:** kept as written.
  - **Sample:** use a grouped diagnostic sample rather than a random one.
  - **Split proportions:** Claude proposed an even split of the sample; Aditya changed it to uneven targets (3/3/4 for dev, 2/4/4 for held-out), with duplicates kept in the same split.
  - **"databricks":** kept, and its effect documented.
  - **R1:** an approved clarification of how a skill matches a résumé entry.
  - **R3:** Aditya tightened the guard to an _exact_ `example.com` domain.
  - **R4:** added by Aditya, so cited résumé evidence is validated, not just the field path.
- **Evidence:** `CONTRACT.md` revision log; `git show 710b152:CONTRACT.md` for the original text.

## [process log] 17:30–17:40 — Implementation and tests

- **Sample:** the procedure and seed were committed (`93fa63a`) before the generator ran (`6caf6db`). The procedure needed no adjustment: dev 3/3/4 and held-out 2/4/4 came out exactly.
- **Surprise:** a Japanese-only title, `デリバリーソリューションアーキテクト`, normalizes to an empty string under contract §4 step 3. It is therefore treated as a missing title and gets `not_relevant`. This is what the contract specifies; it is documented as a limitation rather than changed.
- **Smoke test:** one real call on dev posting 6865698002 took 5.15 s and returned a valid JSON judgment (`evidence/smoke/`). It isn't counted in any experiment.
- **Tests:** 72 tests passed on their first run (`69210f0`). Tests that never fail prove little, so two further checks were run:
  - the hand-written faulty variants (`tests/faulty_variants.py`) are flagged by the contract checks;
  - `tests/mutation_check.py` plants each wrong version into a copy of the real code. All three mutants were caught (`evidence/mutation_check_output.txt`).
  - The weak point: mutant M1 (dropping the posting-id check) is caught by only one test, because the evidence checks usually reject a swapped response anyway.

## [process log] 17:38–… — The two watch runs

- **Run 1:** the seeded baseline from the archived 2026-09-22 response recorded 883 ids and reported 0 new.
- **Run 2** (live, 21:38:23–21:44:46Z):
  - The board returned 902 postings, **258 of them new** against the baseline.
  - All 258 got both verdicts; the run took 259 Claude attempts at about 5.5 s each, 4 at a time.
  - RECORD and JUDGMENT agreed on 258/258; 3 postings were relevant.
- **Real catch:** attempt 1 on posting 8892970002 ("Lead Solutions Architect…") cited `spark` from `skills.languages`, which isn't there. The validator rejected the attempt, and the fresh retry was valid. That is wrong version 2 occurring for real, not only in a test. Evidence: `evidence/runs/20261030T213823Z_live/judgments/8892970002.attempt1.json`.
- **Note:** the 20:39Z snapshot (903 postings) and run 2 (902) differ by one posting. Both have 258 ids that are new since Sep 22.
- **Offline check:** `scripts/verify_evidence.py` recomputes the new-id set and all 258 RECORDs, and re-validates all 258 JUDGMENTs. Every check passed.
- **Commit:** `850d9c1`.

## [process log] 17:44–17:50 — Sampling and prompt experiment (model calls)

- **Sampling:** 5 dev postings × 4 fresh calls with prompt v1, all 20 valid. Verdicts were unanimous within every posting, and each posting got the same set of cited skills every time.
- **v1 on dev:** 10/10 valid, and all 10 match the RECORD. Hand labels were not yet available.
- **Friction:** against the deterministic RECORD (not against hand labels, which had not been received yet), the dev set left v1 no room to improve. The one change for v2 therefore targets the only failure observed anywhere: the résumé-side `spark` mis-citation in watch run 2. That posting is not in the 20-posting sample.
  - v2 adds one paragraph, "Résumé check first…" (see `diff prompts/judge_v1.md prompts/judge_v2.md`).
  - v2 on dev: 10/10 valid, with the same verdicts as v1 (again compared with the RECORD).
  - Claude identified the problem and proposed the change. Aditya accepted the stated rationale at Checkpoint A (2026-10-30, after 17:54 EDT); he has not reviewed the diff itself.
- **Freeze:** both prompts were frozen at 17:46:59 EDT (`prompts/FROZEN.json`, commit `469d0a2`). That was **before** any held-out call and before any hand label was received.
- **Held-out:** v1 and v2 were run on the held-out set afterwards (commit `f97aca7`). Scoring waits for Aditya's labels.
- **Unresolved:** a dev set where the baseline already matches the RECORD on every posting can't show whether the change helps. The comparison mostly checks that v2 does no harm.
- **Independence check** (requested by Aditya): the `spark` posting is in neither split. No held-out label or experiment result was available before the freeze. Three smaller exposures are disclosed in `PROMPT_EXPERIMENT.md`. A fresh held-out set is impossible under the frozen procedure, because all 5 rule-relevant postings are already in the sample.

## [process log] 17:54 — Aditya's own test run (Checkpoint A, step 3; partial)

- Aditya ran `.venv/bin/python -m pytest -q` and `.venv/bin/python tests/mutation_check.py` in his own Terminal and sent a screenshot. Claude received it at 17:54 EDT. The screenshot doesn't show the time of the run.
- **Result shown:** `72 passed in 0.13s`, and all three mutants `CAUGHT`. The failing tests listed match `evidence/mutation_check_output.txt`.
- **Not yet shown:** `scripts/verify_evidence.py`, the personal-data grep, and a RECORD checked by hand.

## [process log] 2026-10-31 14:33 — Hand labels received and scored

- `check_labels.py` reported missing rows: dev 8/10, held-out 4/10.
- **Cause:** in 13 rows the `notes` field opened with `"` but never closed, so a CSV reader merged the following lines into that note. All 20 labels were present, one per line.
- **Response:**
  1. Committed Aditya's files byte-for-byte as received (`83c0b7e`, hashes in the commit message).
  2. Repaired formatting only: a closing `"` added to the 13 notes (`4d6322a`).
  3. Verified that the line-by-line labels are identical before and after. No judgment was changed.
- **Scores:**
  - **Sampling:** 20/20 calls agree with the hand labels.
  - **Prompt experiment:** v1 and v2 both scored 10/10 format and 10/10 agreement on dev and on held-out. The "always not_relevant" baseline scores 7/10 on dev and 8/10 on held-out.
  - **Hand labels vs RECORD:** they agree on all 20.
- **Outcome:** the revision can't be distinguished from the baseline, and the reports say so.

## [process log] 2026-10-31 15:19 — Mode 1 chat demonstration received

- Aditya ran the paste in claude.ai and saved the reply and his own notes. Claude did not edit either file.
- **Re-check by `agent/validate.py`:** the reply is rejected at the format stage. It contains 32 pairs of typographic quotes `“ ”` and no ASCII `"`.
- Its two quotes do occur in posting 6865698002, and the verdict matches the RECORD.
- **Unresolved:** whether the typographic quotes came from the chat output or from copying and saving. The file can't tell us.
- **15:23 EDT:** Aditya revised his notes, removing a paragraph that described the format check inaccurately. SOURCES.md was corrected to match. The earlier version remains only in local commit `fb0abf9`.

## [process log] 2026-10-31 ~15:36 — Aditya's hand check of one RECORD

- **What Aditya did:** worked through posting 8864368002 ("Senior Software Engineer — Backend (Files Team)", drawn with seed 7377 by `scripts/handcheck.py`). He applied A, B and C by hand and wrote down his verdict **before** running `handcheck.py reveal`.
- **What he reported:** his verdict matches the revealed RECORD, `not_relevant`. The RECORD fails on B ("senior") and on C (only one shared skill, databricks).
- **Not recorded:** whether his per-condition reasoning matched the RECORD on both B and C. Only the verdict match was reported.

## [process log] 2026-10-31 16:14 — Aditya's remaining checks

- Aditya confirmed that he saw **no** model output, selection groups or RECORDs before or while labelling.
- He sent a screenshot of his own Terminal; it shows the commands and their output but not the time they ran.
  - `scripts/verify_evidence.py`: **ALL CHECKS PASSED** (16 checks).
  - `scripts/privacy_scan.py`: 658 tracked files scanned, no private-terms file used, 6 findings. They are the same synthetic test values found earlier.
  - `scripts/handcheck.py show` and then `reveal`, in that order.
- The screenshot is not published, because it shows his username and machine name.

## [process log] 2026-10-31 16:28 — Clarifications and sign-off

- **"Assisted labels":** in his entry below, Aditya clarified that the phrase means only that Claude prepared the labelling sheets and rule reminders. He labelled all 20 postings himself.
- **Policy video:** Aditya reports he watched the course AI-policy video.
- **Sign-off:** Aditya instructed Claude to sign on his behalf with his name and the current time. Claude entered "SIGNED — Aditya Raj, 2026-10-31 16:28 EDT" in README.md.

## [process log] Action-surface modes 2 and 3 (real runs)

- **Observed in mode 3:** the agent never received the raw posting. Its `WebFetch` call sent the page through a summarising prompt it wrote itself: _"Return the job id, the exact title, and the full description text verbatim…"_.
  - It kept no raw evidence, and it invented its own state-file format.
  - Its quotes still passed our validator, so this time the summariser returned verbatim text. Nothing guarantees that.
- **Evidence:** `action_surface/mode3_agent_run.json`.

---

## [Aditya] Entries — written by Aditya (2026-10-31)

Rule design and sampling

Claude’s feasibility check found that the rule classified only 5 of 903 current postings as relevant. It also identified that “Databricks” appeared throughout the descriptions because it was the employer’s name, while Spark could not count because it was absent from the permitted résumé fields.

I accepted keeping the rule and documenting those limitations. I also accepted a deliberately selected diagnostic sample rather than relying on a random sample that might contain no relevant cases. The resulting experiment cannot estimate how common relevant jobs are across the board.

Accepted changes and remaining limits

I accepted Claude’s proposed v2 instruction to check résumé evidence first, following a response that incorrectly attributed Spark to a résumé field. This was an AI-proposed change that I approved, not a failure I independently discovered.

Remaining limitations include the assisted labels, the disclosed exposure involving held-out material, the small and deliberately selected sample, and the rule’s omission of factors such as location, work authorization, and actual experience requirements. The system’s “relevant” label should not be treated as proof that a person is qualified or should apply.
