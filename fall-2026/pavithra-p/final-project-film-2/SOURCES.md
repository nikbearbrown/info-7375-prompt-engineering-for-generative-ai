# SOURCES: DryRun Final Project Film

## What I used

| Source | Used for | Licence / terms |
|---|---|---|
| [Brutalist toolkit](https://github.com/nikbearbrown/brutalist.art), commit `b21f625` | Pipeline, quality gates, the show-tell drawing kit (`iso_kit.py`) and the 25 approved original props (`iso_originals_25.py`) | Course toolkit; free local pipeline only |
| [Kokoro-82M](https://github.com/thewh1teagle/kokoro-onnx) via kokoro-onnx, voice `af_heart`, speed 0.95 | Narration (synthetic voice reading my script) | Apache-2.0 model; runs locally, $0 |
| Manim Community v0.18.1, ffmpeg | Drawing and rendering | MIT; LGPL/GPL |
| Helvetica Neue, Menlo | On-screen type | macOS system fonts (Apple's licence) |
| [binpash/try](https://github.com/binpash/try) README | Part 2: what `try` does and what it doesn't | Read 2026-11-23 |
| [ShellCheck](https://github.com/koalaman/shellcheck) and [explainshell](https://github.com/idank/explainshell) READMEs | Appendix, part 2: two tools that read a command's text | Read 2026-11-23; cited only |
| InterCode ([arXiv 2306.14898](https://arxiv.org/abs/2306.14898)) and NL2SH ([arXiv 2502.06858](https://arxiv.org/abs/2502.06858)) abstracts | Part 2: what the research got | Read 2026-11-23; cited only |
| My October pitch film (`fall-2026/pavithra-p/final-project-film/`, v5) | 11 beats reused word for word, with their drawings | Mine |

## What I made

- The project and its decisions: DryRun is my final project, the film is about it, and the plan in part 3.
- The real Claude reply in part 1: asked in a fresh claude.ai chat on 2026-10-11 (`evidence/claude-reply-2026-10-11.png`).
- The preview test in part 1, re-run in my own Terminal on 2026-10-13 (`evidence/mtime-test.md`).
- The choice to check the script against every line of the professor's description, and to apply the three fixes after the strict score.
- Checked the three prior-work pages myself on 2026-11-23 (the `try` README, InterCode and NL2SH on arXiv) against what part 2 says.

## What Claude (Claude Code, Opus 5.5) contributed

- Read the professor's description, the final project brief and my pitch film, and drafted the four-part script, keeping 11 of my pitch lines word for word.
- Read the `try` README and the two arXiv abstracts (2026-11-23) and wrote down what they got (`evidence/prior-work-2026-11-23.md`).
- Checked the facts in the resources line on my Mac (Claude Code version, memory, Docker, Ollama and its model).
- Scored the script strictly against the description and proposed three fixes, which I applied.
- Wrote `make_sheet.py`, the new scenes in `scenes_body.py`, `APPENDIX.md`, FACTCHECK, SHOTLIST, this file and the README, and ran the toolkit and every gate.
- Checked each point of a ChatGPT review of the draft against the files, then changed two narration lines (B05, B07), the evaluation metric in `APPENDIX.md` and one sentence in `FRICTIONAL.md`, and re-ran every gate.
- Graded the fixed draft as the strictest TA (23.5/25), read the ShellCheck and explainshell READMEs, and added them and fixed task counts to `APPENDIX.md`.
- Compared my folder with my classmates' submitted folders and added the ShellCheck baseline to `APPENDIX.md`.
- Organised `FRICTIONAL.md` from the session. The reflection lines in it are mine.

## Other AI

- ChatGPT reviewed the draft as a strict TA (22.5/25). Its four points were checked against the files and applied. A second check found two stale appendix sentences, also fixed. `FRICTIONAL.md` lists them.

## Third-party assets

No stock images, music or footage. Every picture is drawn in code, except the real screenshot in B03 (mine). The props are the toolkit's own approved originals.

## Constructed or real

- Real: Claude's reply (B03, the real screenshot, cropped), my preview test (B04, my own Terminal lines), and the facts about `try`, InterCode and NL2SH (B07, B08, read 2026-11-23). In the appendix only: ShellCheck and explainshell (read 2026-11-23).
- Real, checked 2026-11-23: the resources in B19 (Claude Code 2.1.294 through NEU, Apple M3 with 8 GB, Docker 27.4.0, Ollama with `qwen2.5`).
- Constructed, and labelled on screen: the AI's prediction (B12), the simulated deletion (B13), the WARN decision (B14), the change report and the person's choice (B15).
- Plans, not results: everything DryRun "will" do, the dated steps (B18) and every target in part 4 (labelled PLANNED and TARGETS · NOT MEASURED YET). No DryRun results exist, so the film shows no DryRun measurements.
