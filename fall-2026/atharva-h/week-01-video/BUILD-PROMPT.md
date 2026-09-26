# BUILD-PROMPT — claude-liam-only-the-gaps

Everything needed to rebuild this reel from an empty folder. Commands are in the order
they were actually run. Total spend: **$0.00** — no keys, no network, no paid calls.

## 0. Prerequisite: the virtual environment

The single most load-bearing line in this file. The system `python3` is 3.14 and the
toolkit's dependencies live in `brutalist.art/.venv` (3.12). Without this, `./setup`
reports five of seven features "blocked" and tells you to run `pip install`, which is
the wrong fix.

```bash
cd <toolkit> && source .venv/bin/activate && ./setup
```

Expect: all 7 features ready, `Cost: $0.00`.

## 1. Verify the numbers before building anything around them

```bash
python3 verify/verify_claims.py --json verified-claims-py314.json
```

14/14 claims must pass. Nothing goes on screen that isn't produced here first.

## 2. Generate narration — this is the clock

```bash
cd <toolkit> && source .venv/bin/activate && python runtime/scripts/generate_audio_kokoro.py <reel>
```

Writes `mp3/beat-B00..B11.mp3` and stamps the measured `actual_duration_s` into
`beat_sheet.json`. **Never hand-tune timing** — regenerate audio and recompile.
Measured total: 184.94s across 12 beats. Kokoro runs ~208 wpm, so word-count estimates at 150 wpm
overshoot by more than a minute.

## 3. Compile the review cut (renders Manim + Remotion, runs every gate)

```bash
cd <toolkit> && source .venv/bin/activate && ./art run <reel>
```

To re-render specific Manim beats, delete their mp4s first — filled slots are skipped:

```bash
rm -f <reel>/manim/B03.mp4
```

## 3a. One toolkit edit the outro depends on

The rendered master signs off `@Atharva`. Out of the box it will not: `ClaudeTitleOutro`
hardcodes the handle, and `OUTRO-LOCK.md` states it deliberately — *"HARDCODED. Never
derived from a persona / skin / channel variable."*

**The toolkit clone was deliberately left unmodified**, so a rebuild from a clean clone
renders `@NikBearBrown`. To reproduce the submitted outro, make this one change in
`<toolkit>/runtime/remotion/src/scenes/ClaudeTitleOutro.tsx`:

1. rename the constant `HANDLE` to `DEFAULT_HANDLE`;
2. add `handle: z.string().default(DEFAULT_HANDLE),` to `claudeTitleOutroSchema`;
3. destructure `handle` in the component signature;
4. render `{handle || DEFAULT_HANDLE}` where `{HANDLE}` was.

The default is unchanged, so no other reel is affected — only a beat sheet that sets
`handle` explicitly gets a different credit, and `beat_sheet.json` sets it on B11.
Described here rather than shipped as a patch file because the repo's CI rejects
`.tsx` under its "Non-Python implementation" rule. Rationale and the decision to
revert the clone are in `FRICTIONAL.md`, REV 4.


## 4. Look at the frames — the gates are not sufficient

```bash
open <reel>/qc-sheet.png
```

Pull a full-resolution frame from any beat you want to check properly:

```bash
ffmpeg -ss 8.5 -i <reel>/manim/B03.mp4 -frames:v 1 -y /tmp/b03.png
```

This step found a wrong figure that passed all five gates — GATE V scores contrast and
coverage, so it cannot tell you an annotation points at nothing.

## 5. Export the master

```bash
cd <toolkit> && source .venv/bin/activate && ./art final <reel>
```

Master lands in `brutalist.art/renders/claude-liam-only-the-gaps.mp4`; copy it here.
Verify it decodes with real audio rather than trusting the log:

```bash
ffmpeg -i <reel>/claude-liam-only-the-gaps.mp4 -af volumedetect -f null /dev/null 2>&1 | grep volume
```

Expect 3840×2160, 24 fps, 184.583s, mean ≈ −27 dB / peak ≈ −3 dB.

---

## Authoring prompts — what was asked for, in order

These are the substantive instructions that shaped the reel, not a transcript.

1. **Concept selection.** "Go in depth, find something really interesting that is not
   properly explained — or is explained but could be explained better and in simpler
   words. Doesn't matter if it's the most difficult topic." → rejected a reranking of
   the professor's own topic list; landed on the shift-invariance reading of the
   max-subtraction section.
2. **Simplify without losing the mechanism.** "Explain it like I'm 10, and tell me what
   it's for." → produced the pizza framing and the rotten-kitchen consequence, which
   became B01–B04.
3. **Differentiate against a class using the same chapter and the same tools.** →
   answered by running experiments rather than choosing a different topic: the 2⁵³
   threshold, the two failure modes, the negative control, the passing-but-wrong test.
4. **Pick the strongest ending and justify it.** → chose the rounding-alters-the-gaps
   ending over the underflow ending, because the former is the concept failing while
   the latter is a different bug. Added the temperature-equals-stretching finding,
   which converts the ending from a coincidence into a confirmed prediction.
5. **Lock the evidence before building.** → `verify_claims.py` written and passing on
   two interpreters before a single beat was authored.
6. **Author to the house rules.** Read `skills/make/ai-explainer/SKILL.md` and
   `skills/make/your-turn/SKILL.md` first: body beats 45–70 words, SHOW-DON'T-TELL
   (sketch the `show` block before the narration), four bookends, IN-FOR-BEAR law,
   library-first before authoring any beat.
7. **Fix what the gates find as design problems, not as compliance.** GATE A's
   "shapes never change" on B05 was correct — the beat was a slideshow. The rewrite
   makes the gaps physically stretch, which is both the fix and a better beat.

## Regeneration notes

- `scenes.py` imports the chapter's `probabilities()` and computes every displayed
  value, asserting at import that results still match the recorded tables. Editing a
  number by hand is not possible without tripping an assertion.
- Bookend prop names come from `./art scenes --check <Name>`, not from guesswork.
- `beat_sheet.json` must not carry both `metadata.voice` and `metadata.voice_kokoro`
  unless they are equal; use `persona` for the narrator's name.
- On-screen text must not reference chapter numbers (GATE W recap law). Spoken
  narration may.
