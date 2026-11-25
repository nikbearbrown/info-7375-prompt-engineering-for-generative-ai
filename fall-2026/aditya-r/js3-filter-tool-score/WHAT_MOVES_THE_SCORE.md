# What moves the score (Chapter 9)

## 1. Every number, and where it came from

The origins used below:
- **hand-set:** chosen by reasoning, before any measurement;
- **inherited:** taken from a named earlier source;
- **chosen on dev labels:** picked by looking at Aditya's dev misses. That is fitting by hand. No optimizer fitted anything.

| Object | Value (v1.0 → v1.1) | Where | Origin |
|---|---|---|---|
| Normalization and whole-word matching | lowercase; non-alphanumeric runs become a space | `inherited/rules.py` | **inherited:** JS1 CONTRACT §4 |
| R-core points | +4 | `filters/*.json` `role` | hand-set (FILTER.md v1.0) |
| R-adjacent points | +2 | same | hand-set |
| Role phrases | 9 phrases | same | 5 **inherited** (JS1 §4A); 4 hand-set (`ml engineer`, `llm engineer`, `data scientist`, `research engineer`) |
| Level penalty | −6 | `level` | hand-set |
| Level words | 14 words | same | 12 **inherited** (JS1 §4B); `intern`, `internship` hand-set |
| Topic points | +1 per distinct group | `topic` | hand-set |
| Topic cap | 4 | same | hand-set |
| Topic groups (8) | persona skills | same | hand-set from the **inherited** persona résumé |
| Employer word ignored on its own board | on | same | **inherited idea:** JS1 R2. Hand-set as a rule. |
| Boilerplate segments ignored (v1.1) | off → **on**; share ≥ 0.20 | `topic.ignore_boilerplate_segments`, `js3/boilerplate.py` | change **chosen on dev labels** (the false friend). The 0.20 share is hand-set and not tuned. |
| Early-career points | +1 → **+3** | `early_career` | +1 hand-set; +3 **chosen on dev labels** |
| Years regex | `(\d{1,2})( (to )?\d{1,2})? (years?\|yrs?)` | `years` | hand-set |
| Years bands | N ≥ 5: −3, N 3–4: −1 → **N ≥ 5: −1** | `years.bands` | v1.0 hand-set; v1.1 **chosen on dev labels** |
| Threshold | 6 | `threshold` (overridable with `--threshold`) | hand-set. 5 was tested on dev and rejected. |
| Near-duplicate Jaccard / shingle size | 0.8 / 5 words | `js3/sample.py` | hand-set (amendment A1) |
| Seeds | 7375, 7376, 7377, 7378, 7379 | `js3/sample.py` | hand-set (§5, A3) |
| Sample sizes | 30 random rejects, 6+6 closest, keeps, 23 old held-out, 24 H2 | `js3/sample.py` | hand-set (§5, A2, A3) |
| Quote length | ≤ 300 characters | `js3/text.py` | hand-set (presentation only) |
| Tool server limits | `posting_id` ≤ 200 characters; 4 protocol versions | `js3/mcp_server.py` | hand-set. The version names come from the MCP specification revisions. |
| **Claude prompt** (context experiment) | system prompt `sha256 …` and `<filter_rules>` block (hashes in `FREEZE.json`) | `js3/claude_context.py` | written by Claude Code on 2026-11-25 and frozen before H2. Not tuned: only a 6-call format check on dev. |
| Claude settings | model `claude-opus-5-5`, effort `medium`, fresh isolated session, no tools | same | **inherited:** JS1/JS2 `agent/judge.py`. Temperature cannot be set via the CLI. |
| The JS1/JS2 judge prompt `judge_v2` | — | not used in JS3 | listed for completeness |

**What in this table could move a verdict:**
- **The filter file:** R, S, T, E and Y points, the phrase lists, and the boilerplate switch.
- **One setting:** the threshold.
- **For Claude only:** the context given in the user message (the persona, plus the `<filter_rules>` block or not).

Nothing changes model weights.

## 2. One score worked by hand: S43, `greenhouse:figma:6233043004`, "AI Engineer, Internal Tools"

Open `review/postings/S43.md` (the full captured text), or run `.venv/bin/python -m js3.explain 6233043004 --text`. Use Ctrl-F on the **title** and the **description**. Matching is by whole words after lowercasing, and punctuation counts as a space.

| Term | Rule | Find this | Points v1.0 | Points v1.1 |
|---|---|---|---|---|
| R | highest role tier in the title | title "AI Engineer, Internal Tools" contains `ai engineer` (R-core) | +4 | +4 |
| S | level word in the title? | none of the 14 words appears in the title | 0 | 0 |
| T | distinct topic groups, cap 4 | `llms` (T3) and `agent` (T4) in "Design, build, and productionize AI agents, … using LLMs, …"; `evaluation` (T6) in "Hands-on experience … or evaluation frameworks"; `aws` (T8) in "Knowledge of AWS Bedrock, …". No `python`, `sql`, `machine learning`/`ml`/`mlflow`, `databricks`/`delta lake`/`unity catalog`. Four groups, none of them in Figma boilerplate. | +4 | +4 |
| E | early-career phrase? | none (`new grad`, `entry level`, `early career`, `junior`, … are all absent) | 0 | 0 |
| Y | smallest N in "N years" phrases | one phrase: "**5+ years** of software engineering experience …" gives N = 5 | **−3** (N ≥ 5) | **−1** (N ≥ 5) |
| **Total** | keep if ≥ 6 | | **5 → reject** | **7 → keep** |

**Only Y moved it.** Aditya labeled this posting `yes` ("Building internal AI tools aligns directly with her agent experience"). It is one of the three dev misses that the v1.1 years change was chosen to fix. **Dev therefore cannot confirm that change; H2 tests it.**

## 3. One change at a time, measured on held-out H2

Pre-registered in `FREEZE.json` (commit `9cde2b9`) while the H2 sheet was still blank:
- **Baseline:** filter v1.0, threshold 6.
- **Fixed for every comparison:** the 24 H2 postings and Aditya's H2 labels.
- **Metric:** on the rows labeled yes or no, TP/FP/FN/TN, recall, precision and agreement, with every flip listed.

_Results are pending Aditya's H2 labels. They will be produced by `.venv/bin/python -m js3.experiment --labels labels/heldout2_labels.csv --out experiments/RESULTS_H2.json`, and copied here unedited._

## 4. Persistence is not proof of training

If the agent "remembers" something across sessions, look for a **file, a prompt or a setting**, not training:
- **The tool server** gives the same score for a posting in every Claude session. It recomputes the score each time from the same `raw/` captures and the same `filters/*.json`.
- **v1.1 behaves differently from v1.0 in every later session.** That is because a file changed (`filters/v1.1.json`, diffable in git). No model changed.
- **The Claude calls** were fresh sessions with `--no-session-persistence`, an empty working directory, and no settings, memory or CLAUDE.md. Arm B differs from arm A only by the `<filter_rules>` text in its context. If B keeps differing across sessions, that is the same context being re-sent, not learning.
- **The reverse also holds.** A Claude Code setup with a CLAUDE.md, memory files or project instructions would make behavior persist across sessions, and that persistence would still be context, not weights.
- **What was not done:** no fine-tuning, no gradient update and no training data. Claude's weights are identical across all of these runs. Only Anthropic could change them, and nothing here can show that it did or didn't.
