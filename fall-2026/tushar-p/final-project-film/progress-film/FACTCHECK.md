# FACTCHECK — agent-proving-ground-progress

Status: checked by Claude Code on 2026-11-23 against captures taken the same day (read-only) from `~/Documents/agent-proving-ground` at HEAD `f40f3a1`; author review pending (Tushar).

Tense: past tense only for what ran through M5 (B06–B12); B13's next steps use "will"/"I'll". Every number in the narration is checked in NUMBER-CHECK.md (18 rows, all match).

## Claims

| # | Beat | Claim (as spoken / shown) | Verdict | Source / derivation | Fix |
|---|---|---|---|---|---|
| C1 | B04 | "E2B provides sandboxes for running AI-generated code." | CORRECTED | October PROJECT-BRIEF.md §2, word for word | Beat plan said "E2B and Runtime give agents sandboxes"; Runtime is not in the brief (Tushar chose "brief only", 2026-11-23) |
| C2 | B04 | "Langfuse records LLM traces and scores." | CORRECTED | October PROJECT-BRIEF.md §2, word for word | Beat plan said "Langfuse and Raindrop trace and evaluate model calls"; Raindrop is not in the brief |
| C3 | B04 | oh-my-pi | CORRECTED | not in the October brief; October SOURCES.md calls it "an open-source coding agent", not a harness | sentence removed (Tushar's choice) |
| C4 | B04 | A Drupal project, AI Proving Ground, grades what an agent actually saved instead of what it reports, only for Drupal sites | EXEMPT | Tushar's own line (new in this film); source https://www.drupal.org/project/ai_proving_ground, listed in SOURCES.md. Not fetched in this build (no network beyond pip) | author to confirm wording against the page |
| C5 | B06 | built in Go | PASS | APG go.mod (`go 1.27.3`) | — |
| C6 | B06 | agent is Claude Haiku; three tools: read a file, write a file, run a command | PASS | traces: `model claude-haiku-5-5`; internal/loop/loop.go defines read_file, write_file, run_command | — |
| C7 | B06 | Kubernetes pod with no network | PASS | evidence/B9.txt: TestKindEgressBlocked, tcp and DNS blocked with the policy on | — |
| C8 | B06 | hidden check the agent never sees, after every change | PASS | tasks/README.md: check.sh "the hidden check"; repo/ is the only part the agent sees; trace-schema check_runs (mid-run check on a /workspace change) | — |
| C9 | B06 | real run on task one passed in three steps | PASS | evidence/B6.txt: PLAN.md:120 `001  PASS  steps=3`; trace 20261112T053055Z-92239eb0 has 3 steps | — |
| C10 | B07 | a denied call never runs; it's recorded | PASS | evidence/B7.txt: run 20261118T034327Z-b54f5cd6 step 4 DENIED (rule: path), "/workspace changed: no" | — |
| C11 | B07 | approval bound to the exact bytes; void if the diff changes | PASS | evidence/B7.txt: gate diff_sha256 = recheck_sha256; trace-schema.md:193 "or the approval is void"; trace-schema.md:47 human-answered by Tushar | — |
| C12 | B08 | 16 tasks, 11 normal, 5 failure; split frozen before tuning | PASS | evidence/B8.txt; NUMBER-CHECK N4–N7 | — |
| C13 | B09 | no network, not root, capped CPU, memory, processes, disk; every limit held | PASS | evidence/B9.txt: all isolation tests PASS (2026-11-17T23:44Z) | — |
| C14 | B09 | spend-limited API key; Claude Code wrote the code while Tushar reviewed every change | PASS | APG docs/01-brief.md:27; APG SOURCES.md:38 "with Tushar reviewing each diff before commit" | — |
| C15 | B10 | two system prompts: the original and a longer one Tushar wrote; predictions committed before held-out runs | PASS | evidence/B10.txt: A 623 bytes, B 2,695 bytes (D30: Tushar's text); 6d7bafe Nov 17 22:40 ET, first held-out eval Nov 17 22:41 ET | — |
| C16 | B11 | 70 held-out runs; 20/20 and 15/15 for both; about 41% more cost | PASS | evidence/B11.txt; NUMBER-CHECK N8–N11 (cost ratio 1.409, estimated from list prices) | — |
| C17 | B12 | all 40 passing fixes read; no test edits; 7 of 10 on one task missed documented behaviour; executed check ['X', 'x'] | PASS | evidence/B12.txt; NUMBER-CHECK N12–N14 | — |
| C18 | B13 | next: controlled failure, stranger run, submit Dec 18; code public at github.com/tushar-patel28/agent-proving-ground | PASS | evidence/B13.txt: docs/01-brief.md:40–41, PLAN.md:6, git remote. Public visibility not re-checked online in this build | — |

## Honesty rules this film follows

- CONSTRUCTED beats (B01–B05, B13) show "Constructed" in the top rail for the whole beat.
- REAL beats (B06–B12) show text copied from evidence/<beat>.txt in terminal-style frames whose title bars give the source path and the source's own date; the rail shows "Real output". Lines too long are cut with "…"; nothing is reworded. Annotations added for the viewer (for example "(result line recorded in PLAN.md)", "(computed: b / a = 1.409)") are in grey.
- No Claude responses, no product logos, no people, no channel styling.
