# BUILD-PROMPT — how to rebuild *Fine Print*

The film is fully reproducible from this folder plus the free brutalist.art toolkit. Nothing is paid, nothing needs an
API key, nothing is uploaded. Narration and rendering run locally.

## 1. Toolchain (what built the submitted master)

| Tool | Version |
|---|---|
| macOS | Darwin 27 (Apple silicon) |
| brutalist.art | `github.com/nikbearbrown/brutalist.art` at commit `519fcbb` |
| Python | 3.12.7 in a venv (`brutalist.art/.venv`) with the toolkit's `requirements.txt` (Manim 0.20.1, ManimPango 0.6.1, kokoro-onnx 0.6.1, faster-whisper 1.2.1, Pillow 12.3.0, numpy 2.5.4) |
| Node | 22.11.0 (Remotion 4, installed by `./setup --install`) |
| FFmpeg | 8.1 |
| Voice | Kokoro-82M `am_eric`, model files `kokoro-v1.0.onnx` + `voices-v1.0.bin` |

## 2. Commands

```bash
# the folder layout the scripts expect: the toolkit beside this folder
mkdir film && cd film
git clone https://github.com/nikbearbrown/brutalist.art && git -C brutalist.art checkout 519fcbb
cp -R /path/to/final-project-film .          # this folder

cd brutalist.art
python3 -m venv .venv && source .venv/bin/activate
./setup --install       # installs everything; at 519fcbb it then exits 1 at its own ElevenLabs guard (see FRICTIONAL.md)
cd ../final-project-film

python3 build_scenes.py                       # scenes.py = toolkit iso_kit.py + iso_originals_25.py + scenes_body.py
bash build_audio.sh                           # sheet -> Kokoro am_eric -> name_voice.py (my name) -> pad bookends -> measure
../brutalist.art/art run . --height 2160      # Gates F, L, A, W, B (layout), the renders, the review cut, Gate V
../brutalist.art/art final . --height 2160 --out exports/landscape   # GATE T, then the clean master
python3 make_srt.py                           # captions from the script + measured timings
S=../brutalist.art/runtime/scripts; MP4=exports/landscape/fine-print-pitch.mp4
python3 $S/master_check.py . --mp4 $MP4      # render integrity: 3840x2160, 24 fps, h264, audio, duration = sheet
python3 $S/loudness_check.py . --mp4 $MP4
python3 $S/sharpness_check.py . --mp4 $MP4
python3 $S/srt_check.py . --srt exports/landscape/fine-print-pitch.srt
python3 ../brutalist.art/runtime/qc/factcheck_check.py .
```

Every report these write is in `gate-reports/` (and `TYPECHECK.md`, `MASTERCHECK.md`, `LOUDNESS.md`, `SHARPNESS.md`,
`SRTCHECK.md`, `_qc/REPORT.md`, `layout_audit.md`). I have not tested whether a rebuild on another machine is
byte-identical; the SHA-256 in README.md identifies the master I submitted.

`art run` renders only clips that are missing. After editing a scene, move its `manim/<BID>.mp4` (and `clips/<BID>.mp4`)
into `_superseded/` and run `art run` again.

## 3. The prompts

These are the prompts I gave Claude Code (Claude Opus 5.5 in the Claude desktop app), quoted from the chat. The full
conversation is not included: the assignment asks to leave private transcripts out.

1. 2026-10-13: "create Assignment 4 folder" (it already existed).
2. 2026-10-13: the Canvas assignment text, pasted, then: "Let's start working on this to score absolutely full. marks,
   so lets do it".
3. 2026-10-13: four choices among options Claude Code offered: the posting-reader agent; new-grad ML/AI engineer;
   Kokoro voice reading my script; "Say I'm on F-1".
4. 2026-10-13: my Canvas feedback screenshots for Week 1 and Assignment 3, and: "The Last time's I didn't score full
   marks so, this time I don't want to loose any marks so, take a look again to make zero mistakes from your end as well
   as from my end I will look into it correctly".
5. 2026-10-14: my six answers (FRICTIONAL.md, entry 1), the voice `am_eric` and the title *Fine Print*; my résumé, for
   checking only.
6. 2026-10-14: my review of the script and the render (FRICTIONAL.md, entries 2–3) with four changes; my LinkedIn check;
   my name's pronunciation, सुकेत रेड्डी फ्रंदटूर; then "A-intro-am_eric-from-your-guide.mp3 — This has perfect name
   pronunciation of mine".

## 4. A prompt that rebuilds the film from scratch

To regenerate a film like this one, from this folder, with Claude Code:

> In `final-project-film/`, rebuild the pitch film *Fine Print* with the brutalist.art `show-tell` skill at commit
> `519fcbb`. Read `skills/make/show-tell/SKILL.md` whole first. Keep `beat_sheet.json`'s narration exactly as written
> (first person, voice `am_eric`); every beat is one drawn picture from `scenes_body.py`, using only the toolkit's 25
> original props. Do not use the instructor's name, persona, handle or outro (`ClaudeTitleOutro` hard-codes one; BOUT is
> a drawn beat). Keep each beat's honesty stamp ("real · …" or "constructed · not built"). Run `python3 build_scenes.py`,
> `bash build_audio.sh`, `art run . --height 2160`, then `art final . --height 2160 --out exports/landscape`, look at the
> frames, and stop on any gate failure instead of working around it. Do not publish anything.
