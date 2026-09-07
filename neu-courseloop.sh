#!/usr/bin/env bash
# Persistent local Liam film queue. Default: run continuously.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${NEU_PYTHON:-python3}" "$HERE/scripts/neu_courseloop.py" --root "$HERE" "$@"
