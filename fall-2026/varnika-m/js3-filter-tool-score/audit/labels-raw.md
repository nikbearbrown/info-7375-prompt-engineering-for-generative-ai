# My labels, as I typed them (raw)

Pasted to Claude Code in chat on 2026-11-25 and saved here word for word, typos included. The final labels in
`labels.csv` come from these lines and from any later corrections, which are recorded below each batch.

## Batch 1 (items 1–20), first pass

```text
1  N (needs an active clearance, does not show)
2  N (more than 3+ years of expereicme, shouod be less that or eqial to 3
3  N needs an active clearance, does not show)
4  Y/N not iusre as years of exp is not giuven
5  N (the locatuion is not usa)
6  Y 
7  N (experueinet level does not match , too high
8  Y/N not iusre as years of exp is not giuven
9  Y/N not iusre as years of exp is not giuven
10  N needs an active clearance, does not show)
11 Y/N not iusre as years of exp is not giuven
12  Y/N not iusre as years of exp is not giuven
13  N(not software enegienering role)
14  N(not software enegienering role)
15  N (the job titlke is for engineerng manage)
16  N(the job title is vague , does not specify software engineering)
17 N needs an active clearance, does not show)
18  N(N(not software enegienering role)
19 N needs an active clearance, does not show)
20 N(the job title is vague , does not specify software engineering alos exp is too high)
```

### Batch 1, corrections (2026-11-25)

Claude Code pointed out that items 4, 8, 9, 11 and 12 were "Y/N" (each label must be Y or N; under my rule
"no years given" is not a blocker), and that items 1, 10, 17 and 19 gave "needs an active clearance" although
their postings say "or eligibility / willingness to obtain". I asked Claude Code to do the corrections. It
declined to choose for me, then suggested a label for each of the nine **from my written rules** (JS1 labeling
rule and LABELING-DECISIONS.md), naming the rule and the posting's words. I replied **"confirm all"**.

| # | Label | Suggested reason, confirmed by me |
|---|---|---|
| 1 | Y | new grad infrastructure SWE, Seattle, no years; clearance 'or eligibility and willingness to obtain' -> status unknown |
| 4 | N | must-haves (ChromeOS fleet, Google Admin console, Android device management) not on his résume |
| 8 | N | London, UK only; research role |
| 9 | N | Technical Editor is not engineering |
| 10 | Y | strong coder Python/Java/TypeScript, New York, no years; clearance 'or willingness to obtain' -> status unknown |
| 11 | N | product operations manager: not engineering, manager role |
| 12 | N | developer education lead: not engineering of his kind, lead role |
| 17 | N | must-have 1+ years as mentor or tech lead not shown on his résume |
| 19 | N | internship for students; he has graduated |

## Batch 2 (items 1–62, all), pasted to Claude Code in chat on 2026-11-25

How these lines were made: asked by Claude Code, I answered **"I decided each one myself"** ("I read each posting and chose Y/N; I only tidied the wording (with or without help)"). For items 1–20 every label equals the batch-1 label I had confirmed; the reasons were reworded.

```text
1	Y	New-grad infrastructure engineering; clearance eligibility/willingness accepted. Status unknown.
2	N	Business Affairs; requires 5+ years contracting and MBA/JD.
3	N	Deployment Strategist; requires active Secret clearance.
4	N	ChromeOS client platform role; ChromeOS fleet administration is not demonstrated.
5	N	Internship; requires fluent Korean and 2027/2028 graduation.
6	Y	Software engineering; Java experience, infrastructure, monitoring and CI/CD fit.
7	N	Manager role; requires 12+ years and people management.
8	N	ML research role; located in London.
9	N	Technical Editor, not engineering.
10	Y	Forward-deployed software engineering; clearance willingness accepted. Status unknown.
11	N	Product Operations Manager, not engineering.
12	N	Developer Education Lead; Lead title triggers seniority exclusion.
13	N	Enterprise Account Executive; sales role in Singapore.
14	N	Senior Revenue Accountant; accounting role.
15	N	Engineering Manager; manager title and GPU/ML specialization.
16	N	People Partner; HR role.
17	N	Requires 3+ years (Aarav has 29 months) and mentoring/tech-lead experience.
18	N	Partner Marketing Lead; marketing role.
19	N	Internship; intended for current college students.
20	N	Product Manager; senior/staff-level role.
21	N	Finance and Deal Strategy, not engineering.
22	N	Research Engineer/Scientist; ML research role.
23	N	Research engineering; requires 7+ years and ML research experience.
24	N	Cyber Threat Investigator; requires threat intelligence experience.
25	N	Product Manager; requires 8+ years.
26	N	AI Governance and Policy role, not engineering.
27	N	Operations Analyst; requires classified-environment operations experience.
28	N	Enterprise Account Executive; sales role in South Korea.
29	Y	Frontend infrastructure engineering; 2+ years and TypeScript experience.
30	N	Alignment research engineering; ML research requirements.
31	N	Senior/Staff title; requires 5+ years.
32	N	Requires December 2026 or Spring 2027 graduation; Aarav graduated May 2026.
33	N	Operations Lead; outside US and requires extensive experience.
34	N	Head-level sales leadership position.
35	N	Infrastructure internship; requires 2028 graduation.
36	N	Staff+ engineering; requires 15+ years.
37	N	Operations Analyst; not engineering.
38	N	Talent Strategist; recruiting role.
39	N	Requires 6+ years; Aarav has 29 months.
40	N	Research Resident; located in London.
41	N	Staff+ engineering; requires senior-level infrastructure and observability experience.
42	N	Internship; requires 2027/2028 graduation.
43	N	Product Management, Research; requires 5+ years.
44	Y	Developer Productivity engineering; 2+ years and matching Java/TypeScript/Python skills.
45	N	Deployment Strategist; requires active Top Secret clearance.
46	N	Partner Account Manager; located in Tokyo.
47	N	Applied AI engineering; requires 6+ years and French-market technical advisory experience.
48	N	Deployment Strategist; requires active Top Secret clearance.
49	N	Strategic Account Executive; enterprise sales role.
50	N	Staff+ Software Engineer; senior-level distributed systems and low-level infrastructure requirements.
51	N	Staff Software Engineer; senior title and Salesforce platform experience.
52	Y	Backend infrastructure engineering; Java/Python match, no mandatory clearance or experience threshold.
53	Y	New-grad infrastructure engineering; matching languages. Clearance eligibility accepted. Status unknown.
54	Y	New-grad forward-deployed software engineering; matching languages. Clearance eligibility accepted. Status unknown.
55	N	Mixed Reality Developer; Unity/Unreal experience not demonstrated.
56	Y	New-grad software engineering; recently completed master's degree and Java experience.
57	Y	New-grad software engineering; clearance eligibility accepted. Status unknown.
58	Y	New-grad software engineering; clearance eligibility accepted. Status unknown.
59	N	Offensive Security; requires 5+ years of red-teaming experience.
60	N	Data Scientist; requires 7+ years.
61	N	Computational Chemistry Research Scientist; requires a Chemistry PhD.
62	N	ML Research Engineer; requires large-scale distributed training experience.
```
