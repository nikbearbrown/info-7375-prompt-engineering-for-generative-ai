# Job-Search Agent 3: the filter, the tool, and the score

Ashwin Thankachan · INFO 7375 · Fall 2026.

The persona, Supriya Sharma, is invented (`data/supriya-sharma.resume.json`). No real résumé is used.

## Status on 2026-11-25

**Incomplete parts** are marked ⚠ in the table.

| Brief step | Where | State |
|---|---|---|
| 1. FILTER.md before the build | `FILTER.md` (committed alone at `a3a7a2af`, before any filter code) | Done; approved by Ashwin |
| 2.1 Filter and reject audit | `jobfilter/filter.py`, `filters/`, `runs/`, `labels/`, `audit/` | ⚠ **Hand-judged audit 0 of 47.** Verdicts so far are AI-assisted (`audit/EXPLORATORY-v1.0-ai-assisted.md`). False friend demonstrated from text (`audit/FALSE-FRIENDS.md`) |
| 2.2 Source-grounded shortlist | `SHORTLIST.md`, `shortlist/` | ⚠ **0 of 90 claims labeled** by Ashwin |
| 2.3 Tool server and two evaluations | `serve.py`, `jobfilter/mcp_server.py`, `transcripts/`, `evaluations/` | Built and probed. ⚠ Both trust decisions are Ashwin's to write |
| 2.4 What moves the score | `CHANGE.md`, `changes/` | One change (v1.1) measured on held-out labels; **potentially contaminated** |
| 3. Sign-off and driver's seat | `SIGNOFF.md` | ⚠ Ashwin's to write and sign |
| Frictional | `FRICTIONAL.md` | ⚠ Ashwin's experience lines |

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

- `python3 -m unittest`: all 55 tests.
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
  | v1.1 | 20 | 7 | 748 | 2 Mission Manager postings moved (`CHANGE.md`) |

- **Live Claude claims, 13:23 UTC:** 18 postings, 18 valid replies, 90 claims (`SHORTLIST.md`).
- **Tool server:**
  - 12:38 UTC: our client probed `claude mcp serve` (`evaluations/other-server/`).
  - 13:21 UTC: our client probed our own server, then Claude Code used it as a real client
    (`evaluations/own-server/`, `transcripts/`).

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
| `tests/` | 55 tests |
| `filters/` | v1.0 and v1.1 |
| `runs/` | Decisions; held-out ones are sealed |
| `labels/` | Held-out labels, the audit sheet (hand), AI-assisted verdicts, blind review cards |
| `audit/` | Exploratory audit report and false friends |
| `changes/` | The v1.1 record and the held-out comparison |
| `shortlist/` | Claims run and labeling sheet |
| `evaluations/`, `transcripts/` | Tool-server probes and evaluations |
| `drafting/` | Claude Code's notes: filter interpretations, evaluation sets |
