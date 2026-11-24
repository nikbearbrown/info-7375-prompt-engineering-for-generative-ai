# Predictions — brand-name lookup fix (written BEFORE the fix is built)

Arundhati Kandelkar · INFO 7375 Final Project Film · written 2026-11-23 15:32 EST, before any fix code was written.

**Context (from my 25-row eval, `../final-project-film/evidence/eval-25-rows-2026-10-25.md`):**
typing the brand name missed three strong sponsors stored under a legal name — Robinhood (ROBINHOOD MARKETS INC, 824),
SoFi (SOCIAL FINANCE INC, 182), Chime (matched tiny CHIME INC, 2, and missed CHIME FINANCIAL INC, 580).

**The fix that will be built** (no fuzzy auto-match, per brief §6 / gate G2):
- **A. Whole-word candidates.** If the typed name is the first word(s) of a dataset name (whole words only, so
  "CHIME" does not hit "ARCHIMEDES"), list those rows as candidates and send them to a human (gate G2). Never auto-pick.
- **B. Alias list.** A short hand-written file mapping a brand to its legal name(s), labelled as *my input*, for
  cases where the brand is not part of the legal name.

*Disclosure: Claude has already looked at the dataset rows for these three names while planning the fix. I have not.
My answers below are written without seeing those rows.*

---

## My predictions (my own words — written before the run)

*Answers below are Arundhati's own text, pasted verbatim into this file by Claude at her request; the time is the
moment she sent them.*

1. With **A only**, how many of the 3 (Robinhood, SoFi, Chime) will now show the right company as a candidate? Which ones, and why?

   > I think 2 out of 3 will show the right company. Robinhood should match because the legal name starts with ROBINHOOD. Chime should also match because CHIME FINANCIAL INC starts with the brand name. SoFi probably won't match because its legal name, SOCIAL FINANCE INC, doesn't contain SOFI.

2. Which of the 3 (if any) will **need B** (the alias list)? Why?

   > SoFi will need B because its legal name is completely different from the brand name. Whole-word matching alone won't find it. An alias mapping from SoFi to SOCIAL FINANCE INC should solve this.

3. Of the **other 22** eval rows, will A change any answer — e.g. a new wrong candidate? Guess how many and which kind of name.

   > I think A might introduce a few additional candidates in the other 22 rows. This could happen when a brand name is also the beginning of another company's legal name. Some candidates might not be the correct sponsor, but since we are not auto-selecting anything, the human check should prevent incorrect matches.

4. Will any of the 3 now be **auto-answered** without a human, or will all go through the human check (G2)? Is that what you want?

   > All three should go through the human check (G2). Even if the system finds the correct company, it should only suggest it as a candidate and never automatically select it. Yes, this is what I want because a wrong automatic match could lead to incorrect sponsor information.

5. What result would tell me the fix **did not work**?

   > If Robinhood or Chime still fail to show their correct legal company names as candidates, or if SoFi is not found even after adding the alias mapping, I would consider the fix unsuccessful. Also, if the system automatically selects a company without human approval, that would violate the requirement.

Time written: **2026-11-23 15:32 EST**
