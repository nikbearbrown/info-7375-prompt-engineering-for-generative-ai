# Filter run 2026-11-21T044414Z

FILTER.md v1.0 applied offline to the newest saved answer of each board (FILTER.md Section 6, item 9). Profile: ~/Documents/03-School/info7375/job-search-agent/persona/jane-doe.json. Every number below is computed from verdicts.json in this folder.

## Sources

| Board | Run folder | Saved answer | SHA-256 | Postings |
|---|---|---|---|---:|
| ashby-openai | `2026-11-20T114036Z` | `runs/2026-11-20T114036Z/boards/ashby-openai/attempt-1.json.gz` | `d595afc07e6388c7...` | 854 |
| greenhouse-verkada | `2026-11-20T114036Z` | `runs/2026-11-20T114036Z/boards/greenhouse-verkada/attempt-1.json.gz` | `cface440ae606b2c...` | 348 |
| lever-palantir | `2026-11-20T114036Z` | `runs/2026-11-20T114036Z/boards/lever-palantir/attempt-1.json.gz` | `95b992f2009e7050...` | 307 |
| greenhouse-no-such-board-js2-test | none | no saved HTTP 200 answer in any run | | |

Byte-identical answers saved by other runs: ashby-openai (also saved by 2026-11-20T113915Z); lever-palantir (also saved by 2026-11-20T113915Z).

## Fates

1509 postings: **99 kept**, 1409 rejected, 1 "I cannot tell".

| Board | Kept | Rejected | I cannot tell |
|---|---:|---:|---:|
| ashby-openai | 86 | 767 | 1 |
| greenhouse-verkada | 6 | 342 | 0 |
| lever-palantir | 7 | 300 | 0 |

## Rejected, by rule

The deciding rule is the first that failed, in the order R1 to R8; every rule ran on every posting.

| Rule | Deciding | Failed at all | The only rule that failed |
|---|---:|---:|---:|
| R1 employment type | 75 | 75 | 0 |
| R2 location | 319 | 335 | 9 |
| R3 job level | 480 | 666 | 11 |
| R4 job role | 441 | 1214 | 207 |
| R5 work authorization and sponsorship | 31 | 361 | 28 |
| R6 start date | 0 | 3 | 0 |
| R7 years of experience | 63 | 623 | 63 |
| R8 AI training and data annotation | 0 | 0 | 0 |

## "I cannot tell"

For a whole posting (never shortlisted):

- ashby-openai `1ae64ddb-505f-4ad2-a731-3a857e94edee`: the posting has no title

For one rule, on kept postings (each costs the penalty in Section 1):

- none

The same flags across every posting, rejected ones included (no score is given to those):

- R2 other_us: 161
- R7: 69

## Scores of the kept postings

| Score | Postings |
|---:|---:|
| 50 | 27 |
| 55 | 22 |
| 60 | 33 |
| 65 | 11 |
| 70 | 6 |

50 kept postings score 60 or more; 2 duplicate copies were removed (same board and normalized title; the newest kept); the shortlist holds the top 10.

## The shortlist (top 10)

1. **Software Engineer, Agent Platform** (ashby-openai), score 70: start +50; 4 topic group(s), 5 each, capped at 25 +20
   - Topics: APIs (APIs), Backend (backend), Distributed systems (distributed systems), Cloud infrastructure (cloud infrastructure)
   - Locations: San Francisco; posted 2026-11-05T19:33:17.025+00:00
   - https://jobs.ashbyhq.com/openai/783704d7-5afa-45aa-899b-1d6799f73004
2. **EDA Cloud & Developer Infrastructure Engineer** (ashby-openai), score 70: start +50; 4 topic group(s), 5 each, capped at 25 +20
   - Topics: APIs (APIs), Developer tools (developer tools), Cloud infrastructure (cloud infrastructure), Databases (PostgreSQL)
   - Locations: San Francisco; posted 2026-11-03T02:37:14.184+00:00
   - https://jobs.ashbyhq.com/openai/4f2d9849-ad00-48d5-a22f-0cb943723999
3. **Software Engineer, Compute Infrastructure** (ashby-openai), score 70: start +50; 4 topic group(s), 5 each, capped at 25 +20
   - Topics: Developer tools (developer tools), Distributed systems (distributed systems), Cloud infrastructure (Kubernetes), APIs (APIs)
   - Locations: San Francisco; New York City; Seattle; London, UK; posted 2026-08-14T23:27:55.134+00:00
   - https://jobs.ashbyhq.com/openai/ca300a6d-a2a7-4580-aad7-323fbdfee7b1
4. **Software Engineer, Core Services** (ashby-openai), score 70: start +50; 4 topic group(s), 5 each, capped at 25 +20
   - Topics: Backend (backend), APIs (APIs), Distributed systems (distributed systems), Developer tools (CI/CD)
   - Locations: San Francisco; posted 2025-07-18T18:04:13.589+00:00
   - https://jobs.ashbyhq.com/openai/21bfde35-ffec-42d2-a2c6-8a03dad789d5
5. **Software Engineer - Environment Platform** (lever-palantir), score 70: start +50; 4 topic group(s), 5 each, capped at 25 +20
   - Topics: APIs (APIs), Cloud infrastructure (Kubernetes), Microservices (microservices), Distributed systems (distributed systems)
   - Locations: Seattle, WA; posted 2024-09-05T13:56:40+00:00
   - https://jobs.lever.co/palantir/cd2423c6-da68-430c-8be5-0ae7eea36497
6. **Full Stack Software Engineer, ChatGPT Finances** (ashby-openai), score 65: start +50; 3 topic group(s), 5 each, capped at 25 +15
   - Topics: Backend (backend), APIs (APIs), Distributed systems (distributed systems)
   - Locations: San Francisco; posted 2026-11-13T20:57:10.105+00:00
   - https://jobs.ashbyhq.com/openai/26cfb873-f30a-4a13-b7b6-52833ea48ec9
7. **Software Engineer, Compute Foundations** (ashby-openai), score 65: start +50; 3 topic group(s), 5 each, capped at 25 +15
   - Topics: APIs (APIs), Cloud infrastructure (Kubernetes), Distributed systems (distributed systems)
   - Locations: San Francisco; posted 2026-09-16T23:39:23.616+00:00
   - https://jobs.ashbyhq.com/openai/40f2f959-20f8-40ca-8b8c-154b6774193a
8. **Software Engineer, Ads Integrity** (ashby-openai), score 65: start +50; 3 topic group(s), 5 each, capped at 25 +15
   - Topics: Backend (backend), Distributed systems (distributed systems), Developer tools (build systems)
   - Locations: San Francisco; posted 2026-09-14T18:34:43.801+00:00
   - https://jobs.ashbyhq.com/openai/596e543a-0ab9-471e-a1ff-40fd55c74fce
9. **Software Engineer, Host Assurance** (ashby-openai), score 65: start +50; 3 topic group(s), 5 each, capped at 25 +15
   - Topics: APIs (APIs), Backend (backend), Distributed systems (distributed systems)
   - Locations: San Francisco; Seattle; US - Remote; posted 2026-09-05T14:19:37.047+00:00
   - https://jobs.ashbyhq.com/openai/0b9e565a-ae5f-40fc-8350-b59f71f76df1
10. **Software Engineer, Codex Cyber** (ashby-openai), score 65: start +50; 3 topic group(s), 5 each, capped at 25 +15
   - Topics: Backend (backend), APIs (APIs), Developer tools (developer tools)
   - Locations: San Francisco; posted 2026-07-07T05:36:29.100+00:00
   - https://jobs.ashbyhq.com/openai/eefeb527-4e36-432e-a787-88e4672e29e1

## How often Section 6's implementation choices fired

Claude Code made these choices for FILTER.md v1.0. Counted here so the audit can test them instead of assuming them.

**R7 company words** (a years sentence above the person's years that names the company counts as "cannot tell", not a requirement):

| Word | Sentences | Postings |
|---|---:|---:|
| grew | 0 | 0 |
| grown | 0 | 0 |
| growth | 56 | 51 |
| founded | 0 | 0 |
| revenue | 9 | 9 |
| customers | 12 | 12 |
| history | 0 | 0 |
- *growth*, ashby-openai "AI Support Engineer - San Francisco" (8 years, rejected): "- Have 8+ years of experience in User Operations, Engineering, Support Engineering or similar technical roles, ideally within high-growth tech startups or other fast-paced environments."
- *growth*, ashby-openai "AI Support Engineer - Dublin" (8 years, rejected): "- Have 8+ years of experience in User Operations, Engineering, Support Engineering or similar technical roles, ideally within high-growth tech startups or other fast-paced environments."
- *growth*, ashby-openai "AI Support Engineer - San Francisco (Weekend Shift)" (8 years, rejected): "- Have 8+ years of experience in User Operations, Engineering, Support Engineering or similar technical roles, ideally within high-growth tech startups or other fast-paced environments."
- *growth*, ashby-openai "Growth - Lifecycle Lead (B2B)" (10 years, rejected): "- 10+ years of experience in lifecycle, CRM, retention, growth, product marketing, or marketing technology, ideally in a global B2B business serving self serve small businesses, enterprises, and developers."
- *growth*, ashby-openai "AI Support Engineer - Singapore (Korean Speaking)" (8 years, rejected): "- Have 8+ years of experience in User Operations, Engineering, Support Engineering or similar technical roles, ideally within high-growth tech startups or other fast-paced environments."
- *revenue*, ashby-openai "APAC Vendor Lead, Ads - Sydney" (5 years, rejected): "- 5+ years of experience in vendor operations, commercial operations, outsourced sales, or a scaled revenue organization"
- *revenue*, ashby-openai "Lead Revenue Accounting, Technical (Strategic Partnerships)" (10 years, rejected): "- 10+ years of technical revenue accounting or related advisory experience, with deep ASC 606 expertise and experience leading complex workstreams or teams."
- *revenue*, ashby-openai "Account Director, Higher Education" (10 years, rejected): "- 10+ years of experience selling platform-as-a-service and/or software-as-a-service solutions, with a sustained record of meeting or exceeding meaningful revenue targets through complex, multi-year enterprise sales motions."
- *revenue*, ashby-openai "North America Vendor Lead, Ads" (5 years, rejected): "- 5+ years of experience in vendor operations, commercial operations, outsourced sales, or a scaled revenue organization"
- *revenue*, ashby-openai " APAC Vendor Lead, Ads - Singapore" (5 years, rejected): "- 5+ years of experience in vendor operations, commercial operations, outsourced sales, or a scaled revenue organization"
- *customers*, ashby-openai "Applied AI Engineer, Cyber, Government" (7 years, rejected): "- Bring 7+ years of hands-on technical experience in cybersecurity, cyber operations, or security-focused software engineering, including work directly with government customers or national security mission teams."
- *customers*, ashby-openai "Applied AI Engineer, Codex" (5 years, rejected): "- Have 5+ years of technical consulting, post-sales engineering, solutions architecture, or similar experience working directly with customers."
- *customers*, ashby-openai "Applied AI Engineer, API Platform, Digital Natives" (8 years, rejected): "- Bring 8+ years of deep, hands-on technical experience and an eagerness to work closely with customers."
- *customers*, ashby-openai "Applied AI Engineer, API Platform, Digital Natives" (8 years, rejected): "- Bring 8+ years of deep, hands-on technical experience and an eagerness to work closely with customers."
- *customers*, ashby-openai "Account Director, Cyber" (14 years, rejected): "- 14+ years selling complex platform-as-a-service and/or software-as-a-service products to large enterprise customers, with substantial experience in cybersecurity."

**The season or quarter start rule:** 0 mentions in start sentences; outcomes none.

**The "Dec." splitter fix:** kept 0 month abbreviations with their year; 0 of those sentences contain "start".

**US remote spellings that are not one of the person's remote phrases** (Section 6, item 5 counts them as another US place, minus 15): 0.

## Counts FILTER.md quoted before the build, and the built counts

FILTER.md's note says its counts came from Claude Code's scratch script on the second draft of the rules; these are the built filter's counts on the answers above.

| What | Quoted before the build | Built |
|---|---|---|
| postings measured | 1,508 (the scratch script left out OpenAI's posting with no title) | 1509 read (1508 with a title; 1 without) |
| postings with no employment type (R1) | 0 ("None of today's 1,508 postings had a missing employment type") | 0 |
| rejected for being outside the US (R2) | 9, with R2 checked after every other hard rule | 9 fail R2 and no other hard rule; 335 fail R2 at all |
| kept postings in another US place or unclear (R2) | 0 ("none of the other 99") | 0 |
| titles matching the annotation phrases (R8) | 0 ("None of today's 1,508 postings matched") | 0 |

## Fingerprints

Run 2026-11-21T044414Z started 2026-11-21T04:44:14+00:00; FILTER.md SHA-256 `f1edbf0b5319d0c42645e892d6ef39f738f964128f3146fb82abea06438ba6f1`; code fingerprint `98f6a378c14815f3e7e9aa77c7b3a90cad5b09d7074e369ea6ba464a960d5ab2`; git HEAD `158e49394faa51cbb901819703aaea0e2a1dbb8b` (the commit checked out when the run started; uncommitted changes, if any, are covered by the code fingerprint).
