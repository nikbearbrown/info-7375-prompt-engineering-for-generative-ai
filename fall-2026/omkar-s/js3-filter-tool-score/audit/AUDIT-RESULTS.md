# Audit results (generated)

Generated 2026-11-25T22:00:58Z by `python3 -m js3.audit report` from `audit/sample-key.json`, `audit/omkar-verdicts.csv` and `audit/claude-second-rater.jsonl`. Sample drawn 2026-11-17T06:23:44Z, corpus 2026-11-17T06-16-31Z, filter v1.2, seed 7375003.

Population: 1142 postings, 1133 rejects, 9 kept, 6 close calls, 27 gate near-misses. Cards: 49 (R 30, C 6, G 8, K 9; a card can be in more than one part).

**Omkar's hand verdicts: 49 of 49 cards.**

## Part R: 30 random rejects (the only part that supports a rate)

**The filter was wrong on 0 of 30 random rejects** (Omkar said keep). 0 more were 'cannot tell'.

What a sample of 30 can honestly show: the observed miss rate is 0/30 = 0.0%. The exact 95% interval (Clopper-Pearson) is **0.0% to 11.6%**. That is an **estimate** for the 1133 rejects of this one corpus, not a measured rate: if the true rate were at the top of the interval, about 131 of the 1133 rejects would be postings Omkar wants. A sample this size cannot rule that out, and it says nothing about other boards or other weeks.

## Part C: close calls (score within 1.0 of the threshold)

**2 of 6 disagreed with the filter**; 0 'cannot tell'. This part was chosen on purpose, not at random, so it shows *where* the filter errs, not *how often*.

## Part G: gate near-misses (score ≥ threshold, one gate failed)

**0 of 8 should have been kept**; 0 'cannot tell'. This part was chosen on purpose, not at random, so it shows *where* the filter errs, not *how often*.

## Part K: every kept posting

**5 of 9 should have been rejected (false positives)**; 0 'cannot tell'. This part was chosen on purpose, not at random, so it shows *where* the filter errs, not *how often*.

## Filter v1.2 (when drawn) vs v1.6 (now)

2 of 49 cards have a different verdict now: card 2 Senior Infrastructure Engineer (keep → reject); card 49 Senior Software Engineer, Vision AI (keep → reject). Parts R/C/G/K and their numbers above use the verdict at draw time, because that is the filter the sample measured.

## Every card

| Card | Parts | Company · title | Filter v1.2 (score) | Filter v1.6 | Omkar | Omkar's note | Claude 2nd rater |
|---:|---|---|---|---|---|---|---|
| 1 | G | Senior Software Engineer, Release Engineering | reject (5.0) | reject | reject | i have 3 years of experience and it shows 5 years of experience | reject |
| 2 | K | Senior Infrastructure Engineer | keep (7.25) | reject | reject | it needs 5 years [typed by Omkar in chat, entered by Claude Code] | reject |
| 3 | R | Territory Account Executive, Retail - Columbus, GA | reject (0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 4 | R | Staff Software Engineer, Orders | reject (4.0) | reject | reject | it needs 8 years [typed by Omkar in chat, entered by Claude Code] | reject |
| 5 | C,K | Product Engineer | keep (5.5) | keep | reject | it needs react and graphql [typed by Omkar in chat, entered by Claude Code] | reject |
| 6 | R | Bilingual Hybrid Development Representative - Mandarin | reject (0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 7 | R | Data Scientist  - Business Analytics | reject (2.0) | reject | reject | it needs 5 years [typed by Omkar in chat, entered by Claude Code] | reject |
| 8 | R | Revenue Operations Manager - Spotify Technology | reject (0) | reject | reject | it needs 6 years [typed by Omkar in chat, entered by Claude Code] | reject |
| 9 | G | Fullstack Engineer - Backstage | reject (6.0) | reject | reject | it is in london [typed by Omkar in chat, entered by Claude Code] | reject |
| 10 | G | Technical Account Manager 2 - West | reject (5.0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 11 | R | Enterprise Customer Success Manager (German Speaking) | reject (0) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 12 | C | Senior Software Engineer - Growth | reject (4.25) | reject | reject | it is a senior role [typed by Omkar in chat, entered by Claude Code] | reject |
| 13 | R | Field Enablement Manager (EMEA) | reject (0) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 14 | R | Manager, Business Recruiting - Enterprise Sales | reject (1.0) | reject | reject | it needs 6 years [typed by Omkar in chat, entered by Claude Code] | reject |
| 15 | K | Software Engineer II, Test Frameworks & Tooling | keep (11.25) | keep | reject | it needs react and python [typed by Omkar in chat, entered by Claude Code] | keep |
| 16 | R | Bilingual Strategic Cuisines Account Executive (Spanish) - Pomona, CA | reject (0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 17 | G | Staff Software Engineer, Application Infrastructure  | reject (6.25) | reject | reject | it is a staff role [typed by Omkar in chat, entered by Claude Code] | reject |
| 18 | R | Client Partner - Emerging & Scaled (German Speaking) | reject (0) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 19 | R | Senior Account Executive, Mid-Market -France | reject (-2.0) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 20 | R | Director of Sales - Emerging & Scaled (New Business) | reject (0) | reject | reject | it needs 10 years [typed by Omkar in chat, entered by Claude Code] | reject |
| 21 | R | Lead PreSales Solutions Engineer - Benelux and Nordics | reject (-2.0) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 22 | R | Territory Account Executive, Retail - New Haven, CT | reject (0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 23 | R | Senior Software Engineer, Android  | reject (4.0) | reject | reject | it needs 6 years [typed by Omkar in chat, entered by Claude Code] | reject |
| 24 | R | Territory Account Executive , SMB - Lancaster, PA  | reject (1.0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 25 | R | Sr. Staff Engineer, Applied AI (Customer Agent) | reject (-0.5) | reject | reject | it is a staff role [typed by Omkar in chat, entered by Claude Code] | reject |
| 26 | K | Software Engineer II (Mobile Developer - Android/Kotlin) - Remote | keep (8.25) | keep | keep | klaviyo fits with my profile [typed by Omkar in chat, entered by Claude Code] | reject |
| 27 | G | Android Software Engineer | reject (6.0) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 28 | C,K | Software Engineer II, Backend | keep (5.0) | keep | keep | also fits [typed by Omkar in chat, entered by Claude Code] | keep |
| 29 | G | Software Engineer II - SMS International | reject (8.25) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 30 | C,K | Full Stack Engineer - Music | keep (5.0) | keep | keep | spotify works for me [typed by Omkar in chat, entered by Claude Code] | keep |
| 31 | R | Enterprise Sales Executive (FED) | reject (1.0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 32 | R | Senior Employer Brand Specialist | reject (-2.0) | reject | reject | it needs 5 years [typed by Omkar in chat, entered by Claude Code] | reject |
| 33 | K | Software Engineer, Conversational Products & Agent Workflows | keep (9.0) | keep | reject | does not fit for me [typed by Omkar in chat, entered by Claude Code] | keep |
| 34 | G | Sr. Lead Software Engineer | reject (6.0) | reject | reject | it needs 8 years [typed by Omkar in chat, entered by Claude Code] | reject |
| 35 | R | Manager, Commercial Sales | reject (0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 36 | R | Staff Machine Learning Engineer, Home Surfaces | reject (2.5) | reject | reject | it is a staff role [typed by Omkar in chat, entered by Claude Code] | reject |
| 37 | K | Software Engineer II - Flows Experience | keep (8.25) | keep | keep | also works for me [typed by Omkar in chat, entered by Claude Code] | keep |
| 38 | G | Technical Account Manager 3 - Denver | reject (5.0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 39 | R | Senior Incident and Escalations Manager | reject (-1.0) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 40 | R | Territory Account Executive, Retail - West St. Louis, MO | reject (0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 41 | R | Manager II, Premier Support Engineering - EMEA | reject (0) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 42 | R | Territory Account Executive, Retail- Newburgh, IN | reject (0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 43 | R | Senior / Staff Security Engineer | reject (0.5) | reject | reject | it is a staff role [typed by Omkar in chat, entered by Claude Code] | reject |
| 44 | R | Client Partner - Emerging & Scaled (French Speaking) | reject (0) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 45 | C | Senior Software Engineer, Platform Engineering | reject (4.25) | reject | reject | it needs 5 years [typed by Omkar in chat, entered by Claude Code] | reject |
| 46 | R | Customer Success Manager | reject (0) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 47 | R | Bilingual Strategic Cuisines Inside Account Executive (Mandarin)		 | reject (1.0) | reject | reject | it is a sales job [typed by Omkar in chat, entered by Claude Code] | reject |
| 48 | R | Associate of R&D Strategic Finance (FP&A) | reject (0) | reject | reject | it is not in the US [typed by Omkar in chat, entered by Claude Code] | reject |
| 49 | C,K | Senior Software Engineer, Vision AI | keep (5.0) | reject | reject | it needs 5 years [typed by Omkar in chat, entered by Claude Code] | reject |

## Second rater (Claude) — not a hand verdict

49 of 49 cards have a valid Claude verdict (0 invalid). Each is one fresh `claude -p` call with the same rule and the same card, recorded with its time in `audit/claude-second-rater.jsonl`. Claude's verdicts never change the audit's numbers above; they only show where a second reader disagrees.

On the 49 cards with both: Omkar and Claude agree on 46 (94%); Omkar and the filter agree on 44 (90%).
