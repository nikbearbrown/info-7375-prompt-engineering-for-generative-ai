# Series plan: Professor Bear Does His Assignments

Drafted 2026-10-07. Nothing here is built. Items in [brackets] are mine to confirm.

## Executive summary

**What this is.** A plan for a film series, and a full layout of film 1. The series is called **Professor Bear Does His Assignments**. Professor Bear does the same graded assignments his students do, in the same three courses, keeps the same process log, and films each stage as a dated diary entry: on this date, this is the state of the work.

**Why a series.** One film cannot show a project that is still being built. And the point of the project is the process, not the finished artifact: teachers can see what a student handed in, but not whether the student learned anything. A dated trail of what was tried, what broke and what changed is evidence of learning in a way the artifact is not.

**Film 1 says three things.** What he is doing and why. How the project fits together: one job-search tool, built live in three classes, each asking it a different question. And exactly where it stands today, 2026-10-07: it has run once, it reads 18 company job boards, it kept 97 postings out of 3,446, nothing runs on a schedule, and some of the work is still only a plan. It is told in third person by Liam, in for Bear, so the series title is literal.

**What is not yet decided.** Which assignment is film 3 (see the series list), and whether film 1 is also the final-project pitch film assignment.

## The series (a proposal)

Each film is dated and stands alone. A viewer who has seen none of the others can follow it.

| # | Working title | What it shows | State |
|---|---|---|---|
| 1 | What am I doing, and why | The point, the shape of the project, the state on 2026-10-07 | This plan |
| 2 | Specifying a tool with Gru | The Boondoggle Report in the skepticism course: a downloadable Gru; the wrong application and the build-before-spec mistakes, kept in the log | Work exists, log exists |
| 3 | Collecting the jobs | The data-pipeline assignment in the branding course: Lectern reading three applicant-tracking systems, the filter tuned across one day, the audit that found a bug in its own audit | Work exists; deliverables unfinished, past due |
| 4 | Does it still run tomorrow? | A second Lectern run, so there is a day-over-day difference to show; the question of scheduling | Not done |
| 5 | The probe runner | The skepticism course's third assignment: robustness and explanation | Planned, nothing built |
| 6 | Study mode and Learning Guide | A filmed trial of ChatGPT's Study mode and NotebookLM's Learning Guide on one real task, failures included | Research done, trial not run |
| 7 | The pitch film | Writing the final-project film assignment for students and taking their feedback | Assignment drafted |

[Which of these did you mean by "assignment three"? Branding's data pipeline is film 3 above; the skepticism course's probe runner is film 5.]

## Film 1: layout

**Form.** The `lecture` skill, Liam in for Bear, free local voice, no approval gates on free steps, never published without your word. Because it is made for the course, INFO 7375 is named at the opening and in the outro block. The film is self-contained: it assumes the viewer has seen none of the other films and read none of the books.

**Source.** The status report written on 2026-10-07 for the job-search project, the project brief, and the three FRICTIONAL logs. Everything not used in film 1 goes under "left out" with a reason, and most of it is saved for films 2 to 7.

**Opening (BIDEA).** The hesitant writer types the framing a newcomer arrives with and corrects one phrase: *"A professor assigns work."* becomes *"A professor does the work."* Liam's greeting is spoken over it.

**Key terms (BDEFS), five.** Frictional log: a dated record of what was tried, what went wrong and who did what. Job board: the page where a company lists open roles. Applicant tracking system: the software behind that page. Posting: one open role. Filter: the rules that keep a posting or throw it out.

### Act I: The point
| Beat | What the viewer sees | Best visual, runner-up |
|---|---|---|
| 1 | A stack of finished assignments; one is lifted and nothing inside it shows how it was made | Isometric drawing; runner-up a card |
| 2 | Next to it, a dated trail of entries growing line by line, with a failure in the middle | The real log on GitHub, captured; runner-up an isometric ledger |
| 3 | A teacher looks at both and can only judge the first | Isometric drawing; runner-up Manim diagram |
| 4 | Professor Bear's own folder in the course repository, then the same three course names | Real captured page; runner-up library icons |

Claim made aloud: that is the purpose he states, "evaluating real learning, not just the artifact." It is attributed to him, not presented as a finding.

### Act II: One project, three questions
| Beat | What the viewer sees | Best visual, runner-up |
|---|---|---|
| 5 | One box labelled with the tool's name, three arrows to three class labels | Manim diagram; runner-up icons |
| 6 | Each arrow carries its question: how do we know the output is right; whose problem does it solve; what is the recipe | Manim diagram on spoken cues; runner-up cards |
| 7 | The rule that keeps three copies from drifting: one master, shared code copied out, class writing never copied | Isometric conveyor between three boxes; runner-up Manim diagram |

### Act III: The state on 2026-10-07
| Beat | What the viewer sees | Best visual, runner-up |
|---|---|---|
| 8 | 18 company boards feed a funnel: 3,446 postings in, 97 out | Manim chart with the real numbers; runner-up isometric funnel |
| 9 | The real files on disk and their counts, read from the actual run outputs | Real command output on a plain terminal skin; runner-up a card |
| 10 | A calendar with exactly one marked day, and no schedule behind it | Manim diagram; runner-up isometric |
| 11 | Five boards the tool cannot read, shown as locked | Library icons; runner-up Manim |
| 12 | A CV with four empty slots, then a playlist filling a gap | The real playlist page, captured; runner-up icons |
| 13 | Two columns, "exists" and "not yet": the 36 films on one side; the unwritten book chapters, the unsigned rubric and the unfinished assignment on the other | Drawn table; runner-up isometric |

### Act IV: What went wrong
Four things from the log, each a few seconds: the tool specified for the wrong application and stopped; building started before the design existed; a bug in his own audit; a summary written about the wrong thing. Shown as the real log headings, captured. The film does not explain their causes; it only says they happened and that each is in the log. Films 2 and 3 do the explaining.

### Close
- **Recap (BVDT).** One bare sentence per act, four lines.
- **Your Turn (BHTF).** A prompt the viewer can paste: write one dated line about their own project, in the past tense for what exists and the future for what doesn't, then check each line against a file. Two checks follow.
- **Outro (BOUT).** The title, then "At Nik Bear Brown."

## What the film must not do
- Say "this chapter," "the book," or "in the last video."
- Call the 97 postings jobs. They are a measure of the filter, and the title audit found 23 false positives among them.
- Present an unsigned rubric, an unfinished assignment or a one-run tool as more than it is.
- Show a screen that was not captured or run for real.

## Evidence to produce before building
1. The counts, read from the run output files by a short script, and shown as the script's own output.
2. A capture of the public course-repository folder and of the Figma-series playlist page.
3. A capture of the real FRICTIONAL headings.
4. Every number rechecked in `FACTCHECK.md` against its file, with the status report treated as a pointer and not a source.

## Open questions for you
1. Which assignment is "assignment three" in your head?
2. Is film 1 also your 50-point pitch film, or is that a separate film?
3. Third person ("Professor Bear does...") for the whole series, or first person in diary entries after film 1?
4. May I capture the public GitHub and YouTube pages for the film?
