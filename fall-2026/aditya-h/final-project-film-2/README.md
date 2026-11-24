# ProductLens AI: project film

A documentary-style film for **ProductLens AI**, Aditya Hasija's project for *Prompt Engineering and Agentic AI*
(Northeastern University, 2026). Remotion + React + TypeScript, **1920 × 1080, 30 fps, 16:9**, about **5:57**.
It follows the required four parts in order: Executive summary → Introduction → Methods → Evaluation, then a closing.

> ProductLens AI is **not built yet**. Every interface is a labelled concept, resources are shown as pending, and every
> evaluation number is a labelled *proposed target*. See REFERENCES.md.

## Deliverables in this folder
| File | What it is |
|---|---|
| `out/productlens-project-film.mp4` | The rendered film |
| `out/productlens-project-film.srt` | Subtitles, timed to the real audio, worded exactly as the script |
| `SCRIPT.md` | The approved narration, scene by scene, with the edit log |
| `TIMELINE.md` | Scene-by-scene start, end, length and narration |
| `REFERENCES.md` | Sources, fact checks, implementation status, asset licences, who made what |
| `src/` | The Remotion source (one component per scene) |
| `public/audio/` | One narration track per scene |

## Preview and render
```bash
npm install
```
```bash
npm run preview
```
Opens Remotion Studio; pick **ProductLensFilm**.
```bash
npm run render
```
Writes `out/productlens-project-film.mp4`. Use `npx remotion still src/index.ts ProductLensFilm out/frame.png --frame=300` for a single frame.

## Change things
| To change | Edit |
|---|---|
| Colours, fonts, type scale, palette | `src/config/theme.ts` (`ACTIVE_THEME`: `"dark"` or `"brand"`) |
| Title, tagline, author, course, degree | `src/config/credits.ts` |
| Scene order, pause after each scene | `src/config/scenes.json` |
| Narration text | `src/narration/<scene>.txt`, then run the three audio steps below |
| A scene's visuals | `src/scenes/S01Problem.tsx` … `S12Closing.tsx` |
| Burn subtitles into the video | `SHOW_SUBTITLES` in `src/Film.tsx` |

## Narration audio (local and free)
Scene lengths follow the measured audio, and every animation is keyed to the spoken word (`at(scene, "phrase")`), so
changing narration re-syncs the film automatically. Uses the Kokoro voice already installed in `~/brutalist.art`.
```bash
~/brutalist.art/.venv/bin/python tools/tts.py
```
```bash
~/brutalist.art/.venv/bin/python tools/cues.py
```
```bash
~/brutalist.art/.venv/bin/python tools/make_srt.py && python3 tools/timeline.py
```
**To use your own recorded voice instead:** save one WAV per scene as `public/audio/<scene id>.wav` (ids in
`scenes.json`), then run `tools/tts.py --measure-only`, `tools/cues.py` and `tools/make_srt.py`.

## How it's built
- `src/config/timeline.ts`: the central timeline. Each scene lasts its narration plus a short pause.
- `src/components/`: reusable pieces (`SceneShell`, `RevealText`, `AgentCard`, `Connector`, `SourceCard`, `ClaimRow`,
  `DataTable`, honesty `Badge`s, `Subtitles`, the `at()` cue lookup).
- `tools/qa_stills.sh <scene> <fraction>`: renders a still of any scene for checking.

## QA done before the final render
All four sections are present and in order, with no implementation detail in the executive summary. Competitor wording
was checked against each company's own site. Stills were checked for every scene, plus a frame every 8 s of the full film,
for overflow, clipping and overlaps. Fixed along the way: a wrapped headline, an overflowing tool name and agent card, a crowded source column, a ghosted evaluator layer, an overlapping label, an unverified "blinded graders" claim, and labels below 24 px. Typecheck passes. Audio is 30 fps-synced
per scene, and subtitles come from the real audio timings. No placeholders remain, and evaluation targets are never shown
as results.
