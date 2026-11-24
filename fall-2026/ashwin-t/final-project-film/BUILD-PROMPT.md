# BUILD-PROMPT.md: how the TraceCase film was built

This replaces the October version of this file, which described the 3:53 pitch. The commands to rebuild
are in `README.md` under **Rebuild**; this file is what I asked for and the rules I set.

## The prompts I gave Claude Code

**October (the pitch, 2026-10-13):**

> I want you to understand my resumes, my skills and what are the roles I've been applying to lately using the
> tool and whatever the current job market requires … and build something like that for my AI prompt engineering
> course project … It should be an AI-based project and also include, I don't know if it is possible to include
> Redis, caching and stuff like that. If it is not, it's fine, but not forcefully.

> Yes, please start building it and please add the fictional log … write the fictional log [like] me, don't write
> it like Claude … build me the film properly and make the film look intuitive and make the voice very nice and
> calming.

**November (this film, 2026-11-21 to 2026-11-23):**

> I mean the project doesnt say anything about building now we need to make a detailed film right and we need to
> make this project really really good and production level and tell me if any suggestion are required and start
> building i need to get he highest grade in the class and not lose out on anything

> i dont know i have claude plan from northeastern enterprise what can i do in this situation and yes make it
> 4:30 secinds

> make the visuals better and more real and get back to me

Then, with three screenshots attached:

> Percentage adidnt show up up andnthe cirlcular arrow is wrong. Check the shaepe in the metjds as well

That last one is the useful one. Both arrows in the film were drawn pointing the wrong way, and no gate caught
it — a gate can check that a shape is on the canvas, legible and inside the margins, but not that it points the
right way. `FRICTIONAL.md` has that story under "the thing no gate can check."

I ran the finished cut past a second model (ChatGPT) three times and pasted every review back in. The first found
that a chart's bars matched no agent's published numbers and that one beat contradicted its own narration; the
second found that my own README claimed gate results I had never run; the third found that an executive-summary
beat was explaining mechanism and that my corrected baseline lived only in the documents. All of those were true.
`SOURCES.md` records what each model got right and wrong.

Then, on 2026-11-23:

> what is the recomodende runtime as per prog and how. uch ohter did and is my uncet her dam brackeryy?

This is the question that mattered most, and I asked it eleven hours before the deadline. The answer was that the
assignment caps the film at **240 seconds**, every one of my 22 classmates' films was inside it, and mine was
**4:48** — forty-eight seconds over. Nothing in the toolkit or in either model's review had checked the film
against the brief. `FRICTIONAL.md` has that entry.

> yes please checj througly and make it as requuiest and dont so loing in that case keeping the quslitu intact

So the film was recut to **3:51.6**, folding in every outstanding narration fix at the same time.

## The working rules, in my words

1. Use the Brutalist toolkit's `show-tell` skill: one drawn picture per beat, minimal text, the voice explains.
   Keep one cast across the film (service, logs, trace, magnifier for the agent, fix card, barrier gate).
2. Answer the assignment's seven questions in order, one idea per beat, from `PROJECT-BRIEF.md`. In November this
   grew from the 18 beats of the pitch to 25, in four parts: executive summary, what already exists, methods, evaluation.
   **Part 1 says what it is and why it matters, never how** — the mechanism belongs in part 3. I broke this rule in
   the first cut and had to re-record B04 to put it back.
3. **Runtime 2–4 minutes, hard ceiling 240 seconds.** This is the rule I missed until the last evening; see
   `FRICTIONAL.md`. The delivered cut is 3:51.6. All 25 beats and all four parts survived the recut; the cost was
   narration speed, 1.22 rather than the 0.95 the first cut used.
4. Narrate as me, in first person. Don't use the instructor's name, the "Liam, in for Bear" persona, or the
   instructor's credit line. The final cut uses the synthetic voice (Kokoro `am_michael`) throughout, by my choice.
5. **Honesty rule.** No invented numbers. Every number on screen is either cited on the frame or marked unknown.
   Sentences about the product are future tense, **except** design properties, which use the descriptive present
   ("it's built so you can check it" = this is how it is designed, not this is running today). `FACTCHECK.md`
   states that exception in the same words and marks each such row EXEMPT rather than PASS. Named alternatives are
   described only from facts checked against their own pages. `FACTCHECK.md` carries one row per claim.
6. **Draw objects, not labelled boxes.** A log is a stack of lines, a trace is a span bar, the agent is a
   magnifier. If a thing has to be named in text to be understood, it is drawn wrong.
7. **Cue on words, not on estimates.** Every drawing appears on the word that names it, using word-level
   timestamps from `mp3/words.json`. 91 cues; all 91 resolve to a real timestamp, none falls back to the
   toolkit's character-count estimate.
8. Run the gates and fix anything that fails. Never export over a failed render check.

## What the gates actually are

The October version of this file said `./art run` runs gates L, A, W, B and V. **That was wrong**, and I only
found out in November when I went to report the numbers. `art` runs the reel-level gates; the static per-scene
gates are separate scripts that have to be invoked once per scene class:

| Gate | What it checks | How it runs |
|---|---|---|
| L | beat-mix lint | `./art run` |
| SHAPE | finance-reel shape rules | `./art run`, skipped here |
| V | frame-level QC on the compiled reel | `./art run` |
| T | type-lock: min text height, overlap, WCAG contrast | `./art final` |
| A | static pre-flight on each scene | `runtime/qc/static_scene_check.py --class <Scene>` |
| W | WCAG and margin check on each scene | `runtime/qc/wcag_margin_check.py --class <Scene>` |
| B | layout audit on rendered snapshots | `runtime/qc/manim_layout_audit.py --class <Scene>` |

A, W and B were run across all 25 scenes on 2026-11-23. Results are in `gate-reports/LAYOUT-AUDIT.md`.

## Local changes to the toolkit

Used at commit `b21f625`. Two changes, one of which still matters:

- `build/ashwin.json` → `runtime/pronunciation/ashwin.json`. Voice only: "Redis" is spoken "Reddiss". **Needed**
  to regenerate the narration.
- A patch to `runtime/remotion/src/scenes/ClaudeTitleOutro.tsx` so the outro carries my name rather than the
  instructor's handle. **No longer used:** all 25 beats of this film are Manim, so no Remotion scene is rendered.
  The toolkit's skin lint still warns that B00 and B24 are un-annotated Manim rather than the Remotion cold-open
  and outro. That is the intended design, not a failure.
