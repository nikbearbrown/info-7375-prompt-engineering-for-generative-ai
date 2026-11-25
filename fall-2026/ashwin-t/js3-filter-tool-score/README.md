# Job-Search Agent 3: the filter, the tool, and the score

Ashwin Thankachan · INFO 7375 · Fall 2026.

The persona, Supriya Sharma, is invented (`data/supriya-sharma.resume.json`). No real résumé is used.

## Status on 2026-11-25

The table maps each rubric component to its artifacts and verification evidence.

| Brief step | Where | State |
|---|---|---|
| 1. FILTER.md before the build | `FILTER.md` (committed alone at `a3a7a2af`, before any filter code) | Done; approved by Ashwin |
| 2.1 Filter and reject audit | `jobfilter/filter.py`, `labels/`, `audit/` | 47 required sample rows (30 random rejects, 11 closest calls, 6 kept) confirmed by Ashwin on 2026-11-25 **after** seeing Codex's suggestions and the filter results, without per-posting reasons: a confirmation, not a blind audit (`audit/REPORT-v1.0.md`). 25 of the 30 random rejects failed the role gate, so a further blind draw of 20 engineering-titled rejects was added; Ashwin answered all 20 (`audit/BLIND-EXTRA.md`) |
| 2.2 Source-grounded shortlist (**filter v1.0**, 18 postings) | `SHORTLIST.md`, `shortlist/` | 90 claims labeled with source attribution, all by Codex (29 excerpt-based, 61 checked against text and fields). Ashwin labeled a sample of 15 claims with the Codex label hidden; agreement with Codex 12 of 15 after one re-label (H12's first card stated a false fact) and one correction (`audit/BLIND-EXTRA.md`). Relevance-versus-entailment is measured in `shortlist/RELEVANCE-EXAMPLE-LISTS.md`: 7 of 18 KEEPs rest on topic words found only in "such as…" lists |
| 2.3 Tool server and two evaluations | `serve.py`, `jobfilter/mcp_server.py`, `transcripts/`, `evaluations/` | Built and probed. Both trust decisions approved by Ashwin (wording drafted with Codex). Server 1.1.0 discloses its transcript writes. Later probe: both servers answer `tools/list` before `initialize` (`evaluations/*/preinit-probe-2026-11-25.jsonl`) |
| 2.4 What moves the score | `CHANGE.md`, `changes/` | One controlled v1.1 change with before/after results and disclosed prior label exposure in `CHANGE.md` |
| 3. Sign-off and driver's seat | `SIGNOFF.md` | Signed by Ashwin on 2026-11-25, for the limited checks described, not full rubric completion. Driver's-seat table approved with Ashwin's changes |
| Frictional | `FRICTIONAL.md` | Lines drafted with Codex, confirmed by Ashwin as descriptions of the recorded events; three personal slots filled on 2026-11-25 (evening) with lines Ashwin chose from Claude-drafted options |

## Known unresolved limitations (recorded 2026-11-25, after implementation)

From Ashwin's retrospective review of `drafting/IMPLEMENTATION-NOTES.md`:

- **I5:** structured remote fields are shown but not scored. Ashwin's position is that conflicting fields should
  give REVIEW.
- **I7:** `Munich, DE` is read as Delaware. This parsing defect did not change that posting's decision.
- **I8:** only empty descriptions become REVIEW. Non-empty text can still be truncated.

None of these is fixed. The code and the committed results are unchanged.

## Sample sizes: what the brief requires and what we chose

| Item | Size here | Brief | Origin of the size |
|---|---|---|---|
| Random rejects judged by hand | 30 of 750 | **Required: at least 30** | Brief minimum |
| Closest calls near the threshold | 6 at score 6 + 5 at score 7 | **Required**, no size given | Chosen by Claude Code (`jobfilter/audit.py`) |
| Kept sample | 6 of 13 | **Required**, no size given | Chosen by Claude Code |
| Exclusion-check postings (level II, "manager", forward deployed) | 8 | Not required | Chosen; FILTER.md section 10 promised it; optional |
| REVIEW postings | 7 (all) | Not required | Chosen; optional |
| Held-out labels | 30 | **Required:** "measure on labels you held out", no size given | Chosen by Claude Code (`jobfilter/heldout.py`) |
| Shortlist | all 18 v1.0 KEEPs | **Required:** label every claim for each shortlisted posting | Set by the filter, not by hand |
| Claims per posting | 3 to 5, giving 90 | **Required:** label **every** claim | The 3–5 limit was chosen in `prompts/claims-v1.md` |

The brief allows no reduction below its minimums. The 47-posting minimum audit is the first three rows. The 90
claims are all required, because the brief says "label every claim".

## Language and toolchain

- **Language:** Python 3, standard library only. Tested on Python 3.9.6 (`python3`) and 3.12.15
  (`/opt/homebrew/bin/python3.12`).
- **Model provider:** Claude only, through Claude Code 2.1.285 (`claude -p`, headless) with `claude-opus-5-5`.
  No SDK and no API key.
- **Tool server:** MCP over stdio, newline-delimited JSON-RPC 2.0, written from scratch.

## Commands

Run every command from this folder. All are offline unless they are marked live.

**From the submitted ZIP:** extract it, run `cd js3-filter-tool-score`, then `python3 -m unittest`.
The supplied `corpus/postings.json` supports scoring and tests without JS2.
**Repository-only rebuild:** `python3 -m jobfilter.corpus --build` requires the sibling JS2 folder and its
`runs/2026-11-09T20-21-52Z-live/` raw responses and trace. These source files are not bundled in the JS3 ZIP.
Skip the rebuild when using the ZIP; it is not a prerequisite for tests or scoring.

```bash
python3 -m unittest
```

```bash
python3 -m tests.test_wrong_versions
```

```bash
python3 -m jobfilter.corpus --build
```

```bash
python3 -m jobfilter.run v1.0
```

```bash
python3 -m jobfilter.run v1.1
```

```bash
python3 -m jobfilter.audit_batches
```

```bash
python3 -m jobfilter.audit --exploratory
```

```bash
python3 -m jobfilter.audit --report
```

```bash
python3 -m jobfilter.compare v1.0 v1.1
```

```bash
python3 -m jobfilter.claims --sheet
```

```bash
python3 serve.py
```

What each one does:

- `python3 -m unittest`: all 87 tests.
- `python3 -m tests.test_wrong_versions`: the wrong-version matrix.
- `python3 -m jobfilter.corpus --build`: rebuilds `corpus/postings.json` from the JS2 raw files, checking their
  sha256.
- `python3 -m jobfilter.run v1.0` and `v1.1`: score all 805 postings and seal the held-out decisions.
- `python3 -m jobfilter.audit_batches`: writes the blind review cards for the 47-posting minimum audit.
- `python3 -m jobfilter.audit --exploratory`: writes the AI-assisted exploratory audit.
- `python3 -m jobfilter.audit --report`: the hand-judged audit. It refuses to run until `labels/audit-sheet.csv` has
  all 47 hand verdicts.
- `python3 -m jobfilter.compare v1.0 v1.1`: the held-out comparison, potentially contaminated.
- `python3 -m jobfilter.claims --sheet`: writes the claim-labeling sheet from the saved run.
- `python3 serve.py`: the tool server on stdio. Add `--transcript transcripts/NAME.jsonl` to record both directions.

Two commands are **live** (they call Claude):

```bash
python3 -m jobfilter.claims --run
```

```bash
claude -p "$(cat prompt.txt)" --output-format json --mcp-config mcp-config.json --strict-mcp-config --tools "" --allowedTools mcp__js3__score_posting --no-session-persistence --setting-sources ""
```

The second one ran from `evaluations/own-server/claude-client-2026-11-25/`; `command.txt` there has the details.

## What ran (all 2026-11-25, UTC)

- **Corpus:** 805 postings from the JS2 live run of 2026-11-09. One expected board,
  `greenhouse/klaviyo-nonexistent-js2`, failed on purpose, so coverage is 5 of 6 boards. A 30-posting held-out set
  was drawn and sealed (`labels/heldout-keys.json`), and Ashwin labeled it blind (`9757ee7b`).
- **Filter runs on the 775 development postings:**

  | Version | KEEP | REVIEW | REJECT | Notes |
  |---|---:|---:|---:|---|
  | v1.0 | 18 | 7 | 750 | |
  | v1.1 | 20 | 7 | 748 | The one-change experiment: 2 Mission Manager postings moved (`CHANGE.md`). Not used for the shortlist or the tool server |

- **Live Claude claims, 13:23 UTC:** filter v1.0's 18 shortlisted postings, 18 valid replies, 90 claims
  (`SHORTLIST.md`). v1.1's 2 extra KEEPs have no claims.
- **Tool server:**
  - 12:38 UTC: our client probed `claude mcp serve` (`evaluations/other-server/`).
  - 13:21 UTC: our client probed our own server (1.0.0), then Claude Code used it as a real client
    (`evaluations/own-server/`, `transcripts/`).
  - 20:32 UTC: our client re-probed the corrected server 1.1.0 (`evaluations/own-server/`).

## Wrong versions (FILTER.md section 7)

Each wrong version fails at least one test written to catch it.

| Version | The mistake | Caught by |
|---|---|---|
| W1 | Substring matching: "java" inside "javascript", "sr" inside "sre" | `JavaScript is not Java`, `SRE does not contain the term sr` |
| W2 | A high skill count overrides the role gate | `support role with many tools stays rejected` |
| W3 | Missing or `Remote, Global` location counts as US remote | three REVIEW cases |
| W4 | A missing description becomes a rejection | `missing description -> REVIEW` |
| W5 | Boston in the description sets the location | `Boston in boilerplate, London job -> reject` |
| W6 | Aliases and repeats inflate the score | `python + python3 count once` |
| W7 | A present quote counts as support, even when negated | `tests/test_claims.py::test_w7_negated_quote` |
| W8 | "software engineer" admits Forward Deployed roles | `forward deployed software engineer excluded` |

## Folder map

| Path | What it holds |
|---|---|
| `FILTER.md` | The filter and evidence rules, with the section 10 change log |
| `CHANGE.md` | Step 2.4: where each number comes from, and the one change |
| `SHORTLIST.md` | Step 2.2 |
| `SIGNOFF.md` | Step 3 |
| `SOURCES.md`, `FRICTIONAL.md` | Sources and contributions; the Frictional log |
| `jobfilter/` | The code |
| `tests/` | 87 tests |
| `filters/` | v1.0 and v1.1 |
| `runs/` | Decisions; held-out ones are sealed |
| `labels/` | Held-out labels, the audit sheet (hand), AI-assisted verdicts, blind review cards |
| `audit/` | Exploratory audit report and false friends |
| `changes/` | The v1.1 record and the held-out comparison |
| `shortlist/` | Claims run and labeling sheet |
| `evaluations/`, `transcripts/` | Tool-server probes and evaluations |
| `drafting/` | Claude Code's notes: filter interpretations, evaluation sets |
| `audit/BLIND-EXTRA.md` | Human checks added after review: 20 new engineering rejects (9 corrected after review, so not all blind), 15 claims and 2 hand-computed scores, all answered (`python3 -m jobfilter.blind_extra report`) |
| `shortlist/RELEVANCE-EXAMPLE-LISTS.md` | KEEPs whose topic matches come only from "such as…" lists (`python3 -m jobfilter.such_as v1.0`) |
