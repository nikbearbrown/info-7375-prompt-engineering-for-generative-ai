## `baseline.md` on the held-out set (2026-10-31T16:37:46Z)

- Pass rate (Claude's verdict = my hand label): **4/10**
- Invalid replies (rejected by the validator, counted as a fail): 0
- For comparison: answering "Not Relevant" every time would score 4/10; the written rule (record) matches my labels on 4/10

| Job ID | Company | Title | Claude (judgment) | My hand label | Pass | Rule (record) | Claude's reason |
|---|---|---|---|---|---|---|---|
| 7838591 | Pinterest | University Grad Software Engineer 2027 (USA) | Relevant | Not Relevant | no | Relevant | Title has Software Engineer with no excluded seniority words. Description names Python, Java and TypeScript, which match the candidate. It asks for only 1 year of experience. Location lists US. |
| 8162046 | Pinterest | Machine Learning Engineer II, Responsible AI | Not Relevant | Not Relevant | yes | Not Relevant | Title has Engineer and AI, location is US, and 2+ years is under 3. But only one candidate skill (SQL, in 'SQL/data exploration') appears as a whole word, short of the required two. |
| 8227344 | Pinterest | Software Engineer II, EPD Ads | Not Relevant | Not Relevant | yes | Not Relevant | Title fits (Software Engineer) and the location includes Remote, US. But the description names no candidate skill as a whole word: 'Javascript' is not 'Java', so the two-skill requirement fails. |
| 7816159 | Twilio | Software Engineer L2-Messaging API | Relevant | Relevant | yes | Relevant | Title 'Software Engineer' with no excluded level words; location 'Remote - US'; description names Java, AWS, Docker, Kubernetes (4 skill matches) and asks for no years of experience. |
| 8026207 | Twilio | Software Engineer, Platform Engineering (L2) | Relevant | Not Relevant | no | Relevant | Title has Software and Engineer, no excluded level words. Location 'Remote - US' contains US. Description names Kubernetes, Docker, AWS and Kafka, which match the skills. It asks for 1-2+ years, under 3. |
| 8100236 | Twilio | Software Engineer (L2) | Not Relevant | Relevant | no | Not Relevant | Title 'Software Engineer (L2)' and 'Remote - US' pass, and skills match (Java, Kafka, AWS, Docker, Kubernetes), but the description requires '3+ years of experience', which fails the experience rule. |
| 5551686004 | Figma | Software Engineer - Data Infrastructure | Not Relevant | Relevant | no | Not Relevant | Title 'Software Engineer' and location 'United States' pass, and Python, SQL, Kafka match, but the description asks for '5+ years of backend or infrastructure engineering experience', which fails the under-3-years rule. |
| 5552530004 | Figma | Software Engineer - C++ | Not Relevant | Relevant | no | Not Relevant | Title (Software Engineer), location (United States) and skills (TypeScript, Python) match, but the description asks for "4+ years of professional Software Engineering experience", which breaks the under-3-years rule. |
| 5552560004 | Figma | Software Engineer - Growth & Monetization | Not Relevant | Relevant | no | Not Relevant | Title, location (United States) and skills (TypeScript, Python, PostgreSQL) match, but the description asks for 4+ years of professional experience, which fails the under-3-years rule. |
| 5691911004 | Figma | Software Engineer - Full Stack | Relevant | Relevant | yes | Relevant | Title 'Software Engineer - Full Stack' has no excluded seniority word; the description names TypeScript, Python and PostgreSQL, asks for no years of experience, and the location includes 'United States'. |
