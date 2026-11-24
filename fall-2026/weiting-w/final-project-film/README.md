# The Names Nothing Checks — final project pitch film

**Weiting Wang** · INFO 7375, Prompt Engineering for Generative AI · Fall 2026

A pitch film for my final project, **Stringwatch**: a read-only command-line tool
that indexes the names a Unity project keeps outside its code — shader properties, animator
parameters, tags, layers, Input Actions — checks every string reference in the C# against that
index, and reports the ones it cannot find.

**Built in four parts, in the order the assignment fixes:**

| Act | Beats | What it answers |
|---|---|---|
| 1 · executive summary | B00–B05 | what I am building, and why anybody would care — no "how" |
| 2 · introduction | B06–B10 | what already exists: Unity's Input System codegen, Rider's and Microsoft's analyzers, Project Auditor, the runtime APIs, editor AI tools — and the gap between them |
| 3 · methods | B11–B15 | the plan: where the data comes from, the steps, the scope of version one, what it needs to run, and the build order |
| 4 · evaluation | B16–B19 | the fixture, the four numbers, and the line version one has to clear |

Each act's first beat prints the act name on screen, so the structure is readable with the
sound off. The detail that does not belong on screen is in `APPENDIX.md`.

**Target role:** Unity tools / gameplay engineer, or AI-assisted developer tooling.

**Runtime of the project being pitched:** Python with Claude, a command-line tool. Nothing of it
exists yet; the film says so, and `PROJECT-BRIEF.md` ends with an explicit "exists today" list.

**Runtime of the film itself:** the Brutalist toolkit's `show-tell` skill — one drawn isometric
Manim illustration per beat, Remotion bookends, Kokoro text-to-speech, rendered locally at 4K.
No paid service, no API key, nothing published anywhere.

## The narration is a synthetic voice

The film is read by Kokoro `af_bella` — a synthetic voice reading my own words, not a recording
of me. It is disclosed in the opening beat, spoken again on the end card, and recorded in
`SOURCES.md`. This is the same practice I used on my week-01 film for this course.

## What is in this folder

| File | What it is |
|---|---|
| `Wang_Weiting_INFO7375_FinalProjectFilm.mp4` | the rendered film |
| `PROJECT-BRIEF.md` | the seven answers in one page, ending with "exists today" and "will exist" |
| `APPENDIX.md` | the detail behind acts 2, 3 and 4: sources, file formats, steps, measurement protocol |
| `beat_sheet.json` | the 24 beats: narration, timing, act, and one visual slot each |
| `make_sheet.py` | generates `beat_sheet.json` — the source of truth for the narration |
| `scenes_body.py` | the 20 Manim scenes I wrote |
| `scenes.py` | the toolkit's drawing kit pasted on top of `scenes_body.py`, which is what renders |
| `BUILD-PROMPT.md` | every command needed to rebuild the film from an empty folder |
| `SOURCES.md` | what I used, what I made, what Claude contributed, third-party licences |
| `FACTCHECK.md` | every claim in the narration, with a verdict and a source |
| `SHOTLIST.md` | per-beat work order, generated from the beat sheet |
| `PROMPTS.md` | no generation prompts — what that means here, and how Claude was used |
| `FRICTIONAL.md` | dated log of what broke and what I did about it |
| `_qc/`, `layout_audit.md`, `TYPECHECK.md` | the toolkit's own gate reports |

## How to rebuild the film

Full detail is in `BUILD-PROMPT.md`. The short version, with the toolkit cloned to
`~/dev/brutalist.art` and installed with `./setup --install`:

```bash
REEL=~/Documents/GitHub/info-7375-prompt-engineering-for-generative-ai/fall-2026/weiting-w/final-project-film

cd "$REEL" && python3 make_sheet.py                     # beat_sheet.json
cd ~/dev/brutalist.art
python3 runtime/scripts/generate_audio_kokoro.py "$REEL"  # audio is the clock
./art run   "$REEL" --height 2160                        # gates, then the review cut
./art final "$REEL" --height 2160                        # Gate T, then renders/<slug>.mp4
```

Two things that cost me time on my week-01 film and are worth repeating here: `art final` does
not render — it only assembles what `art run` has already written, so `run` always comes first;
and `run`'s output is a *review* cut with a debug label burned into every beat, while the clean
master is written separately to `renders/<slug>.mp4`.

After the audio exists, do not re-run `make_sheet.py`: it would overwrite the measured durations
in `actual_duration_s` with word-count estimates. To change a line, edit it in `make_sheet.py`,
re-run, and regenerate only that beat's audio with `--only B0X`.

## Honesty

Nothing in the film is presented as finished that is not. Every drawing of the proposed tool
carries "proposed" on screen. Past tense appears in exactly two beats, both describing work I
really did in spring 2026 on *Escape from the Depths* (CSYE 7270). No invented users, employers,
metrics, testimonials or results appear anywhere, and the two bar charts carry no numbers.

Act 2 describes other people's tools. Every claim in it is quoted from that tool's own
documentation, and `FACTCHECK.md` rows 14 to 18 give the sentence, the page and the date. The
film says what each tool does and does not do; it does not say any of them is bad at its own
job, and it does not claim no checker like mine exists anywhere — only that I looked and did
not find one.

Two claims in earlier cuts were wrong and are logged as such. I had written that Unity's console
says nothing when an animator parameter name is wrong. It does — `Parameter 'X' does not exist`.
The claim was rewritten around the shader property, which Unity's own manual says has no effect
and reports nothing, and a beat was added so the film states the difference out loud. And a
draft of act 2 ended on "what nobody does", a negative about every tool in existence; it is now
"what I could not find". See `FACTCHECK.md` rows 3 to 5 and row 18.

No résumé, contacts, application tracker, private data or private conversation transcript is in
this folder or in the film.
