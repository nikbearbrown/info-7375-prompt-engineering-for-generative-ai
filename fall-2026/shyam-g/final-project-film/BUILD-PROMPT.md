# How to rebuild

## Prompt used (summary)
The prototype and drafts were built in one Claude Code session on 2026-10-14. That session's prompt was:
- the assignment text
- a staged plan: a stdlib rule engine with no LLM, at least 8 tests with a saved run report, then the paperwork and the film
- the three outcomes and their precedence
- the stated risk (a misleading paraphrase can pass explicit rules)
- an instruction to leave unknowns as pending rather than guess them

The full transcript is not included, per the assignment.

## 1. Prototype (verified on Windows 11, Python 3.12.5, 2026-10-14)
```bash
python data/build_synthetic.py
python -m stopline data/incidents.json --audit-out reports/audit.jsonl
python -m unittest discover -s tests -v
python -m stopline.evaluate data/incidents.json data/evidence.json data/labels.json --out reports/eval_report.md
```

## 2. Reel folder (verified on Windows, 2026-10-14)
```bash
python film/build_reel.py <path-to-brutalist.art>   # writes film/reel/beat_sheet.json + scenes.py (kit pasted in), and ./beat_sheet.json
```
`film/reel/` also holds FACTCHECK.md, SHOTLIST.md, PROMPTS.md and SOURCES.md, which Gate F requires.
The pre-render checks (factcheck, bookend, beat-lint, Gate A static check on all 11 scenes) passed. See `film/gate_reports/pre_render.txt`.
Do not re-run `build_reel.py` or `make_sheet.py` after audio is generated: it would wipe the measured durations.

## 3. Film (rendered 2026-10-15 in WSL Ubuntu)
Run inside Ubuntu:
```bash
bash "/mnt/d/OneDrive - Amrita Vishwa Vidyapeetham/Desktop/NEU/Fall 26/Prompt Eng & Agentic AI/StopLine/final-project-film/film/wsl_setup.sh"
```
Then, from the project folder inside Ubuntu, `film/wsl_reel.sh` does each step on a render copy at `~/reels/stopline-pitch` (outside OneDrive). Before the first audio run, copy `film/reel/` there.
```bash
python3 ~/brutalist.art/runtime/scripts/generate_audio_kokoro.py ~/reels/stopline-pitch
bash film/wsl_reel.sh pad        # 1.0 s silent tail on the outro
bash film/wsl_reel.sh whisper    # pronunciation check
bash film/wsl_reel.sh scenes     # re-paste the kit + film/scenes_body.py
bash film/wsl_reel.sh stills     # low-res frames into film/stills/
bash film/wsl_reel.sh run        # ./art run --height 2160 (Gates A, B, V + review cut)
bash film/wsl_reel.sh final      # ./art final (Gate T + master)
bash film/wsl_reel.sh collect    # copy the mp4 and gate reports back
```
Gate reports to copy into `film/gate_reports/`: `_qc/REPORT.md`, `_qc/contact_sheet.png`, `TYPECHECK.md`, `layout_audit.md`.
