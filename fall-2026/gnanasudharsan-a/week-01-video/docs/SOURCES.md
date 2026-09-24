# SOURCES — claude-tom-river-moves-the-bank

**"River Moves the Bank."** · INFO 7375 Prompt Engineering for Generative AI ·
Chapter 1, Part 1 · 3:51 · built 2026-09-22, rebuilt the same day (see §7).

---

## 1. The source of record

| | |
|---|---|
| Text | `chapters/01-randomness-and-first-prompts.md`, § *Inside one prediction step* |
| Repository | `info-7375-prompt-engineering-for-generative-ai`, commit `a0d8a1e` |
| What it gave | One clause, quoted verbatim on B07: *"the vector for `bank` after `river` ends up somewhere different from the vector for `bank` after `savings`"* — plus the verb the episode is built on, **revise** |
| What it did **not** give | Any number. No vectors, no scores, no weights, no dimension count. The chapter states the claim and moves on |

Cited on screen once, small, under the B07 figure:
`Source: chapters/01-randomness-and-first-prompts.md`

**Referenced but not relied on:** Vaswani et al., *Attention Is All You Need*,
arXiv:1706.03762 (2017) — named by the chapter as the origin of the transformer.
No claim in this script rests on that paper, so it is not narrated. Recorded
here for provenance only.

---

## 2. The numbers — author's, not anyone's

**Every number in this video was invented by the author for legibility.** None
is measured from a model; none is reproduced from a publication. This is stated
four times in the film itself: the persistent `CONSTRUCTED EXAMPLE` stamp on
B03–B07 (every beat that shows vector math), the B03 ledger headed *EVERY
NUMBER HERE IS INVENTED*, the last line of the B08 boundary card — *no number
in this video is measured* — and the B09 caption *1 head · 2 dimensions ·
numbers I chose*.

Constructed 2-D toy: `the (1,1)` `river (0,3)` `savings (3,0)` `bank (2,2)`,
with `W_Q = W_K = W_V = I`, one head, one layer.

Internal consistency is verified, not asserted: `verify_numbers.py` in this
folder re-derives every on-screen figure from those four embeddings, evaluates
the arithmetic strings B04 prints, and asserts the softmax weights total exactly
1.000. Full claim-by-claim table in `FACTCHECK.md`.

---

## 3. Tools — all local, all free

| Tool | Version / id | What it did | Cost |
|---|---|---|---|
| **Kokoro TTS** (local ONNX) | `voices-v1.0.bin`, voice `am_michael` | All 13 narration tracks. Runs offline, no account | **$0.00** |
| **Remotion** | `runtime/remotion`, via `runtime/scripts/remotion_scenes.py` | All 13 beats rendered deterministically at 3840×2160 | $0.00 |
| **ffmpeg / ffprobe** | system | Conform, mux, QC frame extraction, decode verification | $0.00 |
| **brutalist.art toolkit** | commit `ba2d0e0` | Beat-sheet pipeline, Gates F/L/SHAPE/V, `./art run`, `./art final` | $0.00 |
| **Pillow + NumPy** | in `.venv` | Title-safe bleed check, ink-mask decomposition during QC | $0.00 |
| **Claude Opus 5** (Claude Code) | — | See §4 | — |

**No paid API was called. No key was used. Higgsfield was never invoked** — the
toolkit's optional AI-video path stayed off, and the free path ran silently, as
designed for the Fellow Tier.

---

## 4. What Claude contributed, and what the author did

Honest split, because the assignment asks for one.

**Claude (Claude Opus 5, via Claude Code) did:**

- Searched the scene library (Gate L) and reported the miss.
- Proposed the act structure, the beat timings, and the narration drafts.
- Designed the toy embeddings against constraints the author set, and wrote the
  verification script that checks them.
- Wrote all eight `Ch1AttnStaticRow … Ch1AttnMultiHead` React/Remotion
  components, registered them in `Root.tsx`, and ran the build.
- Performed the visual QC pass — extracted frames, read them, diagnosed six
  defects, fixed the scene source, and re-rendered until Gate V was clean.
- Wrote this file and the other paperwork.

**The author did:**

- Chose the topic and the pedagogical constraints that shaped everything: show
  the mechanism rather than assert it; use a constructed example and label it;
  name the boundary. Those three rules are why the film has a B03 and a B08 at
  all.
- Set the 2–4 minute envelope and the Chapter 1 scope.
- Accepted the identity-matrix simplification after it was flagged as a
  trade-off with a named cost (see below).
- Reviewed and accepted the output.

**Flagged to the author and accepted, not hidden:** `W_Q = W_K = W_V = I`
reduces attention to raw embedding similarity, which risks teaching that
attention *is* similarity. It buys checkable arithmetic. The mitigation is two
explicit on-screen statements (the B03 ledger and the first row of B08's DOES
NOT ESTABLISH column) plus the full-frame B09 boundary card, rather than
silence. A version with real 2×2 learned
projections would need roughly 20 more seconds.

**Not done by Claude, by design:** nothing was published, uploaded, or posted.

---

## 5. Assets and licences

| Asset | Origin | Licence / status |
|---|---|---|
| EB Garamond (serif) | bundled in `runtime/fonts` | SIL Open Font License 1.1 |
| Claude palette tokens | `runtime/remotion/src/tokens/claude.ts` | In-repo. Fidelity palette replicating the Claude desktop app; used for a course explainer, not a product |
| `Ch1Chrome` primitives | `runtime/remotion/src/scenes/Ch1Chrome.tsx` | In-repo, written for the sibling chapter-1 reels; reused here, extended additively |
| `ClaudeComposerAsk`, `BrutalistHesitantWriter`, `ClaudeVerdictArtifact`, `ClaudeTitleOutro` | brutalist.art | In-repo, reused unmodified |
| Narration audio | generated locally by Kokoro | Model weights per their upstream licence; the generated audio is the author's |
| All 13 beat videos | generated by Remotion from source in this repo | Author's |

**No third-party images, stock footage, archive material, pantry stills, or
AI-generated media of any kind appear in this video.** Every frame is a
deterministic render from code in this repository — same input, same output,
every time.

---

## 6. The rebuild pass

The first cut ran 3:12 and carried the multi-head limitation as one row inside
B08's five-row ledger. Two brief requirements were therefore unmet: the
3:30–4:00 runtime window, and a **concluding scene** stating the boundary
explicitly. The rebuild added `Ch1AttnMultiHead` (B09) — which states the
sentence full-frame and verbatim, and reads it aloud — and lengthened B06 and
B08 so the honest magnitude of the shift and the scope of the ledger are
spoken, not just captioned.

The seven existing components were **not** rewritten. They were already
Gate V–clean at 0 BLOCKER / 0 MAJOR after six defect fixes, and re-authoring
working, verified code to satisfy a requirement that two of them already met
would have risked regressing those fixes for no gain. What changed is recorded
beat by beat in `FRICTIONAL.md`.

## 7. Course policy

Built under the [AI policy for Professor Bear's
courses](https://youtu.be/8Ut0Cdl6vMw). AI contribution is disclosed in §4 above
and the process log is in `FRICTIONAL.md`. The academic-honesty requirement that
shaped the film most is the constructed-example rule: the toy is labelled as
constructed on screen for its entire run, not disclosed once in a caption and
then quietly relied on.
