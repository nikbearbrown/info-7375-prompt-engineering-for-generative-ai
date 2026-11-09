# FRICTIONAL — Job-Search Agent 2: The Loop, the Tools, and the Diff

Dated entries, written as the work happened. Times are local (America/New_York).

Each entry says what I tried, what happened, what I accepted, changed, or rejected from Claude, and the commit, prompt, or test it traces to. This log summarizes my Claude Code sessions. It does not paste transcripts: those stay on my machine, as the brief's privacy rules require.

## 2026-11-01 — Read the brief, started this log
- Pasted the JS2 brief into Claude Code and asked for its reading of the assignment, and for new files that continue from Job-Search Agent 1.
- **Where JS1 ended.** It was submitted on 2026-10-31 as branch `atharva-h/js1-contract-and-watch`, commit `f0b7a6b`, in `fall-2026/atharva-h/js1-contract-and-watch/`. It watches one Greenhouse board (Abacus Insights) with a rule judge and a Claude judge. Python standard library only; 43 tests.
- Claude created this folder, `js2-loop-tools-diff/`, with this log and an empty `GATE.md` that has only the six section headings the brief asks for.
- Nothing is built yet: no gate content, no code, no runs.
- Due Tuesday 2026-11-10, 11:59 pm ET.
- **Still to decide:**
  - what to start from: my JS1 code, the Reallocation Engine's ATS providers, or the instructor's Lectern collector
  - which boards (at least 3, on at least 2 applicant-tracking systems)
  - which board fails on purpose

## 2026-11-01 — Gate interview
- I chose to be interviewed for `GATE.md`. Claude asked one section at a time and offered options; the decisions are mine.
- **Probes before the gate.** Claude probed the three systems first. These were not agent runs, and nothing from them was saved.
  - Abacus (Greenhouse) had 18 postings, Valon (Ashby) 27, Weave (Ashby) 29, and Xsolla (Lever) 189, which took about 2.7 s.
  - A misspelled name gets a real 404 on all three systems. Ashby's 404 body is plain text, not JSON.
  - The Greenhouse slug `abacus` belongs to a different employer, "ABACUS", with 45 postings.
- **Start point:** my JS1 code.
- **Boards:** Abacus (Greenhouse), Valon (Ashby), and Xsolla (Lever).
- **Failing on purpose:** Ashby `valonn`, a real 404.
- **Finished wrong answer:** the wrong-board run, Greenhouse `abacus` posing as Abacus Insights. It is caught by a separate name check that doesn't read the loop's report.
- **Exits:** I first picked "finished, with failures listed." Claude pointed out that the gate still had to say when `incomplete` happens. I switched: `finished` only when every board succeeds, and any failed board makes the run `incomplete`.
- **Budgets and repeats:**
  - At most 5 boards, 10 requests, and 60 s per run, changed only by a dated GATE.md entry.
  - A repeat is the same method plus URL; it is refused, logged, and the run goes on.
  - A permission violation stops the run with `error`.
- **Error policy:** a 404 is never retried; a timeout or 5xx is retried once after 2 s; nothing is invented.
- **Permission policy:**
  - HTTPS GET only to the three ATS hosts, with no cookies and no auth.
  - Reads only inside this folder; writes only in `runs/` and `state/`.
  - My approval (y/N in the terminal, "no" without one) is needed to reset state, delete a run, change the board list, or write over 5 MB.
- **Wrong versions:** four, each the plausible mistake for one of my decisions: a prefix path check, a failed board read as "no new jobs", a substring host check, and retries not counted against the budget.

## 2026-11-09 — Gate additions, gate committed before code
- **Three additions to `GATE.md`, all dated, still before any code:**
  - **No judging in JS2.** The loop reports new and closed postings. JS1's judges stay in JS1. In JS1 my rule never produced `relevant` on a real posting, and JS2 doesn't need verdicts.
  - **Closed postings** are part of the `finished` report. It's the same id comparison, so it costs no extra requests.
  - **No overwrite.** A run never overwrites an earlier run's folder or report, and a normal run only adds seen ids.
- **A pre-submit check** will fail if a TODO is still open or the README claims a run with no saved trace. It's a submission tool, not part of the gate.
- **Gate committed first.** `GATE.md` and this log were committed on branch `js2-loop-tools-diff` before any JS2 code existed.
