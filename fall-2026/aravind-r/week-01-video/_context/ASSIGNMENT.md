# Week 1 Explainer Video — Explain One Concept from Chapter 1

Due: Canvas · Points: 25 · Source: Chapter 1 — Randomness and first prompts
(Copied from the assignment text the student pasted into Claude Code on 2026-09-26. Canvas is authoritative.)

Read the course AI policy and watch *AI Policy for Professor Bear's Courses | Using AI Responsibly in Class*.

**Policy note.** The syllabus says an explainer video is optional, carries no separate point category, and that using Brutalist earns no automatic bonus. This assignment supersedes that for Week 1 only, and it is worth 25 points rather than the standard 100. Canvas is the authority on which version applies to your section. The unreconciled wording is logged in instructor decisions, item 7.

## The task
Pick one concept from Chapter 1 and explain it well in a short video built with Brutalist.
One concept. Not a chapter summary. Pick the smallest idea you can explain completely, and spend the whole runtime on it.
Target length: 2–4 minutes. Shorter is allowed if the concept is genuinely done. Padding to reach a number is visible and costs you under Relative Quartile.
Brutalist (Film as Code) playlist: watch the first 3 or 4 videos to learn the system.

## Choosing a concept (examples)
Part 1: a chatbot is one next-token prediction run in a loop · the unit is a token, not a word · roles are text in a document · what pretraining actually targets · why preference tuning can prefer a confident wrong answer · a training-scale slogan restated as a division with a hidden assumption · attention: how "river" changes the vector for "bank" · the stochastic-parrot argument's two halves.
Part 2: why three scores are not yet three chances · **why subtracting the maximum changes the intermediates but not the distribution** · temperature as a concentration control · [1000, 1000] → [0.5, 0.5] · expected count (665.24) vs observed count (630) · a seed makes a run repeatable, not true · constraining the output format narrows the spread without checking anything.
A concept not on the list is fine if it comes from Chapter 1.

## What "explain it well" means
- **Show the mechanism, do not assert it.** The numbers should move on screen. A slide that says "this is numerically stable" while you talk over it is not an explanation.
- **Use a worked example with real numbers.** Run `lessons/01-randomness-and-first-prompts/code/main.py` and use what it actually prints. Do not invent plausible-looking figures.
- **Name one thing your explanation does not establish.**
- **Label constructed illustrations as constructed.** If you show a Claude response, it must be a real one you actually got, **with the date**.
A video that fabricates a Claude transcript has failed the assignment on its own terms, regardless of production quality.

## Using Brutalist
Clone `https://github.com/nikbearbrown/brutalist.art` and work from its README. Free pipeline only: Kokoro narration is local and free; Manim and Remotion render locally. No paid generation, no API keys, no media account, and no YouTube upload. Submit the file.
The prerequisite guide explains the optional workflow and quality expectations; `brutalist-video-sources.md` covers crediting anything you did not make.
If the toolkit fails on your machine, that is a legitimate Frictional entry: record what you tried, what broke, and what you did instead.

## Deliverables
Canvas: `LastName_FirstName_INFO7375_Week01_Video.zip`. GitHub: `fall-2026/first-name-last-initial/week-01-video/`.
- `README.md`: name, concept, one sentence on why, runtime, how to rebuild
- The rendered video (mp4)
- `beat_sheet.json`: the reviewed narration and visual plan
- `BUILD-PROMPT.md`: the prompts and commands that rebuild it
- `SOURCES.md`: what you used, what you made, what Claude contributed, any third-party asset with its licence
- `FRICTIONAL.md`: dated entries, per the Frictional guide
Include the GitHub folder link and final commit hash in Canvas. Omit caches, credentials, and private conversation transcripts.

## Rubric — 25 points
| Component | Points |
|---|---|
| Explanation of the concept | 15 |
| Frictional (honest log) | 2.5 |
| GitHub version posting matching Canvas | 2.5 |
| Relative Quartile | 5 |

Explanation (15): correctly explained and every claim defensible (6) · mechanism shown through motion, a worked example, or real output (4) · numbers real and reproducible; constructed illustrations labelled (3) · names one thing it does not establish (2).
Relative Quartile (5): specificity, substantive improvement, demonstrated understanding, evidence, honesty about verification, usability, professional communication, judged across the whole group. Production polish counts only as professional communication.

## You must be able to explain it
You may use Claude throughout. Name what it contributed in SOURCES.md. You remain responsible: the instructor or a TA may ask you to explain any part of the video, the beat sheet, or the build. Misrepresenting what was verified is an academic integrity matter.

## Related course requirement (prerequisites/brutalist-video.md)
"Use local Kokoro am_onyx or af_bella; disclose synthetic narration." · "Do not imply a synthetic narrator is me, Bear, or an official endorsement." · Include "sources and Claude/synthetic-narration disclosure".
