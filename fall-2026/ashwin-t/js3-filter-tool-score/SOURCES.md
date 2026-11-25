# Sources and contributions

Drafted by Claude Code on 2026-11-25. Ashwin reviews it with Codex.

## What I started from

- **The brief:** "Job-Search Agent 3 — The Filter, the Tool, and the Score", INFO 7375 Fall 2026
  (`assignments/assignment-js3-the-filter-the-tool-and-the-score.md`, and Canvas).
- **My JS2** (`fall-2026/ashwin-t/js2-loop-tools-diff/`, commit `e270605`):
  - Copied unchanged: `jobfilter/providers.py` (byte-identical to JS2's `jobloop/providers.py` at `e270605`, checked
    2026-11-25), `jobfilter/text.py` (says so in its first line), `data/supriya-sharma.resume.json` and `.gitignore`.
  - The corpus is built from JS2's saved live run, `runs/2026-11-09T20-21-52Z-live/raw/`. Every raw file's sha256 was
    checked against JS2's `trace.jsonl`, and all matched.
- **My JS1** (`fall-2026/ashwin-t/js1-contract-and-watch/`, commit `d95f05e`):
  - `text.py` came from JS1 by way of JS2.
  - FILTER.md names the JS1 rule as v0. **v0 was not re-run in JS3** (see SIGNOFF.md, Not checked).
  - The Cloudflare snapshot is unused. Only its titles were counted, for the Mission Manager question.
- **Not used:** the Reallocation Engine and Lectern, both named by the brief. No code from either was copied.
- **Data:** public, keyless job-board listings, Greenhouse `klaviyo` and `hubspotjobs`, Ashby `notion` and
  `supabase`, Lever `palantir`, fetched 2026-11-09 during JS2. The posting text belongs to those companies and is
  kept as evidence.
- **Protocol:** the Model Context Protocol. The server implements the stdio transport and the `initialize`,
  `tools/list` and `tools/call` messages, with protocol versions `2025-11-25`, `2025-06-18`, `2025-03-26` and
  `2024-11-05`. The specification was not re-fetched or link-checked in this session; behavior is shown by the saved
  transcripts, not by a cited page.
- **Tools:** Python 3 standard library; Claude Code 2.1.285 (desktop app and `claude -p`) with Claude Opus 5.5
  (`claude-opus-5-5`); Codex for drafting and review; git.

## What Ashwin decided or supplied

- **Deadline and design choices,** on 2026-11-25: deadline Wed 25 Nov 23:59 ET, use the saved JS2 run, draw new
  blind held-out labels.
- **FILTER.md:** approved before any filter code. The approval wording was drafted by Codex and sent by Ashwin. It
  included the threshold change from 6 to 7 and keeping the level-II and forward-deployed exclusions.
- **Held-out labels:** all 30, blind (`labels/heldout-sheet.csv`, committed alone at `9757ee7b`). Asked directly on
  2026-11-25, Ashwin confirmed these are their own judgments.
- **Clearance rule for labeling:** "keep clearance cases uncertain where Supriya's eligibility is unknown. Don't
  treat willingness as eligibility."
- **Audit verdicts:** supplied the 47 AI-assisted verdicts. Ashwin then stated they were Codex suggestions inferred
  from the held-out labels, not independent hand judgments (corrected in `b03e6b29`). Later on 2026-11-25 Ashwin
  confirmed all 47 unchanged (`7e5c3d02`). That confirmation came after seeing the suggestions and the filter
  results, and no per-posting reason was recorded, so it is a confirmation, not a blind judgment.
- **The v1.1 change:** instructed it (the narrow Mission Manager exception), and kept the held-out comparison
  labeled potentially contaminated.
- **Trust decisions and sign-off:** approved both trust decisions and the sign-off wording on 2026-11-25. Codex
  helped draft the wording. Signed: "Ashwin Thankachan, November 25, 2026", for the limited checks described, not
  full rubric completion.
- **Driver's-seat table:** approved on 2026-11-25 with two changes (the label "Intended division of
  responsibility", and the wording of the signature row).
- **Implementation readings I1–I9:** reviewed retrospectively on 2026-11-25, after implementation. Agreed with I1–I4,
  I6 and I9; disagreed with I5 and I7, which are recorded as unresolved; accepted I8 only as a limitation.
- **Ran the tests personally:** 55 tests at `b616bc09`, OK, exit 0 (`drafting/checks-run-by-ashwin.txt`).
- **FRICTIONAL.md:** supplied draft lines written with Codex, and confirmed them on 2026-11-25 as descriptions of
  the recorded events. Asked that the three personal slots be marked "Not supplied"; later that evening chose and approved one Claude-drafted option for each.
- **Not done by Ashwin before `7e5c3d02`:** blind audit verdicts, per-posting reasons, or human claim labels. The
  blind checks added afterwards are in `audit/BLIND-EXTRA.md`, which counts only what Ashwin actually filled in.

- **After a strict TA-style review (2026-11-25, evening; review text pasted by Ashwin):** Claude Code wrote
  `jobfilter/such_as.py`, `jobfilter/preinit_probe.py` and `jobfilter/blind_extra.py` with their tests, ran the
  before-`initialize` probes on both servers (22:25 UTC), and drew the blind worksheets. Any verdicts, labels or
  hand scores in `audit/BLIND-EXTRA.md` are Ashwin's, typed into the sheets named there.

## What Codex contributed (as relayed by Ashwin)

- Drafted FILTER.md from `drafting/FILTER-QUESTIONS.md`, suggested threshold 7, and drafted the approval wording.
- Labeled all 90 claims (`shortlist/claim-sheet.csv`, `label_source` column):
  - 29 from the excerpt-only review cards;
  - 61 checked against the saved posting text and structured fields, including 6 corrections of the excerpt-based
    labels.
- Drafted `labels/audit-ai-draft.csv`: 61 proposed verdicts inferred from Ashwin's held-out labels. The 47
  AI-assisted verdicts in `labels/audit-ai-assisted.csv` match it except row 35.
- Wrote several of the instructions Ashwin pasted into the chat, including the provenance corrections.
- Reviews this folder.
- On 2026-11-25 Codex confirmed it did not read the Cloudflare snapshot during this work.

## What Claude Code contributed

- **Questions:** drafted `drafting/FILTER-QUESTIONS.md`, and noted that threshold 6 never binds.
- **Code:** all of `jobfilter/` (except the files copied from JS2), `serve.py`, and all tests.
- **The claim prompt,** `prompts/claims-v1.md`: written by Claude Code, never tuned.
- **Runs:**
  - filter v1.0 and v1.1;
  - the live claims run at 13:23 UTC;
  - both tool-server probes;
  - the Claude-as-client run at 13:21 UTC.
- **Drafts:**
  - `README.md`, `CHANGE.md`, `SHORTLIST.md`, this file;
  - both `EVALUATION.md` files (without trust decisions);
  - `audit/FALSE-FRIENDS.md`;
  - the notes in `drafting/`.
- **Choices FILTER.md left open:** where filter.py had to interpret FILTER.md, Claude Code chose. Those choices are
  listed in `drafting/IMPLEMENTATION-NOTES.md`. Ashwin reviewed them retrospectively on 2026-11-25, after
  implementation; two disagreements, I5 and I7, remain unresolved.
- **Corrections and version history:**
  - First reported 59 tests when there were 46.
  - Committed AI-assisted verdicts as "Ashwin's audit verdicts" (`e5828b69` … `54cecbe8`), corrected in `b03e6b29`.
  - Committed `cf210f14` before its test passed, fixed in `036e6fae`.
  - Recorded Codex's 29 excerpt-based claim labels as Ashwin's own (`2d01d368` … `e13682ec`, `267dfff9`); Ashwin
    corrected that on 2026-11-25.
  - Printed the held-out labels while checking the sheet, which is one reason the held-out comparison is
    potentially contaminated.

## What Claude produced as data

- 18 claim replies (`shortlist/claims-v1-2026-11-25T13-23-12Z/raw/`).
- One client session's reply (`evaluations/own-server/claude-client-2026-11-25/claude-reply.json`).

Each is a real, dated `claude -p` response, saved unchanged. No fixture is presented as Claude output.

## Post-package Codex review and corrections (2026-11-25)

Codex compared every file of the **first** ZIP to commit `744630b1` and ran the 56 tests then present on Python
3.9.6 and 3.12.15. That check covers only the first package: the folder changed after `744630b1`. Every later ZIP
is built with `git archive` from the exact pushed commit named in that submission's Canvas comment, and its
extracted copy is re-tested (README, "From the submitted ZIP"). A file cannot name the commit that contains it, so
the final hash is in the Canvas comment, not here.
An initial concurrent run collided on shared test temporary paths; separate runs passed. The ZIP contains
103 files and 22 directory entries, not 125 files. Codex corrected stale approval/status wording, documented
the repository-only corpus rebuild dependency, and narrowed audit uncertainty statements to resolved labels
with explicit unknown-outcome sensitivity bounds. Ashwin subsequently confirmed personal review of reject-audit
postings; all 30 random rejects and then all 17 remaining required sample rows were explicitly confirmed unchanged. The hand sheet now records those later personal judgments and their prior AI exposure. Earlier AI-generated
verdicts and the contaminated evaluation remain disclosed.

The later personal audit review does not restore the independence of the earlier held-out comparison.
Codex applied these documentation/report corrections and transcribed the confirmed audit judgments; Claude
Code authored the original implementation and tests. No scoring rules, historical outputs or claim labels changed.
