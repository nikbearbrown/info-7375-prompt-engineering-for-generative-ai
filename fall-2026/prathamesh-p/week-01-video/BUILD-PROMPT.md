# BUILD-PROMPT.md — Commands run for the Week 1 explainer video

Environment: native Windows 11 (no WSL), PowerShell 5.1 / Git Bash. Git 2.55.0, Python 3.11 (via `py -3.11`).

## 2026-09-27

### Environment check
```powershell
Get-ChildItem C:\info7375 -Force
git --version
py -0p
```

### Step 1 — clone repos into C:\info7375
```powershell
cd C:\info7375
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai
git clone https://github.com/nikbearbrown/brutalist.art
```
Course repo HEAD: `b293224d5c6f078ce5f793c7ea0f73c9af3f19a0`. brutalist.art HEAD: `cd4bf20904be4e7d63babd9622b17963c2361b27`.

### Step 2 — run Chapter 1 code (Python 3.11.9)
```powershell
cd C:\info7375\info-7375-prompt-engineering-for-generative-ai
py -3.11 --version
cmd /c "py -3.11 lessons\01-randomness-and-first-prompts\code\main.py > C:\info7375\week-01-video\main_output_2026-09-27.txt"
git rev-parse HEAD
```
Result (exit 0): probabilities `[0.09003057317038046, 0.24472847105479764, 0.6652409557748218]`, counts `{"1": 268, "2": 630, "0": 102}`. **Matches expected.** Derived: expected count for token 2 = 1000 × 0.6652409557748218 = 665.2409557748218 (≈ 665.24) vs observed 630.

### Step 3 — brutalist.art setup (Git Bash)
```bash
# prerequisite probe
for c in python3 python pip node npm ffmpeg ffprobe curl pdflatex dvisvgm fc-list; do command -v "$c"; done
python3 --version; node --version; npm --version
# install + readiness
cd /c/info7375/brutalist.art && ./setup --install 2>&1 | tee /c/info7375/week-01-video/logs/setup_install_2026-09-27.log
# post-checks
ls -la runtime/models/kokoro/; ls "$HOME/.local/share/fonts" | head
[ -d runtime/remotion/node_modules ] && echo "node_modules: present"
EL_PAT="ELEVEN""LABS_API_KEY|elevenlabs""\.io|\"engine\"[^\"]*\"elevenlabs\"|xi-api-key"
grep -rnoiE "$EL_PAT" --exclude-dir=.git --exclude-dir=node_modules youtube | head -12
git log -1 --format='%H %cd'
```
(`EL_PAT` is copied verbatim from `setup` line 105; the string splitting is the script's own trick so it doesn't match itself.)
Result: exit 1. Python deps FAILED (python3 = Store stub), npm OK, fonts copied, Kokoro model downloaded. Script aborted at the ElevenLabs guard, so **no readiness table was printed**. See FRICTIONAL.md.

### Step 3b — fixes (user-approved) and setup re-run
```powershell
# Python 3.11 venv with a python3 alias
cd C:\info7375\brutalist.art
py -3.11 -m venv .venv
Copy-Item .venv\Scripts\python.exe .venv\Scripts\python3.exe
.venv\Scripts\python3.exe --version
git check-ignore -v .venv; git status --short
# LaTeX
winget install MiKTeX.MiKTeX --accept-package-agreements --accept-source-agreements --disable-interactivity
```
Local, uncommitted edit to `setup`: added `--exclude-dir=youtube` to both ElevenLabs-guard `grep` calls. The exact change is in `brutalist-setup-local-patch.diff`.
```bash
cd /c/info7375/brutalist.art
git diff -- setup > /c/info7375/week-01-video/brutalist-setup-local-patch.diff
source .venv/Scripts/activate
command -v python3; python3 --version; python3 -m pip --version
export PATH="/c/Users/Prathamesh P/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"   # needed in shells opened before the MiKTeX install
command -v pdflatex dvisvgm; pdflatex --version | head -2; dvisvgm --version
./setup --install > /c/info7375/week-01-video/logs/setup_install_2026-09-27_run2.log 2>&1
# font verification
ls "$HOME/.local/share/fonts" | grep -iE "oswald|garamond"
powershell.exe -NoProfile -Command "(Get-ChildItem 'C:\Windows\Fonts','$env:LOCALAPPDATA\Microsoft\Windows\Fonts' | Where-Object Name -match 'oswald|garamond').Name"
```
Result: exit 0, all 7 readiness rows ✅ (font row is a Windows false positive; see FRICTIONAL.md).

### Step 4 — font verification + smoke test
```powershell
Get-ChildItem 'C:\Windows\Fonts', "$env:LOCALAPPDATA\Microsoft\Windows\Fonts" | Where-Object Name -match 'oswald|garamond'
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts','HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'   # filtered for oswald|garamond
```
```bash
cd /c/info7375/brutalist.art && source .venv/Scripts/activate
export PATH="/c/Users/Prathamesh P/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"
./art smoke > /c/info7375/week-01-video/logs/art_smoke_2026-09-27.log 2>&1      # exit 1: fixture slug "_smoke" rejected
# Replica of smoke_test.sh steps in a kept scratch copy (slug changed to "smoke" in the COPY only; repo untouched)
W="<scratchpad>/smoke-kept"; cp -R examples/_smoke/. "$W/"
sed -i 's/"slug": "_smoke"/"slug": "smoke"/' "$W/beat_sheet.json"
python3 runtime/scripts/generate_audio_kokoro.py "$W"
ART_FACTS=0 ART_QC=1 ART_STRICT=0 bash runtime/scripts/run.sh "$W"        # compile fails: drawtext Windows path (compile.py:789)
# frames from the per-beat clips that did render
for b in B00 B01; do ffmpeg -v error -y -ss 2 -i "$W/clips/$b.mp4" -frames:v 1 -vf scale=1280:-1 /c/info7375/week-01-video/_font-check/smoke-$b.png; done
# Manim/Pango font probe (scratch scene, not part of the video)
cd /c/info7375/week-01-video/_font-check
python3 -c "import manimpango as m; print([f for f in m.list_fonts() if 'aramond' in f or 'swald' in f])"
manim -s -ql --disable_caching --media_dir ./media font_probe.py FontProbe
```
Result: fonts installed and registered (HKCU). Smoke FAILED (upstream slug bug). The replica got as far as Kokoro audio and per-beat clips, then compile FAILED (Windows drawtext path bug). Manim resolves EB Garamond and Oswald by name. Remotion is not verified.

### Step 5 — reading guides and constraints (read-only)
Read `prerequisites/frictional.md`, `prerequisites/brutalist-video.md`, `prerequisites/brutalist-video-sources.md`, `frictional/templates/FRICTIONAL-annotated.md`, `NEU-COURSELOOP.md`, `brutalist.art/skills/make/ai-explainer/SKILL.md` (full), and `chapters/01-randomness-and-first-prompts.md` (lines ~246–262). Checked that `bookend_check.py` isn't called by `run.sh`, `compile.py` or `art`.

### Step 6 — compile.py patch (local, uncommitted), evidence runs, voice audition
From here on, every toolkit command runs with the venv active, **`export PYTHONUTF8=1`**, and MiKTeX on PATH.
```bash
# compile.py:789 drawtext escaping; exact change in brutalist-compile-local-patch.diff
cd /c/info7375/brutalist.art && source .venv/Scripts/activate
export PYTHONUTF8=1 PATH="/c/Users/Prathamesh P/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"
ART_FACTS=0 ART_QC=1 ART_STRICT=0 bash runtime/scripts/run.sh "<scratchpad>/smoke-kept"   # run2 without PYTHONUTF8 (charmap), run3 with it (GATE V timecode)
ffprobe -v error -show_entries stream=codec_type -of csv=p=0 "<scratchpad>/smoke-kept/smoke-slate.mp4"
ffmpeg -i "<scratchpad>/smoke-kept/smoke-slate.mp4" -af volumedetect -f null - 2>&1 | grep mean_volume
git diff -- runtime/scripts/compile.py > /c/info7375/week-01-video/brutalist-compile-local-patch.diff
# voice audition (NOT reel audio)
python3 runtime/scripts/generate_audio_kokoro.py /c/info7375/week-01-video/_voice-test
```
```powershell
# B04 evidence: exact seed-7 sequence, verified against main.py counts
cd C:\info7375\week-01-video\evidence; py -3.11 seed7_sequence.py
# B06 evidence: real repeat run, byte-compared to the first
cd C:\info7375\info-7375-prompt-engineering-for-generative-ai
cmd /c "py -3.11 lessons\01-randomness-and-first-prompts\code\main.py > C:\info7375\week-01-video\evidence\main_output_rerun_2026-09-27.txt"
cmd /c "fc /b C:\info7375\week-01-video\main_output_2026-09-27.txt C:\info7375\week-01-video\evidence\main_output_rerun_2026-09-27.txt"
Get-FileHash <both files> -Algorithm SHA256
```
Results: seed-7 counts `{'1': 268, '2': 630, '0': 102}` (match). Re-run is byte-identical (SHA-256 `EC682946…EFB4A7`). Voices: af_bella 9.34 s, am_onyx 8.77 s.

### Step 7 — GATE V timecode patch (local, uncommitted), final-path check, B08 snippet check
```bash
# compile.py review timecode: x=w-text_w-16:y=16 -> x=w*0.95-text_w-8:y=h*0.05+8
cd /c/info7375/brutalist.art && source .venv/Scripts/activate && export PYTHONUTF8=1
S="<scratchpad>"; V=/c/info7375/week-01-video
git show HEAD:runtime/scripts/compile.py > "$S/p1/runtime/scripts/compile.py"
(cd "$S/p1" && git apply --unsafe-paths --directory=. "$V/brutalist-compile-local-patch.diff")
cp runtime/scripts/compile.py "$S/p2/runtime/scripts/compile.py"
(cd "$S" && git diff --no-index p1/runtime/scripts/compile.py p2/runtime/scripts/compile.py | sed 's#a/p1/#a/#; s#b/p2/#b/#') > "$V/brutalist-compile-timecode-local-patch.diff"
git diff -- runtime/scripts/compile.py > "$V/brutalist-compile-local-patch-cumulative.diff"
ART_FACTS=0 ART_QC=1 ART_STRICT=0 bash runtime/scripts/run.sh "$S/smoke-kept"     # exit 0, GATE V BLOCKER=0 MAJOR=0
ffmpeg -v error -y -ss 4 -i "$S/smoke-kept/smoke-slate.mp4" -frames:v 1 "$V/_font-check/smoke-slate-t4-safe.png"
./art final "$S/smoke-kept" --allow-slates --height 1080 --out "$S/smoke-final"      # refused by design: final cannot contain slates
```
```powershell
# B08: run the exact on-screen snippet as a viewer would; output kept out of the video
cd C:\info7375\info-7375-prompt-engineering-for-generative-ai\lessons\01-randomness-and-first-prompts\code
cmd /c "py -3.11 - < C:\info7375\week-01-video\evidence\b08_your_turn_snippet.py > C:\info7375\week-01-video\evidence\b08_snippet_check_2026-09-27.txt 2>&1"
# checked only: exit code, 20 lines, each '<seed> <count>', seeds 1-20
```

### Step 8 — GATE P, reel audio, scenes, review build
Files written in `C:\info7375\week-01-video\` (the reel folder): `beat_sheet.json`, `PEDAGOGY.md` (GATE P verdict, student-signed), `scenes.py`, `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`, `CHECKS-REPORT.md`.
```bash
cd /c/info7375/brutalist.art && source .venv/Scripts/activate
export PYTHONUTF8=1 PATH="/c/Users/Prathamesh P/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"
# library-first queries (GATE L doctrine)
./art scenes --check BrutalistHesitantWriter
./art scenes "expected versus observed bar chart" --reel /c/info7375/week-01-video   # + counter / code block / title card queries
# narration fingerprint for GATE P (re-checked after audio: unchanged)
python3 -c "import json,hashlib; b=json.load(open('/c/info7375/week-01-video/beat_sheet.json',encoding='utf-8'))['beats']; print(hashlib.sha256(json.dumps([{'beat_id':x['beat_id'],'narration_text':x['narration_text']} for x in b],ensure_ascii=False,sort_keys=True).encode()).hexdigest())"
# reel audio (af_bella) — the master clock
python3 runtime/scripts/generate_audio_kokoro.py /c/info7375/week-01-video
# scene dry run, then gates A and W by hand, then the review build
cd /c/info7375/week-01-video && for s in B00_TwoNumbers B02_Mechanism B03_ExpectedCount B04_DrawByDraw B05_SideBySide B06_Rerun B07_Boundary B08_YourTurn B09_Outro; do manim --dry_run -ql --disable_caching scenes.py $s; done
cd /c/info7375/brutalist.art && ./art run /c/info7375/week-01-video --height 1080     # runs 1-4; logs logs/art_run_2026-09-27_{1..4}.log
# clip-vs-audio duration check + end-frame preview sheet (Claude's own check, not GATE V)
ffprobe -v error -show_entries format=duration -of csv=p=0 manim/<BID>.mp4
```
Result (run 4): 9/9 Manim beats pass gates A/W/B and are slotted. B01 (Remotion) is blocked by `npx` lookup on Windows, so no review cut yet.

### Step 9 — remotion_scenes.py npx patch (local, uncommitted) and review cut
```bash
# runtime/scripts/remotion_scenes.py:90  "npx" -> shutil.which("npx") or "npx"
cd /c/info7375/brutalist.art
git diff -- runtime/scripts/remotion_scenes.py > /c/info7375/week-01-video/brutalist-remotion-npx-local-patch.diff
source .venv/Scripts/activate && python3 -c "import shutil; print(shutil.which('npx'))"   # C:\Program Files\nodejs\npx.CMD
export PYTHONUTF8=1 PATH="/c/Users/Prathamesh P/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"
./art run /c/info7375/week-01-video --height 1080 > /c/info7375/week-01-video/logs/art_run_2026-09-27_5.log 2>&1
du -sh runtime/remotion/node_modules/.remotion/chrome-headless-shell        # 270M, downloaded by Remotion
ffprobe -v error -show_entries format=duration -of csv=p=0 /c/info7375/week-01-video/week-01-expected-vs-observed-slate.mp4   # 149.5
# B08/B09 frames (not in GATE V contact sheet image)
ffmpeg -v error -y -ss <t> -i week-01-expected-vs-observed-slate.mp4 -frames:v 1 -vf scale=640:-1 _qc/extra_<t>.png   # t = 133.56 139.04 145.36 148.14
```
Result: review cut compiled (149.5 s, 10/10 filled). GATE V FAILED: B06 BLOCKER edge-bleed ×2, B01 MAJOR underfill ×2. Not fixed yet (student watching first).

### Step 10 — approved fixes (B06 panels, B01 props, B02 code size) and rebuild
```bash
# B01: beat-sheet props only (3 lines, fontSize 92, contextTitle, brandLabel) + narration fingerprint re-check
source /c/info7375/brutalist.art/.venv/Scripts/activate && cd /c/info7375/week-01-video
python3 - <<'PY'   # json load -> update B01 shot.remotion.props -> dump; print narration sha256 (unchanged 8afc5b04...)
PY
# force re-render of only the changed beats (toolkit skips existing outputs)
rm media/B01.mp4 manim/B02.mp4 manim/B06.mp4
cd /c/info7375/brutalist.art && export PYTHONUTF8=1 PATH="/c/Users/Prathamesh P/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"
./art run /c/info7375/week-01-video --height 1080      # run 6: GATE A (B02 raw coords) -> fixed code_block
./art run /c/info7375/week-01-video --height 1080      # run 7: GATE V clean; B02 label collision spotted -> fixed
rm /c/info7375/week-01-video/manim/B02.mp4
./art run /c/info7375/week-01-video --height 1080      # run 8: GATE V 0/0, 149.5 s
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 /c/info7375/week-01-video/week-01-expected-vs-observed-slate.mp4   # 1920,1080
ffmpeg -v error -y -ss 38.6 -i /c/info7375/week-01-video/week-01-expected-vs-observed-slate.mp4 -frames:v 1 /c/info7375/week-01-video/_qc/B02_1080_full.png
```

### Step 11 — ./art final (blocked by GATE T), diagnosis, licence reading
```bash
cd /c/info7375/brutalist.art && source .venv/Scripts/activate
export PYTHONUTF8=1 PATH="/c/Users/Prathamesh P/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"
./art final /c/info7375/week-01-video --height 1080 --out /c/info7375/week-01-video/final > /c/info7375/week-01-video/logs/art_final_2026-09-27.log 2>&1   # exit 2: GATE T min-size B05/B08
# locate the short runs with GATE T's own functions (runtime/scripts/type_check.py)
python3 - <<'PY'   # ffmpeg frame -> tc.visible_text_mask -> tc.labeled_blobs -> tc.text_run_bboxes -> shortest runs + crops
PY
# trial fix in a scratch copy of scenes.py (reel folder untouched), render 4K, re-check
manim -qk --fps 24 -r 3840,2160 --disable_caching --media_dir ./media scenes.py B05_SideBySide   # and B08_YourTurn
python3 - <<'PY'   # tc.check_min_size on frames at 15/50/85/97%
PY
# licences, read locally
head -3 runtime/fonts/EB_Garamond/OFL.txt runtime/fonts/PT_Mono/OFL.txt
python3 -c "import importlib.metadata as m; print(m.metadata('manim').get('License'))"   # repeated for each package
head -4 .venv/Lib/site-packages/kokoro_onnx-0.6.1.dist-info/licenses/LICENSE
sed -n 95,104p .venv/Lib/site-packages/kokoro_onnx-0.6.1.dist-info/METADATA
python3 - <<'PY'   # parse Oswald-Variable.ttf 'name' table (IDs 0,1,5,13,14)
PY
head -30 runtime/remotion/node_modules/remotion/LICENSE.md
ffmpeg -hide_banner -L | head -4
head -5 /c/info7375/info-7375-prompt-engineering-for-generative-ai/LICENSE; cat /c/info7375/info-7375-prompt-engineering-for-generative-ai/ATTRIBUTION.md
```

### Step 12 — relative paths, GATE T fix with margin, rebuild, final (attempt 2), logs/
Note: build logs were written to the folder root when each command ran, and were moved into `logs/` on 2026-09-27. The paths in this file show their current location.
```bash
source /c/info7375/brutalist.art/.venv/Scripts/activate && export PYTHONUTF8=1
# relative-path check: identical stills before/after the edit
cd /c/info7375/week-01-video
for sc in B02_Mechanism B04_DrawByDraw B06_Rerun; do manim -s -ql --disable_caching --media_dir <scratch>/before scenes.py $sc; done   # then again into <scratch>/after after the edit
sha256sum <scratch>/{before,after}/images/scenes/*.png                                                                                 # all identical
# GATE A isolated copy, with and without WEEK01_REEL_DIR
cd /c/info7375/brutalist.art/runtime && T=$(mktemp -d) && cp /c/info7375/week-01-video/scenes.py "$T/"
PYTHONPATH="$PWD/manim" python3 qc/static_scene_check.py "$T/scenes.py" --class B04_DrawByDraw                                        # error without the variable (by design)
WEEK01_REEL_DIR=/c/info7375/week-01-video PYTHONPATH="$PWD/manim" python3 qc/static_scene_check.py "$T/scenes.py" --class B04_DrawByDraw   # clean
# GATE T min-size on fresh 4K renders at 11 points (B05 legend 32, B08 note 30)
cd /c/info7375/week-01-video && manim -qk --fps 24 -r 3840,2160 --disable_caching --media_dir <scratch> scenes.py B05_SideBySide   # and B08_YourTurn
python3 - <<'PY'   # type_check.check_min_size on frames at 2,10,...,90,98 %
PY
# rebuild + final
rm manim/B05.mp4 manim/B08.mp4
cd /c/info7375/brutalist.art && export WEEK01_REEL_DIR=/c/info7375/week-01-video PATH="/c/Users/Prathamesh P/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"
./art run /c/info7375/week-01-video --height 1080 > /c/info7375/week-01-video/logs/art_run_2026-09-27_9.log 2>&1        # GATE V 0/0
./art final /c/info7375/week-01-video --height 1080 --out /c/info7375/week-01-video/final > /c/info7375/week-01-video/logs/art_final_2026-09-27_2.log 2>&1   # GATE T PASS; final frame check refused: B09 underfill 44%
# B09 trial layout (positions only) in scratch, checked with the final check's own analyzer
python3 -c "import final_frame_check as ff; print(ff.analyze_frame('<scratch>/f_0.85.png'))"   # ([], 0.658)
# logs into logs/
cd /c/info7375/week-01-video && mkdir -p logs && mv setup_install_2026-09-27*.log art_smoke*_2026-09-27*.log art_run_2026-09-27_*.log art_final*_2026-09-27*.log audio_2026-09-27.log logs/
```

### Step 13 — B09 layout fix, final master, burn-in and consistency checks
```bash
# B09 positions only (title 1.3->2.1, name 0.0->0.4, provenance -0.8->-1.5, disclosure -1.35->-2.2); identical to the tested scratch trial
cd /c/info7375/week-01-video && rm manim/B09.mp4
cd /c/info7375/brutalist.art && source .venv/Scripts/activate
export PYTHONUTF8=1 WEEK01_REEL_DIR=/c/info7375/week-01-video PATH="/c/Users/Prathamesh P/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"
./art run /c/info7375/week-01-video --height 1080 > /c/info7375/week-01-video/logs/art_run_2026-09-27_10.log 2>&1                                         # GATE V 0/0
./art final /c/info7375/week-01-video --height 1080 --out /c/info7375/week-01-video/final > /c/info7375/week-01-video/logs/art_final_2026-09-27_3.log 2>&1  # GATE T PASS; master written
# final master facts and burn-in frames (B00 6.0 s, B04 67.0/75.5 s, B09 145.5/149.0 s)
cd /c/info7375/week-01-video && F=final/week-01-expected-vs-observed.mp4
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_type,codec_name,width,height,r_frame_rate -of compact=p=0:nk=0 $F
for t in 6.0 67.0 75.5 145.5 149.0; do ffmpeg -v error -y -ss $t -i $F -frames:v 1 _qc/final-check/final_t$t.png; done
python3 -c "..."   # darkest pixel in top-right (timecode) and bottom-left (beat label) regions vs a review-cut control frame
# consistency: README contents table exists; every path cited in FRICTIONAL.md / BUILD-PROMPT.md resolves (checker script in scratchpad)
```
Result: final master 149.5 s, 1920×1080, H.264 24 fps + AAC, 7,112,377 bytes. No burned-in timecode or beat labels. All cited paths resolve.

### Step 14 — name correction, rebuild, submission folder
```bash
# repo naming rule (read-only; working clone stays at b293224)
cd /c/info7375/info-7375-prompt-engineering-for-generative-ai && git fetch origin && git show origin/main:fall-2026/README.md   # "No IDs and no full names are stored here."
# list every match first, then replace the wrong full name -> "Prathamesh P" in text files; delete stale __pycache__
cd /c/info7375/week-01-video && grep -rnI "<wrong last name>" . && grep -rl "<wrong last name>" .
python3 - <<'PY'   # str.replace over the 10 matching text files; narration fingerprint re-checked (unchanged 8afc5b04...)
PY
rm -rf __pycache__
# rebuild B09 + review + final, then burn-in check
rm manim/B09.mp4
cd /c/info7375/brutalist.art && source .venv/Scripts/activate
export PYTHONUTF8=1 WEEK01_REEL_DIR=/c/info7375/week-01-video PATH="/c/Users/Prathamesh P/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"
./art run /c/info7375/week-01-video --height 1080 > /c/info7375/week-01-video/logs/art_run_2026-09-27_11.log 2>&1
./art final /c/info7375/week-01-video --height 1080 --out /c/info7375/week-01-video/final > /c/info7375/week-01-video/logs/art_final_2026-09-27_4.log 2>&1
cd /c/info7375/week-01-video && for t in 6.0 67.0 75.5 145.5 149.0; do ffmpeg -v error -y -ss $t -i final/week-01-expected-vs-observed.mp4 -frames:v 1 _qc/final-check/final_t$t.png; done
# git identity and credentials (read-only)
git config --global --show-origin user.name; git config --global --show-origin user.email
cmdkey.exe /list | grep -iE -B1 -A3 github
# clean submission folder (approved list, option a) and zip
# see the copy list in the submission step; zip written to C:\info7375\submission\ using the Canvas naming LastName_FirstName_INFO7375_Week01_Video.zip
```

### Step 15 — image redaction/regeneration, final sync and zip
```bash
source /c/info7375/brutalist.art/.venv/Scripts/activate && cd /c/info7375/week-01-video
# regenerate the burn-in composite from the current final master's frames (6.0 / 67.0 / 149.0 s)
python3 -c "from PIL import Image; ..."   # stack _qc/final-check/final_t{6.0,67.0,149.0}.png, half size -> _qc/final-check/final_B00_B04_B09.png
# locate the name line in each pre-fix B09 tile (ink rows grouped into text lines), then draw a labelled box over it only
python3 - <<'PY'   # PIL: ImageDraw.rectangle fill #3D3929 + EB Garamond label "name redacted — corrected to Prathamesh P, see FRICTIONAL.md Entry 17"
PY                 # targets: _qc/contact_sheet_B08_B09.png (2 tiles), _qc/manim-preview/sheet.png (1 tile); changed rows checked
# delete the old zip, rebuild the submission folder from the approved list, scan, check references
rm /c/info7375/submission/<old zip>
rm -rf /c/info7375/submission/week-01-video && mkdir -p ... && cp ...   # approved list + cited evidence; __pycache__ removed
grep -rliaE '<old middle name>|<last name>' /c/info7375/submission/week-01-video     # 0 files (binary included)
python3 - <<'PY'   # reference check: every cited reel path is in the folder, external, or a README-noted rebuild output
PY
# zip with Python zipfile (forward-slash entries, single week-01-video/ root), then testzip
python3 - <<'PY'   # zipfile.ZipFile(..., ZIP_DEFLATED, compresslevel=9); written using the Canvas naming LastName_FirstName_INFO7375_Week01_Video.zip
PY
```
