# FILTER-NOTES: how FILTER.md v1 became code

*Drafted by Claude Code on 2026-11-25, alongside the filter code and after FILTER.md was committed
(`5e6a7703`, `3163fdb5`). It was first committed in `a774c4d6` (17:35 EST), after `js3/filtering.py`
(`e8a9c431`, 17:20). An earlier version of this line said "before any filter code existed", which was
wrong, as the independent review found. FILTER.md is Shreyash's and is not edited. This file records how each answer
was made computable in `js3/filtering.py`, so a reader can apply the filter by hand and get the code's
verdict. Where FILTER.md did not force a reading, the line is marked **choice**. The measured counts
come from filter v1 run on all 789 collected postings (`results/filter-v1/`).*

## Where the filter lives

- **The document:** `FILTER.md`.
- **The file the code reads:** `filter-v1.json`, with every word list and number from FILTER.md.
  `tests/test_js3_filter_doc.py` fails if the two disagree. A filter change is a change to this one
  file, which is how SCORE.md changes one object at a time.
- **Inherited unchanged from JS2:** `jsagent/rule.py`, rule v2 rev 3. JS3 calls its term matcher, its
  experience reader (`year_phrases`), and its hybrid, state-list, contract and relocation patterns.
  JS2's tests for them still pass.

## Reading a posting

- **The text the rules read** is `content`, built exactly as JS2 builds it. A test checks this on the
  real Physician Reviewer posting.
- **JS3 adds four things:**
  - the employment type the board reports (Lever `commitment`, Ashby `employmentType`; Greenhouse
    has none);
  - the blocks of the text, and the section each block falls under (`js3/sections.py`);
  - when the agent first and last saw the posting;
  - whether it was open in today's run.
- **Every evidence quote is an exact slice** of the field it names. `verify_quotes()` checks all of
  them (wrong version 4). On the 789 postings, 0 quotes were not found.

## Three outcomes and the verdict (answers 10 and 11)

- **Outcomes.** Each rule passes, fails, or says *cannot tell*. Cannot tell appears only where
  FILTER.md asks for it: 6a, 6b and follow-up A, all in Rule 3.
- **Verdict.** Any fail makes the posting **Not Relevant**. Otherwise, any cannot tell makes it
  **I cannot tell**. Otherwise it is **Relevant**.
  - **Choice:** a fail wins over a cannot tell. Answer 10 says a job is kept "only if it passes all
    the rules", so a posting that fails its title is not kept whatever its location says.
    Answering "I cannot tell" there would hide a certain answer.
- **Closest call:** exactly one rule fails and the other five pass. Strict reading of answer 10: a
  cannot tell is not a pass.

## Rule 1, title (answer 4)

JS2's condition 1, unchanged. Each of the nine phrases matches as a whole phrase, ignoring case, so
"Software Engineering Coordinator" and "HTML Engineer" fail.

## Rule 2, department (answer 5, review/19)

JS2's condition 2, plus one alias: on the `palantir` board only, the department `Dev` counts as
Engineering.

- **Choice:** the alias matches the exact value `Dev`, on that one board. That follows review/19:
  "not automatically to other companies using the same department name".
- **Measured:** no posting fails only Rule 2. Dropping Rule 2 entirely would change 0 of the 789
  verdicts (SCORE.md, F-tests). Turning off the `Dev` alias would also change 0 verdicts, but the
  closest calls fall from 44 to 9.

## Rule 3, location (answer 6, 6a, 6b, follow-up A, wrong version 1)

The order the code follows:

1. **Missing:** no location and no offices means **fail** "missing", as CONTRACT.md and answer 3 say.
2. **Boston:** the location field or an office names **Boston**.
   - If the field and the office list agree, or there is no office list: **pass**.
   - If they disagree about Boston (**6b**), the code checks the description. A sentence that names
     Boston with a workplace word (based, located, office, hub, hybrid, on-site, in-office, commute)
     gives **pass**. Such a sentence for the other city only gives **fail**. Otherwise, **cannot tell**.
   - **Choice:** "check the job description" is read as *a sentence that places the job*. A bare
     "Boston" in company boilerplate (headquarters, offices list) says nothing about where this job
     is.
   - **Choice:** Boston only. Cambridge or another Massachusetts town would fail. None occurs in the
     789 postings.
   - **Measured:** 50 postings got 6b cannot tell and 2 were settled as fail. All 50 also fail
     another rule.
3. **Remote:** a "Remote" tag in the location or offices, or the board's workplace type says remote.
   - **Follow-up A:** if the ad says hybrid or on-site (JS2's pattern) and the job is not in Boston,
     the result is **fail**: the description wins. If the ad *also* says remote is possible
     ("fully remote", "this role can be remote", ...), the result is **cannot tell**. Measured: 10
     fails, 4 cannot tell.
   - **6a and wrong version 1:** an office tag "Remote (State)" limits the job to that state.
     - If Massachusetts is not one of the states and the ad says otherwise, tag and ad **disagree**,
       so the result is **cannot tell**. 32 were measured:
       - in 2, the ad says the US broadly ("reside in the United States"); the real Physician Reviewer
         is one of them;
       - in the other 30, the ad's own state list includes Massachusetts.
     - If the ad says nothing more, the result is **fail** (wrong version 1): 44 measured.
     - An ad list of states without Massachusetts also gives **fail** (2).
   - A remote job open within the US with no state limit gives **pass** (38). So does a job whose
     tag or list includes Massachusetts (8).
   - **Choice:** a remote job that never names the United States gives **fail**, not cannot tell.
     CONTRACT.md requires that it "explicitly support remote employment within the United States".
     Measured: 3.
4. **Neither Boston nor remote:** **fail** (476).
   - But if the ad says the job can be remote, the location tag and the ad **disagree (6a)**, so the
     result is **cannot tell** (36).
   - **Measured false friend:** in 35 Oscar ads and 1 Palantir ad, the ad says something like "This
     is a remote position, open to candidates who reside in: Dallas, TX."; the cities and states vary.
     The words "remote position" matched, but the same sentence limits the job to one place. JS2's reading counts a "reside in" list only when it names
     **two or more** states, a number Claude Code set in JS2 rev 3, so one state is not seen as a
     limit. These should be **fail**, not cannot tell. No verdict changes, because all 36 fail
     another rule. AUDIT.md records it, and v1.1 (decision A4) reads 35 of the 36 as fail.

## Rule 4, skills (answer 7, wrong version 2)

- **Matching:** JS2's whole-term, case-insensitive matching of Alex's ten skills. At least 2 must be
  found.
- **Wrong version 2:** text under a benefits heading is blanked out first.
  - "Benefits" means a block whose heading `js3/sections.py` reads as benefits, perks, compensation,
    pay range, what we offer, why join, total rewards or "Life at".
  - Greenhouse headings come from the HTML: h1 to h6, or a wholly bold paragraph. Ashby and Lever
    headings come from short lines ending in ":" or using a heading word, and from their HTML
    headings.
  - **Choice:** that word list. In today's run, 5,488 of 23,055 blocks were classed as benefits. Most
    are Palantir's "Life at Palantir" and Linear's "What we offer".
- **Not handled (JS1 already named it):** case-insensitive matching makes `React` match the verb
  "react". Measured false friend: "react quickly to new stimuli" in 2 Palantir ads (AUDIT.md). Also,
  "React Native" contains the term `React`.

## Rule 5, experience (answer 8, follow-up B, wrong version 3)

- **Inherited:** JS2 rev 3, unchanged. The highest minimum among the mandatory "N years" phrases must
  be 3 or less. Preferred and benefits phrases do not count. A range counts from its bottom number,
  so "3-5 years" passes.
- **Follow-up B:** no requirement stated gives **pass**. The line says "experience not stated" and
  carries no quote. A test checks that no quote is invented.

## Rule 6, exclusions (answer 9, follow-up C)

- **Inherited from JS2:**
  - the five title words;
  - "unpaid" anywhere in the title or the ad (measured: 1 posting, which also fails other rules);
  - contract in the title, or contract-only phrases in the ad;
  - relocation required while the job is not in Boston (measured: 0 postings).
- **Answer 9 and follow-up C add:**
  - the title words Intern, Interns, Internship, Part-time, Part Time, Temporary, Seasonal,
    Fixed-term and Fixed Term;
  - a board employment type that is not full-time;
  - an ad sentence such as "this is a temporary position" outside the benefits text.
- **Choice:** "full-time permanent" means that when a board gives an employment type, it must be
  Full-time. So Lever's `Internship` (50 postings), `Scholarship` (1) and `Fixed-Term` (1) are out.
  Greenhouse gives no type, so its postings are judged by title and text only.

## The evidence rules and the claims (answer 11, follow-up B)

`js3/claims.py` turns a kept posting's justification into nine claims: role, department, location,
skills, experience, seniority, full-time, paid, relocation.

- **Must-haves:** the ones the accepted text lists (role, location, experience, exclusions).
  Department and skills are not must-haves.
- **Labels:** supported when the code has an exact quote that states the claim; contradicted when a
  quote states the opposite (with quotes both ways, it is contradicted and marked a conflict);
  insufficient otherwise.
- **Choice:** a skill counts as "asked for" only if it is named under the ad's own requirements,
  preferred or responsibilities headings, and not as something to "pick up". SHORTLIST.md shows that
  this is too strict in one case and right in another.
- **Choice:** "full-time" is supported only by the board's employment type or by a sentence outside
  the benefits and legal text. "Full-time employees are eligible for benefits" does not say this job
  is full-time.
- **Abstention:** the agent says "I cannot tell" when a must-have claim is insufficient or in
  conflict, except "experience not stated" (follow-up B).

## What this filter does not do

- It does not read meaning. A matched word is treated as the thing it names: the React verb, and a
  remote position limited to Dallas.
- It does not check that a Boston-tagged job's ad names another city as its base. Only the 6b
  disagreement between field and offices is checked.
- It does not tell a staffing agency or a fake posting from a real one.
- It does not know whether a posting has closed between runs. It only records whether it was in the
  latest run.
