# Sources

## Claude Code (Opus 5.5, Claude Code desktop app, session of 2026-11-09/10)

| part | what Claude Code contributed | what I did |
|---|---|---|
| GATE.md | drafted all of it on 2026-11-10 at my request, after explaining what each section means | read it, accepted it without edits ("Reviewed, commit it"); see GATE.md header |
| BOUNDARY-PREDICTIONS.md | listed the 16 request inputs; asked each as an Allow/Refuse/Hold question | picked all 16 predictions (2 differed from GATE) |
| tests, `jsagent2/`, `run.py`, `check.py`, `demo_wrong_answer.py` | wrote all code and tests | <!-- what did you read / run / check? --> |
| live run `live-1`, demo run | ran them | <!-- did you open the report? --> |
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

<!-- Do at least one yourself: open one board URL in your browser (e.g. the Jasper AI one) and write
     what you saw and when. -->
