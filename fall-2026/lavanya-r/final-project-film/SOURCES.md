# SOURCES: README Checker pitch film

## What the film is based on
- **PROJECT-BRIEF.md**: my seven answers, written 2026-10-13.
- **APPENDIX.md**: the method detail behind Parts 3 and 4 of cut 4 (2026-11-23).
- **Manual README run 1 (2026-10-13):** I followed my own public repo's README, <https://github.com/LavanyaRajesh24/webapp>, in a fresh clone. My terminal output is summarized in PROJECT-BRIEF.md and FRICTIONAL.md.
- **Manual README run 2 (2026-10-13):** I followed the "Running Locally" section of <https://github.com/heroku/node-js-getting-started>.
- **My CI workflows:** `.github/workflows/ci.yml`, `packer-build.yml` and `packer-ci.yml` in my `webapp` repo. I read them on 2026-10-13.

## Prior work named in the film (Part 2, checked 2026-11-23)
- **ExecutionAgent:** I. Bouzenia and M. Pradel, "You Name It, I Run It: An LLM Agent to Execute Tests of Arbitrary Projects," ISSTA 2025. <https://arxiv.org/abs/2412.10133>. Installs and tests 33 of 50 projects.
- **Installamatic:** L. Milliken, S. Kang and S. Yoo, "Beyond pip install: Evaluating LLM Agents for the Automated Installation of Python Projects," SANER 2025. <https://arxiv.org/abs/2412.06294>. Installs 21 of 40 repositories (55%).
- **Runme:** <https://github.com/runmedev/runme> (formerly github.com/stateful/runme). Runs code blocks from Markdown files such as READMEs.
- **Doc Detective:** <https://github.com/doc-detective/doc-detective>. Tests documentation against the product, from test specs or marked-up docs.

## What I made
- The script, the beat sheet (`make_sheet.py` → `beat_sheet.json`) and the drawings (`scenes.py`), written with Claude's help and checked by me.

## What Claude contributed
- Claude (Claude Code, Opus 5.5) helped me choose the project, draft PROJECT-BRIEF.md and the narration, write the Manim drawing code, and run the Brutalist pipeline.
- I made the project choice. I ran both manual README tests myself and reported the results. I reviewed and approved the script.
- The film shows no Claude responses. The terminal lines on screen are my own output from 2026-10-13, not Claude's.
- The narration voice is synthetic (Kokoro `af_bella`) reading my first-person script. My first name is respelled "Luh-vun-ya" in the script so the voice pronounces it correctly.

## Toolkit and third-party assets
- **Brutalist** (<https://github.com/nikbearbrown/brutalist.art>, commit `519fcbb`): show-tell skill, `iso_kit.py` drawing kit, and the Remotion bookend `BrutalistHesitantWriter`.
- **Voice:** Kokoro-82M (Apache-2.0), voice `af_bella`, run locally. It is a synthetic voice reading my script.
- **Fonts:** EB Garamond (SIL Open Font License), bundled with Brutalist. Menlo, the macOS system monospace font, renders the terminal lines; no font file is redistributed.
- **Rendering:** Manim Community (MIT), Remotion and ffmpeg.
- No images, music or video were generated or downloaded.
