# Klaxon: project brief

Aravind Sundaravadivelu · INFO 7375 final project pitch · 2026-10-09 · drafted with Claude from my planning notes, checked by me

**1. What is it?** Klaxon will be an AI on-call engineer for a payments system: when an alert fires, it investigates, proposes a fix with evidence, waits for a person to approve it, and then checks that the system is healthy and the money is right. Done, it will be a public GitHub repo: a small payments system with a fake Stripe-like provider, incidents with known causes, the agent, and an evaluation report. Stack: Python, PostgreSQL, Kafka, Redis, Docker Compose, Kubernetes, Claude, an MCP server built from scratch.

**2. Why would anyone care?** Providers deliver webhooks at least once, so a payment can arrive twice. If the code books it twice, the money is wrong while every request returns 200. Alternatives I looked at: **HolmesGPT**, an open-source SRE agent whose deployment check compares "error rates, latency, restarts, and logs", and the **manual way**, an engineer with Grafana and a runbook. In HolmesGPT's docs I did not find a built-in check that the money is right. So Klaxon will save a payments on-call engineer from approving a fix that looks green while the money is still wrong, and publish how often its diagnosis is right.

**3. Who opens it?** A hiring manager or senior engineer hiring for new-grad backend or infrastructure roles. In the first minute, the README will walk one incident to a passing money check, and one command will replay a recorded, dated Claude run on their machine, with no API key.

**4. What does it prove?** The course skills, each in a part you can open: a prompt contract (a validated diagnosis format), source grounding (every claim cites a metric, log line or trace), a bounded agent loop with budgets and an approval gate, verification after every fix, and an evaluation of accuracy, time and cost. A reviewer could fairly conclude that I can build a gated agent, check its claims and measure where it fails; not that it could run a real company's on-call. Evidence: the tests, traces and evaluation report.

**5. In, out, first.** In: one demo payments system, six incident types, approved fixes with rollback, health and money checks, an evaluation. Out, on purpose: Klaxon will never act without a person's approval, or on a system I don't own. First: the money check, which already ran (below).

**6. What could sink it?** Klaxon grading its own homework: I build both the incidents and the agent, so the incidents could be too easy. I will write the incidents and answers first, hold out a set the agent never sees during development, add misleading symptoms, and report the failures. Second risk, scope: a fixed cut order (Terraform, then Go, then the web panel).

**7. Why this project?** I wanted a real product idea that one person can build small, that uses the skills in the jobs I'm applying for, and that can be my final project for both of my courses. A mix of showing off and learning. Already mine: webhooks, idempotency, code review. At my co-op I caught a webhook data-loss path, an HMAC signature-check crash and a 100x money-unit error (private code; my record is the evidence). In public: the Stripe webhook signature check I wrote for EventEase, a team project (commit `271ead3`, 2025-04-17). New to me: Kafka, Kubernetes, OpenTelemetry, an agent loop and MCP server from scratch, LangGraph, evaluation design.

**Exists today (2026-10-09)**
- The plan, the research and this brief.
- The first piece (Klaxon repo, local commit `801a0bf`): a synthetic, seeded demo of the money check with 91 passing tests. Its run: 7 requests, 0 errors, dashboard GREEN, ledger balanced, money check FAILED (one payment posted twice, off by +$69.68). The idempotent handler passed.

**Will exist (target mid-December 2026)**
- The payments system, the six incidents, the agent and MCP server, the approval gate and rollback, the evaluation report, a public repo and a demo video.
