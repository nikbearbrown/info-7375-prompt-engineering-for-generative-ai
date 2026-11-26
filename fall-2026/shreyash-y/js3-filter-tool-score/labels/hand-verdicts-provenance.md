# How the hand verdicts were given

*Written by Claude Code on 2026-11-25, after the independent review found that the first answers for
items 39 and 49 were missing from the record. `labels/hand-verdicts.jsonl` (frozen in `667a2932`,
sha256 `c678ec0e…`) is not changed. The first answers that never reached it are in
`labels/hand-verdicts-first-answers.jsonl`. Shreyash's words below are quoted from the session
exactly as he sent them.*

## What Shreyash saw

- **Posting 1** was shown in the terminal label tool (`python3 -m js3 label`). Shreyash answered it in
  the chat.
- **Postings 2–70** were shown in the chat, in four messages: 2–11, 12–21, 22–31, then 32–70 all at
  once at Shreyash's request ("send all").
  - Each was a **summary written by Claude Code**: title, board, location, offices, department,
    whether it was closed, and the requirements in short.
  - The summaries never said what the filter decided. They are shorter than the tool's view
    (`python3 -m js3 label --print 1 70` regenerates that view). The four batches and the double-check
    reply are saved word for word in `labels/summaries-shown-2026-11-25.md`, with his agreement; the
    rest of the session stays local, as the brief asks for conversation transcripts.
- **On request,** Claude Code pasted the full requirements of 8 and the full ads of 11 and 20.
- **Postings 32–70 came in one message** and were answered in one reply. Those answers were saved at
  18:03:18 EST, about two and a half minutes after the previous batch was saved (18:00:43). Most were
  rejected on location or role alone.
- **How his answers arrived:** every answer after the first arrived as pasted text, in five replies,
  and so did his 18:07 decisions.
  - The frozen file's `by` field says "typed in the Claude Code chat" on all 74 lines. That was Claude
    Code's wording, and it is wrong for every answer after the first. The file is frozen, so the
    correction is recorded here.
- **How he wrote them, in his words.** After the re-grade raised the question, Claude Code asked him
  how the pasted labels and decision answers were written, offering two answers: "Another tool helped"
  and "I wrote them all". He chose "I wrote them all" (19:42 EST), then sent this account (20:02 EST):

  > I read the posting summaries Claude provided and asked for the full descriptions wherever I
  > needed more information. I wrote my answers and decisions and pasted them into the session. When I
  > said “I reviewed the suggested labels,” I meant that I reviewed the posting information provided
  > by Claude, although some of my final decisions were influenced by its explanation.

  After the second re-grade, Claude Code asked him again where he wrote the answers he pasted, and
  whether any other AI tool or chat drafted, worded or suggested any of them. He wrote (21:06 EST):

  > I wrote my original answers myself and pasted them into the session. The original verdicts and
  > decisions were mine, although Claude's explanation influenced some of my later revisions.

## Where an answer was influenced, item by item

| Item | First answer | What happened in between | Final answer |
|---|---|---|---|
| 8 (`klaviyo:8215593003`) | yes: "No experience requirement is shown." | The excerpt left out the requirements section: a Claude Code bug (curly apostrophe), fixed test-first. Claude Code then pasted the full section, which says "7+ years". | no: "Changed my answer because the full description requires 7+ years of experience." |
| 11 (`klaviyo:8041054003`) | cannot tell: "I need to check the full description" | Claude Code pasted the full ad at his request. | yes |
| 20 (`klaviyo:7696724003`) | cannot tell: "I cannot find two matching skills in the given text." | Claude Code pasted the full ad at his request. | yes |
| 31 (`klaviyo:7855798003`) | no: "The job is closed." | Claude Code had left "judge it as if it were open" out of the chat summaries and asked him to judge it as if open. His second answer was **yes**, and he asked for a double-check (below). | yes: "Keep: I think MySQL and PostgreSQL should count towards Alex's SQL skill. The rule is too strict here." |
| 39 (`klaviyo:7792539003`) | **yes**: "Boston, engineering, 1–3 years of experience and matching technologies like Python, React and TypeScript." Double-check request: "It passes the written rules, but Android development is the main requirement, which is not among Alex's skills." | the double-check (below) | **no**: "Change: The main requirement is Android and Kotlin, which Alex does not have. Just mentioning Python and React does not make it a good match." |
| 49 (`linear:0c7c2e26-…`) | **no**: "Product Engineer is not one of the listed target roles." Double-check request: "I excluded Product Engineer because it is not in Alex's target role list." | the double-check (below) | **yes**: "Change: Even though the title is Product Engineer, the actual work matches Alex's full-stack skills. It is remote, and Alex's 3 years of experience falls within the 2–5 years required." |

**The double-check**

Shreyash wrote "Double-check before saving" and listed 31, 39 and 49. Claude Code held those three
answers, saved the other 37, and replied:

- **The framing:** "Here is what the written rules say about each. Your label doesn't have to agree
  with them: the audit compares the filter with *your* judgment of whether the job should reach Alex.
  So a disagreement is a finding, not a mistake. Any disagreement becomes a candidate rule change that
  you decide on later."
- **31:** "Rule 4 says skill matching 'uses complete terms or phrases'. 'MySQL' and 'PostgreSQL' contain
  SQL but aren't the complete term 'SQL', and the ad never says 'SQL' on its own. 'NoSQL' isn't it
  either. So the written rule counts one skill here, Python." Then: keep yes "if you think SQL-database
  experience is what Alex's SQL skill means", or change to no "if you want the rule to stay literal".
- **39:** "Yes, it passes all six written rules. The question is only whether an Android-first job should
  reach Alex."
- **49:** "Yes, 'Product Engineer' isn't one of the nine role phrases, so Rule 1 rejects it. By your
  judgment, should a remote, North-America, React/TypeScript full-stack job with 2–5 years reach Alex?"

**What that means for the record:**

- In the double-check, Claude Code stated how the rules read all three postings. That gives away the
  filter's outcome for each.
- Shreyash had already worked out those readings himself, in his own double-check notes. But
  Claude Code's reply also framed the question as one of *judgment*, not of the rules. So the final
  answers for 39 and 49 are **not blind**, and nor is the final 31, which `hand-verdicts.jsonl` already
  marks.
- His second answer for 31 (yes) came before the explanation, and the explanation did not change it.
- Six answers changed in all: 8, 11, 20, 31, 39 and 49. Only the first four kept their first answers in
  the frozen file.

## The audit both ways

Computed by `python3 -m js3 audit`, from the same frozen labels plus
`labels/hand-verdicts-first-answers.jsonl`.

| Audit set (46) | Agree | Misses | False positives |
|---|---|---|---|
| **Final answers** (what AUDIT.md reports) | 43 | 2 (31, 49) | 1 (39) |
| **Answers given before any rule explanation** (31 yes, 39 yes, 49 no) | 45 | 1 (31) | 0 |

**The decisions that rest on these:**

- **A1 (add "Product Engineer")** rests on the final, non-blind answer for 49.
- **A2 (SQL family)** rests on 31. That yes was given before the explanation.
- **A5 (minimum skills 1)** was fitted on the audit labels, where 31 is the posting that moves it.
- **A3 was proposed** because of the Android false positive, which exists only in the final,
  non-blind answer for 39. A3 was then rejected on the held-out set.

The held-out set (24) and the 30 random rejects contain none of these items, so their results are the
same either way.
