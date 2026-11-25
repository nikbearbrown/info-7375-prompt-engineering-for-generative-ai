# FRICTIONAL: JS3

The "What happened" and "Evidence" lines are facts Claude Code organized from the commits and outputs on
2026-11-25. Lines marked **(Ashwin)** are blank on purpose: only Ashwin can supply the experience. Nothing about
Ashwin's thinking or feelings is inferred.

## 2026-11-25: writing FILTER.md before any code

- **What happened:** Claude Code drafted questions (`drafting/FILTER-QUESTIONS.md`). Codex drafted FILTER.md from
  them. Claude Code pointed out that threshold 6 never binds, because every eligible posting already scored at
  least 6. Codex suggested 7, and Ashwin approved it.
- **Evidence:** FILTER.md committed alone at `a3a7a2af`, before the filter code.
- **(Ashwin) What I tried or expected, and what I accepted, changed or rejected:** Not supplied.

## 2026-11-25: blind held-out labels

- **What happened:** 30 postings were drawn with seed 20261125: 20 engineering-like titles and 10 others. Ashwin
  labeled them Y 7, N 19, ? 4, before seeing any filter output for them.
- **Evidence:** `labels/heldout-sheet.csv`, committed alone at `9757ee7b`.
- **(Ashwin) What was hard to decide:** Not supplied.

## 2026-11-25: the reject audit, and its provenance

- **What happened:**
  - Codex inferred 61 audit verdicts from the held-out labels (`labels/audit-ai-draft.csv`).
  - Claude Code built blind review cards for the brief's minimum of 47 postings.
  - The 47 verdicts entered in batches were first recorded as hand verdicts. Ashwin then stated they were Codex
    suggestions, not independent judgments, and the record was corrected.
  - The hand-judged audit stands at 0 of 47.
- **Clearance rule:** a posting that needs a clearance, where Supriya's eligibility is unknown, is `?`. Willingness
  to get one is not eligibility.
- **Evidence:** `12cb35b4`, `036e6fae` (cards); `e5828b69` … `7eb48860` (verdicts first mislabeled); `b03e6b29`
  (correction); `audit/EXPLORATORY-v1.0-ai-assisted.md`.
- **(Ashwin, proposed; drafted with Codex, pending confirmation)** I asked for AI-assisted verdicts to save time. They did not satisfy the hand-judged audit, and inferring them from my earlier labels compromised the independence of later evaluation.
- **(Ashwin, proposed; drafted with Codex, pending confirmation)** Next time, I would keep development judgments separate from the held-out labels and record the source of each judgment when it is entered.

## 2026-11-25: claim labels

- **What happened:**
  - Claude Code showed review cards in batches. Their excerpts left out the structured fields.
  - Labels for claims 1–40 came from Codex, working from those excerpts. They were first recorded as Ashwin's own,
    which Ashwin corrected.
  - Codex then labeled the rest against the saved text and structured fields, and corrected 6 of its earlier labels.
  - Claim 42, an "I cannot tell" about remote work, turned out contradicted: the structured field says `onsite`, and
    Claude was never shown that field.
- **Evidence:** `shortlist/claim-sheet.csv` (`label_source`), `SHORTLIST.md`, `267dfff9`.
- **(Ashwin, proposed; drafted with Codex, pending confirmation)** I used Codex's labels to move through the claims faster. I did not independently verify all 90. The excerpt cards omitted structured information needed to evaluate claim 42.

## 2026-11-25: a false friend and one change

- **What happened:** The seniority word "manager" fired on "Software Engineer - Mission Manager". The posting calls
  Mission Manager "Palantir's PaaS", so the word named a product, not a role. Ashwin first kept the fix
  unimplemented, then had it made as v1.1:
  - development set: 2 postings went REJECT → KEEP;
  - held-out set: recall on known labels went 0/7 → 1/7, on a set marked potentially contaminated.
- **What remained unresolved:** no unused sample can test this change, because none of the Cloudflare snapshot's
  titles has the phrase. And on the held-out set, the filter still rejects 6 of the 7 postings labeled Y.
- **Evidence:** `77daf2d1`, `78adf4b9`, `c9821188`; `CHANGE.md`; `changes/HELDOUT-v1.0-vs-v1.1.md`.
- **(Ashwin) What surprised me:** Not supplied.
- **(Ashwin, proposed; drafted with Codex, pending confirmation)** "Mission Manager" names a product here. Correcting that title match is separate from establishing whether the job suits Supriya.

## 2026-11-25: the tool server

- **What happened:**
  - Our client probed `claude mcp serve`. It listed 28 tools with no annotations. Read went outside its working
    directory, and Write created a file, both with no prompt.
  - Claude Code used our server as a client. It first tried `server/discover`, which we don't implement, then scored
    one posting and passed on our held-out refusal word for word.
  - Our server's description says it cannot "write anything", but it writes its transcript.
- **Evidence:** `evaluations/`, `transcripts/`.
- **(Ashwin, proposed; drafted with Codex, pending confirmation)** Use the proposed decisions in `evaluations/*/EVALUATION.md` after I confirm them.

## Still open

- **(Ashwin)** The 47 hand verdicts, any human claim labels, confirmation of the trust decisions and sign-off, and the signature.
- **(Ashwin, proposed; drafted with Codex, pending confirmation)** Unresolved question: how many suitable early-career postings does the filter miss on a fresh, independently judged sample?
