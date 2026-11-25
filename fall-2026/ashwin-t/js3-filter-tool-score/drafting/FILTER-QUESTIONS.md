# Questions for FILTER.md (drafted by Claude Code, 2026-11-24)

> Claude Code drafted these questions. They are not FILTER.md. Ashwin writes FILTER.md (or
> approves a draft and says who drafted it). FILTER.md is committed alone, before any filter code.

## Facts from the data (computed 2026-11-24, not judgments)

The corpus would be the raw responses JS2 saved on 2026-11-09
(`../js2-loop-tools-diff/runs/2026-11-09T20-21-52Z-live/raw/`):

| Board | ATS | Postings |
|---|---|---:|
| klaviyo | Greenhouse | 151 |
| hubspotjobs | Greenhouse | 126 |
| notion | Ashby | 153 |
| supabase | Ashby | 71 |
| palantir | Lever | 304 |
| **Total** | | **805** (no posting had empty content) |

The unchanged JS1 rule (title AND seniority AND location AND ≥2 skills) keeps **4 of 805**.
108 postings pass title + seniority. Most of those fail on **location**: Notion lists only
San Francisco / New York, Supabase says `Remote, Global`, and Palantir lists one city per
posting (New York, Washington D.C., Seattle, London...). Location-only failures include
`Software Engineer, New Grad (Dec 2026)` (Notion, SF) and 11 Palantir `Software Engineer, New Grad`
postings.

The JS1 title phrase "software engineer" also matches every Palantir
`Forward Deployed Software Engineer` (about 30 postings).

## A. Starting point

1. Start from the JS1 rule as **v0** and write **v1** in FILTER.md? (JS1 rule = `jobwatch/rule.py` at `d95f05e`.)

## B. Role words (title)

2. Which title phrases count? JS1 had: software engineer, backend engineer, back-end engineer,
   backend developer, back-end developer. Add or remove any? Candidates seen in the data:
   full stack, platform engineer, site reliability engineer, data engineer, forward deployed.
3. Is "Forward Deployed Software Engineer" a role Supriya wants? (It currently passes as "software engineer".)
4. Seniority: keep the JS1 exclusions (senior, sr, staff, principal, lead, manager, director, architect,
   intern, internship, III/IV/V)? Is "Software Engineer II" in or out for a new grad?
   Should "new grad" / "early career" add points?

## C. Location

5. Is location a **hard gate** (reject) or **part of the score** (fewer points)?
6. Does `Remote, Global` count as remote-US? Does New York (or any other US city) count?
7. What should happen when the location field is missing or just says `Remote`?

## D. Topic words (body text)

8. Use the résumé skills (Python, Java, PostgreSQL, Redis, Docker, Kubernetes, Distributed Systems)
   as topic words? Add others (e.g. backend, API, SQL, AWS)?
9. Threshold: JS1 required 2 distinct skills. Keep, change, or weight some skills more?
10. Which words do you expect to be **false friends** (match for the wrong reason)? Guesses to test, not facts:
    "Python" in a data-science or sales-engineering posting; "Kubernetes" in a support role;
    "distributed systems" in a company boilerplate paragraph; "Java" in "Java/Kotlin" mobile roles.

## E. The score and threshold

11. The audit needs "closest calls near the threshold", so the filter needs a number, not only pass/fail.
    Options:
    - (a) points: title (+T), each distinct topic word (+1), location fit (+L), excluded seniority = reject; keep if ≥ K
    - (b) JS1 gates for title/seniority, then a points score on topics + location
    - (c) your own form
    Every weight and K will be recorded as **hand-set** unless fitted on labels.

## F. Evidence rules (for the shortlist claims)

12. When is a claim **supported**? Suggested test to accept or change: a quoted span appears in the
    posting text (after normalization) and says what the claim says.
13. When is it **contradicted**? Suggested: the posting text states something incompatible
    (claim "Boston-based", location field "London").
14. When is it **insufficient**? Suggested: the text is silent, or only mentions the word without saying the claim
    (relevance ≠ entailment: "Python" appears in a list of *other teams' tools*).
15. When must the agent say **"I cannot tell"**? Candidates: content missing or truncated; location missing or only
    "Remote"; a claim about the candidate (fit, seniority) that the posting cannot settle; Claude's reply invalid.

## G. Expected sources

16. Corpus: (a) the saved 2026-11-09 JS2 raw responses (805, reproducible, already committed), or
    (b) a fresh live run today with the JS2 loop (newer, but adds time)?
17. Which fields does the filter read? (title, location, offices/secondary locations, content.) What is the answer
    when a board fails or a field is missing: "cannot tell", reject, or keep for review?

## H. Wrong versions (at least two the tests must catch)

Candidates to choose from or replace:

- W1 substring matching ("java" matches "javascript"; "sr" matches "sre"). (JS1's wrong version 2.)
- W2 rank by raw skill count with no title gate (a support engineer listing 5 tools outranks a software engineer).
- W3 treat a missing location as remote (keeps a posting the rule cannot place).
- W4 silently reject a posting whose content is missing, instead of "cannot tell".
- W5 read location from the description ("our Boston office") instead of the structured field.
- W6 count one skill twice (e.g. "Python" and "python3" both scoring), inflating the score.
- W7 a shortlist claim marked "supported" because the word appears anywhere, even negated ("no Java required").

## I. Labels

18. Held-out labels: (a) **new** labels you judge blind on a seeded random draw from the 805, never used to tune;
    or (b) reuse the JS1 Klaviyo labels, disclosed as already seen (12 held-out, small).
19. Label meaning: is the question "would Supriya want to see this posting?" (yes / no / can't tell)?
