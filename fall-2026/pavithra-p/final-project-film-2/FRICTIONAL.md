# Frictional: DryRun Final Project Film

Pavithra Prasad · INFO 7375 · Final Project Film (four parts)

Commits in the course repo (`fall-2026/pavithra-p/final-project-film-2/`): final commit: the hash in the Canvas submission. Built from my pitch film, `fall-2026/pavithra-p/final-project-film/` (`4f17ea0`, October 2026).

My main prompts and inputs to Claude Code, 2026-11-23 (the rest is summarised):

- Pasted the professor's description of the film and asked to start from my submitted work.
- Confirmed the film is about DryRun, the final project I pitched in October.
- Asked to check the description line by line and include everything it asks for.
- Asked for a strict score of the script before anything was rendered, then: "Apply fixes".
- Brought a ChatGPT review of the draft and had each point checked against the files before applying it.
- Asked for a final grade as the strictest TA, then: "Yes, fix both".
- Asked for every Markdown file to be checked against my past TA feedback before pushing.

## 2026-11-23: Which project

- Claude Code first suggested making the film about the job-search agent from JS1 and JS2, because that code already exists. I kept DryRun: the film is about my final project, which is the one I pitched.
- Expected before building: I expected I could reuse most of my pitch and rearrange it into four parts, with only a few new scenes.

## 2026-11-23: The script, checked against the description

- The first draft reused the pitch's lines in the four parts and added new ones for the human approval, the data, the steps, the resources and the evaluation targets.
- Friction: when I asked for a line-by-line check against the description, the first draft fell short in three places. The opening line said "Python command-line tool" and "throwaway copy", which is the "how" that part 1 should leave out. Part 2 said what the other tools are, but not what they got. Part 3 did not name token credits, accounts, access and compute one by one.
- All three were fixed. Part 2 now uses what the `try` README and the InterCode and NL2SH abstracts say, read on 2026-11-23 (`evidence/prior-work-2026-11-23.md`).
- I opened the three pages myself (the `try` README and the two arXiv abstracts) and checked them against what part 2 says.
- Claude Code's strict score of the script came to about 21.5 out of 25. It named three more gaps: InterCode's result, the coding agents' own "allow this command?" prompt, and dates for each step. I applied all three.
- From my JS1 feedback (decide what is the truth before labelling): each task's correct end state will be written before any AI reply is seen, and it decides what counts as caught (`APPENDIX.md`, section 4).
- The facts in the resources line were checked on my Mac first: Claude Code 2.1.294 through my NEU account, Apple M3 with 8 GB, Docker 27.4.0, Ollama with `qwen2.5`.

## 2026-11-23: The film

- Eleven pitch beats kept their narration word for word. Fifteen beats are new or redrawn, each with a picture, because my pitch lost a point for being text-heavy. A kicker on every frame names the part ("PART 2 OF 4").
- A quick preview before the 4K render showed overlapping captions in two scenes (the data and the research). Both were fixed before rendering.
- Two 4K runs stopped on layout warnings: captions too close to the edge in the prior-work scenes (B07, B08). Both were fixed, and a layout check of every remaining scene found one more (B22), fixed before the final run (`reports/run-gates.log`).
- The gates that ran all passed on the delivered film: layout (26 of 26 scenes clean), visual QC (0 blockers, 0 major), type check, loudness, master check and sharpness. The master check's duration sub-check was skipped, because its file (`clock_check.py`) is missing from the toolkit, as in my pitch, so the film's length was compared with the narration total instead (the film is 263.25 s and the narration totals 262.73 s; each beat is rounded up to whole frames, and those beats add up to exactly 263.25 s).

## 2026-11-23: A ChatGPT review of the draft

- ChatGPT, as a strict TA, scored the draft 22.5 out of 25 and named four issues. Claude Code checked each one against the files, and all four were real.
- The biggest: the evaluation counted a correct command that gets WARN as "wrongly blocked", although a person can still approve it. The appendix now counts wrong blocks and wrong warnings separately, and the 1-in-10 target in the film is for blocks.
- Two lines were too absolute and were changed and re-rendered: B05 "A deleted file can't be taken back" is now "A delete command has no undo step" (a backup could restore a file), and B07 now says Claude Code "can ask you to approve a command before it runs" (it depends on its permission settings).
- This log said "every gate passes", but one sub-check was skipped. It now says so.
- A second ChatGPT check of the fixed draft found two appendix sentences still using the old wording (a deleted file can't be taken back; the agent always asks first). Both now match the film. No re-render was needed.

## 2026-11-23: A strictest-TA check before pushing

- I asked Claude Code for a final grade as the strictest TA. It gave 23.5 out of 25 and named two gaps, both in the appendix: part 2 left out ShellCheck and explainshell, the tools that read a command's text, and the evaluation had no fixed task counts, so "1 in 10" had no count behind it.
- Both were fixed in `APPENDIX.md`, with no re-render: two prior-work rows (read on 2026-11-23, `evidence/prior-work-2026-11-23.md`), and fixed numbers: 30 tasks, 10 of them held out, six planted wrong commands, at most 90 Claude replies. The Claude vs local model comparison is now reported side by side, not used as a pass or fail test.
- Then every Markdown file was checked against my past TA feedback: Week 1 (reflections in my own words), the pitch (shown, not asserted; Frictional traceability to commits and prompts) and JS1 (decide what is the truth before labelling). One gap was found: the appendix's November 30 step did not say that the planted changes and their expected diff are written before the runner, the next step my pitch feedback gave. It does now.

## Human and AI contributions

- I did: kept DryRun as the film's project, asked for the line-by-line check and the strict score, applied the fixes, checked the three prior-work pages myself, got the ChatGPT review and decided to apply it, asked for a strictest-TA grade before pushing, and gave the reflection lines below.
- Claude Code: drafted the four-part script from my pitch, read the three sources, checked the resources on my Mac, wrote the new scenes and documents, and ran the toolkit and its gates.
- Accepted: the four-part script, the three fixes, the dated steps, reusing the pitch beats word for word, all four points from the ChatGPT review, and the two appendix fixes from the strictest-TA check, with the task counts Claude Code suggested (30 tasks, 10 held out).
- Changed: the opening line, from how DryRun works to what it does and why.
- Rejected: making the film about the job-search agent.

## What I learned, and what is unresolved

- I learned that checking the script against each requirement before rendering caught gaps I had missed, especially the missing results from prior work and the resources I would need.
- Unresolved: no DryRun code exists yet. The film is a plan, and its targets are not measured. Next step, the one my pitch feedback gave: the first piece by November 30, the copy, the run and the file differences, with its planted changes and their expected diff written before the runner.
