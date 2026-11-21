# Klaxon: Final Project Film, script

INFO 7375, Canvas assignment 3551817 (25 pts), due Mon 2026-11-23 11:30 PM ET. Brown's four parts, in his order (announcement of 2026-11-18). Form chosen by Aravind on 2026-11-20: real footage of Klaxon, a few clean title cards, and a disclosed synthetic voice (Kokoro, am_onyx).

**Target length: 4:59.8** (estimate: spoken words at 2.8 per second plus 0.6 s per beat; a spelled letter counts as half a word; the appendix card is silent). The executive summary is 54.1 s and contains no "how".

Status: final. Aravind approved the film with no changes on 2026-11-22. Every claim is in FACTCHECK.md with its source; the footage for each beat is in SHOTLIST.md; `beats.json` holds the same text for the build (made by `beats.py`). The measured length of every beat is in TIMINGS.md (the build writes it to build/out/).

How to read a beat: **Caption** is the on-screen and soft-caption text (digits kept). **Spoken** is what the voice reads, only where it differs (acronyms spelled, numbers in words).


## Part 1. Executive summary (54.1 s)

### B01 · 7.7 s · L1 title card

**Caption:** Hi, I'm Aravind, and this is a synthetic voice reading the script. This film is about my final project, Klaxon.

### B02 · 15.6 s · L2 panel in the browser, full frame

**Caption:** Klaxon is an AI on-call engineer for a payments system. When something breaks, it works out what went wrong, shows its evidence, and asks a person before changing anything. Then it checks what a dashboard can miss: whether the money is right.

**Spoken:** Klaxon is an A I on-call engineer for a payments system. When something breaks, it works out what went wrong, shows its evidence, and asks a person before changing anything. Then it checks what a dashboard can miss: whether the money is right.

### B03 · 18.5 s · L3 saved screenshot, cropped, one highlight

**Caption:** That last check is why it matters. In one run on my own test system, a bad deploy made the ledger count some payments more than once. The other alert rules stayed quiet. Only the money check failed: our books were $461 ahead of the payment provider's.

**Spoken:** That last check is why it matters. In one run on my own test system, a bad deploy made the ledger count some payments more than once. The other alert rules stayed quiet. Only the money check failed: our books were four hundred sixty-one dollars ahead of the payment provider's.

### B04 · 12.3 s · L4 split: footage left, one sentence right

**Caption:** An engineer, or an AI agent, could close an incident like that because everything looks healthy, while the books are still wrong. With Klaxon, a fix isn't done until the money is checked.

**Spoken:** An engineer, or an A I agent, could close an incident like that because everything looks healthy, while the books are still wrong. With Klaxon, a fix isn't done until the money is checked.


## Part 2. Introduction: what others have done (58.6 s)

### B05 · 16.5 s · L5 fact list card, three rows

**Caption:** The industry calls this an AI SRE, an AI site reliability engineer. Resolve AI raised $125 million at a $1 billion valuation in February, Traversal $120 million in November, and Datadog, AWS and Microsoft now offer their own.

**Spoken:** The industry calls this an A I S R E, an A I site reliability engineer. Resolve A I raised one hundred twenty-five million dollars at a one billion dollar valuation in February, Traversal one hundred twenty million in November, and Datadog, A W S and Microsoft now offer their own.

### B06 · 14.6 s · L6 two-number card

**Caption:** What did they get? Microsoft says its agent has mitigated over 35,000 incidents in its own services. But on ITBench, a research benchmark, agents on state-of-the-art models resolved only 11.4% of its SRE scenarios.

**Spoken:** What did they get? Microsoft says its agent has mitigated over thirty-five thousand incidents in its own services. But on I T Bench, a research benchmark, agents on state-of-the-art models resolved only eleven point four percent of its S R E scenarios.

### B07 · 13.9 s · L7 quote card

**Caption:** The open-source agent I looked at, HolmesGPT, can check a deploy by asking a model to compare error rates, latency, restarts and logs. In its docs, I didn't find a built-in check that the money is right.

**Spoken:** The open-source agent I looked at, Holmes G P T, can check a deploy by asking a model to compare error rates, latency, restarts and logs. In its docs, I didn't find a built-in check that the money is right.

### B08 · 13.6 s · L4 split: their four signals left, Klaxon's money readings right

**Caption:** So why build mine? Klaxon is a small copy of this idea, with the check I couldn't find: after a fix, code, not the model, checks the money. And Klaxon changes nothing until a person approves it.


## Part 3. Methods (100.4 s)

### B09 · 16.2 s · L8 flat diagram

**Caption:** It all runs on synthetic data. A small payments system runs in Docker on my Mac: an API, a fake provider that sends signed webhooks, Kafka, and a double-entry ledger. Simulated customers make payments, and six faults with known causes are injected on purpose.

**Spoken:** It all runs on synthetic data. A small payments system runs in Docker on my Mac: an A P I, a fake provider that sends signed webhooks, Kafka, and a double-entry ledger. Simulated customers make payments, and six faults with known causes are injected on purpose.

### B10 · 14.3 s · L2 panel in the browser, zoomed on the steps

**Caption:** When an alert fires, Klaxon asks Claude for one step at a time: call one of eight read-only tools, served by an MCP server written from scratch, or give a diagnosis that cites the tool calls behind it.

**Spoken:** When an alert fires, Klaxon asks Claude for one step at a time: call one of eight read-only tools, served by an M C P server written from scratch, or give a diagnosis that cites the tool calls behind it.

### B11 · 15.6 s · L3 saved screenshot, slow vertical pan

**Caption:** Here is a real run from week seven. The money alert fired, and in 25 seconds and three tool calls, Klaxon found the cause: a ledger deploy that books every message without checking for duplicates. It asked to roll that deploy back.

**Spoken:** Here is a real run from week seven. The money alert fired, and in twenty-five seconds and three tool calls, Klaxon found the cause: a ledger deploy that books every message without checking for duplicates. It asked to roll that deploy back.

### B12 · 11.8 s · L4 split: the gate's trail left, the money readings right

**Caption:** I approved it by typing its id in my own terminal, 70 seconds later. Code then checked the result: healthy, cause removed, but the money still wrong, because a rollback repairs nothing.

**Spoken:** I approved it by typing its I D in my own terminal, seventy seconds later. Code then checked the result: healthy, cause removed, but the money still wrong, because a rollback repairs nothing.

### B13 · 11.7 s · L9 GitHub page in the browser

**Caption:** Weeks one to seven are built and public. Planned by December 4th: a multi-agent version, the webhook receiver in Go, a 72-run comparison of the loops, and a safety pass.

**Spoken:** Weeks one to seven are built and public. Planned by December fourth: a multi-agent version, the webhook receiver in Go, a seventy-two run comparison of the loops, and a safety pass.

### B14 · 22.6 s · L5 two-column card: what I have / its limits

**Caption:** Do I have what I need? There is no API key and no token credits: every call goes through my university's Claude seat, using Claude Code in headless mode. It isn't billed per call, but it has usage limits, so big batches run overnight. Dollar figures are estimates at API prices, not money spent. Compute is my Mac and GitHub's free CI.

**Spoken:** Do I have what I need? There is no A P I key and no token credits: every call goes through my university's Claude seat, using Claude Code in headless mode. It isn't billed per call, but it has usage limits, so big batches run overnight. Dollar figures are estimates at A P I prices, not money spent. Compute is my Mac and GitHub's free C I.

### B15 · 8.2 s · L9 GitHub commit list in the browser

**Caption:** I made the decisions, reviewed and accepted every week, and typed every approval myself. Claude Code wrote the code under my direction.


## Part 4. Evaluation (82.7 s)

### B16 · 12.6 s · L10 terminal card from real output

**Caption:** How will I know it works? Eight test cases, each with its right answer written before any run: the six faults, a false alarm, and a fault where the tools can't see the deploys.

### B17 · 21.8 s · L2 panel evaluation page in the browser

**Caption:** I check three things. Did it name the real cause? A keyword rule written in advance and a Claude judge that never sees which model wrote it both grade that, checked against my own blind labels. Did it name an action only where one fits? And when I approve an action, does code find the system healthy and the money right?

### B18 · 12.0 s · L3 zoom on the report table, one highlight

**Caption:** The first results, from 48 runs on two Claude models: Opus named the cause in all 18 of its fault runs, by both graders. No run named an action where none fits.

**Spoken:** The first results, from forty-eight runs on two Claude models: Opus named the cause in all eighteen of its fault runs, by both graders. No run named an action where none fits.

### B19 · 18.6 s · L4 split: the false-alarm rows left, three short labels right

**Caption:** What didn't work yet: on the false alarm, no run named an action, but each grader found only one run in six that said plainly that nothing was wrong. And every fault was known while I built Klaxon, so this is not yet a test on faults it has never seen.

### B20 · 17.7 s · L11 end card: works if / fails if

**Caption:** So it works if the 72 comparison runs keep naming causes with no wrong actions, the false alarm gets called false, and code keeps catching fixes that leave the money wrong. It fails on a confident wrong cause, or an action where none fits. Klaxon, by Aravind Sundaravadivelu.

**Spoken:** So it works if the seventy-two comparison runs keep naming causes with no wrong actions, the false alarm gets called false, and code keeps catching fixes that leave the money wrong. It fails on a confident wrong cause, or an action where none fits. Klaxon, by Aravind Sundaravadivelu.


## Part Appendix (4.0 s)

### B21 · 4.0 s · L12 appendix card, silent (4 s): sources and the repo link

No narration. The card lists the sources (see SOURCES.md) and the repo link https://github.com/AravindKumar2504/klaxon.
