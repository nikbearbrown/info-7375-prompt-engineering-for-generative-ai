#!/usr/bin/env bash
# Run inside Ubuntu (WSL), not in Windows PowerShell.
# Installs what the Brutalist toolkit needs (HOW-TO.md: python3 3.10+, ffmpeg,
# Node >= 20; Manim needs cairo/pango headers), clones the toolkit into the
# Linux home folder with Unix line endings, then runs the toolkit's own
# installer and readiness check. Free pipeline only: no API keys.
set -euo pipefail

sudo apt-get update
sudo apt-get install -y git curl ca-certificates python3 python3-venv python3-dev \
  build-essential pkg-config libcairo2-dev libpango1.0-dev ffmpeg fontconfig
# Libraries Remotion's headless Chrome needs (the bookends failed without them:
# "libnspr4.so: cannot open shared object file").
sudo apt-get install -y libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
  libgbm1 libxkbcommon0 libxrandr2 libxfixes3 libxcomposite1 libxdamage1 libpango-1.0-0 libcairo2 \
  libasound2t64

# Ubuntu's own nodejs package is older than 20, so use NodeSource's 22.x repo.
node_major=$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)
if [ "$node_major" -lt 20 ]; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

# Ubuntu blocks system-wide pip installs, so the toolkit gets its own venv.
python3 -m venv "$HOME/brutalist-venv"
# shellcheck disable=SC1091
source "$HOME/brutalist-venv/bin/activate"

cd "$HOME"
if [ ! -d brutalist.art ]; then
  git -c core.autocrlf=false clone https://github.com/nikbearbrown/brutalist.art.git
fi
cd brutalist.art
git log -1 --format='toolkit commit: %H (%cd)'

./setup --install
./setup

echo
echo "Versions for SOURCES.md:"
python3 --version; node --version; ffmpeg -version | head -1
python3 -c "import manim, manimpango; print('manim', manim.__version__, '/ manimpango', manimpango.__version__)"
pip show kokoro-onnx | grep -i '^version'
