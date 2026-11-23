# DayThread — Final Project Film script v1 (2026-11-23)

Narration source for the Final Project Film (Canvas assignment "Final Project Film", 25 points).
`film/make_sheet.py` reads the `VO:` lines straight from this file.

**Structure (the assignment's four parts, in its order):**
1. Executive summary: what it is and why anyone would care, no "how" (BIDEA–B03).
2. Introduction: what others have done, then why DayThread again (B04–B05).
3. Methods: the delegation contract, the loop, the fine-tuned checker, data, resources, steps (B06–B12).
4. Evaluation: what will be measured, and what result says it worked or didn't (B13–B16).

**What exists today, and nothing more is claimed:** the October pitch film and brief, and the
two-day replay run on 2026-10-25 (synthetic fixture, fictional client, 30 Claude CLI calls;
`final-project-film/replay/RESULTS.md`). The delegation contract, the fine-tuned checker, the
loop, memory, review page, tests and evaluation do not exist yet. Every sentence about them is
future tense, and every drawing of them is captioned "Constructed — proposed workflow".

**Facts the narration relies on:**
- Replay: all 10 summaries kept the fall (5 normal + 5 constrained); 9 of 10 turned "I don't want
  my daughter fussing about it" into a disclosure prohibition (`RESULTS.md`, Aditya's review).
- Lifeline: "Fall detection technology does not detect 100% of all falls." DailyCall: "DailyCall
  cannot guarantee that every safety concern will be detected, interpreted correctly, or
  delivered to the right person in time." Both from the companies' own pages, read by Aditya on
  2026-10-14 (`SOURCES.md` S1, S4). Neither product was tested.
- Base model: `distilbert/distilroberta-base` on Hugging Face, licence Apache-2.0 (checked via the
  Hugging Face API on 2026-11-23). Not downloaded or trained yet.
- Resources: Claude Code via Aditya's existing claude.ai login (the replay used it; no API key);
  MacBook Pro, Apple M3 Pro, 18 GB. PyTorch is not installed yet.

**Pronunciation spellings (2026-11-23, from the machine transcript):** B11 writes SQLite as
"S-Q-Lite" because Kokoro's first read was heard as "Escuelite". B14 says "will be included"
because "go in" was heard as "going". BOUT reuses the October film's audio for the identical
line "This was DayThread, by Aditya Raj.", since this run's take was heard as "addediraj".

**Fixed rules for every beat:** Kokoro `am_onyx`, a synthesized voice reading Aditya's script,
disclosed on screen in every beat and aloud in the first. Top-right band names the part. Bottom
band: *Constructed — proposed workflow* on `[C]` beats; the documentation caption on B04; the
replay caption on B02. No people on screen, no instructor identity or channel credit.

Lines starting `VO:` are the narration. Everything else is the visual plan.

---

### BIDEA — opening
VO: Hi, I'm Aditya Raj. This is DayThread, my final project. You're hearing a synthesized voice reading my script.
- Visual: the title `DayThread`, "final project · the plan", "Aditya Raj"; a thread with three pages.

### B01 — what it is [C]
VO: DayThread will be a check-in assistant for home care. It will remember what a client says from one day to the next. When something concerning comes up, like a fall mentioned in passing, it will show the client's exact words to a care coordinator, who decides what happens next.
- Visual: Day 1 and Day 2 pages on a thread; a terracotta dot on Day 2; an evidence slip travels to
  the coordinator's desk. Labels: `Day 1` · `Day 2` · `coordinator`.

### B02 — why it matters
VO: Why it matters: a coordinator shouldn't have to reread every conversation, and a summary alone can't be trusted. In my October test, Claude's summaries all kept the fall, but nine of ten changed what the client meant.
- Visual: a check-in page, an arrow, a summary page; two tallies appear: `kept the fall: 10 of 10`
  and `meaning changed: 9 of 10`. Caption: replay run 2026-10-25, synthetic data, fictional client.

### B03 — what exists
VO: That small test is the only part that has run. Everything else in this film is a plan.
- Visual: two shelves. `ran` holds one page with the tumble dot; `planned` holds dashed outlines.

### B04 — what others have done
VO: Others have built parts of this. Lifeline sells automatic fall detection, and says it doesn't detect every fall. DailyCall makes daily AI phone calls with summaries for families, and says it can't guarantee every safety concern is detected or interpreted correctly.
- Visual: two plinths: a pendant with a response tower (`Lifeline`), a phone with a summary page
  (`DailyCall`). No logos. Caption: from each company's own documentation, read 2026-10-14.

### B05 — why DayThread [C]
VO: I'm not claiming they lack anything. DayThread's focus is narrower: every concern linked to the client's own words, a separate check of the raw transcript, and a person who decides before anything leaves the system.
- Visual: the two plinths shrink left; a third, `DayThread · planned`, slides in: three linked
  pages, a scan line, a small closed gate.

### B06 — the delegation contract [C]
VO: Here's how I'll build it. First, a delegation contract: each step must hand the next one something it can check, and if the check fails, the work stops. I'll write the contract and its tests before Claude writes any code.
- Visual: a contract page with a seal; three steps joined by arrows; a check mark lands on each
  handoff; the last handoff gets a stop bar. Labels: `contract` · `handoff` · `stop`.

### B07 — three handoffs [C]
VO: The raw transcript will be saved and can't be edited. Every claim in memory must quote it word for word. And an approval only counts if the evidence and the action haven't changed since the coordinator saw them.
- Visual: an append-only binder; a page linked to the memory drawers by a quote line; a closed
  gate with a lock. Labels: `append only` · `quoted` · `bound to what was seen`.

### B08 — the loop [C]
VO: Each check-in will run as a loop with a turn budget. It stops when the conversation ends or the budget runs out, never just because the model says it's done.
- Visual: a loop ring with a runner, budget slots draining, a stop bar. Labels: `loop` · `budget` · `stop`.

### B09 — the fine-tuned checker [C]
VO: The separate check will be a small open model, DistilRoBERTa, downloaded from Hugging Face and fine-tuned by me to flag concerning sentences. It reads the raw transcript, never the summary, so it fails differently from the thing it checks.
- Visual: a pale box `base model` → arrow → a dark box `fine-tuned`; a terracotta scan line on the
  raw transcript; the summary page is crossed out. Labels: `Hugging Face` · `fine-tuned` ·
  `raw transcript` · `not the summary`.

### B10 — data [C]
VO: All data will be synthetic, with fictional clients. Claude will write the training sentences under labelling rules I set, and I'll spot-check them. I'll write the held-out test sentences myself, before any training, and lock them away.
- Visual: a stack of pages `training · by Claude` with a check on one; pages slide into a vault
  that locks: `held-out · by me`.

### B11 — resources [C]
VO: Do I have what I need? Claude Code through my existing account, so no API credits. The base model is a free download, so no new account. Training will run on my laptop, in Python, with PyTorch and S-Q-Lite.
- Visual: three plinth items, each getting a check: a workstation (`existing account`), a box
  with a down arrow (`free download`), a laptop (`laptop`). Then `Python · PyTorch · SQLite`.

### B12 — the steps [C]
VO: The order: the contract and tests, then the test set, then training data, then the checker, then the loop, memory and review page. Last, one run on the held-out set, before December twentieth.
- Visual: a thread with six numbered dots appearing on cue; the last one ends at a vault. Label:
  `by Dec 20`.

### B13 — evaluating the checker [C]
VO: To evaluate the checker, I'll compare it with a simple keyword list and with the model before training, on the held-out set. I'll write the pass mark down before I look. If it doesn't beat the keyword list, that's the result I'll report.
- Visual: three empty dashed bars labelled `keywords` · `untrained` · `fine-tuned`; a sealed
  envelope `pass mark`; a dashed threshold line.

### B14 — deliberate failures [C]
VO: At least five failure cases will be included on purpose: took a spill, my legs gave out, I didn't fall, my neighbour fell, and I fell asleep.
- Visual: five cards drop in on cue, each crossed. Label: `5 failure cases, on purpose`.

### B15 — the controlled failure [C]
VO: Then one controlled failure. My test never dropped the fall on its own, so I'll force a summary that drops it. It passes only if the separate check catches it and a coordinator reviews it.
- Visual: the check-in page and a summary with a dashed empty row (`forced`); the terracotta scan
  line finds the tumble line; a review item drops into the queue (`review`).

### B16 — what it can't show [C]
VO: What this can't show: whether it works with real clients, or whether it catches a changed meaning. That's why the coordinator will see the original words next to every claim.
- Visual: a dashed fence `synthetic only`; a claim slip beside the original page, joined by a line.
  Label: `original words beside each claim`.

### BOUT — outro
VO: This was DayThread, by Aditya Raj.
- Visual: `DayThread`, `Aditya Raj`, `github.com/aditya-raj-sde`; a thread ending in a terracotta dot.
