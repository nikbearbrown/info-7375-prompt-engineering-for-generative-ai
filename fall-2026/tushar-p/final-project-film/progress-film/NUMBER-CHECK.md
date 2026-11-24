# NUMBER-CHECK — progress film v2 narration vs. captured evidence

Checked by Claude Code on 2026-11-23, before any v2 audio or render. Sources are the captures in `evidence/`, taken the same day, read-only, from `~/Documents/agent-proving-ground` (HEAD `f40f3a1`, clean tree). Two rows also cite the October PROJECT-BRIEF.md (`../PROJECT-BRIEF.md`).

**Result: every number in the v2 narration matches its source, so the build did not stop.** Three wording points that are not numbers are listed under the table. B10's was fixed by Tushar on Nov 23; the B12 and B13 points now have sources. B12's third item changed on Nov 23 (N26).

## Spoken numbers

| # | Beat | Narration says | Source | Source value | Match |
|---|---|---|---|---|---|
| N1 | B01 | "INFO 7375" | the course (course repo `info-7375-…`; October PROJECT-BRIEF.md header) | INFO 7375 | yes |
| N2 | B04 | "In their first minute" | October PROJECT-BRIEF.md:14 "In the first sixty seconds they will … run one command" | 60 seconds (a design target, not a measurement) | yes |
| N3 | B04 | "run one command, read one result line" | `evidence/B6.txt` → PLAN.md:120: `apg run 001` printed one line `001  PASS  steps=3  reason=check_passed` | one command, one result line | yes |
| N4 | B07 | "a Kubernetes pod with no network" | `evidence/B9.txt` → isolation file lines 105–106: tcp and DNS "blocked" with the policy on | no network | yes |
| N5 | B07 | "not running as root" | `evidence/B9.txt` → line 12 `uid=1000(apg)`; line 16 `setuid(0) errno 1` | uid 1000, cannot become root | yes |
| N6 | B07 | "Claude Haiku, gets three tools: read a file, write a file, run a command" | `evidence/B6.txt` → `model claude-haiku-5-5`; `internal/loop/loop.go` tools `read_file`, `write_file`, `run_command` | 3 tools | yes |
| N7 | B08 | "sixteen small Python repos" | `evidence/B8.txt` → 16 task directories 001–016 | 16 | yes |
| N8 | B08 | "Eleven are ordinary bugs" | `evidence/B8.txt` → tasks/README.md "Normal tasks (expected: PASS)" 001–011 | 11 | yes |
| N9 | B08 | "Five are designed so the right answer is no" | `evidence/B8.txt` → "Deliberate failure cases (expected: FAIL)" 012–016 | 5 | yes |
| N10 | B08 | "a wrong test, a task that needs the network, a budget too small" | `evidence/B8.txt` lines 36, 37, 39: `012-wrong-test`, `013-needs-network`, `015-tiny-budget` (`max_steps` 1) | 3 of the 5, named correctly | yes |
| N11 | B08 | "froze a development and held-out split before tuning anything" | `evidence/B8.txt` → `git show --stat 26b5305` (Nov 13 2026, 19:36 −0500); dev 001–005, 009, 010, 013, 014; held-out 006–008, 011, 012, 015, 016 | frozen Nov 13, before contract B (Nov 17) | yes |
| N12 | B09 | "through milestone five" | `evidence/B13.txt` → PLAN.md:457–462, M0 (Nov 3) … M5 (Nov 18) | M0–M5 logged | yes |
| N13 | B09 | "task one passed in three steps" | `evidence/B6.txt` → `001  PASS  steps=3`; trace `steps 3 verdict PASS` | 3 steps, PASS | yes |
| N14 | B09 | "A denied tool call was recorded and never ran" | `evidence/B7.txt` → run `20261118T034327Z-b54f5cd6` step 4 `DENIED (rule: path)`, `/workspace changed: no` | 1 denied call, recorded | yes |
| N15 | B09 | "every limit held" | `evidence/B9.txt` → every test `--- PASS`, line 131 `PASS` | all limits held | yes |
| N16 | B10 | "the five no-tasks" | as N9 | 5 | yes |
| N17 | B10 | "two different system prompts" | `evidence/B10.txt` → `contracts/A-system.txt` 623 bytes, `contracts/B-system.txt` 2,695 bytes | 2 | yes |
| N18 | B11 | "seventy held-out runs" | `evidence/B11.txt` → "all tasks" runs a 35 + b 35 | 70 | yes |
| N19 | B11 | "passed all twenty normal runs" | `evidence/B11.txt` → normal tasks passed a 20/20, b 20/20 | 20/20 each | yes |
| N20 | B11 | "said no on all fifteen no-runs" | `evidence/B11.txt` → failure tasks returned FAIL a 15/15, b 15/15; UNEXPECTED PASS 0 | 15/15 each | yes |
| N21 | B11 | "I read all forty passing fixes" | `evidence/B12.txt` → docs/07-evidence.md:415 "I have reviewed all 40 normal-task PASS diffs" | 40 | yes |
| N22 | B11 | "seven of ten missed what the documentation asks for" | `evidence/B12.txt` → FAILURES.md F2 "7 of 10 keep existing mixed-case tags in their original case" (011) | 7 of 10 | yes |
| N23 | B12 | "Three things are left" | `evidence/B13.txt` → docs/01-brief.md:40 (controlled failure), :41 (stranger run); `evidence/B12-v2.txt` (harden the check, see N26) | 3 | yes |
| N24 | B12 | "All by Dec 18" (on screen since the B12 change; no longer spoken) | `evidence/B13.txt` → PLAN.md:6 "Target submit: Fri Dec 18" | Dec 18 | yes |
| N25 | B13 | "It won't be … a model benchmark" (scope, no number) | `evidence/B13.txt` → APG docs/01-brief.md:47 "Not a model benchmark." | stated in the brief | yes |
| N26 | B12 | "Third, I'll harden the check, so it confirms every test actually ran" (a gap to close, no number) | `evidence/B12-v2.txt` → docs/03-action-surface-map.md:108–113 ("a cheat in code passes like a fix: … `os._exit(0)` on import"); docs/07-evidence.md:517–519, Honest limits point 4: "exit code 0 does not by itself prove that all intended tests completed successfully" | the check cannot yet confirm every test ran | yes |

## Numbers shown on screen (not spoken)

| Beat | On screen | Source | Match |
|---|---|---|---|
| B04 | `001  PASS  steps=3  reason=check_passed` in a mock-up labelled "constructed" | `evidence/B6.txt` (the real line's format) | yes |
| B08 | tiles 001–016; 11 green, 5 red; dev 9 tiles, held-out 7 tiles | `evidence/B8.txt` lines 30–45, 67–69 | yes |
| B09 | `001  PASS  steps=3`; step 4 DENIED; isolation lines 105, 12, 71, 88, 94, 116, 131; M0–M5 | `evidence/B6.txt`, `B7.txt`, `B9.txt`, `B13.txt` | yes |
| B11 | runs 35 / 35; 20/20; 15/15; "all 40"; "7 of 10 … 3 under A and 4 under B"; `['X', 'x']`. No costs | `evidence/B11.txt`, `B12.txt` | yes |
| B12 | "All by Dec 18" (footer) | PLAN.md:6 | yes |

## Wording points (not numbers, so the build did not stop)

1. **B10, resolved Nov 23.** The first v2 wording, "I write my predictions down before every run", was broader than the captures. They show predictions committed in `6d7bafe` (Nov 17, 22:40 ET) a minute before the first held-out run (22:41 ET), covering all 70 held-out runs, but nothing before the earlier dev runs (Nov 13). Tushar changed the sentence to "…and I wrote my predictions down before the held-out runs", which matches `evidence/B10.txt`.
2. **B12, "on a clean machine":** confirmed: Final Project assignment, 'The stranger run' section, checked by Tushar on Nov 23, 2026. The APG captures say "A stranger will run `./demo.sh` from the README alone" (docs/01-brief.md:41). B12's third item changed on Nov 23 from "the full write-up and submission, by December eighteenth" to "I'll harden the check, so it confirms every test actually ran" (N26); "packet + demo" is no longer on screen.
3. **B13, "It won't be a hosted service or a model benchmark":** sourced from APG docs/01-brief.md:47, "Not a model benchmark. With 12–20 tasks and a few runs each, it will not support statistically strong claims about models in general." This line was added to `evidence/B13.txt` on Nov 23 (same read-only capture format; `capture.sh` updated). "Not a hosted service" follows the October PROJECT-BRIEF.md ("will not be a hosted or multi-user service").

## Dates shown on screen

| Beat | Frame | Source timestamp | Eastern |
|---|---|---|---|
| B09 | run 001 | 2026-11-12T05:30:55Z | Nov 12, 00:30 |
| B09 | denied call | 2026-11-18T03:43:27Z | Nov 17, 22:43 (shown as "Nov 17 ET") |
| B09 | isolation | 2026-11-17T23:44:08Z | Nov 17, 18:44 |
| B11 | compare totals | "Ran: Nov 18, 2026" | Nov 18 |
| B11 | review, F2 | docs/07-evidence.md; FAILURES.md "Date: Nov 18, 2026" | Nov 18 |
