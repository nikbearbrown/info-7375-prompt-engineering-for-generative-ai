# Quote It or Refuse. — Final Project Pitch Film

## Executive summary

A short pitch film for my INFO 7375 final project, **ClaimCheck** (working title). It will be an
insurance-claims question-answering tool that answers only with a word-for-word quote from the
documents, checks that quote with code, and otherwise says "not in the documents". **Nothing
of ClaimCheck is built yet.** The film says so, and every picture of the tool is labelled
CONSTRUCTED or PLANNED on screen.

| | |
|---|---|
| Name | Shreyash Yadav |
| Course | INFO 7375 — Prompt Engineering & Agentic AI, Fall 2026 |
| Project (working title) | ClaimCheck |
| Target role | Applied-AI / LLM engineer at an insurtech or health-tech company |
| Film | `Yadav_Shreyash_INFO7375_FinalProjectFilm.mp4` — 3:33 (213.3 s), 3840×2160, 24 fps |
| Made with | Brutalist toolkit (ai-explainer skin), Kokoro TTS, Manim, Remotion. All local and free |

## Files

| File | What it is |
|---|---|
| `Yadav_Shreyash_INFO7375_FinalProjectFilm.mp4` | the rendered film. It is in the Canvas zip; the course repo's student folders don't commit rendered video, so it isn't in git. To check the two match: 19,249,290 bytes, sha256 `3b21e14d8d60cbe6e237256d7205316fee4c411518a402e837556756269c64f5` |
| `PROJECT-BRIEF.md` | the seven answers, plus "exists today" and "will exist" lists |
| `beat_sheet.json` | narration and visual plan, 14 beats, with measured audio durations |
| `scenes.py` | the eight Manim body scenes and the outro card |
| `BUILD-PROMPT.md` | commands and prompts that rebuild it |
| `build.sh` | one-command rebuild |
| `SOURCES.md` | what I used, what I made, what Claude contributed, licences |
| `FRICTIONAL.md` | dated log of what went wrong and what I did |
| `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` | paperwork the toolkit requires before it renders |
| `evidence/dovetail-pytest-2026-10-07.txt` | the only real output shown in the film (Dovetail's test run) |
| `qc/` | the toolkit's gate reports for the final build |

## Rebuild

```bash
source /path/to/.venv-brutalist/bin/activate
./build.sh /path/to/brutalist.art
```

Full steps, prerequisites, and the prompts used are in `BUILD-PROMPT.md`.
