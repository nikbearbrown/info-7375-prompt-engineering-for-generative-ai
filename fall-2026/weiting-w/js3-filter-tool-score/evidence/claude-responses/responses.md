# Claude responses, verbatim

**Provenance, and a limitation to read before the responses.**

These are real responses, obtained on **2026-11-23** from **Claude (Opus 5)** in
the Cowork session in which this repository was built. They were produced by
pasting the rendered prompt and recording the answer unedited.

**The limitation: the model answering is the same assistant that wrote the code
and the prompts.** It is not an independent reader. A model that has just spent
hours on this filter knows what the filter is for and what its author is
worried about, and that knowledge is not available to a fresh model given only
the prompt. Nothing here should be read as evidence about how Claude behaves in
general — only as evidence about what *these three prompts* elicited *here*,
which is what `reports/what-moves-the-score.md` claims and no more.

The prompts are `prompts/explain-P-v1.txt`, `-P-v2.txt`, `-P-v3.txt`, rendered
by `tools/explain_shortlist.py`. The rendered text sent in each case is in
`prompt-P-v1.txt`, `prompt-P-v2.txt`, `prompt-P-v3.txt` beside this file.

**The posting, in all three cases:** `Software Engineer, iOS`, `ashby:ramp`,
score 6 under S-v3. Its requirements are Swift, SwiftUI and a minimum of one
year of mobile development; the three spans that earned its six points are all
in its **NICE TO HAVES** section.

---

## P-v1 — loose rules, full posting body

Asked: *"In one or two sentences, tell me why this posting is a good fit for me.
I am a new graduate software engineer."*

> I don't think it is one, and I'd rather say that than answer the question as
> asked. Under WHAT YOU NEED this posting wants a minimum of one year of mobile
> development, proficiency in Swift and SwiftUI, and at least one shipped
> mobile app — none of which is a new-graduate profile, and none of which is
> what your filter matched on. The Python, Flask, SQL and React/TypeScript
> items that presumably earned it points are in the NICE TO HAVES section, so
> the posting's optional list looks like your résumé and its required list does
> not.

## P-v2 — strict rules, scored spans only

Asked for what the text says, using only the three spans, with an instruction
to abstain on the new-graduate question.

> The spans say the posting mentions experience with backend technologies —
> Python, Flask, SQL and OpenAPI — and with web apps in React and TypeScript.
> I cannot tell whether this is open to a new graduate.

## P-v3 — strict rules, full posting body

Same rules as P-v2, with the whole posting instead of the spans.

> The text requires a minimum of one year of experience in mobile development,
> proficiency in Swift and SwiftUI, and experience launching at least one
> mobile app; it lists experience with backend technologies (Python, Flask,
> SQL, OpenAPI) and with web apps (React, TypeScript) under NICE TO HAVES.
> Because it states a minimum of one year of experience, this is not open to a
> new graduate with no professional experience.

---

## What differs, read off the three answers

| | P-v1 | P-v2 | P-v3 |
|---|---|---|---|
| rules | loose | strict | strict |
| context | full body | 3 spans | full body |
| asserted a fit judgement | **yes** (a negative one) | no | no |
| named the actual requirements | yes | **could not** | yes |
| answered the new-graduate question | implicitly | **abstained** | **answered: no** |
| could the answer be checked against a span? | partly | yes | yes |

**P-v2 abstained because it was starved, not because it was careful.** It was
given three spans drawn from the NICE TO HAVES section and had no way to learn
that the posting demands Swift and a year of mobile work. Its "I cannot tell"
is correct about the spans and wrong about the posting.

That is the result that matters here: the strict prompt looks better behaved
and is less useful, and the reason is the context, not the rules.
