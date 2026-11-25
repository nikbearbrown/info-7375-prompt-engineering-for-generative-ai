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
