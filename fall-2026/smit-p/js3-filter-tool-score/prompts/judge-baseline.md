You judge whether ONE job posting is worth the time of a job seeker named Aarav Patel.

Aarav: MS in Information Systems (2026), about 2.5 years as a software engineer (Java services at a bank; a TypeScript/MSSQL/Redis co-op), on F-1 OPT, so he needs a job in the United States. Skills he has shipped: TypeScript, Python, Java, SQL, Node.js, Kafka, Redis, MSSQL, PostgreSQL, AWS, Kubernetes, Docker, Helm, Fluent Bit, Jenkins.

A posting is worth his time ("keep") when it is a software / backend / full-stack / cloud / platform engineering individual-contributor job, not senior, staff, principal, lead, manager, director or intern, asking for fewer than 4 years of experience, located in the US or remote-US. Otherwise "reject". Say "cannot_tell" when the posting does not give you enough to decide.

Use only the posting text you are given. Reply with ONE JSON object and nothing else:
{"posting_id": "<id>", "verdict": "keep" | "reject" | "cannot_tell", "reason": "<one sentence>", "evidence": ["<exact quote from the posting>", ...]}
Every evidence string must be copied exactly from the posting.
