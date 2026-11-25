# Results, fresh set for FILTER.md v1.1, filter run 2026-11-22T084738Z

Computed by `tools/score_fresh.py` from Aravind's verdicts in VERDICTS.md (last committed in `1bbbcf6`, before the answers were opened) and `sealed/answers.json` (SHA-256 `1be18c40d3ff408c7f79e2089f3153d69833030114069090c66596b42808f27e`, the hash README.md published before any verdict). Claude Code wrote the kit, the script and this file; the verdicts are his. What each outcome means was fixed in PREDICTIONS.md before any verdict.

## In short

- **A, the cutoff of 50:** Keep 10, Reject 2, ? 0 of 12. v1.1's recommendation agrees with him on 10 of the 12 he judged, v1.0's on 2. Prediction (Keep on at least 9): **held**.
- **B, the export-control penalty:** Keep 0, Reject 0, ? 3 of 3. Prediction (? on at least 2): **held**.
- **Controls (C and D):** 0 of 5 off the expected verdict. Prediction (none off): **held**.
- **All 20 cards:** 17 judged; agreement with v1.0's recommendation 7, with v1.1's 15, with v1.1's without the penalty 15; with the filter's keep or reject (the same in both versions) 15.

On A, v1.1 disagrees with him on 2 of 12 judged cards; the exact one-sided 95% upper bound (Clopper-Pearson) is 43.8%. It bounds what this draw supports for that stratum of one day's saved answers, not a rate for all postings.

## By stratum

Agreement counts are over the cards he judged Keep or Reject (a ? is counted on its own).

| Stratum | Cards | Keep | Reject | ? | Judged | v1.0 agrees | v1.1 agrees | v1.1 without the penalty agrees | Keep or reject agrees |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A: v1.1 adds | 12 | 10 | 2 | 0 | 12 | 2 | 10 | 10 | 10 |
| B: the penalty holds back | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |
| C: both recommend | 3 | 3 | 0 | 0 | 3 | 3 | 3 | 3 | 3 |
| D: both reject | 2 | 0 | 2 | 0 | 2 | 2 | 2 | 2 | 2 |
| **all** | 20 | 13 | 4 | 3 | 17 | 7 | 15 | 15 | 15 |

## Every card

Score and whether it is recommended: v1.0 (cutoff 60), v1.1 (cutoff 50), and v1.1 without the export-control penalty.

| Card | Title | Stratum | His verdict | His note | v1.0 | v1.1 | Without the penalty |
|---|---|---|---|---|---|---|---|
| 01 | Senior-Staff Software Engineer, Tooling | D | Reject | Senior-staff level is too advanced for Jane. | rejected | rejected | rejected |
| 02 | Software Engineer, Plugin Developer Platform | C | Keep | Software engineering role focused on APIs, SDKs, and developer platforms. | 60, yes | 60, yes | 60, yes |
| 03 | Software Engineer - Frontend Developer Productivity | A | Reject | Frontend-focused role, outside Jane’s main interests. | 55, no | 50, yes | 50, yes |
| 04 | HR Business Partner, GTM | D | Reject | HR business partner role, not software engineering. | rejected | rejected | rejected |
| 05 | Control Systems Software Engineer, Robotics | A | Reject | Specialized robotics and control systems role requiring hardware-focused experience. | 50, no | 50, yes | 50, yes |
| 06 | Software Engineer - Data Platform | A | Keep | Data platform engineering role with relevant experience requirements and visa sponsorship. | 50, no | 50, yes | 50, yes |
| 07 | Software Engineer, Resilience Engineering | A | Keep | Software engineering role focused on resilience and reliability. | 50, no | 50, yes | 50, yes |
| 08 | Software Engineer, AI for Chip Design | B | ? | Relevant software engineering role, but export-control eligibility is unclear. | 50, no | 40, no | 50, yes |
| 09 | Software Engineer, Applied Emerging Talent (2027) | A | Keep | Early-career software engineering opportunity for 2027. | 50, no | 50, yes | 50, yes |
| 10 | Software Engineer, Backend — Dots | C | Keep | Direct backend engineering role involving APIs and product systems. | 60, yes | 60, yes | 60, yes |
| 11 | Software Engineer, Kernel Performance & AI Tooling | B | ? | Relevant engineering area, but export-control eligibility is unclear. | 50, no | 40, no | 50, yes |
| 12 | Full Stack Software Engineer, Growth | A | Keep | Full-stack software engineering role on the ChatGPT team. | 50, no | 50, yes | 50, yes |
| 13 | Software Engineer, Observability | A | Keep | Software engineering role involving production distributed systems. | 55, no | 55, yes | 55, yes |
| 14 | Software Engineer - Data Aquisition (systems) | A | Keep | Systems and infrastructure engineering role involving Kubernetes. | 55, no | 55, yes | 55, yes |
| 15 | Software Engineer, Accelerators | B | ? | Relevant AI infrastructure role, but export-control eligibility is unclear. | 50, no | 40, no | 50, yes |
| 16 | Software Engineer, Research - Human Data | A | Keep | Software engineering role building backend services and tools for data workflows. | 55, no | 55, yes | 55, yes |
| 17 | Machine Learning Engineer, Implicit Signals | A | Keep | Machine learning engineering role with production engineering responsibilities. | 50, no | 50, yes | 50, yes |
| 18 | Software Engineer, Core Network Engineering | A | Keep | Software engineering role focused on networking and distributed infrastructure. | 55, no | 55, yes | 55, yes |
| 19 | Software Engineer, Fleet Management | A | Keep | Software engineering role supporting large-scale computing infrastructure. | 55, no | 50, yes | 50, yes |
| 20 | Software Engineer, Codex Enterprise | C | Keep | Backend engineering role supporting Codex across developer platforms. | 60, yes | 60, yes | 60, yes |
