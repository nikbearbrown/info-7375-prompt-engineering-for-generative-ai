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

**Run:** 2026-11-25, after the freeze (`9cde2b9`) and after the seal of Aditya's directly edited H2 sheet (`94c0c89`). Command: `.venv/bin/python -m js3.experiment --labels labels/heldout2_labels.csv --out experiments/RESULTS_H2.json`. The table below is generated from that file.

**H2 labels (Aditya):** 1 yes, 21 no, 2 unsure. So 22 rows are decided, and the "yes" denominator is **1**.

| Change (one object vs baseline) | Object | TP / FP / FN / TN | Recall | Precision | Agreement | Flips (H2 sheet id: Aditya's label, before → after) |
|---|---|---|---|---|---|---|
| baseline v1.0, threshold 6 | — | 0 / 0 / 1 / 21 | 0/1 | 0/0 | 21/22 | — |
| C-a | filter file | 0 / 0 / 1 / 21 | 0/1 | 0/0 | 21/22 | none |
| C-b | filter file | 0 / 1 / 1 / 20 | 0/1 | 0/1 | 20/22 | H09 (no): reject → keep, `R 2 + S 0 + T 4 + E 0 + Y -1 = 5` → `R 2 + S 0 + T 4 + E 0 + Y 0 = 6` |
| C-e | filter file | 0 / 0 / 1 / 21 | 0/1 | 0/0 | 21/22 | none |
| C-t | setting: threshold 6 -> 5 | 0 / 2 / 1 / 19 | 0/1 | 0/2 | 19/22 | H09 (no): reject → keep, `R 2 + S 0 + T 4 + E 0 + Y -1 = 5` → `R 2 + S 0 + T 4 + E 0 + Y -1 = 5`; H16 (no): reject → keep, `R 2 + S 0 + T 3 + E 0 + Y 0 = 5` → `R 2 + S 0 + T 3 + E 0 + Y 0 = 5` |
| v1.1 (combination) | three filter-file changes | 0 / 0 / 1 / 21 | 0/1 | 0/0 | 21/22 | none |
| Claude arm A | context: persona + posting | 0 / 0 / 1 / 21 | 0/1 | 0/0 | 21/22 | invalid 0 |
| Claude arm B | context: persona + posting + `<filter_rules>` | 1 / 0 / 0 / 21 | 1/1 | 1/1 | 22/22 | invalid 0 |

Claude context flips, A → B: H10 (yes) reject → keep; H17 (unsure) reject → keep.

**What this shows, and what it cannot:**
- **v1.1 changed nothing on H2 (0 flips).** H2 neither confirms nor refutes the dev gain (recall 9/9 against 6/9). No H2 posting sits where v1.1's changes act, apart from H09 below. **This is a null result, not a confirmation.**
- **C-b alone (the years change) made one false keep, H09.** "Software Engineer - Backend" (Databricks), labeled `no`, reached 6 only because the boilerplate false friend supplied T4 + T7. In v1.1, C-a removes those points, so the combination rejects it. **On held-out, the single change and the combination behave differently**: one-at-a-time effects do not simply add up.
- **C-t (threshold 5) made two false keeps** (H09, H16). That agrees with the dev result, where C-t was rejected for 2 false keeps.
- **Every filter version missed the only yes, H10.**
  - **The posting:** "AI Automation Engineer" (Databricks, Costa Rica). Aditya: "Building and evaluating agents is exactly what she did …".
  - **Why it was missed:** the title does not contain the contiguous phrase `ai engineer`, so R = 0. v1.0's deliberate cap ("no keep without a role phrase") makes a keep impossible. Its "[3yrs]" also escapes the years regex.
  - **Claude arm B** (with the filter rules in context) said **yes** to H10. Arm A, without them, said no, citing Costa Rica and the 3 years.
  - B also turned H17 (`unsure`) into a yes, so B's yes is not free.
- **Size:** each difference here is one or two postings out of 22. None is statistically distinguishable, and none is a population rate. H2 is stratified (A3) and has no v1.0 keep.
- **Candidate for a later version, not adopted:** a role rule that tolerates one inserted word ("AI *Automation* Engineer"), and a years regex that reads "3yrs". Adopting either now would be fitting to H2, which would stop being held-out.

## 4. Persistence is not proof of training

If the agent "remembers" something across sessions, look for a **file, a prompt or a setting**, not training:
- **The tool server** gives the same score for a posting in every Claude session. It recomputes the score each time from the same `raw/` captures and the same `filters/*.json`.
- **v1.1 behaves differently from v1.0 in every later session.** That is because a file changed (`filters/v1.1.json`, diffable in git). No model changed.
- **The Claude calls** were fresh sessions with `--no-session-persistence`, an empty working directory, and no settings, memory or CLAUDE.md. Arm B differs from arm A only by the `<filter_rules>` text in its context. If B keeps differing across sessions, that is the same context being re-sent, not learning.
- **The reverse also holds.** A Claude Code setup with a CLAUDE.md, memory files or project instructions would make behavior persist across sessions, and that persistence would still be context, not weights.
- **What was not done:** no fine-tuning, no gradient update and no training data. Claude's weights are identical across all of these runs. Only Anthropic could change them, and nothing here can show that it did or didn't.
