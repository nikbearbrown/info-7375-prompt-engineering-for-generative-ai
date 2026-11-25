# REFERENCES and asset attribution

## Project sources (Aditya Hasija)
- `06-Narration-and-Storyboard.md` / `ProductLensAI_Narration_Storyboard.docx`: narration and storyboard, the primary source.
  Narration edited for length, tense and verified wording, and approved by Aditya on 2026-11-23 (see SCRIPT.md).
- ProductLens AI documentation package (`01-PRD.md`, `02-Architecture.md`, `03-Agent-Prompts.md`, `04-Evaluation.md`,
  `05-Delivery-and-Film.md`): product scope, workflow, prompt contracts, the evaluation design and the proposed thresholds
  shown in Scenes 06–10. Every doc is marked "proposed"; the film presents them as plans and proposed targets only.

## Implementation status (checked 2026-11-23)
- **No ProductLens AI application or repository exists yet.** Searched GitHub (AdityaHasija37) and this machine. The only
  ProductLens code is the portfolio card `productlens-feature.tsx`, which itself labels the workflow "Concept · planned workflow".
- So **every interface in the film is a concept**, labelled on screen ("Concept · planned, not built", "Concept UI ·
  illustrative", "Illustrative example · not a real run"). No screenshot of a working app is shown.
- Resources (model API access, token credits, research access, deployment) are shown as **Pending**, at Aditya's instruction.
- Evaluation numbers are **proposed targets**, labelled "Proposed targets · not observed results". No evaluation has been run.

## Claims about other tools (Scene 03), verified against each company's own pages on 2026-11-23
| Tool | Film says | Source |
|---|---|---|
| ChatGPT, Claude | General AI assistants that can help brainstorm and analyze ideas | Generic description from the script, no specific feature claim |
| Perplexity | "AI search engine"; "answers with cited sources" | Perplexity help center, "What is Perplexity" (perplexity.ai/help-center/en/articles/10352155-what-is-perplexity); Perplexity blog, "Getting started with Perplexity" (Oct 2024) |
| Productboard | "Product management platform"; "centralize feedback, align on priorities" | productboard.com homepage: "Centralize all product feedback in one place", "Align teams on the right priorities" |

Names only, no logos (trademarks belong to their owners; no affiliation implied).

## Illustrative content
- Scene 05: the sample idea is synthetic scenario S01 from `04-Evaluation.md`.
- Scene 06: the source cards show source *types* (not real documents), and the prompt contract is a condensed draft from `03-Agent-Prompts.md`.
- Scene 07: the flagged claim and its revision are the storyboard's illustrative example, not model output.

## Assets and tools
| Asset | Source | Licence |
|---|---|---|
| Remotion 4.0.486, @remotion/paths, @remotion/google-fonts | remotion.dev | Remotion licence (free for individuals) |
| React 18, TypeScript 5 | react.dev, typescriptlang.org | MIT, Apache-2.0 |
| Inter, JetBrains Mono fonts | Google Fonts | SIL Open Font License 1.1 |
| Narration voice: Kokoro-82M, voice `am_michael` (synthetic, local) | kokoro-onnx model files v1.0 | Apache-2.0 |
| Subtitle timing: faster-whisper `small.en` | github.com/SYSTRAN/faster-whisper | MIT |
| Music | None. No licensed or original track was available, so per the brief none is used. | — |

**The narration is a synthetic voice** reading Aditya's approved script in the first person, not a recording of Aditya.

## Who made what
- **Aditya Hasija:** the project, all documentation, the narration script and storyboard, the decisions (dark palette, course
  name, resources pending, script approval, and keeping the natural-pace runtime of 5:57 over the production brief's 4:45 target).
- **Claude Code (claude-opus-5-5):** the script review and edits (approved by Aditya), fact checks, the Remotion source, the
  scene designs, the narration audio pipeline, subtitles, QA and rendering.
