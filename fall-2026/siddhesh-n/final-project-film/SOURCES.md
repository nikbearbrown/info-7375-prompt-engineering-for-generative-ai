# SOURCES

## What I used
| Thing | Use | Licence / terms |
|---|---|---|
| brutalist.art toolkit (github.com/nikbearbrown/brutalist.art) | the pipeline: show-tell skill, `iso_kit.py` drawing kit (pasted into `scenes.py`), `BrutalistHesitantWriter` and `ClaudeDefinitions` Remotion scenes, gate scripts | course toolkit, used as the assignment directs; no instructor name, persona, or credit line used in the film |
| Kokoro-82M voice `am_onyx` (kokoro-onnx) | narration — **a synthetic voice reading my script in my name**, not a recording of me | Apache-2.0 (Kokoro model) |
| Manim Community | drawing and animating the body beats | MIT |
| Remotion | the two opening cards and the score-table card | Remotion licence (free for individuals) |
| EB Garamond font (bundled with the toolkit) | on-screen labels | SIL Open Font License |
| My own public repos `nikam0420/marketing-campaign-analytics` and `nikam0420/Individual_Siddhesh-Nikam_ExplorataryDataAnalysis` | context for the domain I work in. AI wrote most of their code and the dashboard, so they are not shown as proof of coding skill | mine, with substantial AI help |

## What I made
- Checked the answer key by hand on 2026-10-24: 38860 ÷ 14185 = 2.74, 6150 ÷ 2685 = 2.29, 28000 ÷ 7030 = 3.98 on a calculator, all matching `tests/questions.json`.
- The ChatGPT test in the film: I ran it myself on 2026-10-24 (GPT-6.1 Sol Light, new chat, `campaigns.csv` attached). `build/chat_test_full.png` is my screenshot cropped to the chat pane only (sidebar and tabs removed for privacy; nothing else changed), and `build/chat_test.png` is the crop of its answer sentence, shown in the film with colours inverted (dark mode to light) so the toolkit text check can read it.
- The project idea and the choices in `PROJECT-BRIEF.md` (role, alternatives, skills, scope), which I have read and can explain.
- The rendered film (built on my Mac).
- `FRICTIONAL.md` entries.

## What Claude contributed (claude.ai, Claude Opus 5.5, 2026-10-14)
- Suggested three project options; I chose "Verified SQL Q&A" (now CheckedSQL).
- Drafted `PROJECT-BRIEF.md`, the narration and visual plan (`build/make_sheet.py` → `beat_sheet.json`), all Manim scene code (`build/scenes.py`), `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`, `README.md`, `BUILD-PROMPT.md`, `build_film.sh`, and this file.
- Spotted that the toolkit's stock outro (`ClaudeTitleOutro`) hard-codes the instructor's handle and replaced it with my own title card.
- Ran the Manim-free gates (static pre-flight A, WCAG/margins W, beat lint L, bookend) — all passed.
- No Claude response is shown in the film.

## What Claude contributed on 2026-10-24 (claude.ai, Claude Opus 5.5)
- Chose the ten test questions and wrote the code in `checkedsql/`: `checker.py`, `answer_key.py`, the ten SQL queries and the two trap queries. It also invented the 24 synthetic rows to my spec (3 channels × 2 devices × 4 weeks, with the ROAS trap changing the winner) and generated `HAND-CHECK.md`.
- Redrafted the narration and every scene for v2 of the film (`build/make_sheet.py`, `build/scenes.py`), wrote `build/sync_props.py` and `build/make_srt.py`, and updated `build_film.sh`.
- Fact-checked the new narration against the data and caught one error ("fifteen to twenty times" → "fourteen to twenty").
- No Claude response is shown in the film. The chat-assistant answer on screen is from my own test, not from Claude in this session.

## Third-party assets
None beyond the tools and font above. No stock images, music, or generated video. No real user, company or personal data.
