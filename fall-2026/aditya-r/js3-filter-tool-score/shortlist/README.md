# Source-grounded shortlist (filter v1.1)

- **[`SHORTLIST.md`](SHORTLIST.md)** lists the 15 kept postings and 123 claims. Each claim carries a label, a source field and a verbatim quote, or says that no span was found. The machine-readable version is [`claims.json`](claims.json).
- **Rebuild:** `.venv/bin/python -m js3.reader_labels && .venv/bin/python -m js3.shortlist --filter v1.1`. Every quote is re-checked to occur verbatim in its field, and a mismatch is an error.
- **Who labeled what:**
  - ROLE, TOPIC, LEVEL and LOCATION are labeled **by rule** (FILTER.md §2, C1, C2).
  - DUTY claims and the LEVEL checks were labeled **by Claude Code reading the posting** (`js3/reader_labels.py`, reading rule C3).
  - A reader check that disagrees with a rule keeps both labels ("rule said X → reader").
  - Aditya's blind label is shown when the posting was on his sheet.
- **Posting types:** all postings named below are **observed** postings from the 2026-11-10 capture. The constructed postings live only in `tests/`.

## Relevance is not entailment (observed)

**`greenhouse:databricks:6865704002`**, "Software Engineer - New Grad, Distributed Data Systems (2027 Start)" (Aditya: yes).
- **TOPIC "mentions ml": supported.** The word occurs.
- **DUTY "the role itself involves ML work": insufficient.** The only span is the company mission ("Our mission at Databricks is to radically simplify the whole data lifecycle … all the way up to ML/AI with a unified platform"), which says nothing about this role's duties.
- So the keyword makes the posting *relevant to the filter* but does not *establish* the tempting claim that the job involves ML.

## The abstention rule and an actual abstention (observed)

**Rule** (FILTER.md §2): when no span states a claim either way, the agent says "I cannot tell from this posting". It never guesses. An empty title or description gives the verdict `cannot_tell`.

**Three actual abstentions:**
1. `greenhouse:databricks:8805655002` (title "デリバリーソリューションアーキテクト", Tokyo).
   - The title is empty after normalization, so the verdict is **`cannot_tell`**.
   - It is not counted as a reject. `js3.explain 8805655002` shows it.
2. `greenhouse:databricks:8546367002`: LOCATION is "United States", so **"I cannot tell whether it is in Boston or remote-US."**
3. `greenhouse:databricks:8760167002`: no years and no level word, so **"I cannot tell whether it is open to her level."**

## A counterexample that exposes the rule's limits (observed)

**`greenhouse:databricks:8546367002`**, "AI Engineer – Forward Deployed Engineering (AI FDE)", is **the top-scoring posting (11)**.
- The early-career phrase `new graduate` matches in "It is **not** intended for internship, new graduate, or entry-level applicants."
- Because a span *was found*, the abstention rule never fires:
  - the score adds E +3;
  - the LEVEL rule labels the claim **supported**.
- Read properly, the same sentence **contradicts** it.
- **The abstention rule only protects against missing evidence, not against misread evidence** (negation, or "the most junior data scientists" in `8091041002`).

## Evidence correction found by Aditya: S50 (observed)

**`ashby:notion:85947779-…`**, "Software Engineer, Early Career (AI)".
- **What the rule cited:** the LEVEL rule labeled the claim **supported** and cited "**This is NOT a new grad role!**". The scorer's early-career rule takes the first phrase in list order, and `new grad` comes before `early career`, so it matched a negated sentence.
- **Why that citation is wrong:**
  - The negated sentence excludes people who have **not yet graduated**. A New Grad role hires students who will graduate later.
  - It neither supports nor contradicts Priya, who graduated in December 2025.
- **The real support:** the title, "Early **Career**", and the next sentence, "This role is for candidates with **0-2 YOE** and can start full time right away."
- **The correction:**
  - The **label stays supported**. The **citation is replaced**, and the rule's original quote is kept in the note.
  - **The frozen v1.1 score is unchanged**: E is +3 whichever phrase matched, and "YOE" is not read by the years regex.
  - So this is an evidence error, not a scoring error. It is the third negation case after `8546367002`, and one more reason a v1.2 early-career rule should skip negated sentences.

## What the shortlist shows overall

- **LOCATION:** none of the 15 is in Boston. LOCATION is contradicted for 14 and insufficient for 1.
- **LEVEL:** contradicted for 13; S50 is supported, with corrected evidence. Seven of these are New Grad roles whose own text requires graduating in **fall 2026 to summer 2027** (or by December 2026), while the persona finished in December 2025. Aditya labeled several of these `yes`, with "check the graduation window".
- **"Kept by the filter" is a reason to read, not evidence of fit.** That decision stays with the person (README → driver's seat).
