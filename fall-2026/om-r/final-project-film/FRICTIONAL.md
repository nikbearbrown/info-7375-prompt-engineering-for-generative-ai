# FRICTIONAL.md — agent-reliability-audit-pitch

Where this build pushed back, and what happened. Each entry is dated from
evidence on disk: the transcript of this session, file modification times,
build logs and the `_superseded/` archive. Where no record gives an exact
date, the entry says so instead of guessing.

---

## 1. Instructor branding baked into the show-tell bookends

**Date:** 2026-10-11, on or before 19:04 (`make_sheet.py` mtime; the
decision is recorded in its docstring)

**Friction.** The show-tell skill's default bookends are built for one
channel. `skills/make/show-tell/SKILL.md` scripts the cold-open greeting as
"Hallo. This is Liam, in for Bear. …" and closes on `ClaudeTitleOutro`.
That component hardcodes the handle (`const HANDLE = '@NikBearBrown'`; its
own header says "HARDCODED — no prop, no lookup, no override"), so there is
no way to put my own name on the outro. `bookend_check.py` also falls back
to `DEFAULT_HANDLE = '@NikBearBrown'`. This film is narrated as me, so
neither default works.

**How it was confirmed.** By reading `ClaudeTitleOutro.tsx` and
`bookend_check.py` directly, not by assuming from the docs. Reading
`run.sh` and `compile.py` showed that neither `./art run` nor `./art final`
calls `bookend_check.py`, so dropping the outro bookend fails no gate the
pipeline actually runs.

**Resolution.** Every `narration_text` was rewritten in my own first-person
voice, with no "Liam" or "Bear". `ClaudeTitleOutro` isn't used at all; the
film ends on a plain drawn beat (`BCLOSE_TitleCard`). The sheet records this
as `bookend_exempt` with a reason. Cost: SKIN LINT warns on every build
("OUTRO LAW wants ClaudeTitleOutro"), and the outro's built-in silent tail
went missing (see #4).

---

## 2. pass@k / pass^k: an inferred number attributed to the source

(See entry 6: this 'correction' was itself wrong — the source does state 70% directly.)

**Date:** 2026-10-11, on or before 19:04, which is before the first render
(the corrected narration is already in `make_sheet.py` at that time; the
first manim renders are dated 19:17)

**Friction.** An early draft said the source article reported a ~70%
per-trial success rate. It doesn't. The article ("Building an AI Agent
Evaluation Pipeline: 2026 Methodology," digitalapplied.com, published
2026-06-02) states only the two headline numbers in its stat block: pass@3
= 97% and pass^3 ≈ 34%. The 70% was my own back-calculation (0.7³ ≈ 34%,
1 − 0.3³ ≈ 97%). The math is consistent, but the source never says it.

**How it was caught.** By reading the article's actual content rather than
a search-result snippet.

**Resolution.** The inferred figure was removed from the narration
entirely. B02 and B03 cite only the two quoted numbers. Logged as
FACTCHECK.md #6 (CORRECTED) and explained in SOURCES.md.

---

## 3. Real gate failures and their root causes

### 3a. First-pass fixes: B04, B02/B03, B05/B07/BCLOSE

**Date:** 2026-10-11, on or before 19:14 (`scenes.py` mtime before the
first review run; the fixes are documented in its `FIXES applied` comment
block)

- **B04, Gate A error.** The crack was drawn as two shapes created in one
  call before the first snapshot. Gate A only snapshots after
  `play()`/`wait()`, so two shapes that appear together look like one shape
  forever. *Fix:* draw the crack in two separate `play()` calls.
- **B02/B03, terracotta text and undersized captions.** Both beats used
  terracotta (#D97757) as text colour, which isn't allowed on cream, and
  the captions were below the 32-unit floor. *Fix:* counters in INK, a
  small drawn curve beside each counter, captions raised to 36.
- **B05/B07/BCLOSE, shadow detaching from the crate.** `floor_shadow()` was
  built as a separate object from the crate and label. When only the crate
  moved, the shadow stayed behind. The same cause produced the "AGENT on a
  line" layout-audit error. *Fix:* group shadow, crate and label as one
  unit before any move or scale.

### 3b. B01: shadow and crate overlapping the gate

**Date found:** not recorded. It was flagged from review frames of the
2026-10-11 render, sometime between then and 2026-10-14.
**Date fixed:** 2026-10-14 (`scenes (3).py`, copied in at 14:56)

- **Shadow:** the same separate-object bug as 3a, missed in B01. *Fix:*
  move `VGroup(shadow, crate, label)` as one unit.
- **Overlap:** the crate was wider than the gap between the gate posts.
  With a 2.6-unit travel toward a gate at x=3.2, its body covered both
  posts. *Fix:* travel shortened to 1.6, and the gate moved to x=5.2.

### 3c. B01: the overlap fix pushed the gate off the safe area

**Date:** 2026-10-14, about 14:59 (`./art run` exited 2)

Moving the gate to x=5.2 put its right edge at about x≈6.9, outside the
±6.3 title-safe bound. Gate V reported **2 BLOCKERs** (`edge-bleed` on B01's
50% and 85% frames). Gate A reported a matching warning ("coord outside the
safe area, e.g. (6.8,-1.0)"). *Fix:* gate moved to x=4.4, which puts its
right edge at about 6.14. On the 15:02 rerun, Gate A was clean, Gate V had 0
BLOCKER and 0 MAJOR, and the crate still cleared the posts by about 1 unit.

### 3d. B03: Gate T contrast false positive

**Date:** 2026-10-14, about 15:05 (the first-ever `./art final` was blocked
with exit 2)

Gate T failed B03 on contrast §8.3: "terracotta accent #D97757 on cream
2.74:1 < 4.5:1 WCAG — accent text must switch to INK". B03 has no
terracotta text; every piece of text in it is INK or DIM. Gate T works on
pixels, and its text-run filter read the two short 4px terracotta leader
curves as accent text. *Fix:* both curves recoloured to INK. The 15:07
review run passed Gates A/V/W, and the 15:09 Gate T passed (12 beats, 0
FAILs).

---

## 4. Missing silent tail on the first master

**Date:** 2026-10-14, found about 15:11 and fixed by 15:20

**Friction.** The first master (sha256 `4ca2bd6d…`) passed every gate but
had no true silent tail. There was audio in the final second, peaking at
−19.1 dB, and no −80 dB silence at the end at all. The toolkit's outro
standard is a 1.0 s silent tail.

**Root cause.** That 1.0 s tail belongs to the `ClaudeTitleOutro` /
`outro_voice` bookend spec (`skills/make/show-tell/SKILL.md`: "BOUT:
ClaudeTitleOutro, kind: outro_voice, a 1.0 s tail"). BCLOSE deliberately
doesn't use that bookend (#1), so the build never added the tail. This
comes from the skill docs; the compile code path wasn't traced to confirm
it.

**Resolution.** 1.0 s of digital silence was appended to
`mp3/beat-BCLOSE.mp3` (8.384 s → 9.384 s, −91 dB). BCLOSE's
`actual_duration_s` was set from 8.38 to 9.38 in `beat_sheet.json` and
`mp3/timings.json`; that is the value that drives both the manim
`finish()` hold and the compile timeline. Then BCLOSE was re-rendered, the
review run repeated, and the final run again. New master: sha256
`4a78550dbe0e64567e9f05cb7d251f6f3d3ca2619ed8457be14993e51feb136b`,
140.79 s. silencedetect at −80 dB shows silence from 139.73 s to the end
(1.06 s), peaking at −90.3 dB.

**Fragile.** The pipeline has no `tail_silence_s` field, and the toolkit
treats audio as the master clock ("regenerate audio, recompile"). If
`generate_audio_kokoro.py` is ever re-run for this reel, BCLOSE goes back to
its natural 8.38 s and the tail disappears without any gate catching it.
The originals are kept in `_superseded/`.

---

## 5. Human/AI split

**Dates:** throughout, 2026-10-11 to 2026-10-14

Claude (Claude Code) did the hands-on work and the measuring: it ran each
gate, reported the actual measured results (including when a run had not
actually happened), traced root causes, and proposed fixes with their
tradeoffs. I made the final call on which fix to accept. Two decisions
from 2026-10-14:

- **Gate T false positive (#3d):** three options were on the table:
  recolour the curves, reshape them, or add B03 to `type_check.py`'s
  `STRUCTURAL_TERRACOTTA_PATTERNS` exemption list. I rejected the
  exemption-list edit because it changes the gate for every reel, not just
  this one, and chose the two-line recolour.
- **Silent tail (#4):** switching BCLOSE back to `ClaudeTitleOutro` would
  have added the tail automatically. I rejected it because it would bring
  back the hardcoded @NikBearBrown branding the outro was removed to avoid
  (#1). I chose to pad the audio by hand, knowing it's fragile.

---

## 6. Rechecking the cited source myself — catching an error in my own fact-check

**Date:** 2026-10-14

After the build was done, I went back and independently checked the two
things the film cites as real — the GitHub pull request in B07, and the
pass@k/pass^k article in B02/B03 — rather than just trusting what was
reported to me during the build.

The PR checked out exactly as described. The article is where I found a
real problem: my own SOURCES.md claimed the source never states a
70%-per-trial figure, and that an earlier narration draft had wrongly
attributed that number to the source. Reading the full article myself, that
claim is wrong — the source states the 70%-per-trial figure directly and
explicitly, in several places, including its Key Takeaways and the
Section 01 worked example. The 'correction' recorded earlier in
this build was itself based on an incomplete read of the source material,
not the full published article.

The numbers actually used in the film (97%, 34%) were never wrong, since
they're the source's own headline figures regardless of which framing is
used. But a factual claim about the source's own content was wrong, and
I only caught it by going back and reading the primary source myself
instead of relying on a prior pass's summary of it. SOURCES.md and
FACTCHECK.md are both corrected accordingly.

The full read also turned up a small inconsistency inside the source
itself: its body text gives the gap as 62 points, while its stat block,
reliability table and closing callout all say 63. The film's
"sixty-three" is correct by direct arithmetic (97.3 − 34.3 = 63) and
matches the source's own stat block, table and callout; the source's body
text alone has an internal typo.
