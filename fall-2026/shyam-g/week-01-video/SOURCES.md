# Sources, contributions and licences

## Actual authorship
- User: assignment specification, concept, metadata placeholders and desired speaking style; requested autonomous execution.
- Codex: workspace setup, measurement script, narration, beat sheet, custom Manim diagrams, build/packaging scripts, documents and checks. The user has not reviewed these materials in this session.
- Claude Code: **no generated submission content**. Its attempted run failed with an expired OAuth session. Installed CLI and prepared prompt are not creative contributions by Claude.
- Kokoro: synthetic local narration with the am_onyx preset. No voice cloning, real-person impersonation, paid narration service or API key.

## Scientific and assignment sources
- User-supplied Week 1 assignment text and follow-up prompt, supplied in this conversation. At build time the course repository was unavailable. It was supplied before publication: the relevant Chapter 1 sections and written policy were read, and the reference main.py was run. See evidence/course-review.md and course-example.json. The policy video was not watched.
- [OpenAI tiktoken](https://github.com/openai/tiktoken), especially README's reversible/lossless BPE description and the installed implementation. Exact outputs were independently executed in `measure_tokens.py` using version 0.14.0. Two encodings, six input combinations. Word spellings and counts are not synthetic model responses.
- [Embedding lookup documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.Embedding.html): integer indices select rows of an embedding table. Our graphic is schematic, omits architectural details such as position handling, and does not measure any trained embedding.
- `evidence/tokenization.json`, generated locally on 2026-09-27T18:40:55.221980+00:00, is the numeric source for every token card. The integer labels in scene.py are loaded from this file. Output code views are typeset reconstructions of verified Python expressions, not live screen recordings.

## Software and assets
| Resource | Use | Licence / attribution |
|---|---|---|
| [Brutalist](https://github.com/nikbearbrown/brutalist.art) | Audio-first approach; actual audio-helper module and model paths | Nik Bear Brown; baseline commit cd4bf20904be4e7d63babd9622b17963c2361b27. No root toolkit LICENSE was found in this checkout; no blanket redistribution licence is asserted. Toolkit source is not bundled. |
| [tiktoken](https://github.com/openai/tiktoken/blob/main/LICENSE) | Measured tokenization | MIT, OpenAI / Shantanu Jain; licence copied from installed package into licenses/. |
| [Manim Community](https://github.com/ManimCommunity/manim/blob/main/LICENSE) | Animated vector scenes | MIT; installed licence copied into licenses/. |
| [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx/blob/main/LICENSE) | Local TTS inference | MIT; installed licence copied into licenses/. |
| [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) | Model and preset voice | Model card identifies Apache-2.0. ONNX model and voice bundle obtained from the release linked by Brutalist. Model binaries are not redistributed in this ZIP. |
| [FFmpeg](https://ffmpeg.org/legal.html) | Encode, mux, decode, probe | Local ffmpeg -L identifies this Gyan build as GPL v3 or later. Binaries are not bundled; FFprobe is supplied by Remotion's compositor dependency. |
| [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) | Local FFmpeg binary distribution | Wrapper and bundled binary have distinct licences; this submission does not redistribute the executable. |
| Lato Regular | All on-screen text | Copyright 2010–2014 tyPoland Łukasz Dziedzic; SIL Open Font License 1.1. Font and original OFL notice included under assets/fonts/. |
| Original shapes and diagrams | Token cards, arrows, labels and vector illustrations | Authored by Codex for this submission; no third-party imagery, music or logos. Numerical vectors are explicitly constructed illustrations. |

“Dunkin” identifies the requested informal speaking style only. No affiliation, sponsorship, trademark licence or branded asset is claimed.

## Installed versions
| Package | Version |
|---|---|
| tiktoken | 0.14.0 |
| kokoro-onnx | 0.6.1 |
| manim | 0.18.1 |
| numpy | 2.5.3 |
| Pillow | 10.4.0 |
| imageio-ffmpeg | 0.6.0 |

Full dependency versions are in evidence/environment-freeze.txt. No paid generation, external model answer collection, web video or private transcript is included.
