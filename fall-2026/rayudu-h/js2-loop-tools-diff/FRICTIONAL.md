# FRICTIONAL.md — Job-Search Agent 2

> **How this was written.** Claude Code organized these entries from the working sessions on Oct 31 and Nov 7, 2026 (ET). Every fact comes from that session, a file or a command output. Quotations are Hemanth's words; where Hemanth gave no words, there is no entry for Hemanth's experience.

## Oct 31, about 6:40–7:07 PM: from "watch every company" to a gate

- **What happened:** during JS1, Hemanth twice asked to watch every Greenhouse company. Both times the decision was to keep JS1 to one board, because multi-board watching is JS2's task. Right after JS1, Hemanth asked: "But shouldn't we do JS2?"
- **What Hemanth chose:** Claude listed 8 public boards with live posting counts. Hemanth picked **Anthropic, Notion, Perplexity**, and all three deliberate failures: "a,b,c".
- **What Hemanth delegated:** asked how the exits should work, Hemanth said "do whatever is the best and efficient". Claude proposed the whole rest of the gate, marked as its own proposal, and Hemanth replied "accept". The gate was committed alone as `92b5c77` before any JS2 code.

## Oct 31, about 7:10–7:20 PM: the gate contradicted itself

- **What happened:** while building, Claude found that failure (b), a timeout on the real Perplexity URL, would never run. The repeat rule refuses a second identical GET in one run.
  - A second question came up: is the error policy's one retry a "repeat"?
- **What Hemanth did:** accepted amendment A1 (the timeout moves to OpenAI's board) and A2 (a retry isn't a repeat but counts toward the budget): "yes to A1 and A2".
- **Evidence:** `GATE.md`, Amendments.

## Oct 31, 7:12–7:13 PM: the live run and the finished wrong answer

- **Live run:** **incomplete**. Three baselines; the 404 wasn't retried; the timeout was retried once.
- **The seeded empty Notion response:** the unchanged JS1 logic reported **"finished, 0 new"**, which is wrong. `scripts/check_run.py` caught it from the raw files. Reproducing it also showed the defect had overwritten Notion's saved count with 0.
- **Evidence:** `runs/`, `REVIEW-PACKET.md` §1.

## Oct 31, 7:13–7:40 PM: the review

- **Test first:** the failing test was committed before any patch (`998e487`). Hemanth: "ran it, 2 failed 1 passed — write the patch".
- **The patch:** 8 lines (`bd2bc05`).
- **After:** Hemanth ran the full suite: "the test suite says 52 accepted".
- **Decision:** "accept because tests pass".
- **The case the test misses:** Hemanth chose Claude's suggestion, a partial board (148 → 3) that's still trusted.

## Push timing (Oct 31, 7:17 PM)

- **What happened:** pushing required catching up with classmates' commits, and the rebase rewrote the hashes of the 6 unpushed JS2 commits. Their author times were kept, so the order is still provable.
- **What changed:** after that, every step was pushed immediately, and with a merge instead of a rebase.

## Nov 7, evening (run at 6:42 PM EST): checking against Canvas, then the second live run

- **What happened:** Hemanth pasted the Canvas assignment text and asked where JS2 stood. Claude compared it item by item. One gap: the driver's seat had "—" in the loop row, where the assignment asks what Hemanth should do and why it stays Hemanth's.
- **What Hemanth decided:** "1 yes, 2 yes do the live run". That meant: replace the driver's seat table with Claude's proposed rows, and run the loop live a week after the baseline.
- **The run** (`runs/2026-11-07T184247-live/`, 6:42 PM): **incomplete**. The deliberate failures were handled exactly as on Oct 31. There were 84 new postings; the rule marks 11 relevant; Claude judged 25 and agreed with the rule on all 25.
- **What it exposed, which no Oct 31 run could** (README, "The Nov 7 run"):
  - the Claude budget ran out after 25, so 59 new postings, 5 of them rule-relevant, got no judgment and are now marked seen;
  - the 120 s budget is checked only between boards, and this run used 119.4 s;
  - 61 Anthropic ids changed while the count stayed at 675.

## Still open

- Sign-off: Hemanth accepted Claude's drafted list and asked Claude to type the signature (Oct 31, 2026). The Nov 7 run changes the "Not checked" list, so the sign-off needs Hemanth's confirmation again.
- The three Nov 7 findings are recorded, not fixed. Each would change the gate's budgets or exits, which only Hemanth decides.
