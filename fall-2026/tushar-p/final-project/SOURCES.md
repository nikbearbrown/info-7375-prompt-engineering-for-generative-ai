# SOURCES

Drafted by Claude Code, reviewed by Tushar
Date: Nov 3, 2026

## Tools used so far

| Tool | Version | Role | License (where it was checked) |
|---|---|---|---|
| Go | 1.27.3 darwin/arm64 | Language and toolchain; `go mod init`, `go build` | BSD-3-Clause (GitHub license API for `golang/go`, checked Nov 3, 2026) |
| git | 2.52.0 | Version control | GPL-2.0 (the `COPYING` file in `git/git`, checked Nov 3, 2026) |
| GitHub CLI (`gh`) | 2.101.0 | Created the public repo and pushed | MIT (GitHub license API for `cli/cli`, checked Nov 3, 2026) |
| Docker Desktop | Desktop version not recorded; `docker` CLI 29.7.2 on Nov 3, 2026 | `docker run hello-world` (T0.1) and the dockerver exercise (T0.3) | Docker's own subscription terms; not checked |
| Claude Code | 2.1.306 at T0.1; 2.1.317 on Nov 3, 2026 | Build agent (D6, D14) | Anthropic's terms, under Tushar's university enterprise plan; not separately checked |

## Planned (not used yet)

| Item | Will be used for | License (where it was checked) |
|---|---|---|
| kind | Local Kubernetes cluster for the sandbox (D16) | Apache-2.0 (GitHub license API for `kubernetes-sigs/kind`, checked Nov 3, 2026) |
| kubectl | Pod control from Go via `os/exec` | Apache-2.0 (GitHub license API for `kubernetes/kubectl`, checked Nov 3, 2026) |
| `python:3.12-slim` image | Sandbox base image (Debian-based) | Image Dockerfiles: MIT (`docker-library/python`). CPython: Python Software Foundation License Version 2 (the `LICENSE` file in `python/cpython`, checked Nov 3, 2026). The Debian packages inside carry their own licenses; not checked |
| pytest | Task checks inside the sandbox | MIT (GitHub license API for `pytest-dev/pytest`, checked Nov 3, 2026) |
| `github.com/anthropics/anthropic-sdk-go` | Claude API calls from the agent loop (D2; approved dependency in CLAUDE.md) | Apache-2.0 (GitHub license API, checked Nov 3, 2026) |
| Claude models via the Anthropic API | The agent the harness will run; model not chosen yet | Anthropic commercial terms |
| Calico (only if kindnet does not enforce NetworkPolicy) | Enforcing default-deny egress (T1.2) | Apache-2.0 (GitHub license API for `projectcalico/calico`, checked Nov 3, 2026) |

## What Tushar wrote or did

- T0.1: installed and checked the toolchain, set up the `apg-harness` Console workspace with a spend limit, and ran the test API call.
- T0.3: wrote the `dockerver` exercise by hand, outside this repo, and explained it.
- Every decision in the `PLAN.md` Decision log (D1–D17).
- Edited `PLAN.md` and `CLAUDE.md` after Claude drafted them, and specified every later change Claude Code made to them.
- The pitch film and its brief; see the film's own `SOURCES.md` in the course repo (`fall-2026/tushar-p/final-project-film/SOURCES.md`).

## What Claude contributed so far

- **Claude (claude.ai Project chat)** drafted `PLAN.md`, `CLAUDE.md`, and the pitch's `PROJECT-BRIEF.md`. Tushar edited them.
- **Claude Code** (at Tushar's request, with Tushar reviewing each diff before commit):
  - wrote `.gitignore`, `README.md`, and `LICENSE` (the standard MIT text), and ran `go mod init` to create `go.mod`
  - created the public GitHub repo with `gh` and pushed, after Tushar approved
  - made the `PLAN.md` edits Tushar specified: task ticks, the kubernetes-first replan (D14–D16), and D17
  - made the `CLAUDE.md` and `README.md` edits Tushar specified
  - drafted `docs/01-brief.md`, `docs/02-data-boundary.md`, `docs/06-premortem.md`, and this file for Tushar's review, and created the `FRICTIONAL.md` header (no entries)
  - looked up the licenses in the tables above and fetched the Anthropic data-retention pages cited in `docs/02-data-boundary.md`

The Claude Code session on Nov 3, 2026 ran on Claude Opus 5.5 (`claude-opus-5-5`).

## This repo's license

MIT, copyright 2026 Tushar Patel (`LICENSE`).
