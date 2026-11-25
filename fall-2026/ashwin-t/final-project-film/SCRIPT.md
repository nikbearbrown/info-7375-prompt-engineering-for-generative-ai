# TraceCase — Final Project Film
## Narration, exactly as spoken in the cut

**This file is generated from `beat_sheet.json`, which is the file the cut is built from.**
It is the shipped narration, not a draft — the wording, the beat numbering and the running
order below all match `final/tracecase-final.mp4` line for line.

25 beats · 3:51.9 (231.85s of narration) · narration-clocked ·
four parts in the order the brief asks for. The assignment's ceiling is 240s.
Every factual claim about other people's work is sourced in [FACTCHECK.md](FACTCHECK.md).
Lines marked ⚠️ are mine to re-confirm before submission.

---

## PART 1 — EXECUTIVE SUMMARY
*What it is and why it matters — not how. — 5 beats, 35.5s.*

**B00** · 3.37s

> A dashboard tells you a service broke. It doesn't tell you why.

**B01** · 9.39s

> TraceCase is an agent that reads a broken service's logs, traces and deploy history, works out why it broke, and proposes one fix a person must approve.

**B02** · 7.98s

> Finished, it's one public repository: a demo service to break on purpose, the agent, an approval screen, and an evaluation report.

**B03** · 9.00s

> A team project of mine answered one question: is the service healthy? When the answer is no, an engineer reads logs by hand. That's where time goes.

**B04** · 5.80s

> It's built so you can check it instead of trusting it. It does the digging, and you decide whether any fix runs.

---

## PART 2 — INTRODUCTION (prior work, then the gap)
*Who has tried this, what they got, and what is missing. — 6 beats, 66.9s.*

**B05** · 13.06s

> This isn't new. HolmesGPT is an open-source SRE agent, a CNCF sandbox project, about four thousand stars. It runs an agentic loop over live data, read-only by design.

**B06** · 7.98s

> It's the mature option. What I couldn't find was an independent evaluation. The evidence I can read is the project describing itself.

**B07** · 10.13s

> Microsoft Research's AIOpsLab is the opposite: a benchmark, not a product. Forty-eight problems across two applications, faults injected on purpose.

**B08** · 16.47s

> And it published numbers. Their best agent scored about fifty-nine percent overall. By task: detection, sixty-nine to one hundred percent; root cause, thirty-six to forty-five; mitigation, twenty-seven to fifty-five. In their words, none consistently achieve high accuracy.

**B09** · 10.11s

> It also needs Kubernetes: its SocialNetwork application alone runs twenty-eight microservices. Not something a reviewer opens on a laptop in sixty seconds.

**B10** · 9.13s

> So: a mature tool with thin public evidence, a benchmark that needs a cluster. TraceCase goes between them, laptop-sized, shipping the broken service.

---

## PART 3 — METHODS
*How it will be built, and with what. — 8 beats, 80.3s.*

**B11** · 9.22s

> Step one is the thing that breaks: a Spring Boot API and worker, Postgres, and Redis, in Docker Compose. Open Telemetry writes traces and logs.

**B12** · 9.26s

> Step two: a fixed catalogue of failures, each triggered with one command. Stale cache, slow query, bad deploy, queue backup. True causes written down first.

**B13** · 8.68s

> That's my data: the system generates it. No customer logs, nothing scraped. I break my own service. The ground truth is mine because I caused it.

**B14** · 10.65s

> Step three is the agent. Observe, pick a tool, update the hypothesis. It stops when every claim cites a line that exists, or on a step budget, never on the model's say-so.

**B15** · 9.58s

> Its tools are an allow-list in code: read logs, query traces, read deploys. Not a shell — the Microsoft study gave its agents one. I'm deliberately not.

**B16** · 10.09s

> Every claim must cite a log line or span. A checker reopens the file; if it isn't there, the claim is rejected. Whether that line supports the diagnosis is my call.

**B17** · 8.85s

> The fix comes from a short menu, never free text. Approval binds three things: the action, its target, and its evidence. Change one and it refuses.

**B18** · 13.99s

> Everything else is a laptop and Docker. No cluster, no GPU. Model access is the open question: my seat covers the assistant, not calls from code. So the agent targets a model interface, and a local model can stand in.
>
> ⚠️ states the model-access position; re-check before submission if the seat or an API key changes

---

## PART 4 — EVALUATION
*How I will know whether it worked. — 6 beats, 49.1s.*

**B19** · 6.76s

> About thirty scenarios from that catalogue. Ten locked away before I tune anything, so I can't quietly fit to them.

**B20** · 7.55s

> The baseline gets the same model and the same logs, traces and deploy history, in one prompt. No loop, no tools, no checker.

**B21** · 10.75s

> Four measurements. Did it name the right cause. Did it say I don't know when evidence was missing. How many unsupported claims survived — I score those by hand. And how many steps it burned.

**B22** · 9.54s

> It worked if it names more correct causes than the baseline on the held-out ten, and no unsupported claim survives. It failed if it only wins by guessing more often.

**B23** · 6.40s

> And one test that's simply pass or fail. Approve fix A, swap in fix B, and the system must refuse.

**B24** · 8.11s

> Where it stands tonight: a brief, this plan, and this film. No TraceCase code exists yet. Everything you just heard is what I'm going to build.
>
> ⚠️ says *no TraceCase code exists yet*; must change if any TraceCase code is written before submission

---
