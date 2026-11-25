# Job-Search Agent 3: The Filter, the Tool, and the Score

This repository contains five components built for Job-Search Agent 3:

- **Pre-code filter specification (`FILTER.md`):** Rules, evidence requirements, source expectations, and wrong-version definitions written and committed before any filter code existed.
- **Hand-judged baseline audit (`audit/filter-v1.0/`):** Manual judgments across a random reject sample, close calls, and all kept postings from the `v1.0` baseline run.
- **Source-grounded shortlist (`shortlist/`):** Claim-level verification labeling every claim as `supported`, `contradicted`, or `insufficient` with verbatim quotes from the posting text.
- **Stdlib MCP tool server (`agent/mcp_server.py`, `mcp/EVALUATIONS.md`):** A read-only stdio JSON-RPC 2.0 server written from scratch using the Python standard library, complete with scripted and live Claude Code transcripts and two server evaluations.
- **Single-variable rule iteration (`score/report.md`, `score/origins.md`):** One rule change (`v1.2`) chosen from `dev` labels and the audit, then evaluated once on `heldout` labels.

**Persona:** Sam Rivera, a fictional new-grad software engineer in the US (`examples/persona.example.json`). No real résumé, contacts, tracker, or applications are stored in this repository, and the agent never submits applications, sends emails or messages, or logs into accounts.

## Starting point

This project builds on my Job-Search Agent 2 (`../js2-loop-tools-diff/`), reusing its collection loop, allow-list policy, and skill matcher (`SOURCES.md` records what was copied and modified). Because JS2's Greenhouse responses did not include job description text to quote, JS3 re-collected all three boards with `?content=true` in a single run (`evidence/run-20261123-185425Z`, Nov 23, 2026: 3 GET requests returning 400 postings).

## Language and toolchain

- **Runtime:** Python `3.12.7`, standard library only (zero third-party dependencies).
- **Testing:** `unittest`.
- **Verification:** Tested on macOS. On Nov 24, 2026, Claude cloned this branch fresh at commit `2f40542` into a scratch directory and re-ran every command below except the live `agent.loop` collector (replaying the saved run instead) and `claude mcp add`:
  - All 57 unit tests passed, and all five wrong versions (`W1`–`W5`) were caught.
  - The filter, evaluation, shortlist, and survey-recount commands reproduced every number reported in this README.
  - Re-running the shortlist generator left all committed files unchanged (`git status` remained clean).

## Commands

Run all commands from this folder (`fall-2026/atharva-c/js3-filter-tool-score/`):

```bash
# Run all 57 unit tests
python3 -m unittest discover -s tests -t .

# Verify that wrong versions W1–W5 fail their corresponding tests
python3 -m tests.wrong_versions

# Load the saved Nov 23 run
python3 -m agent.postings

# Run the current filter (v1.2) and compare against dev labels
python3 -m agent.filter --labels labels/dev.csv

# Score a saved filter run against labels (reads saved files only)
python3 -m agent.evaluate evidence/filter-v1.2/decisions.jsonl labels/dev.csv

# Generate the source-grounded shortlist
python3 -m agent.shortlist

# Inspect a single posting in full
python3 -m agent.label_sheet --show affirm:8032173003

# Replay the scripted MCP client session
python3 -m tests.mcp_scripted_client out/scripted.jsonl

# Recompute all survey counts
python3 -m score.recount
```

**MCP server** (waits for a client on stdin; Ctrl+C to stop):

```bash
python3 -m agent.mcp_server
```

**Register it in Claude Code** (local scope, this project only):

```bash
claude mcp add --scope local js3-job-filter -- python3 "$PWD/agent/mcp_server.py"
```

**Re-collect live** (makes 3 real GET requests):

```bash
python3 -m agent.loop
```

## What is where

| Requirement | Location |
| :--- | :--- |
| **`FILTER.md` (rules, evidence rules, expected sources, wrong versions)** | `FILTER.md` (`v1.0` written before code; changelog through `v1.3`) |
| **Agent code and test suite** | `agent/`, `tests/` |
| **Reject audit (30 random rejects, close calls, kept set, confidence interval)** | `audit/filter-v1.0/`; summarized below and in `score/origins.md` |
| **False friend example** | Section below |
| **Source-grounded shortlist, relevance ≠ entailment, abstention counterexample** | `shortlist/shortlist.md`, `shortlist/CASES.md` |
| **From-scratch MCP server, transcripts, and two evaluations** | `agent/mcp_server.py`, `evidence/mcp/`, `mcp/EVALUATIONS.md` |
| **Single rule change on held-out and metric provenance** | `score/report.md`, `score/origins.md` |
| **Persistence vs. model training** | `PERSISTENCE.md` |
| **Human sign-off and driver's-seat record** | `SIGNOFF.md` |
| **Sources and friction log** | `SOURCES.md`, `FRICTIONAL.md` |

## Results

All results below reflect the single 400-posting collection from Nov 23, 2026. The reject miss-rate interval is a sample estimate; every other figure is an exact count for this run.

- **`FILTER.md` v1.0 kept 22 of 400 postings:**
  - Across `30` rejects sampled at random (seed `2026`) from `378`, I judged `0` should have been kept. The 95% Wilson confidence interval is `0%` to `11.4%` (roughly `0` to `43` of this run's `378` rejects)—a sample estimate rather than an exhaustive miss rate.
  - Across all `22` kept postings, I judged `11` to be genuine fits (`50%` precision for this run). `7` of the `11` wrong keeps asked for `3` years of experience.
- **Single rule change (`v1.2`) — `3` years now scores like `4` or more (`−0.40` in `R2`):**

| Version | `dev`: false positives | `heldout`: false positives | Recall (`dev` / `heldout`) |
| :--- | :--- | :--- | :--- |
| **`v1.0`** | `6` | `5` | `6/6` / `5/5` |
| **`v1.2`** | `0` | `4` | `6/6` / `5/5` |

- **`heldout` shows a smaller gain than `dev`:** Penalizing `N ≥ 3` eliminated `6` false positives on `dev` and `1` on `heldout`. `heldout` was evaluated once (`agent/evaluate.py`), and some held-out postings had already appeared in `audit/filter-v1.0/kept.csv` before `v1.2` was chosen (`score/report.md`).
- **Shortlist breakdown (`v1.2`):** The `15` postings kept by `v1.2` sort into `10` ranked entries, `1` `"I cannot tell"`, and `4` contradicted by their own posting text.

## False friend

`Manager, Software Engineering (Resilience Engineering)` (`affirm:7701909003`, Remote US) looks like a valid match under the scoring rules because `R1`'s pattern has no trailing word boundary, so `"Software Engineer"` matches inside `"Software Engineering"` (`+0.50`) and a skill hit adds `R4` (`+0.10`), giving it a passing score of `0.60`. In reality, the posting is for a seasoned Engineering Manager leading a team rather than an individual-contributor role for a new grad with 0–2 years of experience. It is rejected only because the `G1` seniority gate catches `"Manager"` in the title; the `0.60` score is still computed, but a gated posting is never kept. Without `G1`—or if a similar leadership title omitted an explicit seniority keyword—the open-ended `R1` match would surface a management role as a high-scoring junior engineering fit.

## Honesty notes

- **Two Day 1 survey claims in `FILTER.md` v1.0 were incorrect.** Both were documented in later versions while leaving `v1.0` untouched:
  - `"SWE II asks 5+ years"` was wrong: the posting asks for `1.5+` years (corrected in `v1.1`).
  - `"91 postings share a title"` was wrong: `173` postings share a board and title across `82` groups, and `91` is the number of extra copies (corrected in `v1.3`).
- **Live Claude Code transcript miscount:** Claude Code's answer states `"23 Software Engineer II postings"`, whereas a script recount of the 31 matched titles gives `22`. The saved transcript is preserved verbatim without editing.
- **Authenticity of transcripts:** Every Claude response in `evidence/mcp/` is an actual recorded output with its timestamp; the scripted MCP session (`evidence/mcp/scripted-transcript.jsonl`) is explicitly labeled as a deterministic script rather than a model.
