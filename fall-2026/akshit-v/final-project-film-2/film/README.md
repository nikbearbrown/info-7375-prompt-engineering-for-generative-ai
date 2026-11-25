# SponsorScout: Final Project Film

**Akshit Verma** · INFO 7375 Prompt Engineering for Generative AI · the pitch film from October, rebuilt
in the four required parts, with the first piece of the project built and run.

| | |
|---|---|
| **Film** | `sponsorscout-final-project-film.mp4` · **4 min 5 s** (244.5 s) · 1920×1080 · 24 fps · H.264 + AAC · captions burned in (`captions.srt` sidecar) |
| **SHA-256** | `fd3ad7cf47bf45f1a067356f52b7e261c16a7d3d4a8c01cee882a88206c0020f` |
| **Narration** | a **synthetic voice** (Kokoro `am_michael`, free and local) reading my script. Not my recorded voice |

## The four parts

| Part | Beats | What it says |
|---|---|---|
| 1 · Executive summary | P1A–P1C | International students apply to sponsors with nothing open. SponsorScout gives each sponsor a verdict (apply, network, check by hand, skip) with the public record behind it, and keeps strong sponsors with nothing open as networking targets. It never contacts anyone. Why I care. |
| 2 · Introduction | P2A–P2B | MyVisaJobs, H1BGrader, Interstride, and the Reallocation Engine's scorer. The gap: none that I found turns a proven sponsor with nothing open into a networking target. |
| 3 · Methods | P3A–P3E | Public data; the three checks; the **board resolver** loop (built 2026-11-23); the human gate tied to a fingerprint; resources ($0, no keys). |
| 4 · Evaluation | P4A–P4D | **Coverage 16 → 50 of 123** (live run, 629 requests to three sites only). Five wrong-company boards refused; a name-match false negative; 5 empty boards; 67 with no board found; the console bug no test caught. The plan for judging verdicts (held-out set, pass/fail threshold, 14-day re-check) and what the sample can't show. |

## What changed since the pitch (2026-10-14)

- The pitch's "first piece", the board resolver, now exists and has run live (`../board-resolver/`).
  Coverage went from 16/123 to **50/123** after my G1 review.
- The film follows the new four-part brief instead of the old seven questions.
- The evaluation plan is concrete, and its pass line is set: at least 9 in 10 apply verdicts right on a held-out set (approved by me, 2026-11-23). The held-out set itself is still to be built.

## Files

| File | What |
|---|---|
| `sponsorscout-final-project-film.mp4` | the film |
| `make_sheet.py` → `beat_sheet.json` | narration and visual plan |
| `scenes.py` | every drawing (Manim), on the pitch film's kit |
| `FACTCHECK.md` | every claim → its source (30 rows) |
| `SHOTLIST.md`, `PROMPTS.md` | shot list; no generation prompts (nothing AI-generated in the picture) |
| `SOURCES.md` | sources, tools, licences, **who did what** |
| `captions.srt`, `captions.ass`, `mp3/words.json` | captions and the word clock |
| `_qc/` | gate log (`gates-2026-11-23.txt`), Gate V report, listening check |
| `_superseded/` | the failing gate reports (TYPECHECK ×2, Gate B). Superseded videos, logs and copies of toolkit files stay on my machine |
| `toolkit-changes/` | the one toolkit change (`PitchOutro` byline), as a diff |
| `../FRICTIONAL.md` | the log (Entries 1–4); the **In my words** parts are mine to write |

## Rebuild

Same pipeline as the pitch film's `BUILD-PROMPT.md`, with this folder joined at
`brutalist.art/youtube/brutalist/final-project-film-v2` (a junction; remove it with `rmdir`, never a
recursive delete):

```bash
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 ART_CHANNEL_TITLE=0
REEL=youtube/brutalist/final-project-film-v2
python $REEL/make_sheet.py
python runtime/scripts/generate_audio_kokoro.py $REEL && python $REEL/make_sheet.py && python runtime/scripts/align.py $REEL
python runtime/scripts/remotion_scenes.py $REEL
ART_BURNIN=0 ART_QC=1 ART_STRICT=1 bash runtime/scripts/run.sh $REEL --height 1080   # scenes at 4K, cut at 1080
./art final $REEL --height 1080
cp renders/sponsorscout-final-project-film.mp4 $REEL/sponsorscout-final-project-film-nocaptions.mp4
cd $REEL && python tools/make_captions.py
ffmpeg -i sponsorscout-final-project-film-nocaptions.mp4 -vf "subtitles=captions.ass:fontsdir=../../brutalist.art/runtime/fonts/Lato/static" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a copy sponsorscout-final-project-film.mp4
```

## Not done yet

- ~~My sign-off~~: `FACTCHECK.md` signed off 2026-11-23.
- The **In my words** sections of `../FRICTIONAL.md`.
