# 01 — Brief

Drafted by Claude Code, reviewed by Tushar
Date: Nov 3, 2026

Adapted from the pitch's `PROJECT-BRIEF.md` (course repo, `fall-2026/tushar-p/final-project-film/`) and the current decisions in `PLAN.md`. Nothing is built yet; everything below describes what the project will do.

## The need

An agent saying "done" is not the same as the task being done. Agent Proving Ground will run an AI coding agent on small tasks inside an isolated Kubernetes (kind) sandbox, record every step as a trace, and decide PASS or FAIL with a deterministic check that the harness runs itself (D11). It will give one local command that answers three questions:

1. Did the agent's change pass the checks?
2. Did the agent stay inside the sandbox and the permission policy?
3. Did the latest prompt or model change make results better or worse (`apg compare`)?

Tools that cover one piece already exist (E2B for sandboxes, Langfuse for traces and scores). This project will join sandbox, trace, and verification into one small, self-hostable loop.

## Who owns it

Tushar Patel, as the INFO7375 final project. Tushar owns the task contracts and checks, the policy, stop and gate rules and their tests, the dev/held-out split, the premortem choice, FRICTIONAL.md, and sign-off. Claude Code builds the code and drafts the packet docs for Tushar's review (D14, D17).

## Who is affected

- **Tushar:** builds, runs, and answers for every claim.
- **The TA and graders:** will read the packet and may run the demo.
- **Readers of the public repo** (hiring managers, engineers on agent-infrastructure teams): will read the README, run one command, and open a trace.
- **Cost:** API calls will be billed to Tushar's Console workspace `apg-harness`, which has a spend limit.
- **No one else's data:** tasks will be synthetic, written by Tushar. No real users, customers, or private code will be involved.

## What success looks like

Each item is a "Done when" line in `PLAN.md`; none has happened yet.

- `apg run 001` will print one result line (task, PASS/FAIL, steps, exit reason) and write `traces/<run_id>.json` listing every step.
- Denied tool calls will appear in the trace and never execute.
- An agent that says "done" while the check fails will not get PASS.
- `apg eval` will print a results table (task, PASS/FAIL, steps, denied, exit reason, cost) for 12–20 tasks, including at least 5 designed to make the system say no.
- `apg show <trace>` will print a run step by step; `apg compare <run-a> <run-b>` will print per-task changes and the pass-rate delta.
- One test per sandbox limit (no network, non-root, no service-account token, CPU and memory limits) will pass, with results saved for `docs/07-evidence.md`.
- One controlled failure from `docs/06-premortem.md` will be triggered on purpose, caught by an independent check, and recovered.
- A stranger will run `./demo.sh` from the README alone.

## What it is not for

- Not a hosted or multi-user service. It will run on one laptop.
- Not for production agents or production traffic.
- Not a model benchmark. With 12–20 tasks and a few runs each, it will not support statistically strong claims about models in general.
- Not for cloud deployment (EKS) or OpenTelemetry. Those are out of scope for this course project.

## What would make it inappropriate

- Running it on tasks that need real secrets, credentials, or private or customer code.
- Running tasks that need network access, which the sandbox will deny by design.
- Running untrusted, multi-tenant workloads. A local kind cluster is not a hardened isolation boundary.
- Treating its PASS as evidence about code or agents beyond the synthetic tasks it checks.
- Running it without the Console spend limit, or with the API key placed anywhere but the environment.

## Changed since the pitch brief

- **D16:** Kubernetes (kind) from the start. The brief planned Docker first, then a move to kind; Docker is now only a fallback if task 001 cannot run on kind by Thu Nov 12.
- **D14:** Claude Code writes the agent loop. The brief said Tushar would write it by hand; the official Anthropic Go SDK is unchanged (D2).
- **D15:** added `apg compare`, the denied column, `apg show`, `FAILURES.md`, and `demo.sh`.
