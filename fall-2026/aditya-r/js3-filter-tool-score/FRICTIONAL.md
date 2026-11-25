# FRICTIONAL — Job-Search Agent 3

Dated entries. **Claude Code's process notes** are labeled as Claude's: they record what happened in the session, with commits. **Aditya's entries** are his own words, added by him. Claude does not write his experience for him.

---

## 2026-11-25 — Claude Code session notes

**1. Starting point and gate (`80427cc`)**
- *Tried / expected:* write FILTER.md before any JS3 code. Expected the inherited JS1 rule to be too strict to give near-threshold cases, because it kept 5 of 903 in JS1. So v1.0 turns it into an additive score with a threshold.
- *What happened:* the gate was committed alone. The filter tests followed (`5de50f2`), then the scorer (`b33fca0`).
- *Correction:* the `5de50f2` subject says "25 filter tests". The real count is 23 (including parametrized cases). It is left unedited in history and corrected here.

**2. A plan that met the data (`b4284db`)**
- *Expected:* "8 keeps for held-out" to be possible.
- *What happened:* v1.0 kept only 11 of 1,294 postings, and those fall in 7 near-duplicate clusters. Four of them are the same "Software Engineer - New Grad (2027 Start)" job, listed separately for London, Berlin, Aarhus and Amsterdam.
  - The exact-duplicate rule in FILTER §4 would have let these city copies sit on both sides of the split.
- *What I did:* wrote amendments A1 (near-duplicate clusters, Jaccard ≥ 0.8) and A2 (smaller held-out keep stratum) **before drawing any sample**. Both are logged in FILTER.md.
- *Unresolved:* A1's single-link clustering chains one template family to 69 postings. That is conservative against leakage, but coarse.

**3. A bug in my own draw (`e6a3d24`)**
- The first draw put all 7 dev keeps on the sheet, including three city copies of one cluster. That contradicted A1's "one posting per cluster".
- I fixed it before the sheet was shown to anyone. The committed sheet has 63 rows from 63 distinct clusters, and `test_heldout_and_dev_disjoint_by_cluster` checks this.

**4. The tool server meets a real client (`4ee6c00`)**
- *Expected:* Claude Code to open with `initialize`.
- *What happened:* it first sent `server/discover`, with protocol version **2026-07-28**. My server returned -32601, and Claude Code fell back to `initialize` with 2025-11-25.
  - I did not know about this probe before the run. The transcript is the evidence.
- *Learned:* "compatible" here means "compatible through the client's fallback".

**5. My server overstated itself (`85a720b`)**
- While writing "declared vs actual", I found that the `instructions` string sent to Claude said "no writes". With `--log`, though, the server appends a local wire log.
- The string was corrected after the run. The transcript keeps the old string as sent.

**6. The other server surprised me (`85a720b`)**
- *Expected (from the source comments):* client Roots replace the command-line directories.
- *Exercised:* session C confirmed it. A client's root (`other_root/`) became readable, and the operator's `allowed/` stopped being accessible. `--confine-roots` (session D) prevents this.
- *Also:* the package requires Node ≥ 24, but ran on Node 22.14 for these sessions.
- *Not tested:* the 2026-07-28 era, `move_file`/`edit_file`, and resources.

**7. A false friend, larger than predicted (measured, not yet acted on)**
- *Prediction:* `agent` would match support or sales "agents".
- *Measured:* on Databricks, "agent(s)" and "unity catalog" occur in all 995 postings. In about 900 of them, the only match is the company "About" boilerplate ("Agent Bricks … Unity Catalog"). On Notion, "agents" occurs in all 155 postings, 124 of them boilerplate-only.
- So v1.0 gives almost every Databricks posting +2 for words describing the employer.
- *Next step:* whether and how to change the rule is decided on Aditya's **dev** labels. It is not decided on this measurement alone.

**8. Evidence rules made mechanical (`c815b79`)**
- The §2 LEVEL wording "0–2 years" was ambiguous for a person with under one year of full-time work.
- Clarifications C1/C2 were written before any label was returned.

---

## Aditya's entries

_(to be added by Aditya: labeling experience, disagreements with the filter or with Claude, what he checked himself, what remains unresolved)_
