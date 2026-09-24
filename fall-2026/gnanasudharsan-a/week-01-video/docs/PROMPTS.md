# PROMPTS — claude-tom-river-moves-the-bank

Beat-prefixed prompts. **No generation prompts appear here** — this episode has
no AI-generated media of any kind. No Higgsfield, no stills, no pantry, no
archive. Every frame is a deterministic Remotion render from source in this
repository.

Two sections: (1) the prompts the reel actually shows on screen, which are
content; (2) the authoring prompts, recorded so the film is rebuildable by
someone who was not here.

## 1 — On-screen prompts (content, not build steps)

**B00 — the cold open ask**, typed in the composer and answered:

```text
Chapter 1 says the vector for `bank` after `river` ends up somewhere different
from the vector for `bank` after `savings`. Show me the arithmetic that moves it.
```

Output lines shown beneath it:

```text
The chapter states it in one clause and moves on. It publishes no numbers for it.
The mechanism is scaled dot-product attention: score every pair, normalize, mix.
What follows is a constructed 2-D example — small enough to check by hand.
```

**BHTF — the handoff prompt**, read aloud verbatim then discussed:

```text
Take two sentences that reuse one word in different senses. Build a
two-dimensional toy attention example by hand — show the dot products, the
softmax weights, and the output vector. Then tell me which part of your toy is
a lie.
```

The last clause is the point of the exercise. Every toy simplifies somewhere;
the assignment is to make the toy say where.

## 2 — Authoring prompts

The reel was built in one Claude Code session in `brutalist.art/` with the
`.venv` active. The operator's opening instruction, condensed:

```text
Act as an expert AI engineering educator and technical video director for
INFO7375. Build a 2–4 minute Brutalist explainer on "Attention: how 'river'
changes the vector for 'bank'" for Chapter 1, Part 1. Rules: show the mechanism
(static embeddings, Q·K, softmax, weighted sum of V) rather than asserting it;
use a small constructed toy example with honest numbers and label it on screen
as constructed; name the boundary — what single-head attention does not
establish. Produce beat_sheet.json, BUILD-PROMPT.md, SOURCES.md, FRICTIONAL.md
and render the mp4.
```

### B02–B08 — component authoring

There was no single "generate the scenes" prompt. The seven components were
written directly against a spec that existed before any code:

1. `./art scenes "attention vectors embedding dot product softmax"` — Gate L.
   Confirmed miss; see SHOTLIST.
2. The toy's arithmetic was fixed FIRST, in a scratch Python script, and only
   then written into `beat_sheet.json` as props. The components render props;
   they do not compute. One source of truth, checkable by
   `verify_numbers.py`.
3. Each component was authored to the `show` block already in the beat sheet —
   the ordered list of visual events for that beat. SHOW-DON'T-TELL binds at
   beat-sheet time, so the stage directions predate the narration and the code.

### The arithmetic design prompt (to self, recorded)

```text
Pick 2-D embeddings so that: `bank` is exactly ambiguous (on the money/water
diagonal); `river` and `savings` are symmetric opposites; the softmax over
three scaled scores is gentle enough that `bank` keeps most of itself (so the
lesson is "revised, not replaced", not "replaced"); and every printed figure
survives rounding to a number of decimals that still sums to 1.
```

Result: the (1,1)/(0,3)/(3,0)/(2,2) set. The 3-d.p. weight format is a direct
consequence of the last constraint — see FACTCHECK.

### Regenerating

```bash
cd brutalist.art && source .venv/bin/activate
python3 runtime/scripts/generate_audio_kokoro.py <REEL>      # then re-tune
                                                             # Root.tsx frames
python3 runtime/scripts/remotion_scenes.py <REEL> --force
./art run <REEL>
```

Full end-to-end order, with the gates, is in `BUILD-PROMPT.md`.
