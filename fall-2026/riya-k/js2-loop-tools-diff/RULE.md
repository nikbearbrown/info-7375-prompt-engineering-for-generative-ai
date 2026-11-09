# The relevance rule (JS2)

The rule is my JS1 rule (`../js1-contract-and-watch/CONTRACT.md`, "The rule", with amendments 1 and 2), carried
over unchanged in commit `3109ccd`, plus two amendments made for JS2. It is applied only to **new** postings.
A rule verdict is a **record**: anyone can recompute it by hand from the posting and the persona.

A posting is **RELEVANT** only if all of these hold (all matching is case-insensitive and whole-word):

1. **Title words:** the title has one of AI, LLM, GenAI, Generative AI, ML, Machine Learning, Data Engineer, Data Platform,
   Data Scientist, Data Science, Analytics.
2. **Skills:** at least 2 of the persona's shipped skills appear in the title or content (Databricks and Unity Catalog
   are not counted, per JS1 amendment 1).
3. **Location:** US or Remote (not a non-US remote); state codes in capitals only (JS1 amendment 2).
4. **Not senior:** the title has none of Senior, Sr, Staff, Principal, Director, VP, Vice President, Head, Manager.
5. **Not an internship (amendment 3).**
6. **Full-time only (amendment 4).**

## Amendment 3 — no internships (2026-11-09)

- **Decided by:** me, in chat, after the TA's JS1 feedback asked for it.
- **Rule:** the title has the whole word `Intern` or `Internship` → NOT RELEVANT.
- **Made by:** a Claude Code patch I reviewed and accepted. See `review/REVIEW_PACKET.md`.
- **Test:** `tests/test_intern.py`, committed before the patch (`fdae00e`).

## Amendment 4 — full-time jobs only (2026-11-09)

- **Decided by:** me, in chat: "i dont want to see coops and any tpye of part time jobs i just want full time jobs".
  I also agreed to count Contract and Temporary as not full-time.
- **Rule:** NOT RELEVANT if **either**
  - the title has a whole word from: Co-op, Coop, Part-time, Part Time, Contract, Contractor, Temporary, Fixed-Term, Fixed Term; **or**
  - the board states an employment type that is not full-time (Ashby `employmentType` ≠ `FullTime`;
    SmartRecruiters `typeOfEmployment.label` ≠ "Full-time").
- **Why "either", not "the field wins":** on 2026-11-09, Notion's "Outcomes Architect [Contract]" had
  `employmentType: FullTime`. The board's own field was wrong, and only the title caught it.
- **Known cost:** a full-time job whose title uses "Contract" as a subject is excluded too (OpenAI "Legal Contract
  Manager, Public Sector", 2026-11-09; it is also excluded as senior, so no verdict changed that day).
- **Known gap:** Greenhouse gives no employment type, so a Greenhouse part-time job whose title doesn't say so is not caught.
- **Made by:** Claude Code in my main session (not a separately reviewed patch). **Test:** `tests/test_fulltime.py`,
  committed red before the change (`2eb2a7c`).

## Effect on the day-1 data (recomputed from the saved raw responses, 2026-11-09)

Before amendments 3–4, Databricks 6866538002 "Data Science Intern (2027 Start)" was relevant. After them, it is not.
The day-1 report itself was produced **before** both amendments and is left as it ran.
