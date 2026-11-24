# PROMPTS — the-names-nothing-checks

**No generation prompts.** Nothing in this film is generated imagery, generated video, or a
generated voice performance of a person. There are no text-to-image, text-to-video or
image-to-video prompts to record, and no Higgsfield beats: the free path was used throughout.

Every frame is one of two things:

- a drawn isometric Manim scene in `scenes.py`, written by hand against the show-tell kit, or
- a Remotion bookend composition shipped with the toolkit (`BrutalistHesitantWriter`,
  `ClaudeDefinitions`, `ClaudeComposerAsk`, `ClaudeTitleOutro`), driven by props in the beat sheet.

The narration is synthesised locally by Kokoro from the `narration_text` fields in
`beat_sheet.json`. Those fields are the script; they are not model output being passed off as
a recording of a person.

## The one prompt that appears on screen

`BHTF` shows a prompt, read aloud in full, that the viewer is invited to paste into Claude. It
is addressed to the audience and is not used to produce any part of this film:

> Pick a project you know well and ask your AI assistant for code that uses a name stored
> outside the source files: an animator parameter, a shader property, a config key. Then open
> the file that actually defines that name and compare. Tell me whether the assistant read it
> or guessed it.

## How Claude was used in making the film

Recorded here rather than hidden, and repeated in `SOURCES.md`. Claude was used as a writing
and coding assistant: drafting the seven answers in `PROJECT-BRIEF.md` from the author's own
material, drafting narration, writing `make_sheet.py` and `scenes.py` against the toolkit's
`SKILL.md`, running the toolkit's gates, and reading back the rendered frames. For the
2026-11-22 four-act rebuild it also ran the search behind act 2 and read the documentation
pages it quotes; those pages, and the sentences taken from them, are listed in `SOURCES.md` and
`FACTCHECK.md` so the quotes can be checked against the originals. It was not used to generate
any image, video or audio asset.

The author reviewed and corrected the output. Two corrections are on the record in
`FACTCHECK.md`. Row 3: an earlier draft of the narration claimed Unity's console says nothing
about a wrong animator parameter. It does say something. The claim was checked against Unity's
documentation, found wrong, rewritten to the shader property, and a beat (`B03`) was added so
the film states the limit out loud. Row 18: a draft of the act-2 closing line said "what nobody
does", which asserts a negative about every tool that exists. It was changed to "what I could
not find", which is what was actually established.
