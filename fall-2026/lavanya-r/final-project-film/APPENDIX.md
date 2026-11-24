# APPENDIX — README Checker (pitch film, cut 4)

**Lavanya R · INFO 7375 · Final project pitch · Updated 2026-11-23**

This holds the detail the film keeps out of its executive summary. The film follows four parts:
what and why, what already exists, methods, and evaluation. Nothing in the README Checker has been
built yet. Everything about the tool is planned work, written as "will".

## A. What already exists (Part 2 sources)

| Approach | What it does | What it got | Why it doesn't answer "which README line is wrong?" |
|---|---|---|---|
| Following a README by hand | A person runs each step | My two runs on 2026-10-13: my `webapp` README failed (placeholder, missing `config/config.json`, 503); Heroku's starter README worked with two unmentioned gaps | Finds only what a person happens to hit, and costs a person's time for every README |
| CI (GitHub Actions) | Runs build and test steps written for CI | My `webapp` `ci.yml` installs Node 18 and a `postgres:14.16` service itself | CI never reads the README, so it can pass while the README is wrong |
| Runme ([runmedev/runme](https://github.com/runmedev/runme)) | Runs code blocks from a Markdown file | Runs blocks and shows their output | Leaves judging the output to the person |
| Doc Detective ([doc-detective/doc-detective](https://github.com/doc-detective/doc-detective)) | Tests docs against the product, mostly in a browser | Pass/fail per test you define | Needs test specs or marked-up docs written first |
| ExecutionAgent (Bouzenia & Pradel, ISSTA 2025, [arXiv 2412.10133](https://arxiv.org/abs/2412.10133)) | LLM agent that installs a project and runs its tests | 33 of 50 projects | Goal is to get the project running by any route, not to diagnose the README |
| Installamatic (Milliken, Kang & Yoo, SANER 2025, [arXiv 2412.06294](https://arxiv.org/abs/2412.06294)) | LLM agent that writes a Dockerfile to install a Python repo | 21 of 40 repositories (55%) | Same: measures install success, not README faults |

**The gap:** none of these follows a README exactly as written and reports which line broke, on a
README nobody prepared for testing. That is what the README Checker will do.

## B. Methods (Part 3)

### B1. What I'll build
A Python command-line tool in a public GitHub repo. For each README setup step it will:
1. run the step in a fresh Docker container with no secrets and no access to my files;
2. read the real exit code and output;
3. let Claude decide the next move: **continue**, **stop**, or mark the step **unclear**. The model
   picks the move; the verdict comes from the command that actually ran.

It writes `report.md`: pass, warning or fail for each step, citing the README line and the real
error. It only reports. It will not fix the README.

### B2. Data
About ten small sample projects that I will make myself:
- **Five broken:** each gets one planted problem of a kind I hit by hand (for example a missing
  config file, a placeholder clone link, a missing dependency, a wrong command, an unmentioned
  version requirement).
- **Five working:** the README is correct, so any "fail" on these is a false alarm.
- **Answer key:** for every sample, which README line is broken (if any) and why. It is written
  before the tool is run on that sample.

### B3. Build order
1. **Runner (first milestone):** one sample README runs in a container and writes `report.md` with a
   real exit code for every step. *Done when:* `report.md` exists and every row has an exit code.
2. **Agent loop:** add Claude's continue / stop / unclear decision, under a **prompt contract** (a
   fixed output format) that my code validates, with tests that reject malformed output.
3. **Samples and answer key:** build the ten projects and write the key.
4. **Evaluation:** run all ten, score against the key, and write up where Claude was wrong and how I
   caught it.

### B4. Resources

| Need | What I have | Checked |
|---|---|---|
| Container runtime | Docker 29.1.2 on my laptop | `docker --version`, 2026-11-23 |
| Code hosting | My GitHub account (LavanyaRajesh24); the tool goes in a new public repo | — |
| Model access | Claude Code on my Northeastern login, called non-interactively (`claude -p`); already used as the judge in my JS1 job-search agent | JS1, submitted 2026-10-30 |
| Token budget | About one model call per README step: ten samples × roughly 5–7 steps is well under a hundred calls per full evaluation run | Estimate |
| Compute | My laptop; no cloud machines needed | — |

### B5. Safety and limits
- A README can contain any command, so every step runs only in a disposable container with no
  secrets and no access to my files, deleted after each run.
- Vague steps ("set up your database") are marked **unclear**, not guessed.
- Out of scope: projects that need secrets, paid services or a GUI.

## C. Evaluation (Part 4)

**Measured on the ten samples, against the answer key:**
- **Catch rate:** planted problems flagged as fail or warning **at the right README line** (out of 5).
- **False alarms:** fails raised on the five working samples (plus any fail on a broken sample's
  correct lines).
- **Grounding check:** every verdict in `report.md` must trace to a saved exit code and output.

**Targets, set before anything is built:**

| Result | Verdict |
|---|---|
| At least 4 of 5 caught at the right line, at most 1 false alarm, every verdict backed by a real exit code | **It worked** |
| 3 or fewer caught, **or** 2 or more false alarms, **or** any verdict without a real command behind it | **It didn't work** |

Either way, the write-up lists every miss and false alarm, and where Claude's decision was wrong.

## D. Moved out of the film in cut 4
To fit the four parts in under four minutes, these cut-3 beats now live here and in
`PROJECT-BRIEF.md` instead of on screen:
- **Terms** (README, container, agent loop): the method beats now explain them in passing.
- **Who opens it:** a hiring manager runs one command on a sample project and gets a report in
  about a minute (planned command, constructed: `readme-check ./sample-app`).
- **Course skills it will show:** agent loop, verification with real output, evaluation with a
  score, source grounding to README lines, and a prompt contract checked by code.
- **Why this project:** CI/CD and cloud proof in github.com/LavanyaRajesh24/webapp; Docker used but
  with no public proof yet; agent loops, evaluation, grounding and prompt contracts are new to me.
- **Exists today:** the pitch film, my two README tests, and the `webapp` repo. The tool, the
  samples and the scores will exist later.
