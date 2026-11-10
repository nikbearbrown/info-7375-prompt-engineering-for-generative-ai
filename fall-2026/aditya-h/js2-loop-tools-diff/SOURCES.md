# SOURCES — what I used, what I wrote, what Claude contributed

## External sources and data

| Source | Used for | When |
|---|---|---|
| Greenhouse Job Board API `boards-api.greenhouse.io/v1/boards/<slug>/jobs` (public) | stripe, anthropic, ramp (stale), stripe-js2-bad (deliberate 404) | live runs 2026-11-09, 2026-11-10 |
| Ashby posting API `api.ashbyhq.com/posting-api/job-board/<slug>` (public) | openai, notion; ramp as the check's cross-check source | same |
| Lever postings API `api.lever.co/v0/postings/<slug>?mode=json` (public) | palantir | same |
| My JS1 (`../js1-contract-and-watch/`) | the rule `title-us-v1`, the persona guard, the system-CA TLS fallback, the persona file | — |
| `fall-2026/nik-bear-brown/lectern/ATS.md` (instructor) | **reference only:** the Ashby endpoint, and the lesson that a wrong slug can return a valid empty board. No code copied. | read 2026-11-09 |
| `nikbearbrown/the-reallocation-engine` `search/examples/maya-sehgal/resume.example.json` | the fictional persona (via JS1) | — |
| JS2 assignment brief (Canvas, and the repo copy `assignments/assignment-js2-…md`) | requirements | 2026-11-09 |
| Python 3.13 standard library | everything | — |

I did not open or use any other student's folder. Three commits by another student (`anisha-g`) were on `main` when I pulled; I checked only their file paths, to confirm they don't touch my folder.

## Who did what

The build took one Claude Code session (Claude Opus 5.5), on 2026-11-09 and 11-10. Commits marked `Co-Authored-By: Claude` were made by Claude Code.

| Part | Aditya | Claude Code |
|---|---|---|
| **GATE.md** | Chose: the board set (5 + 2 demo), the budgets (10 / 15 / 120 s), retrying transient errors once, the same-URL repeat rule, the approved write (board reset), the 3 wrong versions. Approved it. | Probed 12+ endpoints (found the Ramp stale board and the 404). Drafted the text and the 19 predicted boundary cases. |
| Code (`jobwatch2/`, `check_run.py`) | — | Wrote all of it. |
| Tests (gate round) | Ran them in the review steps. | Wrote them from the gate and committed them before the code. Wrote `wrong_versions.py`. |
| Live runs | — | Ran all three, plus the check. |
| **Review packet** | **Decided the expected behavior** ("refuse and stop"). Created and ran both test files and watched them fail. Read both diffs. Ran the suite and the harness. **Decided REVISE on v1** after weighing the named gap. **Decided ACCEPT on v2.** | Found the defect, wrote the repro, drafted the test text, wrote patches v1 and v2, named the cases still missed. |
| Write-ups | Reviews them, writes FRICTIONAL Part 2, signs or withholds the sign-off. | Drafted all of them. |

## Accepted, changed, rejected

- **Accepted:** the gate drafts (with my answers), the implementation, and review patch v2.
- **Changed:** review patch v1. I chose to revise it rather than accept it with a known gap.
- **Rejected:** nothing outright. Claude Code's own record of overwriting saved check output (FRICTIONAL #6) led to restoring the committed evidence, not to keeping the new output.
