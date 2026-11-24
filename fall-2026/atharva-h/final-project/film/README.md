# The demo film

| | |
|---|---|
| **File** | `atharva-sponsorsql-final.mp4` (not in GitHub; MP4s are kept out of the repository) |
| **SHA-256** | `1112de3c041398fc540cc719420a37ea24813b400cb40b37faf25a40d87e143e` |
| **Length** | 3 min 54 s (233.8 s), under the four-minute target and the brief's five-minute limit |
| **Format** | 1920×1080, H.264 video, AAC audio, 10.9 MB |
| **Link** | *To be added by the owner after uploading (for example, an unlisted video or a shared drive link). Posting publicly is the owner's decision.* |
| **Built** | 2026-11-23 (second version, after the owner's script edits), with the local Brutalist toolkit (Manim, Remotion, Kokoro narration). No paid services. |

## What it shows, in the order the course asks for

1. **Executive summary** (B00–B01): what SponsorSQL is and why it matters, with H-1B defined.
2. **Introduction** (B02): existing tools (MyVisaJobs, an H-1B salary explorer, the owner's ChatGPT test), and what SponsorSQL adds.
3. **Methods** (B03–B07):
   - the data and how it's loaded
   - the agent loop and its budget
   - the tool and its permission policy, with real output of refused queries
   - **a real run and the human gate**
   - the resources used
4. **Evaluation** (B08–B11):
   - the frozen question sets and answer keys
   - 4/10, then 9/10, then held-out 5/5
   - the ten deliberate failures and the controlled failure
   - the limits the independent review left open
5. Outro (B12).

## Honesty notes

- **Output on screen is real.** Every number and output line comes from the saved evidence in this project (source per claim: [FACTCHECK.md](FACTCHECK.md)), re-typeset for legibility and labelled on screen as real output. The B06 run is from 2026-11-23 (`../evidence/gate-view-D2-2026-11-23.txt`).
- **The model's SQL** shown or scored was a real Claude reply from 2026-11-21, replayed. No live CLI call is shown or claimed.
- **The gate prompt** is shown as the text the interactive mode prints. No approval by the owner is shown or claimed.
- **The narration** is a synthetic voice (Kokoro `am_onyx`) reading a first-person script. Claude drafted it; the owner reviewed it and directed the edits in the second version. The closing line credits "Written by Atharva Hambir with Claude" (the owner's wording). The synthetic voice is disclosed here, not in the narration, at the owner's choice.
- **B11 says "I've reviewed it since"** about contract v2. That is the owner's own statement (2026-11-23), not yet recorded elsewhere in the project. Until the owner records the review, `gates.md` still says v2 was scored before owner review.
- **The decision** (ship, narrow or defer) is stated as the owner's open sign-off. The film doesn't make it.

## Quality checks run

- Every Brutalist gate passed. The final GATE V report shows 0 BLOCKER and 0 MAJOR across 26 sampled frames ([GATE-V-REPORT.md](GATE-V-REPORT.md)). The build log is [build-run.log](build-run.log).
- The final frame of every beat was inspected by eye. Five content and timing defects the gates didn't catch were fixed before the final export:
  - events that ended after the narration did
  - two loop arrows starting inside box borders
  - an unreadably small caption
  - a check mark overlapping text
  - a late check mark
- **Second version (same day):** the owner edited the script (B00, B01, B05, B08, B09, B11, B12). All twelve scenes were re-rendered and every gate re-run until clean (GATE V 0 BLOCKER and 0 MAJOR). Three problems were found and fixed along the way:
  - the outro looked empty at its midpoint (the gates flagged this)
  - B09's 5/5 bar appeared only half a second before the beat ended
  - word spaces were missing in small text across the film (for example "invisibletabs"), so all small text is now rendered at four times the size and scaled down
- **Final full pass (same day):** every beat checked at four points in time. The film's sound was checked for gaps (none) and clipping (none). The time each cue phrase is spoken was measured by re-running the same local voice on the script, and every visual lands within about a second of its words. Two more fixes came out of this pass:
  - B05: the "SQL query" definition had been replaced after about two seconds. It now stays for the whole beat, and the permission-policy definition is a card in the middle of the screen until the real output appears.
  - B08: "counted the right answer straight from the file" overstated it; the key scripts count from the database the loader builds from the checked file. It now says "from the data".
- **Owner's last edit:** the owner removed "never just because the model says it's done" from B04: the spoken sentence, the on-screen chip and the fact-check row. B04 was re-rendered and every gate re-run (clean), its cue timing re-measured, and the film re-exported.
- The Brutalist toolkit's files were compared before and after each build: unchanged.

## Rebuild

From the `brutalist.art` checkout with its Python 3.12 virtual environment active, put `beat_sheet.json`, `scenes.py`, `FACTCHECK.md`, `SHOTLIST.md` and `PROMPTS.md` in a reel folder, then run:

```bash
python3 runtime/scripts/generate_audio_kokoro.py <reel>
python3 runtime/scripts/remotion_scenes.py <reel> --only B01 --force
./art run <reel>
./art final <reel> --height 1080 --out <reel>
```
