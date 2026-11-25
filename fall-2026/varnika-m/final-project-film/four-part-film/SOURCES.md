# Sources

**Film:** A Job-Search Agent You Can Check (Final Project Film, four-part)
**Author:** Varnika M · INFO 7375
**Status:** rendered 2026-11-23. Watched and approved by me on 2026-11-23 (section 4).

Read the [course AI policy](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/prerequisites/ai-policy.md) and [AI Policy for Professor Bear's Courses | Using AI Responsibly in Class](https://youtu.be/8Ut0Cdl6vMw?si=9w3aEpt1ZyAR4Kiz).

## 1. Disclosures

**Narration.** A synthetic computer voice (Kokoro `am_onyx`, generated locally, free). It is not my
voice or any real person's. I chose the animated film with a computer voice on 2026-11-23. It's
the same stock voice as my Week 01 video and my October pitch film. The narration is first person,
as me, and uses no instructor name, persona or credit line. Claude Code drafted the script from my
JS1 and JS2 records and from my answers (section 4).

**Claude output.** No Claude reply is shown in the film.

**Constructed material.** Every drawing of something not built yet (the shortlist with reasons,
the approval step, JS3–JS5, the four planned checks) carries an on-screen "planned" label. Real
numbers carry a source tag that names the run they come from. B15's JS2 catch is labeled
"seeded", because it was a constructed response, as `../../js2-loop-tools-diff/FINISHED-WRONG.md`
says.

**Other companies' products.** Part 2 reports what seven company pages say about their own
products, fetched 2026-11-23. Nobody tried the products for this film. The page copies stay on my
machine. Their URLs, quotes and SHA-256s are in `evidence/others-2026-11-23/README.md`.

## 2. Sources used

| Source | Used for |
|---|---|
| My JS1 folder, `../../js1-contract-and-watch/` (README run table, `CONTRACT.md` Rules 1–5, `SOURCES.md`) | B02 (675 postings, 1 match), B09 (five rules, 73 tests) |
| My JS2 folder, `../../js2-loop-tools-diff/` (README, `GATE.md`, `POLICY.md`, `FINISHED-WRONG.md`, `REVIEW-FINDINGS.md`, `jobs/runs/2026-11-10T212848Z.json`, `config/boards.json`, `persona/`) | B03, B08, B10, B12, B15 |
| Assignment briefs JS3, JS4, JS5 and Final Project, `assignments/` in this repository | B11 (next steps), B14 (the skip-at-least-half rule), APPENDIX dates |
| LinkedIn Help a511279 (Job Alerts) and a793433 (Skills Match); Indeed job-alerts help article 204488890; jobright.ai/ai-agent; lazyapply.com; Simplify help articles 1784339 (Autopilot) and 2415391 (Copilot). All fetched 2026-11-23 | B05, B06, B07 |
| Professor Bear's film guidance, "What your project film needs to show", and the Canvas assignment "Final Project Film" (25 points, due Monday 2026-11-23, 11:30 pm) | The four-part structure and order |
| Brutalist toolkit, https://github.com/nikbearbrown/brutalist.art, revision `b21f625`, used unmodified | Show-tell format, the drawing kit at the top of `scenes.py` (as in my October film), narration audio, rendering, quality gates |

## 3. What I made

- `make_sheet.py` (writes `beat_sheet.json`): the narration and visual plan, 18 beats
- `scenes.py`: all 18 scenes, drawn in Manim. The kit block at the top is the same trimmed
  toolkit kit as in my October film. The cast and scenes are new.
- `APPENDIX.md`: the detail behind each of the four parts
- `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`: the toolkit's required paperwork
- `evidence/others-2026-11-23/README.md`: the Part 2 sources
- The rendered film in `final/`

## 4. Contributions

**Me (Varnika):**
- Asked for the assignment to be explained in plain English.
- Asked whether it was a new assignment, and pasted the Canvas listing.
- Asked for project ideas, and chose my job-search agent (idea 1) as the project.
- Asked for the complete assignment to be done, meeting every criterion.
- On 2026-11-23, made the decisions the film depends on: the animated film with a computer voice;
  my reason for caring ("I'm job searching myself"); the "strict" pass line for Part 4; and that
  Claude Code would research Part 2 from public pages.
- The JS1 and JS2 work the film describes is mine, with Claude Code's contributions recorded in
  those folders' own `SOURCES.md`.
- Watched the final cut on 2026-11-23 and approved it: "yes the film is okay".
- Confirmed the strict wording of check 2 the same day ("yes"), after Claude Code explained its
  wording mistake in the option I was first shown.

**Claude Code (NEU-provisioned):**
- Explained the assignment, confirmed from the repository that classmates were re-cutting into
  four parts, and flagged that JS3 was due the same night.
- Suggested three project ideas.
- Researched Part 2 through a sub-agent that fetched the seven company pages, then matched every
  quote against the saved pages itself.
- Re-ran my JS1 and JS2 tests to confirm the counts (73, 122).
- Drafted all the narration and every file in this folder.
- Generated the voice, checked pronunciation with a speech-to-text pass, and reworded two lines
  that could be misheard.
- Wrote `scenes.py`, fixed the layout and the toolkit-gate failures, and rendered the film.
- Wrote check 2's pass line as "every must-skip posting is skipped, and the run skips at least half
  of what it evaluates". This is stricter than the option text I was shown ("skips at least half
  of a should-skip list"), which had misread the course rule. See `FRICTIONAL.md`.

No conversation transcripts are included.

## 5. Third-party material and licences

- Brutalist toolkit: used as an external tool at `b21f625`, unmodified, and not vendored. The
  pasted drawing kit is credited at the top of `scenes.py`.
- Kokoro-82M voice model (Apache-2.0), run locally through `kokoro-onnx`.
- Company names and product claims in Part 2 are quoted from public pages for identification and
  comparison. No logos, screenshots or page copies are published.
