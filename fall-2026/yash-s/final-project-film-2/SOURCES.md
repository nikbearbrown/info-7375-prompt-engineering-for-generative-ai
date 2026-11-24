# SOURCES — Final Project Film

## What I used

| Source | Version or date | Licence or terms | How I used it |
|---|---|---|---|
| LinkedIn job search | 2026-11-23 | LinkedIn terms | Searched "Machine Learning Engineer Databricks", US; three screenshots in `evidence/` |
| Jobright.ai | 2026-11-23, free plan | Jobright terms | Uploaded Priya Nair's fictional JSON résumé (`../js2-loop-tools-diff/persona/priya-nair.resume.example.json`); five screenshots in `evidence/` |
| Claude (Sonnet 5.5, Claude app) | 2026-11-23 | Anthropic terms | One prompt asking for early-career Databricks jobs for the fictional candidate; two screenshots in `evidence/` |
| Priya Nair, fictional persona | as copied in JS1 (sha256 `a4fdbc96…`) | from The Reallocation Engine (`search/examples/`, `resumes/`) | The candidate in every test; no real résumé used |
| My JS1, JS2 and JS3 work | JS1 2026-10-28 to 10-31; JS2 2026-11-09 to 11-10; JS3 from 2026-11-18 | my own work | Facts, numbers and the terminal output in the film (each claim's source is in `youtube/job-search-agent/FACTCHECK.md`) |
| Course assignment briefs | `assignments/` in this repository | course materials | JS4, JS5 and final-project requirements for the plan and the evaluation |
| My October pitch | `../final-project-film/` | my own work | What I changed and why; its drawing kit (the top of `scenes.py`) is reused |
| Brutalist toolkit (`brutalist.art`) | local checkout | toolkit terms | `art run` / `art final`, the quality gates, the hesitant-writer opening |
| Kokoro (`kokoro-onnx`), voice `am_onyx` | local, free | Kokoro licence | The synthetic narration voice reading my script |
| Manim Community, ffmpeg | local | MIT / LGPL | Drawing and rendering each beat; audio padding |

Screenshots of third-party sites are used for comparison and comment. LinkedIn, Jobright,
Databricks, Anthropic and OpenAI names and marks belong to their owners.

## What I did myself

- Chose to change the final project from the docs Q&A tool to the job-search agent, and why.
- Wrote my predictions before comparing any tool (`FRICTIONAL.md`, 2026-11-23).
- Ran the three comparisons myself, took the screenshots, and wrote the observations in
  `FRICTIONAL.md`.
- Chose to build the film with the Brutalist pipeline, as in my earlier films, and approved the
  script. The narration is my first-person script, read by the synthetic Kokoro voice.

## What Claude contributed

Claude Code (Claude Opus 5.5), in this session, on 2026-11-23:

- Checked each of my FRICTIONAL observations against the screenshots and the résumé files, and
  pointed out two things to check: Priya's separate CV lists PyTorch (the JSON résumé I uploaded
  does not), and one LinkedIn screenshot showed my profile photo.
- Ran the JS1, JS2 and JS3 test suites and the JS2 demonstration commands to confirm what the film
  can claim. Nothing was committed, and no committed file changed.
- Drafted `SCRIPT.md`, this file and `README.md` from my notes and the repository evidence, for my
  review and rewriting.
- Built the film: wrote `make_sheet.py` (the beat sheet) and the film's scenes in `scenes.py`
  (reusing my pitch's drawing kit), recorded the terminal output, generated the Kokoro voice,
  rendered it with `art run` / `art final`, fixed what the gates flagged, and wrote `FACTCHECK.md`,
  `SHOTLIST.md` and `PROMPTS.md`.
- Blurred my profile photo in the LinkedIn screenshot at my request, and moved the original out
  of the repository.

I review and own every claim in the film.
