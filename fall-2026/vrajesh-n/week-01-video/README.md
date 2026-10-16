# A Slogan Is a Division

**Student:** Vrajesh Nasit
**Course:** INFO 7375 — Prompt Engineering for Generative AI
**Week:** 1 · **Lesson:** `lessons/01-randomness-and-first-prompts/`
**Date:** 2026-09-26

---

## The concept

**A training-scale slogan restated as a division with a hidden assumption.**
(Chapter 1, Part 1 — "Scale, in units you can check".)

**Why I chose it, in one sentence:** it is the only concept in Chapter 1 where the
deliverable *is* auditing a number, which is what the course is actually about — and
because the answer visibly moves by more than fourteen hundred years on an input that
nobody in the slogan ever states.

## What the video shows

The claim "it would take a person thousands of years to read GPT-3's training data" is
not a measurement. It is a division with three inputs, and only two of them are ever
said out loud:

```
300e9 tokens x 0.75 words/token = 225e9 words

        225e9 words
------------------------------  =  1,711.2 years
250 words/min x 525,960 min/yr
```

That third input — the reading rate — is the hidden one. Sweep it across the four rates
the course's own script uses and the answer moves:

| Reading rate | Years to read |
|---|---:|
| 150 wpm | 2,851.9 |
| 200 wpm | 2,138.9 |
| 250 wpm | 1,711.2 |
| 300 wpm | 1,426.0 |

**Spread: 1,425.9 years, on an assumption nobody wrote down.**

The film then applies the same move to the compute slogan: GPT-3's reported 3.14e23 FLOPs
is about 9,950,060 years at a billion operations per second, whereas the commonly heard
"over 100 million years" needs 3.16e24 FLOPs — roughly **10x** GPT-3, a different claim
about a different model. Both sentences can be true. They are not the same sentence.

## What this does NOT establish

Stated on screen in B06, because every concept in this chapter has a boundary:

> This does not establish that the comparison is wrong, or that the slogan should not be
> used. Only that it has an input nobody stated.

Every version of the comparison still says the same true thing — *more text than a person
could read in many lifetimes*. What the sweep establishes is narrower: the headline number
carries a hidden parameter, so until someone states the reading rate you cannot check the
figure you were handed. And none of it is evidence about whether anything the model
*writes* is true.

## Runtime

**2:27 (146.85 s)** — measured Kokoro narration, which is the pipeline's master clock.
Inside the assignment's 2–4 minute window. My pre-audio estimate was 202 s; the real audio
came in shorter and I did **not** pad it to reach a number.

4K (3840x2160), 30 fps, h264 + AAC.

## Gate status

| Gate | Result |
|---|---|
| GATE T — type-lock (`type_check.py`) | **PASS** — 9 beats, 0 FAILs (`TYPECHECK.md`) |
| gate-v — visual (`final_frame_check.py`) | 0 BLOCKER, 10 MAJOR, all one class (`underfill`) |

The 10 MAJORs are shipped deliberately, not suppressed. They arise from a contradiction
between three of the toolkit's own rules — a 12-word cap per card, a 55% ink-coverage
floor, and a design document prescribing 15–35% coverage — which cannot all hold at once.
I inspected the flagged frames by eye and judged them correctly composed. The full
reasoning, what I fixed instead, and what I deliberately did not change is in
[`_qc/QC-NOTE.md`](_qc/QC-NOTE.md) and entry 4 of [`FRICTIONAL.md`](FRICTIONAL.md).

`./art final` therefore refuses this reel. The master was assembled from the identical
conformed clips in `clips/` that `./art final` would have used — no slates, no review
markers, no beat labels, no burned-in timecode.

## Honesty notes

- **Every number on screen is executed, not typed.** `build_beats.py` runs
  `course/research/llm_scale.py` at build time and writes whatever it prints into
  `beat_sheet.json`, keeping a verbatim copy of its stdout under
  `metadata.evidence.recorded_output`. The film cannot silently disagree with its source.
- **No Claude transcript appears in this video** — real or reconstructed. The Claude-style
  composer frames in B00 and B07 render text I wrote; they are a title device, not a claim
  that a model was asked or answered anything.
- **No generated imagery, no stock, no archival media.** See `PROMPTS.md`.
- **Nothing was published.** The toolkit has no uploader by design; the master stays here.
- Cost: **$0.00**. Kokoro narration is local; no API key was used at any point.

## How to rebuild this video from this folder

Full detail, including the five fresh-clone failures and the one-line Windows patch, is in
[`BUILD-PROMPT.md`](BUILD-PROMPT.md). The short version:

```bash
# 1. beat sheet, generated from executed evidence
python build_beats.py --course ../../.. --toolkit /path/to/brutalist.art

# 2. narration — this sets the clock
python3 /path/to/brutalist.art/runtime/scripts/generate_audio_kokoro.py .

# 3. render the scenes (1920x1080 comps at --scale=2 => true 4K)
python3 /path/to/brutalist.art/runtime/scripts/remotion_scenes.py .

# 4. review cut, then clean master
cd /path/to/brutalist.art
./art run   "<this folder>"
./art final "<this folder>"
```

## Files

| File | What it is |
|---|---|
| `week-01-scale-slogan.mp4` | The rendered video |
| `beat_sheet.json` | Reviewed narration + visual plan, with the executed evidence embedded |
| `build_beats.py` | Generates the beat sheet from `llm_scale.py` output; asserts its own arithmetic |
| `BUILD-PROMPT.md` | Prompts and commands that rebuild it |
| `SOURCES.md` | What I used, what I made, what Claude contributed, licences |
| `FACTCHECK.md` | One row per on-screen claim, with verification status |
| `FRICTIONAL.md` | Dated log of what broke and what I did |
| `SHOTLIST.md` | Per-beat work order with measured durations |
| `PROMPTS.md` | Generation prompts (there are none — by design) |
| `mp3/` | Per-beat Kokoro narration + `timings.json` |
| `media/` | Per-beat Remotion renders |
| `_qc/` | Sampled frames and the visual QC report |

## Beats

| # | Act | Component | Measured |
|---|---|---|---|
| B00 | ASK | `ClaudeComposerAsk` | 11.95s |
| B01 | BLUF | `BrutalistHesitantWriter` | 10.71s |
| B02 | EVIDENCE | `FormACard` | 19.84s |
| B03 | MECHANISM | `TypesetMath` | 17.54s |
| B04 | MECHANISM | `ExecutedData` | 25.55s |
| B05 | MECHANISM | `FormACard` | 21.65s |
| B06 | LIMIT | `FormACard` (dark) | 22.63s |
| B07 | HANDOFF | `ClaudeComposerAsk` | 10.62s |
| B08 | OUTRO | `FormACard` | 6.36s |

No slates, no request cards, no human media — nothing in this film needed a photograph,
so under the toolkit's `nopunt` doctrine there is no legitimate HOLD and every beat animates.
