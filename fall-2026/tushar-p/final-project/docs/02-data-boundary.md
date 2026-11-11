# 02 — Data boundary

Drafted by Claude Code, reviewed by Tushar
Date: Nov 3, 2026

Every source the project will touch, with a label: **public**, **synthetic**, **internal**, **personal**, **unknown**, or **credential**. Nothing is built yet; rows describe planned handling unless they say otherwise.

| Source / file | Label | Where it lives | Retention | Deletion |
|---|---|---|---|---|
| Task repos, contracts, checks (`tasks/*/repo/`, `contract.json`, `check.sh`) | synthetic (written by Tushar) | This public repo; copied into the sandbox pod for each run | Life of the repo | `git rm`; earlier versions stay in public git history and any forks |
| Python base image (`python:3.12-slim`, built as `apg-sandbox:dev`) | public | Docker Hub; local Docker image cache; the kind node's image store after `kind load` | Until pruned or the cluster is deleted | `docker image rm`; `kind delete cluster` |
| Go dependencies (`github.com/anthropics/anthropic-sdk-go` and its transitive deps) | public | Go module cache (`~/go/pkg/mod`); `go.mod`/`go.sum` in the repo pin versions | Until the cache is cleaned | `go clean -modcache`; remove from `go.mod` |
| Traces (`traces/<run_id>.json`) | synthetic (synthetic tasks plus model output about them) | Local `traces/` folder. **Whether traces are committed to the public repo is not decided yet.** | Not decided yet | Delete the file; if committed, it stays in git history |
| Eval log (`results/eval-log.jsonl`) | synthetic | Local `results/` folder. **Whether it is committed is not decided yet.** | Not decided yet | Delete the file; if committed, it stays in git history |
| `ANTHROPIC_API_KEY` (Console workspace `apg-harness`) | credential | Environment only, set in `~/.zshrc`. Never in the repo, a trace, a log, or a sandbox pod | Until revoked | Revoke or rotate the key in the Anthropic Console |
| Data sent to the Claude API by the harness (task contract text, file contents and command output from the sandbox, tool calls and results) | synthetic | Anthropic's API backend | Anthropic API: "we automatically delete inputs and outputs on our backend within 30 days of receipt or generation", with exceptions for longer-retention services under your control (e.g. Files API), agreements such as zero data retention, Usage Policy enforcement, and law. Flagged Usage Policy violations: inputs and outputs "for up to 2 years". [1] Not used for training by default. [2] | Automatic per [1]; no manual deletion path is stated for API inputs and outputs |
| Claude Code transcripts (building this project) | internal | Local: plaintext under `~/.claude/projects/`. The conversation content is also sent to Anthropic to run Claude Code, under Tushar's university enterprise plan | Local: 30 days by default (`cleanupPeriodDays`). Anthropic side, commercial users (Team, Enterprise, API): "Standard: 30-day retention period". [3] **UNVERIFIED** that the university plan is on these standard commercial terms; Tushar to confirm with the university | Local: delete files under `~/.claude/projects/`. Anthropic side: per [3]. Transcripts sent via `/feedback`, `/bug`, or `/share` are kept 5 years [3], so don't send them |
| `FRICTIONAL.md` | personal (Tushar's own reflections) | This public repo; the course repo copy at each milestone | Life of both repos | `git rm`; stays in git history of both repos |
| Demo video (MP4, T7.4) | personal (Tushar's screen and voice) | Local only; kept out of GitHub (T7.4). Its filename and SHA-256 will be recorded in the packet. Submission channel not decided yet | Not decided yet | Delete the local file |
| Course repo copy (`fall-2026/tushar-p/final-project/`) | internal (course submission) | The course's GitHub repo | Set by the course | Course repo rules; stays in its git history |

## Sources

Read by Claude Code (web fetch) on Nov 3, 2026:

1. Anthropic Privacy Center, "How long do you store my organization's data?" (page dated July 1, 2026). https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data (redirected from privacy.anthropic.com)
2. Anthropic Privacy Center, "Is my data used for model training?" (page dated August 18, 2026): "By default, we will not use your inputs or outputs from our commercial products (e.g. Claude for Work, Anthropic API, Claude Gov, etc.) to train our models." https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training
3. Claude Code docs, "Data usage" (undated). https://code.claude.com/docs/en/data-usage
