# A Job-Search Agent You Can Check — Final Project Film

**Name:** Varnika M · INFO 7375 · Final Project Film (four-part)
**Project:** my job-search agent (JS1 and JS2 built; JS3–JS5 and the final project to come)
**Film:** `final/varnika-final-project-film.mp4` · 3:20 (199.7 s, measured from the file) · 1920×1080, 24 fps, H.264/AAC, 7.5 MB · sha256 `bc7a74d0be9da6c8d5d6259bf9b72b43f316c881556a2eac98afeb7186d46e9d`. Rendered 2026-11-23. All toolkit gates passed (F, L, A, W, B, V, T; reports in `gate-reports/`).
**Status:** watched and approved by me on 2026-11-23 (see `SOURCES.md`, section 4).

**One sentence:** an agent that reads public job boards, picks out the few postings that fit one
person, shows why each one made the list, and leaves the decision to that person. It never applies
or sends anything.

This replaces my October pitch film (`../`, *Terraform Docs, Quoted*) as my project film. The
project changed to the job-search agent (reasons in `FRICTIONAL.md`). The October film and its
files are unchanged.

## The four parts, in order

| Part | Time | Beats | What it says |
|---|---|---|---|
| 1 · What and why (executive summary) | 0:00–0:44 | B01–B04 | What the agent does; most postings don't fit (1 of 675); a person decides; why reasons matter. No "how". |
| 2 · What others have done | 0:44–1:25 | B05–B07 | Job alerts (LinkedIn, Indeed); AI matching and auto-apply (LinkedIn Skills Match, Jobright, LazyApply, Simplify); what none of them mention, and what mine adds |
| 3 · How I'll build it (methods) | 1:25–2:32 | B08–B12 | Data (three public boards, a fictional candidate); what JS1 and JS2 built; the next steps (JS3, JS4, JS5); what I have (Python, Claude Code through NEU, free boards, laptop, no paid credits) |
| 4 · How I'll know it worked (evaluation) | 2:32–3:15 | B13–B17 | Four checks with pass lines: reject audit (at most 1 of 30), must-skip list (0 let through; skip at least half), planted failures (all caught), approval binding (a changed shortlist loses its approval) |
| Outro | 3:15–3:20 | BOUT | Title and name |

Every scene shows its part label at the top left. Detail for each part is in
[APPENDIX.md](APPENDIX.md).

## Files

| File | What it is |
|---|---|
| `final/varnika-final-project-film.mp4` | The film |
| `APPENDIX.md` | The four parts in detail: sources, step-by-step plan, resources, pass lines, and what the checks can't show |
| `FACTCHECK.md` | Every claim in the film with its source |
| `evidence/others-2026-11-23/README.md` | Part 2's seven company pages: URLs, quotes, SHA-256s (the page copies stay on my machine) |
| `beat_sheet.json`, `make_sheet.py` | Narration and visual plan, 18 beats, with measured durations |
| `scenes.py` | Every scene, drawn in Manim |
| `SHOTLIST.md`, `PROMPTS.md` | Toolkit paperwork |
| `SOURCES.md` | Sources, who did what, the computer-voice disclosure |
| `FRICTIONAL.md` | Dated log |
| `BUILD-PROMPT.md` | Prompts and commands that rebuild the film |
| `gate-reports/` | The toolkit's quality-gate reports |

## How to rebuild

Full steps are in `BUILD-PROMPT.md`. In short, with brutalist.art at `b21f625` and its virtual
environment active:

```bash
python3 make_sheet.py                                   # only before re-voicing
python3 <brutalist.art>/runtime/scripts/generate_audio_kokoro.py <this folder>
./art run   <this folder> --height 1080
./art final <this folder> --height 1080 --out <this folder>/final
```

## Disclosure

The narration is a synthetic Kokoro voice (`am_onyx`), first person, as me. Claude Code drafted the
script and built the film from my JS1/JS2 records and my decisions. Who did what is in
`SOURCES.md`.
