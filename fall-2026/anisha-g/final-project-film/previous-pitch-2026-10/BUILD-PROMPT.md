# Build Prompt — how to rebuild this film

## 1. Prompts I gave Claude
- 2026-10-10: "help to do this assignment choose easy topic and tell me what to do" (assignment text attached)
- 2026-10-10: "choose easy topic bcoz I have to submit today"
- 2026-10-10: "lets get started with hour 1 …" → Claude drafted `PROJECT-BRIEF.md`
- 2026-10-10: "tell me step by step to do assignment" → Claude read the Brutalist docs and drafted the beat sheet and support files
- 2026-10-13: "my name is Anisha Gaikar and plz fix the 4 questions" → Claude filled in my name and questions 2 and 7
- 2026-10-13: "use ai generated voice …" → narration switched to the macOS text-to-speech voice
- 2026-10-13: "add little more animation and elements … make sure it has visuals", "add more color aesthetic, presentable" → subtitles, question titles, looping motion, extra drawings, more colours
- 2026-10-13: shared a classmate's pitch film and asked for "same with different topic" and "change the design" → Claude rewrote the beat sheet in the same show-tell structure (typing intro, terms card, one drawing per beat) and wrote `tools/render.py` to draw and animate the scenes in its own teal/coral palette. No content, drawings or files were taken from the classmate's film; only the format was followed.

- 2026-10-13: "have we pushed everything and covered every requirement … I don't want to lose marks" → Claude ran the toolkit's Gate V, fixed the design until it passed, and added `tools/run_gate_v.sh`
- 2026-10-13: tried ChatGPT myself on a real posting for question 2 (screenshots in `evidence/`); gave my MBTA pipeline repo as question 7 evidence

- 2026-10-14: "see [brutalist.art] and tell me I have done every part like the minor parts too" → Claude compared the folder with the show-tell workflow, wrote FACTCHECK.md, SHOTLIST.md and PROMPTS.md, and `tools/run_gate_f.sh`

- 2026-10-14: "did u see brutalist and tell if u did same way professor asked" → tried `./setup --install`; log saved to `reports/brutalist-setup-log.txt`

## 2. Brutalist
```bash
git clone https://github.com/nikbearbrown/brutalist.art
cd brutalist.art
./setup --install
```
The show-tell skill needs Manim, Remotion (Node 20+), ffmpeg and the Kokoro voice model. See FRICTIONAL.md for what happened. The film follows the show-tell format, but its scenes were drawn with `tools/render.py` (Python + Pillow) instead of Manim.

## 3. How the film is built
```bash
# draw + animate the ten scenes from the beat sheet (silent clips)
python3 tools/render.py beat_sheet.json tools/fonts clips
# narration: macOS `say -v Samantha -r 180` reads each block of RECORDING-SCRIPT.txt,
# then ffmpeg joins each clip with its narration (holding the last frame) and concatenates them
bash make_film.sh Gaikar
```
Scene timing comes from the narration: each drawing appears when its phrase is spoken (estimated at 180 words per minute), and `make_film.sh` stretches each scene to the real length of its narration so the drawings and subtitles stay in sync.

## 4. Checks
Toolkit gate (Brutalist GATE V, `runtime/qc/final_frame_check.py`), run on the finished film:
```bash
bash tools/run_gate_v.sh      # clones brutalist.art if needed, writes reports/GATE-V-REPORT.md
bash tools/run_gate_f.sh      # Gate F: paperwork present + factcheck_check.py, writes reports/GATE-F-REPORT.md
```
My own checklist:
- [x] Runtime between 2 and 4 minutes: 3:45
- [x] Every drawing shows "CONSTRUCTED · not built yet"
- [x] Nothing described in past tense unless it exists today
- [x] All seven questions answered
- [x] Video plays start to finish with narration on every scene
