# NEU prerequisite: explain your assignment with Brutalist

**Audience:** students taking INFO 7375 at Northeastern only  
**When:** optional preparation before your first optional recorded explanation  
**Practice material:** one completed Python exercise with saved results and a failure  
**Outcome:** a working video workflow for explaining your assignments

This is optional course preparation, not a numbered book lesson or an extra assignment. Neither NEU students nor independent readers are required to use Brutalist. Choose another suitable explainer workflow if preferred. Canvas determines actual submission requirements. The [AI policy](ai-policy.md) and [Relative Quartile rubric](relative-quartile.md) assess the quality of your explanation, not your choice of media tool.

Use your NEU-provisioned Claude Code access. This prerequisite uses [brutalist.art](https://github.com/nikbearbrown/brutalist.art), the public **dot** repository, not the instructor's larger `brutalist-art` sandbox. The media pipeline is free and local; Claude Code still uses your account allowance. No direct API credits, paid video service, voice cloning, or public upload is required.

## What you need to learn

Download the toolkit, prepare a small evidence folder, direct Claude to make a beat sheet, and review a rendered explanation. Learn enough to read the plan and request a correction; you do not need to learn Remotion or write a video engine.

## The Problem

A recording of “my code passed” does not explain the assignment. Your viewer needs to see the question, the mechanism, the result, and what that result does not establish. For example, in the prompt-contract exercise, valid JSON can still contain a false claim. Make that distinction visible.

## The Concept

A **beat** is one teaching moment. A **beat sheet** is the JSON plan containing narration and visual instructions for those moments. Claude writes it; you check that it explains your actual work. Narration audio is generated and measured first; visuals follow that clock.

The loop is simple: evidence → beat sheet → audio → review video → watch and revise → final file. The command `./art ai-explainer` points an agent to instructions; it is not a one-command autonomous video generator.

## Download and set up once

Use a parent folder containing your course checkout. The commands below assume you start **at the course repository root** and the sibling `brutalist.art` directory does not yet exist:

```bash
cd ..
git clone https://github.com/nikbearbrown/brutalist.art.git
cd brutalist.art
python3 -m venv .venv
source .venv/bin/activate
./setup --install
./setup
./art --list
git rev-parse HEAD
```

If the toolkit already exists, open that checkout; do not clone over it or reset its changes. Record its revision with your video. Reactivate its virtual environment in later sessions.

Before installing, have Claude inspect `README.md`, `CLAUDE.md`, and `setup`. You need Git, Python (use the course's 3.11+), Node 20+ with npm, and FFmpeg/ffprobe. The installer installs Python and Node packages, installs user fonts, and downloads the Kokoro model (roughly 340 MB). It does not install every system prerequisite. Let Claude explain missing items and propose the platform-appropriate fix before you approve system changes. Avoid the system Python environment.

LaTeX/dvisvgm is only needed for equation-rendering beats. For this first video, use existing chart/diagram components and avoid equation beats. The doctor may still report that unused feature as blocked: record it honestly and check that every feature your chosen reel uses is ready. A green readiness table is not proof of a successful video render. On Windows, ask for help with the toolkit's Bash environment rather than assuming these macOS/Linux commands run in PowerShell.

Start Claude Code from the activated toolkit environment with normal permissions:

```bash
claude
```

Do not copy old tutorial flags that bypass permission prompts. Only grant access to the toolkit and your sanitized assignment/reel folders.

## Prepare the evidence

Keep your existing Python assignment under `learning-artifacts/`. Ask Claude to create a new film project at `youtube/assignment-02-your-name/` in this course repository (use your actual assignment number and name). See the [film-folder conventions](../youtube/README.md). Do not overwrite an existing project. Give it only approved inputs:

- Your short notes: question, prediction, method, observed result, and one limitation.
- The actual Python file and the exact test command/output.
- Baseline and revised prompts with sanitized responses, including one failure.
- Underlying values for any chart, plus source/assistance credits.

Use any completed course exercise, such as the sampling report or prompt experiment. Do not fabricate results to get a video started. A reference demo is labeled as a reference fixture, not presented as your own implementation or a live Claude run.

Plan the explanation in plain language before rendering:

| Moment | What the viewer should see |
|---|---|
| Question and takeaway | What you tested and why it matters |
| Mechanism | A small real code excerpt or an input moving through the validator |
| Evidence | Your actual prompt/output and observed check |
| Failure and correction | What passed incorrectly, what you changed or checked next |
| Limit and handoff | What remains unproved and one experiment the viewer can try |

This is a planning outline, not a renderable beat-sheet schema. Claude maps it to the current builder's bookends and scene contracts. Keep one insight; use the time it needs rather than padding to a duration. Canvas supplies any required runtime.

## Direct Claude Code

Replace the bracketed paths and facts before pasting:

```text
Help me explain my INFO 7375 assignment using this brutalist.art checkout.
Read CLAUDE.md, README.md, RENDER-TARGETS.md, and the full
skills/make/ai-explainer/SKILL.md plus its required references.
Use the free beginner ai-explainer path, not an advanced or paid builder.
My approved evidence folder is [absolute assignment path].
My output reel folder is [absolute course path]/youtube/[unique-film-slug].
My name is [name]. My question is [question].
My observed result is [result with its evidence filename].
My one takeaway is [takeaway]; my limitation is [limitation].

First inspect the evidence and propose the teaching moments.
Use actual code and results, and label fixtures and reconstructed UI.
Do not imply a synthetic narrator is me, Bear, or an official endorsement.
Use local Kokoro am_onyx or af_bella; disclose synthetic narration.
Search the existing scene library before proposing custom visuals.
Keep assignment code Python; use existing toolkit components and keep the
Node/Remotion runtime outside the course. Do not modify reference solutions.
Show me narration and the evidence for each claim before building.
Wait for my review; never invent approval.

Then generate measured audio, build the review cut, run the toolkit checks,
and inspect rendered frames. Give me the real output path to watch.
After my feedback, fix the source, re-render, and verify the result.
Preserve beat_sheet.json, sources, build commands, and review notes.
No paid calls, direct Claude API calls, permission bypass, or publishing.
```

You may describe an observed problem in ordinary language: “The narration says five cases, but the chart shows four,” or “The code is too small to read.” Claude handles the technical correction.

## Render, watch, revise

Once the evidence and narration are reviewed, Claude can run these commands from the activated toolkit checkout. Replace the example absolute paths; do not run the placeholder literally.

```bash
python3 runtime/scripts/generate_audio_kokoro.py "/absolute/path/to/course/youtube/assignment-02-your-name"
./art run "/absolute/path/to/course/youtube/assignment-02-your-name"
./art todo "/absolute/path/to/course/youtube/assignment-02-your-name"
```

`run` builds the review cut; `todo` reports incomplete beats. Ask Claude for the actual output filename. Watch the entire review cut with sound. Check the numbers against your saved output, code readability, pronunciation, caption timing, and whether the failure is understandable. A file probe cannot make those judgments for you.

Record a timestamp, the problem, and the requested fix. If narration changes, regenerate and remeasure audio before recompiling; do not patch timing by guesswork. Clear required checks and missing-asset placeholders before making the final:

```bash
./art final "/absolute/path/to/course/youtube/assignment-02-your-name" --height 1080 --out "/absolute/path/to/course/youtube/assignment-02-your-name/final"
```

These preparation instructions explicitly choose a 1080p local master; upstream defaults to 4K. The explicit output folder avoids hunting in toolkit defaults. Watch the final too. A successful compile is not evidence that the teaching works.

## If you choose to include a recorded explanation

If using this Brutalist workflow, include the MP4, `beat_sheet.json`, sources and Claude/synthetic-narration disclosure, and one review/revision record with your assignment. Other workflows do not require a Brutalist beat sheet; provide your optional recording and relevant source/assistance credits. Keep the Python evidence alongside it. Submit through the course's assigned channel; do not publish to YouTube as part of this prerequisite. Canvas publishes Assignment deadlines; the optional video has no separate points.

If setup or rendering fails, keep the error log and draft, ask for instructor help, and say “render blocked”—not “video complete.” Do not purchase a service to work around it.

## Check the result

Can another student explain your finding after watching, locate the exact supporting output, and name its limitation? Show the before/after of your correction. Confirm that the final has audible narration, readable evidence, no unfinished slates, and no exposed secrets or private data.

## Irreducibly Human

Read [Tier 1's offloading boundary](../docs/irreducibly-human.md#foundations-before-offloading). Delegate video mechanics without delegating understanding.

**AI should:** Draft and structure the explanation, generate local narration, render visuals, run checks, and implement specific revision requests.

**Human should:** Supply truthful evidence, decide the takeaway, explain the Python mechanism, watch the complete video, and judge whether it teaches. Own the decision to submit or share it.

**Record the split:** Name one change you requested after watching and explain how it improved understanding, not just appearance.

## Sources and tutorial notes

The [Brutalist tutorial source guide](brutalist-video-sources.md) names the matched instructor beat sheets and the current upstream files used for these instructions. It also flags outdated installation, voice, and publishing advice. Reviewed 2026-09-06.
