# FRICTIONAL — the-names-nothing-checks

Weiting Wang · INFO 7375, Fall 2026. Dated entries, written as the work happened.

---

### 2026-10-13 — picked the project, then made it bigger than my own bad afternoon

The starting point was something that happened to me: an AI assistant kept pointing me at
script and member names that did not exist in my own Unity project. That is an anecdote, not a
project. The general problem underneath it is that a Unity project keeps a large part of its
interface outside the code — in `.shadergraph`, `.controller`, scene YAML and project settings —
and C# can only reach that part through strings. I scoped the project to verifying that layer,
and the anecdote became one line of motivation instead of the thesis.

I also could not remember enough about my own CoplayDev/unity-mcp experience from spring 2026 to
make claims about what it did or did not read. So the film says only what I actually saw: it
wrote into my project, its scene layout was wrong, and I went back to building scenes by hand.

### 2026-10-13 — the toolkit's bookends are the instructor's, and the assignment forbids that

show-tell hard-codes a persona and a credit line. `BIDEA` opens with "Hallo. This is Liam, in
for Bear." `metadata.persona` is "Liam (in for Bear)". `folderLabel` in `BDEFS` and `BHTF` and
both the `handle` and the narration in `BOUT` are `@NikBearBrown`. `SKILL.md` marks the outro
"never exempt" and there is an `OUTRO-LOCK.md` at the repo root enforcing it.

The assignment says to narrate as myself and not to use the instructor's name, persona or
credit line. These cannot both hold, and the assignment is the one I am graded against, so I
changed four things: the opening greeting, the persona in metadata, all three credit labels,
and the voice (Kokoro `af_bella` instead of the default `am_onyx`, which is "Liam" — show-tell
law 6 says Liam by default).

I assumed this would make the film fail the bookend check, and wrote that down before testing
it. **That was wrong, and reading the code is what corrected me.** `OUTRO-LOCK.md` scopes itself
in its own first lines to "claude-liam / @NikBearBrown reels (slug `claude-liam-*`)" and says
other channels "have their OWN outros and NEVER get this card, handle, or mascot" — this reel is
neither. And `bookend_check.py` does not hardcode the handle: it compares the outro's handle
against `metadata.channel_title`, defaulting to `@NikBearBrown` only when that key is absent.

Two things were genuinely wrong in my sheet, and the gate would have caught both: I had no
`channel_title`, and I had put `"subline": "INFO 7375"` on the outro, which the gate rejects
outright ("subline is opt-in per video"). Set `channel_title` to my own handle, emptied the
subline, and `bookend_check.py` now exits 0: *PASS — four bookends correct*. So this is a
deviation from the skill's default persona, not a gate failure, and I should not have claimed
friction I had not measured.

### 2026-10-13 — four beats were two beats each

My first sheet had 17 beats and four body beats over 15 seconds. `SKILL.md` says a beat past
about 15 seconds is usually two ideas. Split B04, B05, B07 and B08 into pairs. 18 beats,
3 minutes 32 seconds estimated, no body beat over 14 seconds.

### 2026-10-13 — `FadeIn(shift=[0, 0.5, 0])` crashes, and the layout audit found a label on a line

Five scenes crashed the layout audit with
`ValueError: operands could not be broadcast together with shapes (n,3) (0,)`. Manim's fade
`shift` wants a vector, not a plain list; a list makes it compute an empty array. Wrapped all
nine in `np.array(...)`.

Then the audit reported one real error: in B05B the "read only" label sat on top of the crate's
outlines. Moved it clear. After that: `static_scene_check` 14 clean, `manim_layout_audit
--curve-strict` 14 CLEAN.

### 2026-10-13 — both gates were green and four frames still did not work

This is the entry I would most want a reviewer to read. With every check passing I rendered the
last frame of each scene at low resolution and looked at a contact sheet, as step 4 of the
skill's workflow says to. Four problems that no gate catches:

- B07B: the labels "false alarms" and "caught" ran together into "false alarmscaught".
- B01: the string — the whole subject of the beat — was a short line hidden between two dark
  blocks and was effectively invisible. Redrawn as an arc that clears the crate.
- B02: I had dropped the pages and blocks and left a bare slab, which breaks the skill's
  "same objects, whole film" law one beat after establishing the cast.
- B08: my drawn sword rendered as a rocket. Replaced with the thing it was standing in for —
  one terracotta arc of glow over the block, which is also closer to what `_GlowActive`
  actually does.

A gate tells you the frame is legal. It does not tell you the frame is the picture you meant.

### 2026-10-13 — I had written something false into the narration, and the fact-check caught it

Drafting `FACTCHECK.md` meant finding a source for every claim, and one claim did not have one.
Beat B02 said that a wrong string produces no console message. That is true for a shader
property: Unity's manual says a call for a property the current shader does not have "will have
no effect", and nothing is reported. It is **not** true for an animator parameter — Unity prints
`Parameter 'Jump' does not exist` at runtime.

So the beat was rewritten around `material.SetFloat("_GlowActive", 1f)`, which is a real line
from my own game, and a new beat B02B was added that says out loud which case Unity warns about
and which it does not. The project's scope changed with it: the first piece I will build is now
the shader-property path, not the animator path, because the animator path is the one Unity
already partly covers.

I had also written "it says nothing about a wrong tag, or a wrong object name." I had not
checked it, and Unity raises an exception for an undefined tag, so I cut the clause instead of
hedging it. Both are rows 3, 4 and 5 of `FACTCHECK.md`.

### 2026-10-13 — a reworded line silently broke a beat's pacing

`iso_kit.py`'s `until(self, phrase)` waits for a spoken phrase by finding it in that beat's
narration. If the phrase is not there it returns immediately and the scene simply plays out of
sync with the voice — no error, no warning, nothing in any gate. When I reworded B03 for row 6
of the fact-check, its `until("It does not read")` stopped matching and I did not notice.

Found it by writing a check of my own that pulls every `until()` string out of `scenes.py` and
asserts it appears verbatim in that beat's `narration_text`. 14 phrases, 1 broken. Fixed to
`until("cannot know the name")`. This check now runs whenever the narration changes.

### 2026-10-13 — Gate F wants more paperwork than the assignment lists

`run.sh` refuses to render without `FACTCHECK.md`, `SHOTLIST.md` and `PROMPTS.md`, and
`factcheck_check.py` additionally blocks on any unresolved verdict. Wrote all three plus
`SOURCES.md`. `factcheck_check.py . --strict-coverage` exits 0; `lane_check`, `content_check`,
`beat_lint` and `placeholder_check` all pass.

### 2026-10-14 — my own week-01 reel corrected four things

Connecting the course repository put `fall-2026/weiting-w/week-01-video/` in front of me: a
finished Brutalist film with its whole paper trail. Reading it changed four decisions.

**The toolkit bug is not new, and I had already met it.** My week-01 `FRICTIONAL.md` says:
"`./art doctor` exits early on ElevenLabs references inside Brutalist's own example files (not
mine). Did not block my reel; noted and moved on." Same wall, four weeks earlier. The difference
this time is that I treated the readiness table as a prerequisite and went looking for the cause;
in September I shrugged and carried on. Bisecting all 78 commits puts the breakage at
`92689c2`, 2026-09-15, and it is still broken at HEAD — 29 days.

**`art final` does not render.** Week-01 me learned this the hard way: `final` only assembles
what `run` has already written, so running it on a cleared cache yields a reel of slates. And
`run`'s output is a *review* cut, `<slug>-slate.mp4`, with a debug label in the corner; the clean
master is `renders/<slug>.mp4`. I had written the wrong order and the wrong output path into
`BUILD-PROMPT.md`; both are corrected.

**GATE T's text floor is 41 px, and serif renders short.** Week-01 B02 failed by one pixel on a
serif run. Every label in this film is EB Garamond, and they were sitting at 30 to 36. Raised
them all to 42. That re-introduced two label collisions — "compilerconsole" in B02 and
"false alarmscaught" in B07B — which, again, passed Gate A, Gate W and the layout audit and were
visible only in the rendered frame. Widened the columns.

**The voice needed disclosing.** Week-01's `beat_sheet.json` records the persona as "Synthetic
Kokoro af_bella voice (disclosed in narration, on the end card, and in SOURCES.md)", and its end
card reads "One Word, Same Answer. Read by a synthetic voice, for Weiting." This film's opening
had a synthetic voice saying "I am Weiting Wang" with no such disclosure anywhere. Week-01 never
had that problem because its opening said "we ran the experiment" and never claimed a voice. So I
took the end-card formula verbatim and added one sentence to the opening, which week-01 did not
need. Disclosed now in three places.

Also, for the record: that film's 4K master is 16 MB for 198 seconds, and the whole folder is
24 MB. My earlier worry about GitHub's 100 MB file limit was unfounded; no Git LFS is needed.

### 2026-10-14 — a comment quoting the warning triggered the warning

First real `./art run` stopped at Gate A: *"GATE A FAILED: BNN_Name has static errors."* There
is no scene called `BNN_Name` in this film. `run.sh` finds scenes by grepping `scenes.py` for
the literal class-definition text, and the header comment I had written above the scenes quoted
`SKILL.md`'s own warning verbatim — including its placeholder example, spelled out exactly as a
real class definition. The grep counted the comment as a fifteenth scene and the gate failed on
a class that does not exist.

So the line of documentation warning me how `run.sh` finds scenes is the line that broke it.
Reworded the comment so the pattern no longer appears as literal text, and added a check: the
file must contain exactly fourteen matches of that pattern and every one of them must start at
column zero. `scenes_body.py` has the same text but `run.sh` only ever reads `scenes.py`.

Nothing else changed; all fourteen scenes still pass Gate A, Gate W and the layout audit.

### 2026-10-14 — audio measured, and the sheet is now on the real clock

Kokoro generated all 18 beats on the first attempt, `af_bella`, $0.00. Measured total 180.2 s,
three minutes exactly, against my 214 s word-count estimate — the estimates ran long by about
16%, which is worth knowing for the next film. `actual_duration_s` and `audio_file` were written
back for every beat with nothing missing.

`tail_silence_s` and `lead_silence_s` turn out to be declarative only: nothing in `runtime/`
reads either field. My week-01 film never set them and shipped fine. Since this sheet declared a
1.0 s tail, I padded `beat-BOUT.mp3` with `ffmpeg -af apad=pad_dur=1` and wrote the measured
5.12 s back, so the sheet and the audio agree rather than the sheet claiming something untrue.

### 2026-10-14 — first full render, and Gate V caught one beat

Everything rendered: fourteen Manim scenes at 4K, all CLEAN on the per-scene layout audit, four
Remotion bookends, 18/18 slots filled, a 181.5 s review cut. Gate V then failed the reel —
BLOCKER 0, MAJOR 2, both the same defect on B03: *"ink/background luminance separation 0.24 <
0.30."*

B03 is the beat where a veil covers the asset half of the project, because an assistant reading
only the C# cannot see what is in there. The veil was pale `GHOST` at 0.92 opacity, which hid
the dark blocks underneath completely and left a frame that was almost entirely cream and kraft.
`SKILL.md` warns about exactly this — Gate V averages every non-background pixel, so a pale panel
reads as low contrast even when the type is dark ink, and it prescribes giving the panel a dark
element to carry it.

Rather than re-render on the Mac for each attempt, I reimplemented Gate V's measurement from
`runtime/qc/final_frame_check.py` (modal background from the corner patches, ink = pixels more
than 28 per channel from it, separation = |luminance of the mean ink pixel − luminance of the
background|) and measured every beat locally. B03 came out at 0.226; the next lowest were B08
and B08B at 0.319, and the rest sat between 0.34 and 0.44.

Then I measured the fixes instead of guessing at them. Dropping the pale veil's opacity reached
0.30 only at 0.50, by which point the hidden blocks are plainly visible and the beat no longer
says what it means. Adding a thin dark bar to the panel, as the skill suggests, moved it from
0.237 to only 0.271 — too few dark pixels against that much pale area. Changing the veil itself
from pale `GHOST` to the mid-grey `DIM` passed at every opacity tried, 0.338 to 0.347.

Settled on `DIM` at 0.72, measured 0.342. It reads better than the original: the half is blacked
out rather than fogged, and the blocks show faintly through, so the beat says "something is in
there and it cannot be read" instead of "there is a pale smudge here". Gate A, Gate W and the
layout audit all still pass on the changed scene.

### 2026-10-14 — the review cut showed a beat that said the opposite of its narration

With every gate green I watched the review cut, and B02 was wrong. Not broken — wrong.

The beat is the heart of the film: a wrong shader property compiles, the console stays quiet,
and the effect never happens. On screen a terracotta dot travels through the compiler gate and
the console gate to an indicator lamp that is supposed to stay dark. Except I had sent the dot
to the lamp's exact centre, and terracotta is this film's accent for a thing that is live — the
sword glow in B08 is the same colour. So the final frame was a grey ring with a glowing orange
centre: the universal picture of a light that is ON. The narration says the effect never
happens; the picture said it worked.

No gate can catch this. Gate A, Gate W, the layout audit, Gate T and Gate V all passed the
frame, because it is legal, legible, well-contrasted and inside the margins. It is simply the
wrong picture. I had looked at this beat in two contact sheets and missed it both times,
because in a still the dot is just the end of a path; it took watching the cut to see it as a
lit lamp.

Fixed by stopping the runner short of the lamp in both B02 and B02B, so the lamp is visibly
never lit and the dot arrives at nothing. Three gates re-run clean on both, contrast 0.42 and
0.41.

The lesson is the same one the film is about, which I did not expect to learn from the inside:
the checks tell you the output is well-formed, not that it means what you meant.

### 2026-10-14 — the film was crediting the instructor, and every gate said it was fine

Reading the QC contact sheet — the 36 frames sampled from the compiled cut — the end card says:

> **The Names Nothing Checks.**
> **@NikBearBrown**

Not my handle. The assignment's rule is explicit: do not use the instructor's name, persona or
credit line. The rendered film was breaking it.

The beat sheet is not wrong. It sets `handle: "@WeitingWang0704"` and `channel_title` to match,
and `bookend_check.py` passes, because that gate compares two fields inside the JSON and never
looks at a frame. `ClaudeTitleOutro.tsx` line 19 is `const HANDLE = '@NikBearBrown';` — a module
constant. The component does not accept a handle prop at all; it destructures only `title`,
`slug`, `mascotAnimation` and `lectureLayout`. Everything I passed was discarded.

I had read the warning and filed it wrong. Three days ago I noted that `OUTRO-LOCK.md` scopes
itself to `claude-liam-*` slugs and concluded there was therefore no conflict for this film.
What I missed is that the scope note describes which reels *should* use the card — it does not
stop the component rendering that handle for any reel that does use it, and the toolkit ships no
alternative outro.

Fixed by changing that one constant in my local `brutalist.art` checkout to my own handle and
re-rendering BOUT. The exact one-line patch is in `BUILD-PROMPT.md` so the film still rebuilds
from a clean clone. The component's own header says it is for "claude-liam / @NikBearBrown reels
ONLY" and this is not one of those, so the patch puts a non-claude-liam reel outside a card that
was never meant for it, rather than overriding a rule that applies to it. The toolkit checkout
is not vendored into the course repository, so nothing of the instructor's is modified in what
I submit. I kept the Claude mascot: that is Anthropic's mark, not the instructor's.

Two gates passed this film while it carried someone else's credit on screen, and a third
(`SKIN LINT`) reported something unrelated. The only thing that caught it was looking at the
contact sheet. Nothing in the toolkit told me to look.

---

### 2026-10-14 — GATE T failed two beats, and neither of them contains any text

`./art run` finished clean — Gate V with no blockers and no majors, 18 of 18 beats filled, a
181.5 s review cut. `./art final` then stopped before the master:

```
[typecheck] GATE T: FAIL (2 pixel beats, 0 sweep, 0 shape)
[art final] GATE T BLOCKED: TYPECHECK.md has FAILs — fix before final cut.
```

`TYPECHECK.md` named them:

| beat | finding |
|---|---|
| B04 | bbox-overlap §8.6b: text-run bbox overlap 36% — `blob@(1756,219)–(2611,691) ∩ blob@(1245,523)–(2695,1466)` |
| B08B | contrast §8.3: terracotta accent `#D97757` on cream 2.74:1 < 4.5:1 WCAG |

Both labels were wrong about what they had found. Converting those pixel coordinates back to
Manim units, B04's two "text runs" are the robot arm and the crate — the arm's bounding box
hangs into the crate's by a third. B08B's "accent text" is the glow over the block. There is no
type in either finding. `type_check.py` builds its text mask from colour alone and then keeps
any blob that is at least ~34 px tall, between 1.5 and 15 times wider than tall, and at least 4%
filled; a jointed ink arm and a shallow terracotta arc both fit that shape. The gate is reading
drawings as words.

The toolkit's own answer to this is a list of exemptions — `STRUCTURAL_TERRACOTTA_PATTERNS` and
the §8.6b list — naming scene classes from the instructor's reels, with comments saying the same
thing I just wrote: the terracotta is structural, the overlap is a box border. I could have added
my two classes to those lists. I did not: that edits the gate instead of the film, and this
film's whole argument is that a green check is not the same as a correct result. Also the toolkit
checkout is not part of what I submit, so an exemption living there would not travel with the
film.

So I changed the drawings, using the one property the checker actually tests — a text run is
wider than it is tall:

- **B04.** The arm now reaches *down* from `(0.45, 3.3)` instead of *in* from `(-0.6, 3.15)`.
  Its blob goes from 1.81× wider than tall to 1.14×, below the 1.5 threshold, so it is no longer
  counted as a run at all and the overlap cannot be reported. It also reads better: an arm
  lowering something into the crate rather than swiping across the frame.
- **B08B.** The glow is now a 300° ring with its opening at the bottom, not a 115° arc over the
  block. Ratio 1.07. This one is a straight improvement — the arc was the leftover of the sword
  that read as a rocket in the first contact sheet, and a ring around the block says "this one
  lights up" more plainly than a curve above it.

I checked both before touching the render. `type_check.py` is importable, so I rendered the two
midpoint frames at 3840×2160 in the Linux container and called `check_bbox_overlap` and
`check_contrast` on them directly: the unmodified frames reproduced both failures with the same
numbers printed in `TYPECHECK.md` (36%, 2.74:1), and the modified frames pass. Gate A, Gate W and
the layout audit stay clean on `B04_WritesIn`, `B08_HaveTray` and `B08B_NewTray`, and Gate V's
separation metric on the two new frames is 0.425 and 0.327 against its 0.30 floor. `B08` changes
too, because both beats share the `glow()` helper — the same object has to look the same in both.

Re-rendered those three beats on the Mac at 2160p: GATE T PASS, 0 FAILs, Gate V still 0
BLOCKER / 0 MAJOR, and `art final` wrote the master — 3840×2160, 24 fps, 181.5 s, 10.3 MB, with
the one-second silent tail intact (last 1.2 s at −50 dB).

What I take from it: this is the third time in this film that a gate has been *precise and
wrong*. It is also the third time the fix was cheap once I stopped arguing with the label and
measured what the gate measures.

---

### 2026-11-22 — the assignment changed shape, and the film had to be rebuilt around it

The instructor fixed the order a project film has to follow: executive summary, then what other
people have done, then methods, then evaluation. I held the October cut against it:

| Part | What the October cut had |
|---|---|
| Executive summary | Not there. It opened on a hook — "I used to check whether it compiled" — and three definitions. A viewer who watched only the first minute got the problem, not the project. |
| Introduction | **Nothing at all.** Eighteen beats and not one sentence about anything that already exists. |
| Methods | Half. Two beats said what the tool does. Where the names are read from, the steps, and the resources it needs were nowhere. |
| Evaluation | Most of it. The fixture, the false-alarm risk and the three numbers were there; the pass mark was not. |

So the missing act was act 2, and it is the one act that makes claims about other people's
work. I did not want to describe those tools from memory — I got a Unity fact wrong in October
doing exactly that — so each one was read in its own documentation before it was written into
the narration. `FACTCHECK.md` rows 14 to 18 carry the sentences and the pages.

Two things in that reading changed the pitch itself:

- **Unity has already solved this once**, for one of the four name kinds. The Input System can
  generate a C# class from an `.inputactions` asset so that those names "become code"; the
  manual's own section is called "Type-safe C# API Generation". That is a better argument than
  the one I had. The claim is no longer "nobody thought of this"; it is "it exists for one kind
  out of four, and the other three are still strings".
- **Both big analyzers look at exactly the line my tool is about.** Rider's inspection is
  titled "String based graphics property lookup is inefficient"; Microsoft's UNT0041 and
  UNT0046 say cache the hash and cache the ID, both filed under Performance. The whole film now
  turns on that: the same line of code, a different question — fast, or right.

One sentence I had to take back before it was ever spoken. The draft ended act 2 on "what
nobody does is take the whole project and list every name that does not resolve". That is a
negative about every tool that exists and I cannot check it. It became "what I could not find
is anything that reads a whole project…", which is what the search actually established.
`FACTCHECK.md` row 18 says what the search was.

What the rebuild cost: every beat's narration changed, so all of it is re-voiced; nine scenes
are new; eleven are the October scenes renamed, because a beat's ID and its scene class have to
match and the running order changed. Two beats were cut — "by hand" and "why me" — because the
four parts leave no room for them, and B09 keeps the editor-AI story as an example of what
exists rather than as a personal aside.

What I did differently this time: everything that could be checked before the laptop was. The
container got Manim installed, all twenty scenes were rendered at 3840x2160, and they were run
through Gate A, Gate W, the layout audit, `type_check.py`'s own contrast and bbox-overlap
checks and Gate V's separation metric. Twenty for twenty, worst separation 0.339 against a 0.30
floor. In October I found out about GATE T from a failed `art final` on the Mac; this time the
first full render should be the only one.

**It was not.** The first full render of the new cut came back with four Gate V blockers and
three GATE T failures, and both have the same root: I pre-checked the wrong frame.

| Where | What the gate said | What it actually was |
|---|---|---|
| B06, B07 (Gate V, 4 blockers) | `edge-bleed` — content crosses the title-safe left edge | The standalone C# page I drew for those two beats hung 25 px and 143 px past the 5% box. My pre-flight had no title-safe check in it at all. |
| B06 (GATE T §8.2) | 1 text run outside the title-safe box | The same page, this time caught as a "text run" because the dark block sitting on it fuses with its outline. |
| B04 (GATE T §8.3) | terracotta accent 2.74:1 on cream | The terracotta scan line was still sweeping across the frame at the sampled midpoint. |
| B08 (GATE T §8.3) | mean foreground 4.41:1, fg ≈ (124, 107, 77) | At the midpoint the only dark pixels on screen were the kraft outlines of twenty-five grey squares. The ink — the ring, the leader, the second label — had not landed yet. |

The two contrast failures are the same mistake in different clothes: I checked **final** frames,
and GATE T and Gate V sample the **midpoint**. Everything I verified was true of a frame the
gates never look at.

Underneath that is a timing problem I should have predicted. Every scene waits for a spoken
phrase before it moves (`until(…)`), and `until` places the phrase by its character position in
the narration. The new narration is longer and the key phrase in several beats sits late in the
sentence, so the animation that follows it now runs across the midpoint instead of finishing
before it. I wrote a small simulator — walk each scene's `self.play(... run_time=…)` calls,
resolve each `until` against the measured audio, and print when the pre-midpoint work actually
ends — and ran it over all twenty scenes against the real durations:

```
B04  dur= 9.62 mid= 4.81 last-pre-mid-play ends  6.22  <-- STRADDLES MIDPOINT
B07  dur=13.61 mid= 6.80 last-pre-mid-play ends 12.87  <-- STRADDLES MIDPOINT
B11  dur=12.20 mid= 6.10 last-pre-mid-play ends 10.36  <-- STRADDLES MIDPOINT
…11 of 20 scenes
```

Eleven of twenty. Three of them failed a gate; the other eight were benign and would have kept
being benign until one of them was not. B07 was the worst of it: the whole lower half of the
picture — the thread that ends nowhere, the thing the beat is *about* — landed in the last
second of a fourteen-second clip, because the phrase I had tied it to is the last clause of the
narration.

Fixed: B04, B08, B11, B12 and B15 now wait for an earlier phrase (and the earlier phrase is a
better sync in every case — the scan sweeps as "an assistant" is said, the ticks fill as the
file kinds are named); B06 and B07 moved right, clear of the title-safe edge; B08's grid now
has ink outlines instead of kraft, so the frame has ink in it whatever the timing. The
title-safe check and the timing simulator are both in the pre-flight now, and both are written
down in `BUILD-PROMPT.md` so the next cut starts with them.

---

## Still open

- **Voice.** Currently Kokoro `af_bella`. Recording my own voice would fit "narrate as yourself"
  better; if I do, only the audio files change.
- **"AI" through Kokoro.** `SKILL.md` records that Kokoro mangles some acronyms ("API" spelled
  out comes back as "PI key"). "AI" appears in BIDEA and in the Your Turn prompt. It needs a
  whisper transcript check once the audio exists; if it comes back wrong, reword.
- **The dated record.** I do not have a saved, dated transcript of the assistant inventing a
  script name in my project. Unless I find one, the film describes it as something I
  experienced and does not present it as evidence — and no private conversation transcript goes
  into this repository either way.
- **The toolkit's step 7 says to send the master to the instructor and publish only on his
  word.** I am submitting to Canvas and GitHub instead, per the assignment, and publishing
  nowhere.
- **Length.** The October assignment capped the film at four minutes. The four-part brief does
  not state a length, and four parts told properly come out at roughly four and a half to five.
  If the cap still applies, the structure is modular: act 2 and act 3 each lose a beat before
  anything load-bearing goes.
- **B09's pacing.** The crooked blocks land in the last second and a half of the beat, in sync
  with the line that describes them, which leaves the middle of the clip static. Checked frame
  by frame against the October clip — it is the same in both, and it is the price of keeping
  picture and narration in step. Left as it is, deliberately.
