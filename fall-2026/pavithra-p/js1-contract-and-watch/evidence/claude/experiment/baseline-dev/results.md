## `baseline.md` on the dev set (2026-10-31T00:27:55Z)

- Pass rate (Claude's verdict = my hand label): **3/10**
- Invalid replies (rejected by the validator, counted as a fail): 0
- For comparison: answering "Not Relevant" every time would score 5/10; the written rule (record) matches my labels on 3/10

| Job ID | Company | Title | Claude (judgment) | My hand label | Pass | Rule (record) | Claude's reason |
|---|---|---|---|---|---|---|---|
| 7697137 | Pinterest | Machine Learning Engineer II, Visual AI | Not Relevant | Not Relevant | yes | Not Relevant | Title 'Machine Learning Engineer II, Visual AI' has no Software/Backend/Full-stack/Cloud/AI qualifier directly with Engineer; only SQL matches a skill in the description, so fewer than two skills match. |
| 8015547 | Pinterest | Security Software Engineer II, Detection and Response | Not Relevant | Not Relevant | yes | Not Relevant | Title has Software Engineer, and location is US with no seniority terms or 3+ years asked. But only one candidate skill, Python, appears in the description (scripting e.g. Python, Go, Ruby), below the required two. |
| 8213988 | Pinterest | Software Engineer II, Data Analytics & Engineering | Relevant | Not Relevant | no | Relevant | Title 'Software Engineer II' has Engineer+Software and no seniority terms; description names SQL and Python (2 skills); minimum 2 years is under 3; location includes 'US'. |
| 7661919 | Twilio | Software Engineer - Video | Not Relevant | Relevant | no | Not Relevant | Title, location (Remote - US) and skills (Java, Kafka, AWS) match, but the description requires "Minimum 2-3+ years" of experience, which reads as 3+ years and fails the experience rule. |
| 8009057 | Twilio | Software Engineer L3 | Not Relevant | Relevant | no | Not Relevant | Title, 'Remote - US' location and skills (Python, Java, Kafka, AWS, Docker, Kubernetes) match, but the description requires '4+ years of professional software engineering experience', which fails the under-3-years rule. |
| 8026211 | Twilio | Software Engineer, Platform Access (L2) | Relevant | Not Relevant | no | Relevant | Title 'Software Engineer' has no excluded level words; description names AWS, Docker and Kubernetes (3 skills); it asks for 1–2+ years; location 'Remote - US' contains US. |
| 5551532004 | Figma | Software Engineer - Machine Learning | Not Relevant | Not Relevant | yes | Not Relevant | Title and location pass, but only Python matches the candidate's skills (one, not two). The description also asks for 5+ years of experience, with 3+ in applied ML/AI, which breaks the experience rule. |
| 5551730004 | Figma | Software Engineer - AI Product | Not Relevant | Relevant | no | Not Relevant | Title and US location pass, but the description names none of the candidate's skills (no Python, Java, SQL, AWS, Docker, etc.), and it requires 5+ years of experience, so skills and experience both fail. |
| 5552549004 | Figma | Software Engineer - Distributed Systems | Not Relevant | Relevant | no | Not Relevant | Title, location (United States) and skills (TypeScript, Python, Redis, Kafka, AWS) pass, but the description asks for "5+ years of Software Engineering experience", which breaks the under-3-years rule. |
| 5691886004 | Figma | Software Engineer - AI Platforms | Not Relevant | Relevant | no | Not Relevant | Title 'Software Engineer - AI Platforms' and location 'United States' pass, but only TypeScript and Python match (2 skills), and the description asks for 5+ years of experience and 3+ years in AI/search, failing the experience rule. |
