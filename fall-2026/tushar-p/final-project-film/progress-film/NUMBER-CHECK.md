# NUMBER-CHECK — progress film narration vs. captured evidence

Checked by Claude Code on 2026-11-23, before any audio or render, against the captures in `evidence/` (taken the same day, read-only, from `~/Documents/agent-proving-ground` at HEAD `f40f3a1`, clean tree).

**Result: every number in the narration matches its source. Nothing was changed.**

| # | Beat | Narration says | Source (capture → repo file) | Source value | Match |
|---|---|---|---|---|---|
| N1 | B6 | "three tools: read a file, write a file, run a command" | `internal/loop/loop.go` tool definitions (lines ~385–404); see also `evidence/B6.txt` steps | `read_file`, `write_file`, `run_command`: 3 tools | yes |
| N2 | B6 | "a real run on task one" | `evidence/B6.txt` → PLAN.md:120, trace header | `task 001-fix-function` | yes |
| N3 | B6 | "it passed in three steps" | `evidence/B6.txt` → PLAN.md:120 `001  PASS  steps=3  reason=check_passed`; trace JSON `steps` length | 3 steps, PASS, `check_passed` | yes |
| N4 | B8 | "sixteen small Python tasks" | `evidence/B8.txt` → `ls tasks/0*/`, tasks/README.md | 16 task directories (001–016) | yes |
| N5 | B8 | "Eleven are normal bugs" | `evidence/B8.txt` → tasks/README.md "Normal tasks (expected: PASS)" | 001–011: 11 | yes |
| N6 | B8 | "Five are built to make the system say no" | `evidence/B8.txt` → tasks/README.md "Deliberate failure cases (expected: FAIL)" | 012–016: 5 | yes |
| N7 | B8 | "froze that split before tuning anything" | `evidence/B8.txt` → `git show --stat 26b5305` (Nov 13 2026, 19:36 −0500); first contract-B text is Nov 17 (`052b62b`) | split committed before contracts/held-out runs | yes |
| N8 | B11 | "Seventy held-out runs" | `evidence/B11.txt` → compare "all tasks" runs a 35 + b 35 | 70 | yes |
| N9 | B11 | "Both prompts passed all twenty normal runs" | `evidence/B11.txt` → "normal tasks" passed a 20/20, b 20/20 | 20/20 each | yes |
| N10 | B11 | "both said no on all fifteen failure runs" | `evidence/B11.txt` → "failure tasks" returned FAIL a 15/15, b 15/15; UNEXPECTED PASS 0 | 15/15 each | yes |
| N11 | B11 | "cost about forty-one percent more" | `evidence/B11.txt` → all-tasks total cost (estimated) a $0.04711, b $0.06637 | 0.06637 / 0.04711 = 1.4088 → +40.9% | yes (rounds to 41%) |
| N12 | B12 | "I read all forty passing fixes myself" | `evidence/B12.txt` → docs/07-evidence.md:415 "I have reviewed all 40 normal-task PASS diffs" | 40 | yes |
| N13 | B12 | "on one task, seven of ten fixes missed behavior" | `evidence/B12.txt` → FAILURES.md F2: "7 of 10 keep existing mixed-case tags in their original case" (011) | 7 of 10, task 011 | yes |
| N14 | B12 | executed check output `['X', 'x']` (on screen) | `evidence/B12.txt` → FAILURES.md F2 "printed `['X', 'x']`" | `['X', 'x']` | yes |
| N15 | B13 | "M0–M5" ticked (on screen) | `evidence/B13.txt` → PLAN.md milestone table M0 (Nov 3) … M5 (Nov 18) | all six logged | yes |
| N16 | B13 | "submit Dec 18" (on screen) | `evidence/B13.txt` → PLAN.md:6 "Target submit: Fri Dec 18" | Dec 18 | yes |
| N17 | B7 | denied call from a contract B 008 held-out trace | `evidence/B7.txt` → eval-log rows; `apg show` step 4 | run `20261118T034327Z-b54f5cd6`, step 4, `write_file /tmp/unused.txt`, DENIED (rule: path); 4 of 5 B runs on 008 had 1 denied call each | yes |
| N18 | B7 | approval bound to exact bytes | `evidence/B7.txt` → gate `diff_sha256` = `recheck_sha256` = `cbdbe61d…`, 193 bytes; trace-schema.md:193 "or the approval is void" | equal hashes | yes |

## Dates shown on screen (not spoken)

The beat plan's dates are Eastern; some sources record UTC. The film shows the source's own timestamp, plus the Eastern date where they differ.

| Beat | Beat plan | Source timestamp | Eastern |
|---|---|---|---|
| B6 | Nov 12 | 2026-11-12T05:30:55Z | Nov 12, 00:30 |
| B7 denied call | Nov 17 | 2026-11-18T03:43:27Z | Nov 17, 22:43 |
| B7 approval | Nov 13 | 2026-11-13T22:47:40Z | Nov 13, 17:47 |
| B8 split | — | Nov 13 2026 19:36 −0500 | Nov 13 |
| B9 | Nov 17 | 2026-11-17T23:44:08Z | Nov 17, 18:44 |
| B10 | — | Nov 17 2026 22:40 −0500 (commit 6d7bafe); first held-out eval 2026-11-18T03:41Z = Nov 17, 22:41 ET | Nov 17 |
| B11 | Nov 18 | "Ran: Nov 18, 2026" | Nov 18 |
| B12 | Nov 18 | FAILURES.md "Date: Nov 18, 2026" | Nov 18 |
