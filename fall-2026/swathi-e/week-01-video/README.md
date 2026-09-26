# The Unit Is a Token, Not a Word

**Name:** Swathi Baba Eswarappa
**Course:** INFO 7375 — Prompt Engineering and Generative AI
**Assignment:** Week 1 Explainer Video (Chapter 1, Part 1)
**Runtime:** **3:58.12** (238.12 s) — inside the 2–4 minute window
**Video:** `BabaEswarappa_Swathi_INFO7375_Week01_Video.mp4` (1920×1080, 60 fps, 13.1 MB)
**Captions:** `token-not-word.srt`

---

## The concept

**The unit is a token, not a word — and why that breaks letter-counting prompts.**

## Why I picked it

Because it is the smallest idea in Chapter 1 that can be shown rather than asserted:
I can print the exact integers a tokenizer hands the model and point at the moment
the character positions stop existing — which turns a folk explanation ("the model
is bad at counting") into a mechanical one ("the letters were never in the input").

## What the video actually shows

| Beat | Claim on screen | Evidence |
|------|-----------------|----------|
| B01–B02 | the failed prompt, and the claim under test | no data on these cards |
| B03 | `strawberry` → `[496, 675, 15717]` (`str`/`aw`/`berry`) | `tiktoken`, `cl100k_base`, live |
| B04 | the `r`s live at char index `[2, 7, 8]`; per token that is `[1, 0, 2]` | computed from the encoding |
| B05 | the embedding step is `E[496] → row` — a row index, not a spelling | operation real; the 8-dim vectors are **labelled CONSTRUCTED** on screen (seed 7375) |
| B06 | `o200k_base` cuts the *same* word as `st`/`raw`/`berry` = `[302, 1618, 19772]` | the split belongs to the merge table, not the word |
| B06B | `berry` alone = **1** token `[15717]`; `zyzzyva` (7 chars) = **4** tokens | merges follow frequency — *why* the boundary lands where it does |
| B07 | `banana` → `[88847]` — **one** token, three `a`s, no boundary to blame | a token is an atom |
| B08 | spaced out → 10 tokens; id `436` appears **3×** at positions `[2, 7, 8]` | the exact indices tokenization destroyed, handed back |
| B09 | what this does **not** establish | see below |
| B10 | recap: 10 chars → 3 ints → 3 vectors | character positions dropped at step 1 |

Every integer spoken or drawn is read at render time out of `code/token_probe_output.json`
and `code/embedding_probe_output.json`, which are produced by the two probe scripts on
this machine. Nothing is hand-typed into the animation. Re-run the probes and the frames
change with them.

## The boundary — what this does NOT establish

I show that **BPE tokenization removes character positions at the input**. I do **not**
show that a language model can never count letters. Given a chain-of-thought scratchpad,
a code tool, or character-level input, a model can get the right answer — by routing
*around* the representation, not by reading inside a token. And many current models now
answer the strawberry question correctly because the example is widespread in training
data; **memorising an answer is not the same as seeing the letters.**

## Constructed vs. measured

The only constructed element in the video is the 8-dimensional embedding vector display
in B05 — real embedding tables are not public, so those numbers are random with seed 7375.
It carries a red **CONSTRUCTED · random vectors, seed=7375** badge on screen for its whole
duration. The *operation* it illustrates (fetch row `id` from a table) is real. No Claude
transcript is shown anywhere in the video, so none is fabricated.

---

On the chapter's reference script: I ran
`lessons/01-randomness-and-first-prompts/code/main.py` rather than assume it did not apply.
It is the Part 2 softmax/sampling implementation (`probabilities [0.0900, 0.2447, 0.6652]`,
`counts {1: 268, 2: 630, 0: 102}`) and contains no tokenization code — full check in
`code/chapter1_main_check.md`.

## Rebuild from this folder

**Prerequisites** (macOS, Apple Silicon; versions are the ones used):

```bash
brew install ffmpeg espeak-ng
pip install tiktoken==0.14.0 manim==0.18.1 numpy
```

Kokoro runs in its own venv because `kokoro-onnx` pins a different NumPy than the
system environment (see `FRICTIONAL.md`):

```bash
python3 -m venv ../.venv-kokoro && ../.venv-kokoro/bin/pip install kokoro-onnx soundfile
```

Brutalist toolkit and the Kokoro weights:

```bash
git clone https://github.com/nikbearbrown/brutalist.art ../brutalist.art
mkdir -p ../brutalist.art/runtime/models/kokoro && cd ../brutalist.art/runtime/models/kokoro
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

**Full rebuild** — probes → narration → scenes → mux:

```bash
./build.sh
```

**Re-mux only** (scenes and audio already rendered):

```bash
./build.sh --mux-only
```

Individual stages, if you want them one at a time:

```bash
python3 code/tokenize_probe.py
python3 code/embedding_probe.py
ART_HOME=../brutalist.art \
  PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/lib/libespeak-ng.dylib \
  ESPEAK_DATA_PATH=/opt/homebrew/share/espeak-ng-data \
  ../.venv-kokoro/bin/python ../brutalist.art/runtime/scripts/generate_audio_kokoro.py .
manim -qh --disable_caching scene.py B01_Hook
python3 build_mux.py --gap 0.30
python3 make_srt.py
```

## How the timing works

Audio is the master clock, per the Brutalist convention. `generate_audio_kokoro.py`
writes ground-truth durations to `mp3/timings.json` and back into `beat_sheet.json`
as `actual_duration_s`. `scene.py` reads that file and every scene ends with
`Beat.lock()`, which pads the scene to its own narration length. Result: each beat's
picture and audio agree to within **0.02 s**, with no stretching and no cumulative drift.

Within a beat, cues are pinned to the narration rather than played back to back:
`self.pin("Token four hundred thirty six")` holds the animation until just before that phrase
is spoken. `lock()` reports each beat's trailing hold so a scene that finishes early — and
therefore gives away its payoff before the voice gets there — is visible at build time.

## Folder contents

```
README.md                  this file
beat_sheet.json            11 beats, narration + visual plan + measured durations
scene.py                   Manim scene definitions (the visual engine)
build.sh                   one-command rebuild
build_mux.py               A/V pairing + concat
make_srt.py                caption generation
qc_frames.py               frame-safety sweep: fails if any scene puts content
                           in the outer border (added after a clipped caption)
code/tokenize_probe.py     tiktoken probe -> the real token IDs
code/embedding_probe.py    tokenizer-dependence + spacing control + lookup illustration
code/*_output.json/.txt    captured probe output (what the animation reads)
code/chapter1_main_check.md  I ran the chapter's main.py; what it prints, and why a
                             Part 2 sampling script has no number a Part 1 tokenization
                             claim can use
mp3/timings.json           Kokoro ground-truth durations (the master clock)
                           NOTE: the 11 .mp3 narration tracks are NOT committed —
                           this repo's .gitignore keeps generated audio out at any
                           depth. `./build.sh` regenerates them from beat_sheet.json.
token-not-word.srt         captions
BUILD-PROMPT.md            prompts and commands that rebuild this
SOURCES.md                 attribution and licences
FRICTIONAL.md              dated build log, including what broke
BabaEswarappa_Swathi_INFO7375_Week01_Video.mp4
```

## References

Cited on screen in the video, and listed here for the record. The distinction that
matters: the **source** is the artifact the information came from; my probe scripts are
only the *method* by which I read it.

### Primary sources — where the numbers actually come from

| # | what it supports | source |
|---|---|---|
| 1 | every token ID in `cl100k_base` (B03, B04, B06, B06B, B07, B08) | OpenAI, `cl100k_base.tiktoken` — the published BPE merge table. <https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken> · `sha256 223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7` · 100,277 tokens |
| 2 | the second encoding in B06 | OpenAI, `o200k_base.tiktoken`. <https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken> · `sha256 446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d` · 200,019 tokens |
| 3 | byte-pair encoding as a method (B02) | Sennrich, R., Haddow, B., & Birch, A. (2016). *Neural Machine Translation of Rare Words with Subword Units.* ACL. [arXiv:1508.07909](https://arxiv.org/abs/1508.07909) |
| 4 | a scratchpad lets a model reach answers it otherwise misses — shown in B09 as **not measured here** | Wei, J., et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models.* NeurIPS. [arXiv:2201.11903](https://arxiv.org/abs/2201.11903) |

**Verification of ref 1 and 2.** `tiktoken` downloads those files and checks them against
the sha256 recorded in `tiktoken_ext/openai_public.py`. I confirmed the cached copies on
this machine hash to `223921b7…` and `446a9538…`, matching the published values — so the
vocabulary behind every ID in the video is the real distributed artifact, not something
generated locally.

### Method — how I read those sources

| tool | version | role |
|---|---|---|
| [`openai/tiktoken`](https://github.com/openai/tiktoken) | 0.14.0 (MIT) | loads the merge tables above and performs the encoding |
| `code/tokenize_probe.py` | mine | reads out IDs, pieces, character spans; asserts `decode(encode(w)) == w` |
| `code/embedding_probe.py` | mine | tokenizer-dependence, spacing control, frequency ladder |

### Production

| tool | version | licence |
|---|---|---|
| [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) (voice `am_michael`) via [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) 0.6.1 | v1.0 weights | Apache-2.0 |
| [Manim Community](https://www.manim.community/) | 0.18.1 | MIT |
| [FFmpeg](https://ffmpeg.org/) | 9.0.1 | LGPL-2.1+ |
| [Brutalist (Film as Code)](https://github.com/nikbearbrown/brutalist.art) | commit `6a8380a` | see upstream |

### What is deliberately *not* claimed

I make no claim about any production model's tokenizer. `tiktoken` ships **OpenAI's**
encodings; Anthropic does not publish one. The mechanism shown — text → subword tokens →
integer IDs → embedding rows — is a property of BPE tokenization generally (ref 3). The
specific IDs belong to `cl100k_base` and to nothing else.
