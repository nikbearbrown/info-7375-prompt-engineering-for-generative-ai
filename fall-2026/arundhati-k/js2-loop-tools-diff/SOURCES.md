# Sources

## Claude Code (Opus 5.5, Claude Code desktop app, session of 2026-11-09/10)

| part | what Claude Code contributed | what I did |
|---|---|---|
| GATE.md | drafted all of it on 2026-11-10 at my request, after explaining what each section means | read it, accepted it without edits ("Reviewed, commit it"); see GATE.md header |
| BOUNDARY-PREDICTIONS.md | listed the 16 request inputs; asked each as an Allow/Refuse/Hold question | picked all 16 predictions (2 differed from GATE) |
| tests, `jsagent2/`, `run.py`, `check.py`, `demo_wrong_answer.py` | wrote all code and tests | ran the full suite (43 OK), `review/reproduce_defect.py` and `git diff` myself (`review/02-my-commands.txt`) |
| live run `live-1`, demo run | ran them | ran the approved live run myself and saw its report in my terminal (`402ac73`); Claude ran `live-1` and the demo |
| review packet | found the Ashby defect (from Lectern ATS.md), ran the curl check, wrote reproduction, test, patch, sections 1–4 | sections 5–7: ran the commands, decision |
| README, SOURCES skeleton | wrote | checked |

## Data and references

- Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/{board}/jobs` (public, GET). Boards: stripe, figma.
- Ashby Posting API, `https://api.ashbyhq.com/posting-api/job-board/{board}` (public, GET). Boards: notion; Jasper AI (review only).
- Instructor's Lectern collector: `fall-2026/nik-bear-brown/lectern/sources.json` (board slugs, 1 call per board),
  `lectern/ATS.md` (Ashby names may contain spaces; "Jasper AI"). Read only; no code copied.
- My JS1 agent: `../js1-contract-and-watch/` (allow-list idea, board-name rule, persona).
- Course brief: `assignments/assignment-js2-the-loop-the-tools-and-the-diff.md`.

## My own look-up

*My words:* I opened the Jasper AI Ashby API in my browser on November 10, 2026. It returned JSON with 3 jobs:
Enterprise Account Manager, Senior Director, Product Marketing, and Senior Product Designer.

*Note added by Claude Code, 2026-11-10:* the same URL returned **7** jobs to Claude Code's curl at ~16:37 and
16:53 EST. Its first three titles are the three above; the others are Director, Strategic Finance; Senior
Accountant; Senior Manager, Customer & Experiential Marketing; Strategic AI Outcomes Manager. The difference is
unresolved: the browser may have shown only the top of the JSON, or the board may have changed in between.
