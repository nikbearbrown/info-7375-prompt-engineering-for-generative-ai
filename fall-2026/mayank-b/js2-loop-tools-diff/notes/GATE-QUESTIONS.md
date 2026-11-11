# JS2 gate — your questions (answer before any code exists)

**How to answer.** Under each question, write **A / B / C** or your own words after `→ Your answer:`. Short is fine. My recommendation is marked ★, but these are **your decisions**. The brief says you write the gate before Claude Code touches the code, so I'll turn your answers into `GATE.md` *in your words* and list any change I make, the same way CONTRACT.md was built in JS1.

Each block also says which **midterm section** it practices. Read that section's "In one line" first: it's the answer key for *why*.

## 0. Language (decide first)

The brief allows any language, **but the course repo's CI rejects it**. `scripts/validate_course.py` fails on any `.js/.ts/.tsx/.jsx/.rs/.jl/.go` file outside `learning-artifacts/`. The latest CI run (commit `3e3fa86`, 2026-11-04) lists **all 15 of your JS1 `.js` files** as "Non-Python implementation" failures, alongside other students' `.ts`/`.tsx` files. CI has been red on every commit since at least Nov 1, so it's a class-wide state, not only yours. The grading rubric doesn't mention CI.

  A. **Python 3, standard library only** (`urllib`, `json`, `pathlib`, `unittest`): passes the repo's validator; matches Lectern (Python) and Chapter 5's `authorize()` reference; zero dependencies, so a TA can run it from a fresh clone with no install. JS1's logic gets **ported** (allow-list, safe write, seen ids, raw + SHA-256), not copied ★
  B. **Node.js** (reuse JS1 code directly): faster to start, but adds more `.js` files to CI's failure list.
  (Either way, it might be worth asking a TA whether the `.js` failures in JS1 matter for the GitHub-posting points.)
→ Your answer:

**The plan these questions assume** (change anything you disagree with):
- **Language:** see question 0. Starts from **JS1** (allow-list, safe write, seen-ids state, raw response + SHA-256), plus the Reallocation Engine's Greenhouse/Ashby provider pattern and Lectern's verified board list.
- **Boards in the real run:**

| Board | Role |
|---|---|
| Greenhouse `anthropic` | your JS1 board |
| Greenhouse `hubspotjobs` | real board |
| Ashby `notion` | the second ATS |
| a deliberately bad name | the deliberate failure |

- **The "finished wrong answer" demo:** Greenhouse slug `hubspot`. Lectern's ATS.md (verified 2026-09-26) records that it returns **a valid but empty board**, because the real slug is `hubspotjobs`. A naive agent finishes cleanly and says "HubSpot: no new jobs."

---

## 1. Exits (midterm §11: "stopping ≠ success")

Every way the loop can end, and what each run reports. ★ = these four:

| Exit | When | What it reports |
|---|---|---|
| `finished` | every board in the plan was attempted within budget | per-board result: `ok` / `error` / `suspect`. **Not** "the answers are right" |
| `incomplete` | the board list ran out **before** the plan was covered, or a board was skipped by the repeat rule | which boards weren't done, and why |
| `budget-exhausted` | a cap was hit (boards, requests or seconds) | which cap; which boards were never tried |
| `error` | something that must stop the whole run: invalid persona, invalid config, a write refused by the permission policy, an off-list host requested | the reason; **nothing written to state** |

**1a.** Is a run where one board failed (and was handled) `finished` or `error`?
  A. `finished`, with that board marked `error` inside the report ★ (one bad board shouldn't hide the other two)
  B. `error` (any failure fails the run)
→ Your answer:

**1b.** Should the run's exit **ever** be called "success"?
  A. No. The exit says how the loop ended; whether the answer is right is a separate, independent check ★
  B. Yes, `finished` = success
→ Your answer:

## 2. Budgets (§11 "bound the loop", §28 "write the caps into the gate")

**2a.** Caps per run. ★ max boards **5** · max HTTP requests **10** (one per board plus up to one retry each) · max wall-clock **60 s** · per-request timeout **10 s**.
→ Your numbers:

**2b.** Who may change a budget?
  A. Only you, by a new dated line in GATE.md's "Decisions" log; the code reads caps from one config file, and a test fails if the config differs from GATE.md ★
  B. Command-line flags anyone can pass
→ Your answer:

## 3. Repeat rule (§11 "repetition ≠ progress")

**3a.** What counts as "the same action"?
  A. Same ATS **and** same board slug (case-insensitive, after URL-decoding) within one run ★
  B. Same full URL string
  (A also catches `Notion` vs `notion` and `Jasper%20AI` vs `Jasper AI`, which B misses.)
→ Your answer:

**3b.** What does the loop do on a repeat?
  A. Doesn't send it; records `skipped: repeat` in the trace; it doesn't count against the request budget ★
  B. Sends it anyway
→ Your answer:

## 4. Error policy (§13 "don't invent a value")

**4a.** A board fails (HTTP 404, network error, timeout, or a body that isn't the expected JSON). What happens?
  A. **Retry once only for timeouts and 5xx** (transient: the same request may succeed a moment later); **never retry a 404/4xx or a malformed body** (the same request will fail the same way, so a retry is just repetition). Then mark the board `error` with the reason, **keep its previous state untouched**, continue to the next board ★
  B. Retry everything 3 times
  C. Stop the whole run
→ Your answer:

**4b.** When do you get escalated to?
  A. The report's top line lists every `error` and `suspect` board as "needs Mayank". The agent never "fixes" a slug by itself ★
→ Your answer:

**4c.** What must the agent **never** do with a failed board? (★ report "0 jobs" or "no new jobs" for it; copy last run's jobs in as if fetched)
→ Your answer:

## 5. The finished-wrong answer and its independent check (§13 evidence vs testimony, §12 solve-verify)

The agent's own report is testimony. The check must not ask the agent.

**5a.** Which independent check catches "HubSpot: 0 jobs, no new jobs"?
  A. A **separate checker script** (not imported by the agent) that reads only the **saved raw responses** plus a **human-maintained, dated** `expected-boards.json` (board → minimum plausible postings, each with its source, e.g. "Lectern ATS.md 2026-09-26: hubspotjobs 133"). Any board at 0, or below its floor, is flagged `suspect` ★
  B. Re-run the agent and see if it agrees (← that's the first opinion run twice)
  C. Also: a board whose count falls >80% versus your last saved run is `suspect`
→ Your answer (A, A+C, …):

**5b.** Who writes the floors in `expected-boards.json`? (★ you, from a source you can name. If you can't name a source, the floor is "unknown", not a guess.)
→ Your answer:

## 6. Permission policy (§14 need-to-know; Chapter 5)

**6a.** Hosts the agent may call. ★ only `boards-api.greenhouse.io` and `api.ashbyhq.com`, over HTTPS, **no redirects followed**. (Drop `api.anthropic.com` unless the JS1 Claude judge stays in. Do you want the judge in this layer?)
→ Your answer (judge in / out):

**6b.** Folders. ★ **read**: `config/`, `persona/`, `state/`, `runs/`. **write without asking**: `runs/<this-run>/` only. **write that needs your approval**: `state/seen-ids.json` (updating "what I've seen" changes what future runs call new). **never**: anything else.
→ Your answer:

**6c.** How does approval work? ★ the run writes a proposed state file; you approve with an explicit `--approve-state <run-id>` that must exactly match the run id (not just any truthy value: Chapter 5's "truthy approval" wrong version).
→ Your answer:

**6d.** Never-do list. ★ apply, email, message, log in, submit forms, send any request that isn't GET, read or send credentials, follow a redirect, write outside the output folder.
→ Add / remove:

## 7. Wrong versions your tests must catch (Chapter 5 + Chapter 4)

Tick the ones you want (★ all), and add one of your own:
- [ ] **W1 prefix trick:** path check by `startsWith("runs")` lets `runs-evil/` through.
- [ ] **W2 symlink escape:** `..` is cleaned textually but a symlink inside `runs/` pointing outside is followed (JS1's `safeWrite` has exactly this gap: it doesn't resolve real paths).
- [ ] **W3 truthy approval:** `--approve-state yes` or `1` approves a write.
- [ ] **W4 empty = fine:** an empty board (`hubspot`) reported as "no new jobs" with no flag.
- [ ] **W5 failure as zero:** a 404 board reported as 0 jobs instead of `error`.
- [ ] **W6 stopped = success:** a budget-exhausted run labelled `finished`.
- [ ] **W7 repeat counted as progress:** the same board fetched twice, both counted.
- [ ] **W8 host check by substring:** `boards-api.greenhouse.io.evil.com` passes.
→ Yours:

## 8. The failure sentence (Chapter 1 + 2: dated, written before you see output)

Write one sentence: *"If my loop were wrong, I would see ___."*
→ Your sentence (date it):

## 9. The review packet change (Chapter 6, 14 points)

Pick the defect you'll reproduce, write a failing test for first, then ask Claude Code to fix:
  A. **JS1's `safeWrite` follows symlinks** (W2): realistic, already in your code, a clean before/after ★
  B. Ashby slugs with spaces aren't URL-encoded (`Jasper AI`)
  C. Something you noticed in JS1
→ Your answer:

---
When you've answered, tell me "gate answers done". I'll draft GATE.md from them, you read and approve it, and we commit it as **JS2-CP1** before any code. That way the commit history shows the gate came first.
