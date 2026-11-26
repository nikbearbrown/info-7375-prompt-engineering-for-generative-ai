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

**9. The labels arrived as screenshots (`1a774a0`, `b8852e8`)**
- Aditya labeled in his own CSV and sent two screenshots.
- I transcribed the labels and checked all 63 titles against the committed sheet (63/63 matched), but **in doing so I read the 23 held-out labels before any freeze.**
- I disclosed this in `labels/TRANSCRIPTION.md`, and Aditya decided to draw a fresh held-out set (amendment A3). He had already deleted his CSV, so the transcription can only be re-checked against the screenshots.

**10. The fresh held-out set could not contain a keep**
- All 7 v1.0 keep clusters were already on the first sheet, so H2 (24 postings) has no v1.0 keep.
- This is stated in A3, `FREEZE.json` and the README. It limits what H2 can say about precision.

**11. Fixing the false friend made things worse (`61c999b`)**
- *Expected:* removing the boilerplate matches (C-a) would improve the filter.
- *Measured on dev:* recall fell from 6/9 to 3/9. The boilerplate +2 had been carrying the correct New Grad keeps.
- The three real misses (S05, S26, S43) came from the years penalty instead: Aditya labels "5+ years" roles `yes` and "Senior" titles `no`.
- Aditya chose v1.1 = C-a + C-b + C-e over C-b alone. Both were 9/9 · 9/9 on dev, so dev cannot separate them.

**12. My privacy check did not gate a commit (`fbfd556`)**
- I ran a grep for private strings in the same command as `git commit`, and the commit went ahead even though the grep printed matches.
- The matches were all "Northeastern University" from the **fictional persona's** education line, which is already public in JS1/JS2. So nothing leaked.
- *Lesson:* a check that only reports is not a gate.

**13. After the freeze, v1.1 amplified two false friends (`d966622`)**
- While labeling the shortlist I found that v1.1's top-ranked posting (`8546367002`, score 11) gets E +3 from "It is **not** intended for … new graduate …". Negation is invisible to whole-word matching.
- "the most junior data scientists" (`8091041002`) also became +3.
- Separately, all seven New Grad keeps require graduating in 2026–27, while the persona graduated in December 2025.
- Logged in FILTER.md as found after the freeze. **Not fixed**: a change now would need new held-out evidence.

**14. Claude disagreed with Aditya on a dev posting**
- In the 6-call format check, Claude answered "no" for S35 (New Grad, Aarhus) in both arms, citing the graduation window. Aditya had labeled it `yes`, "check the graduation window".
- This is not an error on either side: it is a different judgment about the same sentence. It is recorded in the driver's-seat table.

**15. The held-out set mostly said "nothing changed" (`94c0c89` and after)**
- *Expected:* H2 would show whether v1.1's dev gains generalize.
- *What happened:* v1.1 flipped no H2 posting, so this is a null result. H2 has only 1 yes in 22 decided labels.
- *Single changes:* C-b alone produced one false keep (H09), which v1.1 avoids only because C-a removes the boilerplate points. The single changes and the combination did not behave additively.
- *The one H2 yes:* "AI Automation Engineer" was missed by every filter version. The `ai engineer` phrase is not contiguous in that title, and v1.0 deliberately caps postings with no role phrase. Claude with the rules in context (arm B) caught it.
- *Not acted on:* fixing the role rule now would mean fitting to H2.
- *Learned:* a held-out set that cannot contain the cases a revision targets cannot validate that revision. Its value here was catching the interaction and the role-phrase blind spot.

**16. A test had been erasing Aditya's labeled sheet**
- While checking traceability, I found that `review/LABEL_SHEET.csv` was blank in git and on disk.
- *Cause:* `test_draw_is_reproducible` re-ran `draw()`, which rewrites the sheet, so every test run after the transcription had blanked it. I had fixed exactly this hazard for H2 (`44d3915`) without checking the first sheet.
- *No label was lost:* `labels/dev_labels.csv` was extracted before the first such test run.
- *Recovery:* I rebuilt the sheet from it, and the result's sha256 equals the seal recorded at import (`bf228882…`), so it is byte-identical.
- *Fixes:* `draw(write=False)` in the test, plus a new test that both labeled sheets still match their seals.
- *Lesson:* a reproducibility test must not have side effects on human data.

**17. Aditya caught a wrong citation in the shortlist; then a fresh audit of v1.1 (A4)**
- **The citation (found by Aditya while reviewing the shortlist):** S50's LEVEL claim was "supported", but its cited quote was the negated "This is NOT a new grad role!".
  - The very next sentence, "0-2 YOE", and the title "Early Career" are the real support.
  - *Cause:* the early-career rule takes the first phrase in list order. The score is unaffected, but the evidence was wrong.
  - *What I changed:* only the citation (a reader override that keeps the rule's original quote on record). The frozen scorer is unchanged.
  - *What it shows:* neither my reader checks nor the quote verifier would catch this. The verifier proves a quote exists, not that it supports the claim.
- **The A4 audit:** Aditya asked for a fresh blind audit of the frozen v1.1 (amendment A4, written before the draw).
  - 37 rows: 30 random rejects, 5 just-below calls, and the 2 keep clusters he had not seen.
  - *Limitation:* only 2 of the 11 v1.1 keep clusters were still unseen.

**Unresolved:**
- whether the v1.1 changes generalize (this is what H2 tests);
- a negation-aware early-career rule (a v1.2 candidate);
- whether eligibility, such as graduation windows, belongs in the filter or should stay a human check.

---

## Aditya's entries

2026-11-25 — How I decided which postings were worth Priya’s time

I read each posting and wrote down my verdict and reason before looking at the filter’s score. The question I used was, “Would I tell Priya to spend ten minutes reading this?” A yes meant I saw a duty that connected to her experience. I used unsure when a missing or conflicting detail could change my answer.

A07, “Skills Systems Architect,” was one of my yes calls. The title gave me pause, but the posting described building LLM extraction and agent pipelines with Python and SQL. I could connect that work to Priya’s co-op. When I checked the score afterward, I saw that the word “architect” had cost the posting six points. I’d keep v1.1 frozen and test that rule on fresh examples, including both hands-on engineering jobs and senior consulting roles.

A07 was the one yes among the 30 randomly sampled rejects. A05 and A25 were also misses, but I reviewed them because they were close to the cutoff. I reported those separately so a reader could tell how each posting entered the audit. Evidence: audit/AUDIT.md.

2026-11-25 — What I verified on my Mac

I ran scripts/personal_checks.sh at commit 0981dae and saved the output. All 49 tests passed, the suite caught all six deliberately wrong versions, and the H2 sheet matched its saved hash after the run.

S43 made the scoring change easiest to follow. The script showed the same four role points and four topic points in both versions. The experience penalty changed from −3 to −1, taking the total from 5 to 7 across a cutoff of 6. That explains exactly why this posting flipped. Whether the lighter penalty helps on future postings is still open. Evidence: evidence/aditya_personal_checks.txt.

2026-11-25 — Why I changed the evidence for S50

While reviewing S50, I looked up the sentence cited for the claim that Priya’s experience fit the role. The shortlist quoted “This is NOT a new grad role!” I could find those exact words, but they didn’t tell me whether eight months of experience was acceptable. The next sentence did: the employer explicitly said the role was for candidates with “0–2 YOE.”

I kept the supported label and corrected the citation. The score stayed the same. For future spot-checks, I’d ask one more question after locating a quote: Could someone reach this verdict from the quoted words alone? Evidence: review/postings/S50.md and shortlist/SHORTLIST.md.
