# Project brief: TraceCase

**Ashwin Thankachan** · INFO 7375 · revised 2026-11-23
Revises my brief of 2026-10-13, which itself replaced a ProvenDocs brief of 2026-10-11 (why: `FRICTIONAL.md`).
**Target role:** backend software engineer (new grad).
**Planned stack:** Spring Boot demo service with PostgreSQL and Redis; a Python agent (FastAPI, Pydantic, Claude
API); OpenTelemetry traces viewed in Jaeger; Docker Compose; pytest and JUnit; GitHub Actions; a small approval page.

## What changed since the October pitch, and why

The project itself did not change. The **film** was rebuilt from scratch in November: the pitch's 18 beats at 3:53
became 25 beats at 3:52.4, every picture was redrawn as objects rather than labelled boxes, and the drawings were
re-cued to word-level narration timestamps instead of running on estimated durations. It was recut on 2026-11-23
when I found it had grown to 4:48, past the assignment's 240-second ceiling.

Two things in this brief changed on evidence, both found by a review of the finished cut and both recorded here
rather than quietly corrected:

- **The baseline was unfair as originally written** (§4 below). "Summarize the logs" gave the baseline less
  evidence than the agent, so a win would have measured the extra evidence, not the loop.
- **"Unsupported claims" conflated two different checks** (§4 below). The evidence checker can verify that a
  cited log line exists; it cannot judge whether that line supports the conclusion drawn from it.

Both corrections are now **spoken in the film**, not just written here: B20 states the fair baseline and B16
separates what the checker enforces from what I score. The brief and the film agree.

**1. What is it?** An agent that investigates failures in a small Spring Boot service using its logs, traces and
deploy history, and proposes one fix that a person must approve before it runs. When it's done, it will be one
public GitHub repo that starts with one Docker Compose command. The repo will hold:
- the demo service: an API, a worker, PostgreSQL, and Redis as a cache and queue, with synthetic data
- the agent
- an approval page
- a library of failures I can trigger
- an evaluation report

**2. Why would anyone care?** My CloudPulse team project answered "is the service healthy?" When the answer is no,
an engineer still digs through logs and traces by hand. TraceCase will do the digging, show its evidence, and leave
the decision to a person.

Alternatives I checked (read 2026-10-13, re-checked 2026-11-22):
- **HolmesGPT** is an open-source incident agent, read-only by default; its optional remediation toolset asks
  before every change.
- **Microsoft AIOpsLab** is a research framework for evaluating such agents, and it runs on Kubernetes.
- **By hand:** dashboards, logs and recent deploys.

TraceCase will run on a laptop with no Kubernetes, ship its own service to break, make every claim cite a real log
line or trace span, and void an approval if the fix or its evidence changes. I'm not claiming the others can't do
these things.

**3. Who opens it, and what do they do in the first 60 seconds?** A backend hiring manager. They start the demo,
break the service with one command, watch the agent investigate step by step, and approve or reject its fix.

**4. What does it prove?**
- **Loop with a budget:** observe, call one allowed tool, record evidence, update the hypothesis. It stops on a
  supported cause, on thin evidence, or at a step, time or cost limit, never on the model's say-so.
- **Prompt contract:** each step must return a fixed, schema-checked format.
- **Permissions in code:** allow-listed tools only, and fixes chosen from a few predefined actions, never a shell.
- **Grounding:** a validator rejects any claim citing a log line or span that doesn't exist.
- **Human gate:** the approval records action, target, parameters and evidence version, and it stops counting if any
  of them change.
- **Evaluation:** about 30 failure scenarios, 10 held out before tuning. **Revised 2026-11-23, in two places:**

  - **The baseline gets the same evidence.** Not "summarize the logs." The baseline is the **same model, given the
    same logs, traces and deploy history in one prompt, with no loop, no tools and no checker.** This compares the
    complete agent workflow against a single-prompt read of the same evidence. It does not isolate the loop on its
    own — loop, tool use and checker all differ — and nothing here claims it does.
  - **Three numbers, reported separately, not one.** **Citation validity** — enforced in code; the checker confirms
    a cited log line or span exists, which catches an invented reference. **Claim support** — scored by me against
    the held-out cases; a real line can be cited and still not justify the diagnosis ("database request timed out"
    is a real line and does not prove a deploy changed a password), and no checker I can write decides that.
    **Diagnosis accuracy** — against the fault I injected.

  "I don't know yet" counts as correct only on cases labelled insufficient-evidence **before** tuning, not whenever
  the agent abstains. Also measured: blocked actions and cost. With ten held-out cases one case moves accuracy by
  ten points, so correct, incorrect and abstained are reported separately and the result is presented as what it
  is — a small controlled evaluation.

**5. In, out, first.**
- **In:** one demo service and failures I design (stale Redis cache, backed-up queue, bad config deploy, slow query).
- **Limitation:** it will only be tested on those failures, so it proves nothing about real production systems.
- **Out:** it will never run arbitrary commands or touch anything outside the demo. Kubernetes is a stretch goal;
  Kafka is out.
- **First piece:** the demo service with one failure I can trigger and a trace that shows it. A saved trace and a
  dated log will show it ran.

**6. What could sink it?** Approving one thing and running another. I'll trigger this on purpose: approve fix A,
swap in fix B, and show that execution is refused until a person reviews it again. A second risk is an agent that
sounds sure without evidence, and the evaluation will check that it says "I don't know yet" when it should.

**7. Why this project?** Mostly learning. Across 3,254 entry-level postings my job pipeline collected (Oct 8–12),
agents, observability and evaluation keep coming up, and my resume shows none of them. It also builds on CloudPulse
rather than copying it.
- **New to me:** OpenTelemetry tracing, agent loops with budgets, code-enforced permissions, approval invalidation,
  Redis as a cache and queue, held-out agent evaluation.
- **Already have:**
  - Spring Boot health monitoring with JUnit/MockMvc tests (my lifecycle, threshold and incident work in the
    CloudPulse team repo).
  - Python/FastAPI services calling an LLM, with pytest tests for mocked LLM failures (MyEdMaster internship; the
    code is private, so the evidence is my account).
  - Docker and CI/CD (LTIMindtree).

## Exists today (2026-11-23)

- this brief, `beat_sheet.json`, and the film: `tracecase-final.mp4`, 25 beats, 3:52.4, 3840×2160 (the assignment's ceiling is 240s)
- the film's sources in `build/` and its narration with word-level alignment in `mp3/`
- the gate reports in `gate-reports/`: type-lock, frame QC, layout audit, WCAG
- **No TraceCase code, no traces, no evaluation results.** The film says this in its closing beat.

## Will exist

- the demo service, its tracing, and the failure library
- the agent loop, tool dispatcher, permission policy, evidence validator, and approval page with invalidation
- the recorded stale-approval failure
- the held-out evaluation, run against the baseline defined in §4 above, reporting the three numbers separately
