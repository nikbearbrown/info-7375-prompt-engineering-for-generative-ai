#!/usr/bin/env bash
# rebuild-film2.sh: rebuild CueGate film 2 (the project film) from this folder with one command.
#
#   ./rebuild-film2.sh                  builds in ./_rebuild (created fresh; must not already exist)
#   ./rebuild-film2.sh /some/new/dir    builds there instead
#
# What it does, in order:
#   1. checks the prerequisites and stops with a clear message naming anything missing
#   2. clones the Brutalist toolkit (github.com/nikbearbrown/brutalist.art) at commit 519fcbb
#   3. creates a Python virtual environment (inside WORKDIR, or a short temp folder if WORKDIR's path is too long
#      for espeak-ng) and puts it first on PATH
#   4. applies the two local patches in patches/ (setup-guard.patch, outro-handle.patch)
#   5. runs the toolkit's setup (bash setup --install), then restores one lockfile npm rewrites
#   6. copies beat_sheet.json, the film's scene, audio and caption code, its GATE P paperwork and the E1 base still
#      into the reel folder, and builds the E1 still (reel/make_e1.py)
#   7. assembles scenes.py from the pinned kit plus scenes_film.py (reel/build_scenes.py)
#   8. generates the Kokoro narration in two voices (the master clock), then adds the fixed pauses (reel/pad_audio.py)
#   9. renders the outro card, runs `art run` and `art final` (4K) with --out
#  10. writes the captions with speaker tags (reel/make_captions.py), runs every gate, and writes the reports into
#      WORKDIR/gates/
# Nothing is published or uploaded. Free and local; no API keys.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="${1:-$HERE/_rebuild}"
TOOLKIT_COMMIT="519fcbb96e9e1898d374c8794117cab494ffc5cb"
SLUG="cuegate-film2"

die() { echo "rebuild-film2.sh: $*" >&2; exit 1; }

# ---- 1. prerequisites (versions observed on the build machine, 2026-11-23) -------------
command -v git >/dev/null      || die "git is missing."
command -v curl >/dev/null     || die "curl is missing (setup downloads the Kokoro model with it)."
command -v python3 >/dev/null  || die "python3 is missing. Install Python 3.13 (built with 3.13.2)."
python3 -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 13) else 1)' \
  || die "python3 must be 3.13 (found $(python3 --version 2>&1)); the film was built with 3.13.2."
command -v node >/dev/null     || die "node is missing. Install Node 24 or newer (built with v24.21.0)."
[ "$(node -p 'process.versions.node.split(".")[0]')" -ge 24 ] \
  || die "node must be 24 or newer (found $(node --version)); built with v24.21.0."
command -v npm >/dev/null      || die "npm is missing (built with 11.19.0)."
command -v ffmpeg >/dev/null   || die "ffmpeg is missing: brew install ffmpeg (built with 9.0.1)."
command -v ffprobe >/dev/null  || die "ffprobe is missing: brew install ffmpeg (built with 9.0.1)."
command -v pkg-config >/dev/null || die "pkg-config is missing: brew install pkgconf (built with pkgconf 3.0.8). manim's pycairo needs it."
pkg-config --exists cairo      || die "cairo is missing: brew install cairo (built with cairo 1.18.4). manim's pycairo builds against it."
[ ! -e "$WORK" ] || die "$WORK already exists; pass a new folder or remove it."

mkdir -p "$WORK"
WORK="$(cd "$WORK" && pwd)"
ART="$WORK/brutalist.art"
REEL="$WORK/youtube/$SLUG"
echo "rebuild-film2.sh: building in $WORK"

# ---- 2. toolkit at the pinned commit -------------------------------------------------
git clone --quiet https://github.com/nikbearbrown/brutalist.art "$ART"
git -C "$ART" -c advice.detachedHead=false checkout --quiet "$TOOLKIT_COMMIT"

# ---- 3. virtual environment, first on PATH ---------------------------------------------
# espeak-ng (used by the Kokoro voices) keeps its data path in a fixed 160-byte buffer. If the venv's
# .../site-packages/espeakng_loader/espeak-ng-data path is longer, espeak silently falls back to a path baked in
# at build time and every narration line fails ("phontab: No such file or directory"). So the venv goes in
# WORKDIR only when that path stays under 150 characters; otherwise it goes in a short temporary folder.
VENV="$WORK/.venv"
if [ $(( ${#VENV} + 61 )) -gt 150 ]; then
  VENV="$(mktemp -d /tmp/cgv.XXXXXX)/venv"
  echo "rebuild-film2.sh: WORKDIR path is long; creating the virtual environment at $VENV so espeak-ng can find its data"
fi
python3 -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# ---- 4. the two local patches (never committed to the toolkit) -------------------------
git -C "$ART" apply --check "$HERE/patches/setup-guard.patch" "$HERE/patches/outro-handle.patch"
git -C "$ART" apply "$HERE/patches/setup-guard.patch" "$HERE/patches/outro-handle.patch"

# ---- 5. toolkit setup ---------------------------------------------------------------
# setup exits 1 while any feature is blocked; "Manim equation beats" stays blocked without LaTeX,
# which this film does not use (it has no equation beats). The checks below decide readiness instead.
(cd "$ART" && bash setup --install) || true
# npm install rewrites runtime/remotion/package-lock.json: at 519fcbb the lockfile is out of step with
# package.json (its root dependency list lacks @remotion/zod-types and zod). No resolved version changes,
# and `npm ci` refuses to install while the two disagree, so the committed lockfile is restored.
git -C "$ART" checkout -- runtime/remotion/package-lock.json
python3 -c "import kokoro_onnx, manim, faster_whisper, PIL" || die "Python packages failed to install (see setup output above)."
python3 -c "import espeakng_loader, sys; p = espeakng_loader.get_data_path(); sys.exit(0 if len(p) <= 150 else 1)" \
  || die "espeak-ng data path is longer than 150 characters; run rebuild-film2.sh with a shorter WORKDIR."
[ -f "$ART/runtime/models/kokoro/kokoro-v1.0.onnx" ] && [ -f "$ART/runtime/models/kokoro/voices-v1.0.bin" ] || die "Kokoro model files missing."
[ -d "$ART/runtime/remotion/node_modules" ] || die "Remotion node modules missing."
git -C "$ART" diff --stat

# ---- 6. reel folder ------------------------------------------------------------------
mkdir -p "$REEL/media"
cp "$HERE/beat_sheet.json" "$REEL/beat_sheet.json"
for f in scenes_film.py build_scenes.py pad_audio.py make_captions.py make_e1.py FACTCHECK.md SHOTLIST.md PROMPTS.md PEDAGOGY.md; do
  cp "$HERE/reel/$f" "$REEL/$f"
done
cp "$HERE/reel/media/B01.base.png" "$REEL/media/"
python3 "$REEL/make_e1.py"
cmp -s "$REEL/media/B01.png" "$HERE/reel/media/B01.png" || echo "rebuild-film2.sh: note: rebuilt media/B01.png differs byte-wise from the submitted one (PNG encoder); compare by eye"

# ---- 7. scenes.py = pinned kit + this film's code ------------------------------------
python3 "$REEL/build_scenes.py" "$ART"

# ---- 8. narration (the master clock), then the fixed pauses ----------------------------
(cd "$ART" && python3 runtime/scripts/generate_audio_kokoro.py "$REEL")
(cd "$REEL" && python3 pad_audio.py)

# ---- 9. render -------------------------------------------------------------------------
(cd "$ART" && python3 runtime/scripts/remotion_scenes.py "$REEL" --only BOUT --force)
(cd "$WORK" && ./brutalist.art/art run "youtube/$SLUG" --height 2160)
(cd "$WORK" && ./brutalist.art/art final "youtube/$SLUG" --height 2160 --out "$WORK/out")
MASTER="$(ls "$WORK/out"/*.mp4 | head -1)"
[ -f "$MASTER" ] || die "no master mp4 in $WORK/out"
[ -f "${MASTER%.mp4}.verified.json" ] || die "art final wrote no verified.json, so the render-integrity check (compile.py verify_output) did not pass"

# ---- 10. captions and gates --------------------------------------------------------------
G="$WORK/gates"; mkdir -p "$G"
S="$ART/runtime/scripts"; Q="$ART/runtime/qc"
gate() { local name="$1"; shift; local rc=0; "$@" > "$G/$name.log" 2>&1 || rc=$?; echo "$name exit=$rc" | tee -a "$G/summary.txt"; }
gate bookend    python3 "$S/bookend_check.py" "$REEL"
gate factcheck  python3 "$Q/factcheck_check.py" "$REEL"
gate beat_lint  python3 "$Q/beat_lint.py" "$REEL/beat_sheet.json"
gate master     python3 "$S/master_check.py" "$REEL" --mp4 "$MASTER"
gate loudness   python3 "$S/loudness_check.py" "$REEL" --mp4 "$MASTER"
gate sharpness  python3 "$S/sharpness_check.py" "$REEL"
gate pace       python3 "$ART/skills/make/duration-planner/scripts/pace_check.py" "$REEL"
# captions: the film's own make_captions.py (every narration word, a speaker tag on every cue, at most two
# 42-character lines per cue). The toolkit's stage_publish.py keeps only the first three lines of each beat.
(cd "$REEL" && python3 make_captions.py) > "$G/make_captions.log" 2>&1
cp "$REEL/$SLUG.srt" "$WORK/out/"
gate srt        python3 "$S/srt_check.py" "$REEL" --srt "$REEL/$SLUG.srt"
for f in TYPECHECK.md MASTERCHECK.md LOUDNESS.md SHARPNESS.md SRTCHECK.md layout_audit.md build-state.json _qc/REPORT.md _qc/contact_sheet.png qc-sheet.png; do
  [ -f "$REEL/$f" ] && cp "$REEL/$f" "$G/$(echo "$f" | tr '/' '_')"
done
cp "${MASTER%.mp4}.verified.json" "$G/"
echo "rebuild-film2.sh: done. Film: $MASTER"
echo "rebuild-film2.sh: gate exits in $G/summary.txt"
