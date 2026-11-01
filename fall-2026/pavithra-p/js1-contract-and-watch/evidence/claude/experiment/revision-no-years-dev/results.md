## `revision-no-years.md` on the dev set (2026-10-31T16:36:42Z)

- Pass rate (Claude's verdict = my hand label): **7/10**
- Invalid replies (rejected by the validator, counted as a fail): 0
- For comparison: answering "Not Relevant" every time would score 5/10; the written rule (record) matches my labels on 3/10

| Job ID | Company | Title | Claude (judgment) | My hand label | Pass | Rule (record) | Claude's reason |
|---|---|---|---|---|---|---|---|
| 7697137 | Pinterest | Machine Learning Engineer II, Visual AI | Not Relevant | Not Relevant | yes | Not Relevant | Title 'Machine Learning Engineer II, Visual AI' has no Software/Backend/Full-stack/Cloud/AI-prefixed Engineer title (AI is not adjacent to Engineer). Only 'SQL' matches a skill, so skills fail. Location is US. |
| 8015547 | Pinterest | Security Software Engineer II, Detection and Response | Not Relevant | Not Relevant | yes | Not Relevant | Title (Software Engineer II), location (US) and no seniority words pass, but the description matches only one candidate skill as a whole word (Python); the rule requires at least two. |
| 8213988 | Pinterest | Software Engineer II, Data Analytics & Engineering | Relevant | Not Relevant | no | Relevant | Title has 'Software' and 'Engineer' and no senior-level words. Location lists 'US'. Description names SQL and Python, both in skills.languages, as whole words. |
| 7661919 | Twilio | Software Engineer - Video | Relevant | Relevant | yes | Not Relevant | Title 'Software Engineer - Video' has Engineer+Software and no senior-level words; location 'Remote - US' contains US; description names Java, Kafka and AWS, three of the candidate's skills. |
| 8009057 | Twilio | Software Engineer L3 | Relevant | Relevant | yes | Not Relevant | Title 'Software Engineer L3' has Engineer+Software and no excluded seniority words; location 'Remote - US' contains US; description names Python, Java, Kafka, AWS, Docker and Kubernetes. |
| 8026211 | Twilio | Software Engineer, Platform Access (L2) | Relevant | Not Relevant | no | Relevant | Title 'Software Engineer, Platform Access (L2)' has Engineer+Software and no senior-level words; location 'Remote - US' contains US; description names AWS, Docker and Kubernetes as whole words (3 skills). |
| 5551532004 | Figma | Software Engineer - Machine Learning | Not Relevant | Not Relevant | yes | Not Relevant | Title (Software Engineer) and location (United States) pass and no seniority words appear, but only Python matches the candidate's skills as a whole word. The rule requires at least two. |
| 5551730004 | Figma | Software Engineer - AI Product | Not Relevant | Relevant | no | Not Relevant | Title (Software Engineer - AI Product), no excluded seniority words in the title, and location (United States) pass, but the description names none of the candidate's skills (no Python, Java, SQL, AWS, Docker, etc.), so the 2-skill rule fails. |
| 5552549004 | Figma | Software Engineer - Distributed Systems | Relevant | Relevant | yes | Not Relevant | Title 'Software Engineer' has no excluded level words; location includes 'United States'; description names TypeScript, Python, Redis, Kafka and AWS, which are 5 matching skills (at least 2 needed). |
| 5691886004 | Figma | Software Engineer - AI Platforms | Relevant | Relevant | yes | Not Relevant | Title 'Software Engineer - AI Platforms' has Engineer+Software and no seniority words; description names TypeScript and Python (2 skills); location includes 'United States'. |
