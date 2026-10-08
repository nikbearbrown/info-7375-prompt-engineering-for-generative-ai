# Film 2 layout: Bear's Agentic Approach to Finding Work

Drafted 2026-10-08, revised the same day on Professor Bear's answers. Nothing here is built. Items in [brackets] are mine to confirm. The file keeps its original name so links stay valid.

## Executive summary

**What this is.** The layout of film 2 in the series *Professor Bear Does His Assignments*. Film 2 is not a diary entry. It is a detailed overview of what is being built, told from the software design document that Gru produced in silent mode on 2026-10-07 (`SDD-job-search-project.md`, in all three instructor folders).

**What the film says.** One tool and its surroundings: a collector that reads company job boards; the filter and the audits that say what its output is worth; a ranking of which companies want teaching work done; the rule that keeps three course folders consistent; the public work that fills the gaps the search found. And, because the design document compared itself with the code, what is not built: the "what is new since last time" memory, the scheduler, the five companies the tool cannot read, and a quality-report writer the code only promises in a comment.

**Decisions from Professor Bear (2026-10-08).**
- **Title:** "Bear's Agentic Approach to Finding Work." Not "What Is Being Built."
- **No specific date.** The film says "fall 2026" and nothing narrower, on screen or in the narration. The one run's counts may appear, labelled "fall 2026".
- **The not-built list is a current thought, not a verdict.** It is what the plan is today, and it will change as the thing is built. The film's idea is the loop: write down a good enough plan, start building, let the real world push back, change the plan. Do not spend two years designing something that turns out wrong. AI's real power is quick ideation: build something fast, see whether it is promising; if not, let go and move on; if so, extend it until you get stuck, then do it again. Constant ideation, constant iteration.

**Why that last part is the point.** The series argues that the AI does the AI work and the person's judgment makes it good. This film shows it on the author's own project: the design document is fluent and complete, and the person is the one who checks it against the code. The finding that the earlier design and the code disagree is the film's central example of computational skepticism.

**Form.** The `lecture` skill, Liam in for Bear, free build, never published without Professor Bear's word. The film opens on the narrated card (series name, film title, a short summary), then the hesitant writer. It is told in third person. Video 02 of the series.

**What is not decided.** Whether to build it now.

## Source

The software design document, read whole. Its seventeen sections map to the acts below; anything not used is listed under "left out" with a reason. The film is self-contained: it never says "this document" or "the earlier film."

## Opening

- **BOPEN (narrated card).** "Professor Bear Does His Assignments. Bear's Agentic Approach to Finding Work. Learn how a professor uses AI to look for work, how each part is checked, and why the plan keeps changing as it is built." Card title in two balanced lines: "Bear's Agentic Approach" / "to Finding Work". Series field "Video 02 / 08".
- **BIDEA (hesitant writer).** Types "Plan everything before you build anything." and corrects "everything" to "enough". [Confirm the phrase.]
- **BDEFS (terms, 17 characters or fewer, 3 to 6).** Collector: a program that downloads postings from company job pages. Filter: the rules that keep or throw out a posting. Audit: a check on what the filter got wrong. Design doc: the plan written before or about a build. Human gate: a stop only a person clears.

## Acts

### Act I: The question and the shape
| Beat | What is said | Best visual (runner-up) |
|---|---|---|
| 1 | The question: how does a working professor find advocate, educator and teaching-materials work, and how does anyone know the tool's answer is right | Hesitant-writer follow-on, then a drawn question over a pile of boards (isometric) |
| 2 | The three courses ask three things of one tool: is the output right, how do we work with the AI, how do we present it | Three labelled boxes around one box (Manim diagram) |
| 3 | The system in one sentence: a human-supervised chain from public hiring pages to a person's decisions | A chain of boxes ending in a person (isometric conveyor) |

### Act II: The collector
| Beat | What is said | Best visual (runner-up) |
|---|---|---|
| 4 | Three public job-board systems, eighteen boards watched; one command reads them all | Real watch-list file, captured; (library icons) |
| 5 | The response is saved first, before anything reads it | Isometric: a document drops into a drawer before it moves on |
| 6 | Each posting is normalized, judged, de-duplicated, validated; the source's own record travels inside every kept record | Manim pipeline with the original tucked under the kept record |
| 7 | One board failing does not stop the others | A row of boards, one greyed, the rest still flowing (Manim) |
| 8 | The real command line, run read-only | `python3 collect.py --help` and a file listing on a plain terminal skin, captured from a real run |

### Act III: Checking the output
| Beat | What is said | Best visual (runner-up) |
|---|---|---|
| 9 | The filter is a file: three ways to keep a posting, and every kept record says why | The three rules drawn as three doors (Manim); the real `keywords.json` heading, captured |
| 10 | The first audit asked what was missed and found what was wrongly kept: recruiters, and a salary footer that put one word in every posting of one company | Two cards: expected, found (Manim) |
| 11 | Title families: judge twenty kinds of job instead of thousands of postings | Twenty small tiles sorted into keep, judge, reject |
| 12 | The reject sample: only a person can say what should have been kept | A seeded sample with a blank Verdict column, shown as the real file |
| 13 | The demand report ranks companies, not postings, on five kinds of evidence | Five stacked bars for one company (Manim chart) [numbers only if approved] |

### Act IV: What surrounds it
| Beat | What is said | Best visual (runner-up) |
|---|---|---|
| 14 | One master copy of shared code, copied out to two other folders; class writing is never copied | Isometric: one master box, two copies, a wall between the writing |
| 15 | The sync check once said "all in sync" while a file was missing, because the file was not on its list | The check's output beside the missing file |
| 16 | The facts file: a résumé as structured facts, with an attestation that resets on any edit | A file with a stamp that peels off when edited |
| 17 | The engine's watcher and recipes: one board, with a memory of what it saw, ending at a person | Real skill description, captured |
| 18 | The process log and the film series: how each change is recorded | The real log page, captured |
| 19 | The public work against the gaps: a film series on Figma for education | The real playlist page, captured |

### Act V: Plan, build, learn, change
| Beat | What is said | Best visual (runner-up) |
|---|---|---|
| 20 | Write down a plan good enough to start. Do not spend two years designing something that may be wrong | A short plan page, then a hand starting to build (Manim or isometric) |
| 21 | The design said the tool would remember what it has seen. The code does not yet. That is not a failure: the real world arrives, and the plan changes | Two columns, "planned" and "built so far", with the row that differs ringed; the real file listing, captured |
| 22 | The code's own comment promises a quality report that nothing writes. Another thing found by building, not by planning | The real comment and the real list of files, captured |
| 23 | Right now the plan says: remember what was seen, run on a schedule, read the five companies that cannot be read. It will change as it is built | Three open boxes with a pencil mark, not a locked list |
| 24 | The power of AI here is fast ideation: build something quickly, see if it is promising, drop it if not, extend it if so, until you get stuck, then repeat | A loop drawn as build, look, keep or drop, extend (Manim) |
| 25 | The AI did the fast building; the person decides what is promising and when to let go. That is the part that stays human | The ledger: the AI did, the human decided, doubt caught |

### Act VI: Who decides
| Beat | What is said | Best visual (runner-up) |
|---|---|---|
| 26 | Open questions, all Professor Bear's: schedule or not, readers for the five, build the memory or drop it. Each is a bet, not a promise | A short list drawn as open boxes |
| 27 | The last step is always a person: nothing here applies, emails or posts | The chain from Act I, ending on the person, with the gate ringed |

### Close
- **Recap (BVDT).** Four bare lines, one per major act group.
- **Your Turn (BHTF).** Pick a tool you rely on. Find one thing its documentation says it does, and check that line against the tool's behavior. Two checks follow.
- **Outro (BOUT).** The title, then "At Nik Bear Brown."

## The through-line in this film

| Beat | The AI did | The human decided | Doubt caught |
|---|---|---|---|
| 10 | Wrote the sampler and found both problems while checking snippets | Whether to change the filter; it was not changed without his decision | Recruiters were being kept; one word was in 618 of 618 postings |
| 15 | Ran the sync | Added the missing file to the list | A check that passed while a file was absent |
| 25 | Compiled the design document in silent mode and built quickly | What to keep, what to drop, when to stop designing | The design and the code disagree in two places, which is how the plan gets corrected |

## Left out, with reasons
- **The full risk register and the data tables:** too large to show; one beat names them and the document stays public.
- **The domain model and invariants:** detail for a reader of the document, not a viewer of the film.
- **Figma, YouTube and quota specifics:** other films cover them.
- **The one run's counts:** may appear, labelled "fall 2026" with no narrower date.

## Evidence to produce before building
1. Capture `collect.py --help` and a directory listing as real terminal output.
2. Capture the real pages named above, as in film 1; Claude's and ChatGPT's front pages cannot be captured and are not shown.
3. Recheck every claim against the design document and, where the document cites a file, against the file.
4. Run no network collection for the film; the film reads files and a `--help`.

## Answered by Professor Bear, 2026-10-08
1. Title: "Bear's Agentic Approach to Finding Work."
2. Counts: allowed, labelled "fall 2026" only.
3. The not-built act: reframed as a plan that changes, the iteration idea (above).

## Open
1. Build film 2 now, with these changes?
2. Confirm the hesitant-writer phrase: "Plan everything before you build anything" corrected to "enough".
