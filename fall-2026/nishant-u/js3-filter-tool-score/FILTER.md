# FILTER — Job-Search Agent 3 (nishant-u), version 1

Written by Nishant U on 2026-11-24, before any JS3 code. Drafted with Claude (claude.ai); reviewed and approved by me. Builds on my JS1 contract rule and JS2 loop (f956e22).

## Sources expected
All postings collected by my JS2 loop and saved verbatim: Greenhouse faire and instacart (fields title, location.name, content), Ashby poshmark (fields title, location, descriptionHtml or descriptionPlain). Greenhouse poshmark is unverified-empty and contributes nothing. If a field is missing or empty, the rule that needs it fails as "missing: <field>" and the posting is never accepted on a default.

## Relevance rules (v1), each with its reason
- F1 Title role words (whole word, case-insensitive): data, analytics, analyst, scientist, machine learning, ML. Reason: Priya targets data and ML roles; these are the words such titles use.
- F2 Title exclusions: manager, director, head, lead, intern. Reason: people-management roles and internships don't fit a graduate on OPT.
- F3 US location: at least one location part ends in a US state code or says Remote with US (e.g. "Remote - US"). Reason: the visa clock is in the US.
- F4 Skill: at least 1 of Priya's 10 shipped skills appears as a whole word in the posting text (HTML removed). Reason: ties the verdict to her résumé.
A posting is accepted only if F1–F4 all hold; otherwise it is rejected with the first failing rule and the field it read. Seniority (Senior, Staff) is not judged.

## Evidence rules for shortlist claims
For each accepted posting, the shortlist states four claims, each labeled against the posting text only:
- C1 "US-based": supported if a US location part exists; contradicted if every location part is outside the US; insufficient if the location is missing.
- C2 "Uses <skill>": supported for each shipped skill found as a whole word; never inferred from a related word.
- C3 "Sponsors visas": supported only if the text explicitly says it sponsors or supports visas/H-1B; contradicted if it says it cannot sponsor, requires work authorization without sponsorship, or requires US citizenship or a clearance; otherwise insufficient. Silence is never "supported".
- C4 "Remote": supported if the location or text says remote; contradicted if it says onsite or in-office only (a hybrid schedule counts as contradicted for fully remote); otherwise insufficient.
Every label quotes the exact text it rests on, or says "no text found" for insufficient.

## Abstention rule ("I cannot tell")
The agent abstains (no accept/reject verdict, marked "abstain: cannot tell") when the posting text is shorter than 300 characters after removing HTML, or when the board it came from is unverified-empty. Reason: too little text to judge F4 or C1–C4 honestly.

## Wrong versions the tests must catch
1. Substring matching: "ML" inside "HTML" or "data" inside "metadata" counts as a role or skill word.
2. Silence as sponsorship: a posting that never mentions visas is labeled "sponsors visas: supported".
3. Ranking by keyword count: a posting that repeats "data" ten times outranks one with fewer mentions but more supported claims.
4. Missing field defaulted: a posting with no location is treated as US-based.

## Changes after measurement
(Recorded here with dates: every rule added, cut, or rejected after the reject audit.)

### 2026-11-25 — decisions after the reject audit (Nishant U)

Evidence: my 45 audit verdicts (`audit/audit.csv`, commit `b8b0a20`) against the v1 run (`out3/filter-run/`, commit `8e759bf`); measurements in `audit/AUDIT-REPORT.md`. "Fixes" turn a disagreement into agreement; "breaks" turn an agreement into disagreement; "unaudited" counts verdict changes among the 137 postings I did not judge. These counts come from the same 45 verdicts that suggested the changes, so they overstate the improvement; v2 has not been tested on a fresh sample.

| # | Decision | Change | Reason | Fixes | Breaks | Unaudited |
| --- | --- | --- | --- | ---: | ---: | ---: |
| 1 | ACCEPT | Cut "lead" from F2's exclusions | "Lead" often marks a senior individual contributor, not a people manager (row 4). | 1 (row 4) | 0 | 1 |
| 2 | ACCEPT | F4 also counts Priya's résumé practices: A/B testing (also "A/B test", "A/B tests"), experimentation, LLM evaluation, LLM-as-judge | Her skills include practices, not only tool names (rows 8, 27, 35, 44). Row 15 becomes a known miss: the filter can't see managing duties. | 4 | 1 (row 15) | 0 |
| 4 | REJECT | F1 passes when the text says "machine learning"/"ML" at least N times | One case (row 30), and N would be a guess. | (1) | (0) | (0) |
| 5 | REJECT | Add "insights" to F1 and cut "manager" from F2 | Would let real managers through (row 10 stays a miss). | (1) | (0) | (0) |
| 6 | REJECT | F1 passes for a "Strategy" title whose text says "individual contributor" and names SQL | Swaps one error for another (fixes row 28, breaks row 38). | (1) | (1) | (1) |
| 7 | ACCEPT | F3: a location part of the form "US <State> (<City>) - Office" counts as US | A parsing bug: Poshmark writes US offices this way (e.g. "US California (Redwood City) - Office"). | 0 | 0 | not measured |
| 8 | ACCEPT | C4: "hybrid" contradicts "Remote" only in a sentence that also says office, day(s) or schedule | The "hybrid" false friend: "preload vs. tool-calling vs. hybrid" is about AI architecture (row 9). Changes a claim label, not a verdict. | 0 verdicts | 0 | — |

Change 3 in the audit report was changes 1 and 2 together, not a separate decision. Counts in parentheses are for rejected changes, which are not applied.

## Version 2 (2026-11-25)

This file now specifies **version 2**. The v1 text above is kept unchanged for the record; v2 is v1 with accepted changes 1, 2, 7 and 8 applied:

- **F2 Title exclusions (v2):** manager, director, head, intern. ("lead" removed.)
- **F3 US location (v2):** as v1, plus a part of the form "US <State> (<City>) - Office", where <State> is the full name of a US state or the District of Columbia.
- **F4 Skill (v2):** at least 1 of Priya's 10 shipped skills, or one of her résumé practices (A/B testing, A/B test, A/B tests, experimentation, LLM evaluation, LLM-as-judge), appears as a whole word in the posting text (HTML removed). The practice list is hand-set from her résumé bullets. C2 claims still name shipped skills only.
- **C4 Remote (v2):** as v1, except "hybrid" counts as contradicting only when its sentence also contains office, day(s) or schedule.
- **Known miss (accepted):** an individual-contributor-looking title whose text describes managing people (row 15) is accepted when F4 now passes; v2 does not read managing duties.

Everything else (F1, the evidence rules C1–C3, the abstention rule and the four wrong versions) is unchanged from v1.
