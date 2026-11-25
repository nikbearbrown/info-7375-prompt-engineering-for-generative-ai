# FRICTIONAL: JS3

The "What happened" and "Evidence" lines are facts Claude Code organized from the commits and outputs on
2026-11-25. The three personal slots, first marked "Not supplied", were filled on 2026-11-25 (evening) with lines Ashwin chose from options Claude Code drafted and approved in chat. Confirmed Codex-drafted descriptions
are attributed below; no personal thinking or feelings are inferred.

## 2026-11-25: writing FILTER.md before any code

- **What happened:** Claude Code drafted questions (`drafting/FILTER-QUESTIONS.md`). Codex drafted FILTER.md from
  them. Claude Code pointed out that threshold 6 never binds, because every eligible posting already scored at
  least 6. Codex suggested 7, and Ashwin approved it.
- **Evidence:** FILTER.md committed alone at `a3a7a2af`, before the filter code.
- **What I tried or expected, and what I accepted, changed or rejected** (Ashwin; chosen from options drafted by Claude Code, approved by Ashwin in chat on 2026-11-25): "I accepted 7, but I would rather have compared 6, 7 and 8 on labeled postings before choosing."

## 2026-11-25: blind held-out labels

- **What happened:** 30 postings were drawn with seed 20261125: 20 engineering-like titles and 10 others. Ashwin
  labeled them Y 7, N 19, ? 4, before seeing any filter output for them.
- **Evidence:** `labels/heldout-sheet.csv`, committed alone at `9757ee7b`.
- **What was hard to decide** (Ashwin; chosen from options drafted by Claude Code, approved by Ashwin in chat on 2026-11-25): "Clearance postings were hardest: Supriya might be willing, but nothing says she is eligible, so I marked them '?'." (All 4 of the '?' held-out labels are Defense or US Government postings.)

## 2026-11-25: the reject audit, and its provenance

- **What happened:**
  - Codex inferred 61 audit verdicts from the held-out labels (`labels/audit-ai-draft.csv`).
  - Claude Code built blind review cards for the brief's minimum of 47 postings.
  - The 47 verdicts entered in batches were first recorded as hand verdicts. Ashwin then stated they were Codex
    suggestions, not independent judgments, and the record was corrected.
  - At that stage the hand sheet was empty. On 2026-11-25 Ashwin later confirmed personal review of all 47 sample postings, retaining the suggested verdicts; the later review was not blind.
- **Clearance rule:** a posting that needs a clearance, where Supriya's eligibility is unknown, is `?`. Willingness
  to get one is not eligibility.
- **Evidence:** `12cb35b4`, `036e6fae` (cards); `e5828b69` … `7eb48860` (verdicts first mislabeled); `b03e6b29`
  (correction); `audit/EXPLORATORY-v1.0-ai-assisted.md`.
- **(Ashwin; drafted with Codex, confirmed by Ashwin on 2026-11-25 as a description of the recorded events)** I asked for AI-assisted verdicts to save time. They did not satisfy the hand-judged audit, and inferring them from my earlier labels compromised the independence of later evaluation.
- **(Ashwin; drafted with Codex, confirmed by Ashwin on 2026-11-25 as a description of the recorded events)** Next time, I would keep development judgments separate from the held-out labels and record the source of each judgment when it is entered.

## 2026-11-25: claim labels

- **What happened:**
  - Claude Code showed review cards in batches. Their excerpts left out the structured fields.
  - Labels for claims 1–40 came from Codex, working from those excerpts. They were first recorded as Ashwin's own,
    which Ashwin corrected.
  - Codex then labeled the rest against the saved text and structured fields, and corrected 6 of its earlier labels.
  - Claim 42, an "I cannot tell" about remote work, turned out contradicted: the structured field says `onsite`, and
    Claude was never shown that field.
- **Evidence:** `shortlist/claim-sheet.csv` (`label_source`), `SHORTLIST.md`, `267dfff9`.
- **(Ashwin; drafted with Codex, confirmed by Ashwin on 2026-11-25 as a description of the recorded events)** I used Codex's labels to move through the claims faster. I did not independently verify all 90. The excerpt cards omitted structured information needed to evaluate claim 42.

## 2026-11-25: a false friend and one change

- **What happened:** The seniority word "manager" fired on "Software Engineer - Mission Manager". The posting calls
  Mission Manager "Palantir's PaaS", so the word named a product, not a role. Ashwin first kept the fix
  unimplemented, then had it made as v1.1:
  - development set: 2 postings went REJECT → KEEP;
  - held-out set: recall on known labels went 0/7 → 1/7, on a set marked potentially contaminated.
- **What remained unresolved:** no unused sample can test this change, because none of the Cloudflare snapshot's
  titles has the phrase. And on the held-out set, the filter still rejects 6 of the 7 postings labeled Y.
- **Evidence:** `77daf2d1`, `78adf4b9`, `c9821188`; `CHANGE.md`; `changes/HELDOUT-v1.0-vs-v1.1.md`.
- **What surprised me** (Ashwin; chosen from options drafted by Claude Code, approved by Ashwin in chat on 2026-11-25): "The random reject audit looked fine because 25 of 30 were sales or ops jobs. It could not show the misses the held-out set showed."
- **(Ashwin; drafted with Codex, confirmed by Ashwin on 2026-11-25 as a description of the recorded events)** "Mission Manager" names a product here. Correcting that title match is separate from establishing whether the job suits Supriya.

## 2026-11-25: the tool server

- **What happened:**
  - Our client probed `claude mcp serve`. It listed 28 tools with no annotations. Read went outside its working
    directory, and Write created a file, both with no prompt.
  - Claude Code used our server as a client. It first tried `server/discover`, which we don't implement, then scored
    one posting and passed on our held-out refusal word for word.
  - Server 1.0.0 said it could not "write anything", but wrote its transcript. Server 1.1.0 corrects the disclosure and identifies filter v1.0; see `bf491431`.
- **Evidence:** `evaluations/`, `transcripts/`.
- **(Ashwin; drafted with Codex, confirmed by Ashwin on 2026-11-25 as a description of the recorded events)** Approved in evaluations/*/EVALUATION.md on 2026-11-25.

## Follow-up verification

- **(Ashwin)** All 47 required audit rows now have Ashwin's confirmed personal verdicts, with prior AI exposure disclosed. Claim labels remain AI-assisted. The trust decisions, sign-off and signature were already confirmed on 2026-11-25.
- **(Ashwin; drafted with Codex, confirmed by Ashwin on 2026-11-25 as a description of the recorded events)** Unresolved question: how many suitable early-career postings does the filter miss on a fresh, independently judged sample?
