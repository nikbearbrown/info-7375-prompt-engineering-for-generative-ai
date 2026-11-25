#!/bin/sh
# tools/qa_stills.sh <scene_id> <fraction> [<fraction> ...]: renders stills of one scene at fractions of its length
# into out/qa/, using the scene's real start frame in the full film. Requires node.
cd "$(dirname "$0")/.."
ID="$1"; shift
mkdir -p out/qa
for f in "$@"; do
  FR=$(node -e "
    const s=require('./src/config/scenes.json'), d=require('./src/config/durations.json');
    let t=0; for (const x of s){ const n=Math.ceil(((d[x.id]??x.fallbackSeconds)+(x.padSeconds??0.6))*30); if(x.id==='$ID'){console.log(t+Math.floor(n*$f)); process.exit(0)} t+=n }")
  npx remotion still src/index.ts ProductLensFilm "out/qa/${ID}_$f.png" --frame=$FR --log=error && echo "out/qa/${ID}_$f.png (frame $FR)"
done
