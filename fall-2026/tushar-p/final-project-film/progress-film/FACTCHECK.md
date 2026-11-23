# FACTCHECK — agent-proving-ground-progress (v2)

Status: checked by Claude Code on 2026-11-23 against captures taken the same day (read-only) from `~/Documents/agent-proving-ground` at HEAD `f40f3a1`, and against the October PROJECT-BRIEF.md. Author review pending (Tushar).

Narration: v2 BEAT-PLAN.md (Tushar, Nov 23, 2026), word for word. Tense: past or present perfect for what ran through M5; "will"/"I'll" for what's left (B12). Every number in the narration is checked in NUMBER-CHECK.md (26 rows, all match).

## Claims

| # | Beat | Claim (as spoken / shown) | Verdict | Source / derivation | Fix |
|---|---|---|---|---|---|
| C1 | B01 | final project for INFO 7375 | PASS | the course; October PROJECT-BRIEF.md header | — |
| C2 | B02 | an agent can fix the bug, edit the test so it passes, or give up, and its message can look the same | EXEMPT | general framing, drawn as a constructed illustration; task 012-wrong-test exists because a test edit is the tempting wrong fix (evidence/B8.txt:36) | — |
| C3 | B03 | a command-line tool with its code in a public GitHub repo | PASS | `apg` CLI (`go run ./cmd/apg`); evidence/B13.txt `git remote` → github.com/tushar-patel28/agent-proving-ground. Public visibility not re-checked online in this build | — |
| C4 | B03 | runs an agent in a locked sandbox, records every step, decides pass/fail by its own tests | PASS | evidence/B6.txt (trace steps, `check_passed`); evidence/B9.txt (isolation) | — |
| C5 | B04 | first minute: one command, one result line, open the trace | PASS | October PROJECT-BRIEF.md:14 ("first sixty seconds", "run one command"); evidence/B6.txt (one result line). Shown as a mock-up labelled "constructed" | — |
| C6 | B05 | "E2B provides sandboxes for running AI-generated code. Langfuse records LLM traces and scores." | PASS | October PROJECT-BRIEF.md §2, word for word | — |
| C7 | B05 | a sandbox doesn't tell you whether the work is right; a trace doesn't stop an agent doing what it shouldn't | EXEMPT | Tushar's own characterisation of the gap; not checked against either product's current documentation (no network in this build) | — |
| C8 | B06 | one loop on a laptop: sandbox, trace, independent check, human approval | PASS | evidence/B7.txt (gate), B9.txt (sandbox), B6.txt (trace, check) | — |
| C9 | B06 | Go and Kubernetes were both new to Tushar | PASS | October PROJECT-BRIEF.md:38 "Skills that are new to me: Go, Kubernetes, …" | — |
| C10 | B07 | Kubernetes pod, no network, not root | PASS | evidence/B9.txt lines 105–106 (blocked), 12 (`uid=1000(apg)`), 16 (`setuid(0) errno 1`) | — |
| C11 | B07 | Claude Haiku with three tools | PASS | evidence/B6.txt `model claude-haiku-5-5`; internal/loop/loop.go | — |
| C12 | B07 | every tool call passes a permission policy written in code first | PASS | evidence/B7.txt step 4 `DENIED (rule: path)`, `/workspace changed: no` | — |
| C13 | B07 | hidden check after every change; pass/fail only from that check | PASS | tasks/README.md (check.sh "the hidden check"); trace `exit_reason check_passed` (evidence/B6.txt) | — |
| C14 | B07 | approval bound to the exact bytes seen | PASS | evidence/B7.txt gate `diff_sha256` = `recheck_sha256`; trace-schema.md:193 "or the approval is void" | — |
| C15 | B08 | 16 tasks, 11 ordinary bugs, 5 where the right answer is no; split frozen before tuning | PASS | evidence/B8.txt; NUMBER-CHECK N7–N11 | — |
| C16 | B08 | Docker and kind, a spend-limited key; Claude Code writes the code while Tushar reviews every change | PASS | evidence/B9.txt (docs/01-brief.md:27); APG SOURCES.md:38 | — |
| C17 | B09 | built and tested through M5; run 001 PASS in 3 steps; a denied call recorded, never ran; every limit held | PASS | evidence/B13.txt, B6.txt, B7.txt, B9.txt; NUMBER-CHECK N12–N15 | — |
| C18 | B10 | judged on three things; "I wrote my predictions down before the held-out runs" | CORRECTED | evidence/B10.txt: predictions committed (6d7bafe, Nov 17 22:40 ET) before the first held-out run (22:41 ET) | was "I write my predictions down before every run", broader than the captures; changed by Tushar, 2026-11-23 |
| C19 | B11 | 70 held-out runs; 20/20 and 15/15 for both; all 40 fixes read; 7 of 10 on one task missed documented behaviour | PASS | evidence/B11.txt, B12.txt; NUMBER-CHECK N18–N22. No costs shown | — |
| C20 | B12 | three things left: controlled failure (caught, recovered), stranger run, harden the check so it confirms every test actually ran; on screen "All by Dec 18" | PASS | evidence/B13.txt: docs/01-brief.md:40–41, PLAN.md:6 (Dec 18); evidence/B12-v2.txt: docs/03-action-surface-map.md:108–113 and docs/07-evidence.md:519 (Honest limits, point 4) name `os._exit(0)` as a cheat the check can't catch, so exit code 0 doesn't prove every test ran | item 3 was "the full write-up and submission, by December eighteenth" (changed by Tushar, 2026-11-23); "clean machine": confirmed: Final Project assignment, 'The stranger run' section, checked by Tushar on Nov 23, 2026 |
| C21 | B13 | code under test can fool a check; answered by diff review and documented gaps | PASS | evidence/B12.txt (review of all 40 diffs; FAILURES.md F2, a pass that missed the spec); B8.txt:36 (012 tempts a test edit) | — |
| C22 | B13 | won't be a hosted service or a model benchmark | PASS | evidence/B13.txt → APG docs/01-brief.md:47 "Not a model benchmark."; October PROJECT-BRIEF.md §5 "not … a hosted or multi-user service" | — |
| C23 | B13 | code at github.com/tushar-patel28/agent-proving-ground | PASS | evidence/B13.txt `git remote get-url origin` | — |

## Honesty rules this film follows

- CONSTRUCTED beats (all except B09 and B11) show "Constructed" in the top rail for the whole beat. B04's terminal is a mock-up and its title bar says so.
- REAL beats (B09, B11) show text copied from evidence/<beat>.txt in terminal-style frames whose title bars give the source path and the source's own date; the rail shows "Real output". Lines too long are cut with "…"; nothing is reworded. Grey annotations such as "(result line recorded in PLAN.md)" are added for the viewer.
- No costs on screen. No Claude responses, no product logos, no people, no channel styling.
