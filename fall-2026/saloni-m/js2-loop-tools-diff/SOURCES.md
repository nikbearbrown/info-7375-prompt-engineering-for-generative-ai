# SOURCES — Job-Search Agent 2

## What I started from

- **My Job-Search Agent 1** (`../js1-contract-and-watch/`, commits `JS1-1`…`JS1-9`). I re-used the
  ideas, not the files: an https + exact-host allow-list (`agent/watch.py::check_allowed`), a first
  run that is a baseline, and the bare-id state shape. That state shape is the defect in the review
  packet.
- **Lectern** (instructor's collector, `fall-2026/nik-bear-brown/lectern/sources.json`), read on
  2026-11-10 for its Greenhouse and Ashby API URL patterns and board slugs. I chose
  `anthropic`, `figma` and `openai` from it. No Lectern code was copied.
- **Classmates' posted JS2 folders**: on 2026-11-10 Claude Code listed their file names, test
  counts, commit counts and job systems, so I could see how the class organised the work. It did
  not read or copy their code, GATE files or decisions. Nothing in this folder comes from them.

## Public endpoints (no login, GET only)

- Greenhouse Job Board API: `https://boards-api.greenhouse.io/v1/boards/{board}/jobs`
- Ashby public posting API: `https://api.ashbyhq.com/posting-api/job-board/{board}`

Both are documented public job-board feeds. The agent makes one GET per board per run (four per
run, ten at most), identifies itself in the User-Agent, and never applies, posts or logs in.
I did not read each company's site terms beyond the APIs being published for job boards; that is
listed under "Not checked".

## What Claude Code contributed (Claude Code desktop app, Claude Opus 5.5, 2026-11-10)

| Part | Claude Code | Me (Saloni) |
|---|---|---|
| GATE.md | wrote example options for each heading; wrote §8 (implementation details) | chose `1A fail=a, 2A, 3A, 4A, 5B`; wrote the wording of the three wrong versions (§6) and the failure sentence (§7). The ideas for §6 came from Claude's example list (a, b, g); §7 filled in Claude's template |
| Code: `jsagent/`, `scripts/`, `tests/` | wrote all of it and ran the first runs | — |
| Boundary cases | wrote the 21 cases and tests | wrote my prediction for every case before the run (`39dea2de`) |
| Review packet | wrote the test before the patch, both patches, the diffs; compared run-1/run-2 raw and found the hidden Korea job | ran the review commands myself (`review/04-07`, `11-14`); decided REVISE on v1 and ACCEPT on v2 (on two conditions, both met); named the case my tests miss |
| README, TRACE, FINISHED-WRONG, REVIEW-PACKET, this file | drafted from the runs and commits | read and corrected them |
| FRICTIONAL.md | the commit/evidence timeline table only | my own dated entries |
| Sign-off | drafted Checked / Not checked from tests and runs | read, edited and signed (or withheld) |

No Claude output is shown as a run result. The agent does not call Claude. Every number in the
README comes from a file in `out/` or `review/`.
