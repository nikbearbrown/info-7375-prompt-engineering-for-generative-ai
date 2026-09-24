# FACTCHECK — claude-tom-river-moves-the-bank

Source of record: `chapters/01-randomness-and-first-prompts.md`
§ *Inside one prediction step*, this repository, commit `a0d8a1e`.

**This episode has an unusual fact profile and it is worth stating plainly up
front.** The chapter makes the CLAIM this video is about in a single clause and
publishes **no numbers** for it — no vectors, no scores, no weights, no
dimensions. So the episode splits cleanly in two:

- **What comes from the source** (claims 1–4 below) — checked line by line.
- **What comes from the course brief** (claim 5, the B09 boundary statement) —
  an author's statement about this video's scope, not a claim about the chapter.
- **What comes from the author** (every number on screen) — a constructed 2-D
  example, labelled as such on screen for the whole of B03–B07, and verified
  internally for arithmetic consistency rather than against any published
  figure, because there is no published figure to check it against.

No number in this video is measured from a model. That is not a caveat buried
here; it is the last line of the B08 boundary card and the last line of the
verdict.

## Part 1 — claims, and where each one comes from

| # | Beat | Claim | Verdict | Where in the source |
|---|---|---|---|---|
| 1 | B00, B07 | "the vector for `bank` after `river` ends up somewhere different from the vector for `bank` after `savings`" | ✓ **VERBATIM** | § *Inside one prediction step* — reproduced character for character on the B07 card, cited once beneath the figure |
| 2 | B01, B02 | attention "lets those lists read each other and **revise themselves** according to context" | ✓ | Same §. The episode's whole framing — *revised, not replaced* — is taken from the source's own verb, not invented for the script |
| 3 | B02 | "Each token becomes a list of numbers" before attention runs | ✓ | Same § — the static-embedding premise B02 dramatises |
| 4 | B08 | the block repeats: "both operations repeat, layer after layer" | ✓ | Same §. Stated on the boundary card as something this video does **not** show, which is the honest direction to use it in |

| 5 | B09 | the boundary statement — *"What this single-head 2D example does not establish is how multi-head attention handles dozens of nuanced semantic dimensions simultaneously."* | ✓ **AUTHOR'S, not the chapter's** | Supplied by the course brief, not the source text. It makes no claim ABOUT the chapter; it states what this video has not shown. Rendered verbatim on screen and read aloud |

**Checked and deliberately NOT used:** the chapter attributes the transformer to
Vaswani et al., *Attention Is All You Need*, arXiv:1706.03762 (2017). It is
recorded in SOURCES.md as the origin of the mechanism but no claim in the script
rests on it, so it is not narrated — citing a paper the episode does not draw a
claim from would be decoration.

**De-dated per DOUBLE-CHECK LAW:** an early B08 draft read "what stacking
ninety-six layers does." The chapter publishes no layer count, and 96 is a
figure from one specific historical model. Replaced with "stacking the block
dozens of times," which the source supports and which will not age.

## Part 2 — the constructed numbers

Declared on screen (B03 ledger, and again on the B08 boundary card):
`d_model = 2` · `W_Q = W_K = W_V = I` · 1 head · 1 layer · no positional
encoding, no residual, no layer norm.

| Quantity | Value on screen | How it was checked |
|---|---|---|
| embeddings | the (1,1) · river (0,3) · savings (3,0) · bank (2,2) | Author's choice. Stated as invented, in the ledger headed EVERY NUMBER HERE IS INVENTED |
| raw scores q·k | 4 · 6 · 8 | Re-derived from the embeddings. B04 also prints the multiply-and-add (`2×1 + 2×1`) and the verifier **evaluates those strings** and asserts each equals its stated result |
| scaled, ÷√2 | 2.828 · 4.243 · 5.657 | Re-derived. √2 ≈ 1.414 shown on screen |
| softmax weights | 0.045 · 0.187 · 0.768 | Re-derived. Sum asserted **exactly 1.000** |
| contributions | (0.045,0.045) · (0.000,0.561) · (1.536,1.536) | Re-derived as wᵢ·vᵢ |
| output, run A | (1.581, 2.142) → (1.58, 2.14) | Re-derived. Exact value shown before the rounded one |
| output, run B | (2.14, 1.58) | Re-derived from the `savings` context |
| displacement | money −0.42 · water +0.14 · ‖Δ‖ = 0.44 | Re-derived. **Drawn to scale** on an equal-scaled plane |
| separation | 0.79 | Re-derived as the distance between the two outputs |

Verifier: `verify_numbers.py` in this folder. It rebuilds every figure above
from the four embeddings and fails on any mismatch. Run it before any re-render.

### Three honesty decisions the numbers forced

1. **Weights print to 3 d.p., not 2.** At 2 d.p. they read 0.05 + 0.19 + 0.77 =
   **1.01**. A softmax beat whose weights visibly fail to sum to 1 refutes
   itself. The verifier asserts both directions — that 3 d.p. totals 1.000 and
   that 2 d.p. does not — so nobody "tidies" it later.
2. **The shift is small and is drawn small.** `bank` keeps 0.768 of itself, so
   it moves 0.44 units — roughly a fifth of the way to `river`. Scaling the
   arrow up would have made a punchier frame and a false one. The magnitude is
   printed next to the arrow and the caption says *drawn to scale*.
3. **The mirror is disclosed as a design property.** Run B is an exact
   reflection of run A. That follows from symmetric embeddings the author chose,
   not from anything attention did, and the B07 card says so in its own line.

## What this episode does not establish

Reproduced from the B08 card, which is the falsifiability beat, not a footnote:

- That real learned W_Q / W_K / W_V behave like the identity matrices used here.
- How multi-head attention assigns different relations to different heads.
- What repeated layers do to a representation.
- That any real model's axes are interpretable directions like "money"/"water".
- Any quantitative claim at all: no number in this video is measured.

And restated full-frame in B09, verbatim: *"What this single-head 2D example
does not establish is how multi-head attention handles dozens of nuanced
semantic dimensions simultaneously."* The narration for B09 says a real model
runs many heads "over far more dimensions than two" — deliberately **not** a
figure, because the chapter publishes none and inventing one would break the
rule this beat exists to enforce.
