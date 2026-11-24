#!/usr/bin/env bash
# Assemble scenes.py = show-tell iso_kit + approved original props + recorded first-run output + this film's scenes.
# Gate A copies only scenes.py, so the kit is pasted in, never imported (show-tell SKILL.md).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
KIT="${ART_HOME:-$HERE/../../Brutalist}/skills/make/show-tell/templates"
# the recorded first-run output, typeset by B06–B09 (see embed_recorded.py; $RESULTS overrides the newest dated folder)
python3 "$HERE/embed_recorded.py" > "$HERE/recorded_block.py"
cat "$KIT/iso_kit.py" "$KIT/iso_originals_25.py" "$HERE/recorded_block.py" "$HERE/scenes_body.py" > "$HERE/scenes.py"
echo "scenes.py: $(grep -c '^class B' "$HERE/scenes.py") scenes"
