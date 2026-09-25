# SOURCES

**Swathi Baba Eswarappa** · INFO 7375 · Week 1 Explainer Video
Build date: **2026-09-23** · macOS 26.6.2, Apple Silicon (arm64)

---

## 1. What I made

| Artifact | Description |
|----------|-------------|
| `code/tokenize_probe.py` | tiktoken probe over `strawberry` / `banana` / `occurrence` in two encodings |
| `code/embedding_probe.py` | tokenizer-dependence test, spacing control, embedding-lookup illustration, frequency ladder |
| `scene.py` | all 11 Manim scenes, the `Beat` base class, the narration-pinned cue system (`at`/`pin`), the chip/ruler/cell components |
| `beat_sheet.json` | the narration script and visual plan (Brutalist schema) |
| `build.sh`, `build_mux.py`, `make_srt.py`, `qc_frames.py` | the build pipeline + frame-safety sweep |
| Narration **script** | written for this assignment; spoken by a synthetic voice (below) |
| Concept, structure, argument, boundary condition | mine |

## 2. What Claude Code (Opus 5) contributed

I used Claude Code throughout, as the AI policy permits. Specifically it:

- wrote the first drafts of `tokenize_probe.py`, `embedding_probe.py`, `scene.py`,
  `build_mux.py`, `make_srt.py`, and `build.sh`;
- drafted the beat-sheet narration in the register I specified, then trimmed four
  beats when the measured audio came in at 3:56 and I wanted headroom under the ceiling;
- diagnosed the two build failures logged in `FRICTIONAL.md` (the NumPy ABI break and
  the espeak-ng data path) and found the fixes;
- caught and fixed two layout defects by inspecting rendered frames (a clipped header, and
  colliding position labels in B08), and wrote `qc_frames.py` after **I** spotted a third in
  playback — a caption in B02 running off the right edge that its four-scene spot-check had
  missed. The sweep now covers all 11 scenes and runs as a build step — and when that sweep
  in turn missed B07's off-frame line, added the geometric `assert_in_frame()` beside it, plus
  `hold_until()` after I spotted the B10 sign-off appearing before it was spoken. Three of the
  four layout/timing defects in this build were found by me watching, not by the tooling.

**What Claude did not do:** it did not choose the concept, and it did not supply any of
the numbers. Every integer in the video comes from `tiktoken` executing locally. I have
verified the central claims by hand — see §5.

I am responsible for this submission and can explain any part of it.

## 3. Tools and licences

| Tool | Version | Licence | Role |
|------|---------|---------|------|
| [Brutalist (Film as Code)](https://github.com/nikbearbrown/brutalist.art) | commit `6a8380a` (2026-09-20) | see upstream repo — no `LICENSE` file present at root as of this commit | beat-sheet schema; `runtime/scripts/generate_audio_kokoro.py` used unmodified as the narration engine |
| [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) | weights `v1.0` | **Apache-2.0** | narration voice `am_michael` |
| [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) | 0.6.1 | MIT | ONNX runtime wrapper for Kokoro |
| [tiktoken](https://github.com/openai/tiktoken) | 0.14.0 | MIT | BPE tokenizer — the source of every token ID |
| [Manim Community](https://www.manim.community/) | v0.18.1 | MIT | visual engine |
| [FFmpeg](https://ffmpeg.org/) | 9.0.1 | LGPL-2.1+ | A/V mux and concat |
| [eSpeak NG](https://github.com/espeak-ng/espeak-ng) | 1.52.0 | GPL-3.0 | phonemizer backend for Kokoro |
| NumPy | 1.26.4 (system) / 2.5.3 (venv) | BSD-3-Clause | array maths |
| onnxruntime | 1.30.0 | MIT | Kokoro inference |

**Free pipeline only.** No paid generation, no API keys, no media account, no upload.
Total generation cost reported by the Kokoro engine: **$0.00**.

## 4. Third-party assets

**None.** No stock footage, no images, no music, no fonts beyond the system monospace
face (Menlo, bundled with macOS). No AI-generated video or imagery. Every frame is drawn
by `scene.py`.

The narration voice `am_michael` is a **Kokoro preset voice, not a human recording and
not my voice** — it is a synthetic voice from an Apache-2.0 model, disclosed here and
credited on the closing card of the video.

## 5. Verification — what I checked, and how

| Claim | How verified |
|-------|--------------|
| `strawberry` → `[496, 675, 15717]` in `cl100k_base` | `tiktoken` locally; round-trip `decode(ids) == word` asserted in the probe and printed `True` |
| the pieces are `str` / `aw` / `berry` | `enc.decode([i])` per id |
| `r` at char index `[2, 7, 8]`; per-token `[1, 0, 2]` | computed from the string and the token spans; sums to 3, the true count |
| `o200k_base` cuts it `st` / `raw` / `berry` = `[302, 1618, 19772]` | second encoding in the same probe run |
| `banana` is **one** token, id `88847` | `len(enc.encode("banana")) == 1` |
| spaced form is 10 tokens, id `436` ×3 at positions `[2, 7, 8]` | `embedding_probe.py` §B output |
| `berry` = 1 token `[15717]`; `zyzzyva` = 4 tokens `['zy','z','zy','va']` | `embedding_probe.py` §D output |
| runtime 3:58.12 and A/V lock | `ffprobe` on the master; per-beat deltas ≤ 0.02 s printed by `build_mux.py` |
| nothing runs off frame | `qc_frames.py --border 16 --step 8` decodes all 11 scenes to raw RGB; PASS |
| nothing sits outside the frame geometrically | `Beat.assert_in_frame()` runs at the end of every scene; all 11 pass |
| no two text elements overlap | `Beat.assert_no_text_overlap()` runs at the end of every scene; all 11 pass |
| content stays between the chrome rules | `Beat.assert_in_safe_area()`; flagged exactly B03 and B04, both fixed, all 11 now pass |
| the sign-off lands when spoken | the voice reaches the name at 15.86 s into B10; frame pulled from the muxed master at 3:55.0 shows the card already up |
| cues land on the words that justify them | `lock()` reports every beat's trailing hold; worst is 6.38 s, down from 22.25 s. B08 frames at 10.0 s (payoff absent) and 15.0 s (payoff present) confirm the reveal follows the voice |

**Not verified / constructed:** the 8-dim vectors in B05 are random (seed 7375) and
labelled **CONSTRUCTED** on screen. I make no claim about any real model's embedding values.

**No Claude transcript appears in the video.** I deliberately avoided showing one rather
than risk presenting an unverifiable screenshot — the claim is carried by tokenizer output
I can re-run on demand. The statement in B09 that "many current models answer strawberry
correctly now" is offered as a limitation of my own argument, not as measured evidence.

## 6. Course materials

Concept taken from **Chapter 1, Part 1** — "The unit is a token, not a word — and why that
breaks letter-counting prompts", one of the listed eligible concepts in the assignment brief.

**On `lessons/01-randomness-and-first-prompts/code/main.py`.** The brief says to run it and
use what it prints. I did run it (2026-09-23) rather than assume it was irrelevant — full
write-up with its actual output in **`code/chapter1_main_check.md`**. Summary:

- it prints `probabilities [0.0900, 0.2447, 0.6652]` and `counts {1: 268, 2: 630, 0: 102}`;
- it imports only `math`, `random`, `collections.Counter`, and a grep for
  `token|tiktoken|encode|bpe|char` returns **no matches** — there is no tokenization code in it;
- its numbers are the source for the **Part 2** concepts on the assignment's own list —
  `1000 × 0.6652409557748218 = 665.24` against an observed `630` at `seed=7` is verbatim
  the listed "Expected count (665.24) versus observed count (630)".

My concept is a **Part 1** tokenization topic, so that file has no number my claims could
rest on. Quoting `630` over a frame about token IDs would be a real number attached to an
unrelated claim. I generated the Part 1 equivalent with `tiktoken` instead and shipped the
probe scripts so the numbers are re-runnable, which is the standard the instruction is
actually asking for.

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
