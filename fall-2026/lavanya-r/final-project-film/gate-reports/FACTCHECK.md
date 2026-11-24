# FACTCHECK: README Checker pitch film

Status: cut 4 (2026-11-23). Rows 1–21 were reviewed and approved by Lavanya R on 2026-10-14 for cut 3. Rows 22–31 are new in cut 4 and were reviewed and approved by Lavanya R on 2026-11-23, after watching cut 4. That approval includes the evaluation targets (row 30), the sample-set plan and the Claude Code resource line (rows 29–30). Rows 12–14 and 21 refer to beats cut from cut 4 and are kept for the record.

| # | Beat | Claim | Verdict | Source | Fix |
|---|---|---|---|---|---|
| 1 | BHELLO | Nothing is built yet | PASS | No README Checker code exists as of 2026-10-13 | — |
| 2 | B01 | On Oct 13 I followed my webapp README exactly as written | PASS | My terminal session, 2026-10-13, fresh clone at ~/Desktop/readme-test | — |
| 3 | B01 | The clone step had a placeholder | PASS | webapp README step 1: `git clone <repository-url>` | — |
| 4 | B01 | The database step failed on a missing config file | PASS | `yarn sequelize db:migrate` → `Cannot find ".../config/config.json"` | — |
| 5 | B01 | The health check returned 503 | PASS | `curl -i localhost:8080/healthz` → `HTTP/1.1 503 Service Unavailable` | — |
| 6 | B02 | Heroku's starter README worked | PASS | `npm start` → `Listening on 5006`; `curl localhost:5006` → `200 OK` | — |
| 7 | B02 | Its README asked for a tool I didn't need | PASS | README lists Heroku CLI; `heroku: command not found`; the app still ran | — |
| 8 | B02 | It skipped the npm version it wanted | PASS | `npm warn EBADENGINE required npm 12.x, current 10.9.0`; the README only names Node.js | — |
| 9 | B03–B05, B07–B11 | Tool behaviour (will run, will write a report, etc.) | EXEMPT | Plans, spoken in the future tense; the report is labelled "constructed mock-up" | — |
| 10 | B06 | My CI installs Node and the database with its own steps | PASS | webapp `ci.yml`: `setup-node` with node-version 18 and a `postgres:14.16` service | — |
| 11 | B08 | The numbers don't exist yet | PASS | No evaluation has been run | — |
| 12 | B12 | My public repo has GitHub Actions workflows and AWS and GCP machine images | PASS | webapp: 3 workflows in `.github/workflows/`, `packer/machine-image.pkr.hcl`; README title "Health Check API - AWS, GCP" | — |
| 13 | B12 | Docker: no public proof yet | PASS | No Dockerfile in my public repos that I could point to (my own statement, 2026-10-13) | — |
| 14 | B13 | Exists today: this pitch, two README tests, that repo | PASS | Items 2–8 and 12 | — |
| 15 | B01 | My webapp README: per-step marks, with "placeholder", "missing file" and "503" | PASS | My run 2026-10-13 (step 1 placeholder, step 3 config.json missing, step 7 → 503) | — |
| 16 | B01T | Terminal lines `ERROR: Cannot find ".../config/config.json".` and `HTTP/1.1 503 Service Unavailable` | PASS | Copied from my terminal output, 2026-10-13; the long path is shortened to "…" | — |
| 17 | B02 | Heroku README: per-step marks, "it worked", "2 small warnings" | PASS | My run 2026-10-13: 200 OK; warnings were the Heroku CLI not being needed and the npm version | — |
| 18 | B02T | `npm warn EBADENGINE … npm: '12.x' }` and `HTTP/1.1 200 OK` | PASS | Copied from my terminal output, 2026-10-13; the middle of the long line is shortened to "…" | — |
| 19 | B05 | Report rows: step 1 warning (placeholder), step 3 fail (missing file), step 5 warning (placeholder) | EXEMPT | Constructed mock-up, labelled on screen; the rows match my real run | — |
| 20 | B06 | My CI pipeline runs its own steps; my README is never run by CI | PASS | webapp/.github/workflows/ci.yml (setup-node 18, postgres 14.16 service, yarn install) | — |
| 21 | B07 | `$ readme-check ./sample-app` | EXEMPT | Planned command, labelled "planned command (constructed)" on screen | — |
| 22 | B06A | Runme runs a README's code blocks; it doesn't judge the output | PASS | github.com/runmedev/runme (formerly stateful/runme): runs named code blocks from Markdown | — |
| 23 | B06A | Doc Detective checks docs against the product, using tests you write first | PASS | github.com/doc-detective/doc-detective: parses test specs / marked-up docs and runs them, mostly in a browser | — |
| 24 | B06B | ExecutionAgent (2025) set up and tested 33 of 50 open-source projects | PASS | Bouzenia & Pradel, "You Name It, I Run It", ISSTA 2025, arXiv 2412.10133: "installs and tests 33 out of 50 projects" | — |
| 25 | B06B | Installamatic installed 21 of 40 Python projects | PASS | Milliken, Kang & Yoo, "Beyond pip install", SANER 2025, arXiv 2412.06294: 21 / 40 repositories (55%) | — |
| 26 | B06B, B06C | Both aim to get a project running, not to say which README line is wrong | PASS (characterization) | Both papers measure install/test success; neither reports README-line faults | — |
| 27 | B06C | Comparison table marks (by hand / CI / doc tools / AI agents / README Checker) | EXEMPT (summary) | Summarizes rows 6–8, 10, 22–26; the README Checker row is labelled "(planned)" | — |
| 28 | B05C | Docker is installed on my laptop (version 29.1) | PASS | `docker --version` → Docker version 29.1.2, 2026-11-23 | — |
| 29 | B05C | I already used Claude Code on my university login for a course agent | PASS | INFO 7375 JS1 job-search agent: Claude judge runs through `claude -p` on my NEU login (submitted 2026-10-30) | — |
| 30 | B05A, B05B, B05C, B08, B08A | Sample set, build order, ~1 model call per step, metrics, thresholds | EXEMPT | Plans and targets, spoken in the future tense; B08A is labelled "targets set now, before anything is built" | — |
| 31 | B00A | "It only reports. It won't fix anything." | EXEMPT | Scope decision from PROJECT-BRIEF.md §5 | — |
