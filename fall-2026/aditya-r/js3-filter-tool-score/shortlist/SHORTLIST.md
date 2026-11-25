# Shortlist: filter v1.1

15 kept postings. Each claim has a label, a source field and an exact quote. The quotes are verified verbatim by `js3/shortlist.py`, and any mismatch is an error. Labels by **rule** are mechanical, following FILTER.md §2. **DUTY** labels were made by a reader, who is named on each one. 'Aditya' is his blind audit label, where the posting was on his sheet.

## `ashby:notion:85947779-6b87-466a-98bc-30a640448c28`: Software Engineer, Early Career (AI)

- score: `R 2 + S 0 + T 3 + E 3 + Y 0 = 8` → keep · location: 'San Francisco, California'
- Aditya: **yes (Both early-career level and AI engineering match her profile.)**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-adjacent role ('software engineer'). | **supported** | rule | posting.title: “Software Engineer, Early Career (AI)” |
| TOPIC: The posting mentions llm ('llms'). | **supported** | rule | posting.description: “You'll work on cutting-edge AI-powered features, leveraging LLMs, embeddings, and other AI technologies to make Notion more intelligent and capable.” |
| DUTY: The role itself involves llm work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “You'll work on cutting-edge AI-powered features, leveraging LLMs, embeddings, and other AI technologies to make Notion more intelligent and capable.” |
| TOPIC: The posting mentions ml ('ml'). | **supported** | rule | posting.description: “Expertise building and prototyping: You’re excited to build and iterate quickly, and you’ve started exploring AI/ML through coursework, projects, internships, or hackathons.” |
| DUTY: The role itself involves ml work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “Expertise building and prototyping: You’re excited to build and iterate quickly, and you’ve started exploring AI/ML through coursework, projects, internships, or hackathons.” — describes the applicant's past exploration, not the role's work |
| TOPIC: The posting mentions evaluation ('evaluation'). | **supported** | rule | posting.description: “Evaluation & quality (evals): creating evaluation frameworks and automated/ human-in-the-loop testing to measure and improve model and product quality” |
| DUTY: The role itself involves evaluation work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Contribute to evals and iteration loops: build or extend an evaluation set, run experiments, analyze results, and translate learnings into product or system changes.” |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **supported** | rule (FILTER.md §2 C1) | posting.description: “This is NOT a new grad role!” (early-career phrase 'new grad') |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “San Francisco, California” |

## `ashby:notion:e32799d2-8ef8-4803-8189-c72514afa816`: Software Engineer, New Grad (Dec 2026)

- score: `R 2 + S 0 + T 1 + E 3 + Y 0 = 6` → keep · location: 'San Francisco, California'
- Aditya: **not on his sheet**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-adjacent role ('software engineer'). | **supported** | rule | posting.title: “Software Engineer, New Grad (Dec 2026)” |
| TOPIC: The posting mentions python ('python'). | **supported** | rule | posting.description: “Working towards a proficiency of one or more programming languages such as TypeScript, Node.js, or Python.” |
| DUTY: The role itself involves python work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “Working towards a proficiency of one or more programming languages such as TypeScript, Node.js, or Python.” — Python is one example among TypeScript, Node.js, or Python |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule said supported -> Claude Code (reading), 2026-11-25 | posting.title: “Software Engineer, New Grad (Dec 2026)” (early-career phrase 'new grad')<br>posting.description: “To be eligible for this role, you need to graduate in December 2026 and be able to start full time by January/February 2027.” — Priya completed her MS in 2025-12 (persona), so this graduation window excludes her. The rule said 'supported' from the 'New Grad' title. Whether it disqualifies her is Aditya's call (his label: check the window). |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “San Francisco, California” |

## `greenhouse:databricks:6865698002`: Software Engineer - New Grad (2027 Start)

- score: `R 2 + S 0 + T 1 + E 3 + Y 0 = 6` → keep · location: 'Bellevue, Washington; Mountain View, California; San Francisco, California; Vancouver, Canada'
- Aditya: **yes (New-grad SWE merits checking team fit and graduation window.)**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-adjacent role ('software engineer'). | **supported** | rule | posting.title: “Software Engineer - New Grad (2027 Start)” |
| TOPIC: The posting mentions python ('python'). | **supported** | rule | posting.description: “You have implementation skills with a general purpose program language, such as Python, Java, or C++” |
| DUTY: The role itself involves python work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “You have implementation skills with a general purpose program language, such as Python, Java, or C++” — Python is one example in 'Python, Java, or C++' |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule said supported -> Claude Code (reading), 2026-11-25 | posting.title: “Software Engineer - New Grad (2027 Start)” (early-career phrase 'new grad')<br>posting.description: “You will graduate in fall 2026 or spring 2027 with a degree in Computer Science, Engineering, or related subject” — Priya completed her MS in 2025-12 (persona), so this graduation window excludes her. The rule said 'supported' from the 'New Grad' title. Whether it disqualifies her is Aditya's call (his label: check the window). |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “Bellevue, Washington; Mountain View, California; San Francisco, California; Vancouver, Canada” |

## `greenhouse:databricks:6865704002`: Software Engineer - New Grad, Distributed Data Systems (2027 Start)

- score: `R 2 + S 0 + T 1 + E 3 + Y 0 = 6` → keep · location: 'Bellevue, Washington; Mountain View, California'
- Aditya: **yes (New-grad distributed data engineering merits checking the graduation window.)**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-adjacent role ('software engineer'). | **supported** | rule | posting.title: “Software Engineer - New Grad, Distributed Data Systems (2027 Start)” |
| TOPIC: The posting mentions ml ('ml'). | **supported** | rule | posting.description: “Our mission at Databricks is to radically simplify the whole data lifecycle from ingestion to ETL, BI, and all the way up to ML/AI with a unified platform.” |
| DUTY: The role itself involves ml work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “Our mission at Databricks is to radically simplify the whole data lifecycle from ingestion to ETL, BI, and all the way up to ML/AI with a unified platform.” — company mission statement, not the role's duties (relevance without entailment) |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule said supported -> Claude Code (reading), 2026-11-25 | posting.title: “Software Engineer - New Grad, Distributed Data Systems (2027 Start)” (early-career phrase 'new grad')<br>posting.description: “You will graduate in Fall 2026 or Spring 2027 with a degree in Computer Science, Engineering, or related subject” — Priya completed her MS in 2025-12 (persona), so this graduation window excludes her. The rule said 'supported' from the 'New Grad' title. Whether it disqualifies her is Aditya's call (his label: check the window). |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “Bellevue, Washington; Mountain View, California” |

## `greenhouse:databricks:6866549002`: Software Engineer - New Grad (2027 Start) - Amsterdam

- score: `R 2 + S 0 + T 1 + E 3 + Y 0 = 6` → keep · location: 'Amsterdam, Netherlands'
- Aditya: **not on his sheet**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-adjacent role ('software engineer'). | **supported** | rule | posting.title: “Software Engineer - New Grad (2027 Start) - Amsterdam” |
| TOPIC: The posting mentions python ('python'). | **supported** | rule | posting.description: “You have implementation skills with a general purpose program language, such as Python, Java, or C++” |
| DUTY: The role itself involves python work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “You have implementation skills with a general purpose program language, such as Python, Java, or C++” — Python is one example in 'Python, Java, or C++' |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule said supported -> Claude Code (reading), 2026-11-25 | posting.title: “Software Engineer - New Grad (2027 Start) - Amsterdam” (early-career phrase 'new grad')<br>posting.description: “You will graduate between fall 2026 and summer 2027 with a degree in Computer Science, Engineering, or related subject” — Priya completed her MS in 2025-12 (persona), so this graduation window excludes her. The rule said 'supported' from the 'New Grad' title. Whether it disqualifies her is Aditya's call (his label: check the window). |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “Amsterdam, Netherlands” |

## `greenhouse:databricks:6886281002`: Software Engineer - New Grad (2027 Start) - Berlin

- score: `R 2 + S 0 + T 1 + E 3 + Y 0 = 6` → keep · location: 'Berlin, Germany'
- Aditya: **not on his sheet**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-adjacent role ('software engineer'). | **supported** | rule | posting.title: “Software Engineer - New Grad (2027 Start) - Berlin” |
| TOPIC: The posting mentions python ('python'). | **supported** | rule | posting.description: “You have implementation skills with a general purpose program language, such as Python, Java, or C++” |
| DUTY: The role itself involves python work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “You have implementation skills with a general purpose program language, such as Python, Java, or C++” — Python is one example in 'Python, Java, or C++' |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule said supported -> Claude Code (reading), 2026-11-25 | posting.title: “Software Engineer - New Grad (2027 Start) - Berlin” (early-career phrase 'new grad')<br>posting.description: “You will graduate between fall 2026 and summer 2027 with a degree in Computer Science, Engineering, or related subject” — Priya completed her MS in 2025-12 (persona), so this graduation window excludes her. The rule said 'supported' from the 'New Grad' title. Whether it disqualifies her is Aditya's call (his label: check the window). |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “Berlin, Germany” |

## `greenhouse:databricks:8091041002`: Applied AI Engineer

- score: `R 4 + S 0 + T 2 + E 3 + Y 0 = 9` → keep · location: 'Belgrade, Serbia'
- Aditya: **yes (Applied AI matches her co-op. Check level and Belgrade location terms.)**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-core role ('ai engineer'). | **supported** | rule | posting.title: “Applied AI Engineer” |
| TOPIC: The posting mentions agents ('agent'). | **supported** | rule | posting.description: “You will work on Databricks’ Genie Code, an agent and an ML “exoskeleton” that is authoring ML, training and deploying models, monitoring and self-healing production ML, all at the top-expert level.” |
| DUTY: The role itself involves agents work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “You will work on Databricks’ Genie Code, an agent and an ML “exoskeleton” that is authoring ML, training and deploying models, monitoring and self-healing production ML, all at the top-expert level.” |
| TOPIC: The posting mentions ml ('machine learning'). | **supported** | rule | posting.description: “As Applied ML/AI Engineer at Databricks, you will define and create the Agentic Machine Learning revolution.” |
| DUTY: The role itself involves ml work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “You will help world’s largest companies build and deploy massive classical machine learning solutions (such as personalized recommendations, fraud detection, dynamic pricing, forecasting) fully using Databricks’ agents a” |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule said contradicted -> Claude Code (reading), 2026-11-25 | posting.description: “After 30 years of painfully slow progress, expensive knowledge acquisition and tedious processes in classical ML, the agentic era has ushered innovation, scale and visibility for all: from the most junior data scientists” ('30 years' (N >= 2))<br>posting.description: “2-8 years of engineering experience in high-velocity, high-growth companies.” ('2 8 years' (N >= 2))<br>posting.description: “After 30 years of painfully slow progress, expensive knowledge acquisition and tedious processes in classical ML, the agentic era has ushered innovation, scale and visibility for all: from the most junior data scientists” (early-career phrase 'junior')<br>posting.description: “2-8 years of engineering experience in high-velocity, high-growth companies.” — The rule also cites E 'junior', but that sentence describes the product's users ('the most junior data scientists'), not the role. It is a false friend that scores E +3 in v1.1. |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “Belgrade, Serbia” |

## `greenhouse:databricks:8133691002`: Software Engineer - New Grad (2027 Start) - Aarhus

- score: `R 2 + S 0 + T 1 + E 3 + Y 0 = 6` → keep · location: 'Aarhus, Denmark'
- Aditya: **yes (New-grad SWE merits reading for duties, location terms and graduation window.)**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-adjacent role ('software engineer'). | **supported** | rule | posting.title: “Software Engineer - New Grad (2027 Start) - Aarhus” |
| TOPIC: The posting mentions python ('python'). | **supported** | rule | posting.description: “You have implementation skills with a general purpose program language, such as Python, Java, or C++” |
| DUTY: The role itself involves python work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “You have implementation skills with a general purpose program language, such as Python, Java, or C++” — Python is one example in 'Python, Java, or C++' |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule said supported -> Claude Code (reading), 2026-11-25 | posting.title: “Software Engineer - New Grad (2027 Start) - Aarhus” (early-career phrase 'new grad')<br>posting.description: “You will graduate between fall 2026 and summer 2027 with a degree in Computer Science, Engineering, or related subject” — Priya completed her MS in 2025-12 (persona), so this graduation window excludes her. The rule said 'supported' from the 'New Grad' title. Whether it disqualifies her is Aditya's call (his label: check the window). |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “Aarhus, Denmark” |

## `greenhouse:databricks:8546367002`: AI Engineer – Forward Deployed Engineering (AI FDE)

- score: `R 4 + S 0 + T 4 + E 3 + Y 0 = 11` → keep · location: 'United States'
- Aditya: **not on his sheet**
- **I cannot tell** from this posting: whether it is in Boston or remote-US

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-core role ('ai engineer'). | **supported** | rule | posting.title: “AI Engineer – Forward Deployed Engineering (AI FDE)” |
| TOPIC: The posting mentions llm ('llm'). | **supported** | rule | posting.description: “This role is intended for experienced engineers with demonstrated industry experience designing, building, and deploying production GenAI and LLM applications at scale.” |
| DUTY: The role itself involves llm work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Develop cutting-edge GenAI solutions, incorporating the latest techniques from Databricks AI research to solve customer problems” |
| TOPIC: The posting mentions agents ('agent'). | **supported** | rule | posting.description: “Experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc., with tools such as HuggingFace, LangChain, and DSPy” |
| DUTY: The role itself involves agents work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc., with tools such as HuggingFace, LangChain, and DSPy” |
| TOPIC: The posting mentions ml ('machine learning'). | **supported** | rule | posting.description: “Extensive years of hands-on industry data science experience, leveraging common machine learning and data science tools, i.e.” |
| DUTY: The role itself involves ml work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Experience building production-grade machine learning deployments on AWS, Azure, or GCP” |
| TOPIC: The posting mentions evaluation ('evaluation'). | **supported** | rule | posting.description: “Expertise in deploying production-grade GenAI applications, including evaluation and optimizations” |
| DUTY: The role itself involves evaluation work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Expertise in deploying production-grade GenAI applications, including evaluation and optimizations” |
| TOPIC: The posting mentions cloud ('aws'). | **supported** | rule | posting.description: “Experience building production-grade machine learning deployments on AWS, Azure, or GCP” |
| DUTY: The role itself involves cloud work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “Experience building production-grade machine learning deployments on AWS, Azure, or GCP” — AWS is one of 'AWS, Azure, or GCP' |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule said supported -> Claude Code (reading), 2026-11-25 | posting.description: “It is not intended for internship, new graduate, or entry-level applicants.” (early-career phrase 'new graduate')<br>posting.description: “It is not intended for internship, new graduate, or entry-level applicants.” — The rule said 'supported': its early-career phrase 'new graduate' sits inside a NEGATED sentence. A span was found, so the agent did not abstain. This is the abstention rule's limit. |
| LOCATION: The role is in Boston or remote within the US. | **insufficient** | rule (FILTER.md §2) | posting.location: “United States” |

## `greenhouse:databricks:8574655002`: AI Engineer - FDE (Forward Deployed Engineer)

- score: `R 4 + S 0 + T 4 + E 0 + Y -1 = 7` → keep · location: 'Seoul, South Korea'
- Aditya: **not on his sheet**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-core role ('ai engineer'). | **supported** | rule | posting.title: “AI Engineer - FDE (Forward Deployed Engineer)” |
| TOPIC: The posting mentions llm ('genai'). | **supported** | rule | posting.description: “This team is the right fit for you if you love working with customers, teammates, and fueling your curiosity for the latest trends in GenAI, LLMOps, and ML more broadly.” |
| DUTY: The role itself involves llm work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Develop cutting-edge GenAI solutions, incorporating the latest techniques from Databricks AI research to solve customer problems” |
| TOPIC: The posting mentions agents ('agent'). | **supported** | rule | posting.description: “7+ years of experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc., with tools such as HuggingFace, LangChain, and DSPy” |
| DUTY: The role itself involves agents work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “7+ years of experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc., with tools such as HuggingFace, LangChain, and DSPy” |
| TOPIC: The posting mentions ml ('machine learning'). | **supported** | rule | posting.description: “Extensive years of hands-on industry data science experience, leveraging common machine learning and data science tools, i.e.” |
| DUTY: The role itself involves ml work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Experience building production-grade machine learning deployments on AWS, Azure, or GCP” |
| TOPIC: The posting mentions evaluation ('evaluation'). | **supported** | rule | posting.description: “Expertise in deploying production-grade GenAI applications, including evaluation and optimizations” |
| DUTY: The role itself involves evaluation work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Expertise in deploying production-grade GenAI applications, including evaluation and optimizations” |
| TOPIC: The posting mentions cloud ('aws'). | **supported** | rule | posting.description: “Experience building production-grade machine learning deployments on AWS, Azure, or GCP” |
| DUTY: The role itself involves cloud work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “Experience building production-grade machine learning deployments on AWS, Azure, or GCP” — AWS is one of 'AWS, Azure, or GCP' |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule (FILTER.md §2 C1) | posting.description: “7+ years of experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc., with tools such as HuggingFace, LangChain, and DSPy” ('7 years' (N >= 2)) |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “Seoul, South Korea” |

## `greenhouse:databricks:8760167002`: AI Engineer – Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus)

- score: `R 4 + S 0 + T 4 + E 0 + Y 0 = 8` → keep · location: 'Maryland; Virginia; Washington, D.C.'
- Aditya: **yes (AI FDE aligns with her co-op. Read the federal role's eligibility terms.)**
- **I cannot tell** from this posting: whether it is open to her level

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-core role ('ai engineer'). | **supported** | rule | posting.title: “AI Engineer – Forward Deployed Engineering (AI FDE), U.S.” |
| TOPIC: The posting mentions llm ('genai'). | **supported** | rule | posting.description: “This team is the right fit for you if you love working with customers, teammates, and fueling your curiosity for the latest trends in GenAI, LLMOps, and ML more broadly.” |
| DUTY: The role itself involves llm work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Develop cutting-edge GenAI solutions, incorporating the latest techniques from Databricks AI research to solve customer problems” |
| TOPIC: The posting mentions agents ('agent'). | **supported** | rule | posting.description: “Experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc., with tools such as HuggingFace, LangChain, and DSPy” |
| DUTY: The role itself involves agents work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc., with tools such as HuggingFace, LangChain, and DSPy” |
| TOPIC: The posting mentions ml ('machine learning'). | **supported** | rule | posting.description: “Extensive years of hands-on industry data science experience, leveraging common machine learning and data science tools, i.e.” |
| DUTY: The role itself involves ml work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Experience building production-grade machine learning deployments on AWS, Azure, or GCP” |
| TOPIC: The posting mentions evaluation ('evaluation'). | **supported** | rule | posting.description: “Expertise in deploying production-grade GenAI applications, including evaluation and optimizations” |
| DUTY: The role itself involves evaluation work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Expertise in deploying production-grade GenAI applications, including evaluation and optimizations” |
| TOPIC: The posting mentions cloud ('aws'). | **supported** | rule | posting.description: “Experience building production-grade machine learning deployments on AWS, Azure, or GCP” |
| DUTY: The role itself involves cloud work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “Experience building production-grade machine learning deployments on AWS, Azure, or GCP” — AWS is one of 'AWS, Azure, or GCP' |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **insufficient** | rule (FILTER.md §2 C1) | no span found |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “Maryland; Virginia; Washington, D.C.” |

## `greenhouse:databricks:8847747002`: Software Engineer - New Grad (2027 Start) - London

- score: `R 2 + S 0 + T 1 + E 3 + Y 0 = 6` → keep · location: 'London, United Kingdom'
- Aditya: **not on his sheet**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-adjacent role ('software engineer'). | **supported** | rule | posting.title: “Software Engineer - New Grad (2027 Start) - London” |
| TOPIC: The posting mentions python ('python'). | **supported** | rule | posting.description: “You have implementation skills with a general purpose program language, such as Python, Java, or C++” |
| DUTY: The role itself involves python work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “You have implementation skills with a general purpose program language, such as Python, Java, or C++” — Python is one example in 'Python, Java, or C++' |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule said supported -> Claude Code (reading), 2026-11-25 | posting.title: “Software Engineer - New Grad (2027 Start) - London” (early-career phrase 'new grad')<br>posting.description: “You will graduate between autumn 2026 and summer 2027 with a degree in Computer Science, Engineering, or related subject” — Priya completed her MS in 2025-12 (persona), so this graduation window excludes her. The rule said 'supported' from the 'New Grad' title. Whether it disqualifies her is Aditya's call (his label: check the window). |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “London, United Kingdom” |

## `greenhouse:databricks:8878946002`: Evergreen - AI Engineer, AI FDE

- score: `R 4 + S 0 + T 4 + E 0 + Y -1 = 7` → keep · location: 'Bengaluru, India'
- Aditya: **yes (AI FDE matches her co-op closely enough to check level and location terms.)**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-core role ('ai engineer'). | **supported** | rule | posting.title: “Evergreen - AI Engineer, AI FDE” |
| TOPIC: The posting mentions llm ('llm'). | **supported** | rule | posting.description: “The Machine Learning (ML) Practice team is a highly specialized customer-facing ML team at Databricks facing an increasing demand for Large Language Model (LLM)-based solutions.” |
| DUTY: The role itself involves llm work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Develop LLM solutions on customer data such as RAG architectures on enterprise knowledge repos, querying structured data with natural language, and content generation” |
| TOPIC: The posting mentions agents ('agents'). | **supported** | rule | posting.description: “Experience building Generative AI applications, including RAG, agents, text2sql, fine-tuning, and deploying LLMs, with tools such as HuggingFace, Langchain, and OpenAI” |
| DUTY: The role itself involves agents work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Experience building Generative AI applications, including RAG, agents, text2sql, fine-tuning, and deploying LLMs, with tools such as HuggingFace, Langchain, and OpenAI” |
| TOPIC: The posting mentions ml ('machine learning'). | **supported** | rule | posting.description: “The Machine Learning (ML) Practice team is a highly specialized customer-facing ML team at Databricks facing an increasing demand for Large Language Model (LLM)-based solutions.” |
| DUTY: The role itself involves ml work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “We deliver professional services engagements to help our customers build, scale, and optimize ML pipelines, as well as put those pipelines into production.” |
| TOPIC: The posting mentions cloud ('aws'). | **supported** | rule | posting.description: “Experience building production-grade machine learning deployments on AWS, Azure, or GCP” |
| DUTY: The role itself involves cloud work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “Experience building production-grade machine learning deployments on AWS, Azure, or GCP” — AWS is one of 'AWS, Azure, or GCP' |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule (FILTER.md §2 C1) | posting.description: “5+ years of hands-on industry data science experience, leveraging typical machine learning and data science tools including pandas, scikit-learn, and TensorFlow/PyTorch” ('5 years' (N >= 2)) |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “Bengaluru, India” |

## `greenhouse:figma:5551532004`: Software Engineer - Machine Learning

- score: `R 2 + S 0 + T 4 + E 0 + Y 0 = 6` → keep · location: 'San Francisco, CA • New York, NY • United States'
- Aditya: **yes (ML software engineering warrants a read given her AI co-op.)**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-adjacent role ('software engineer'). | **supported** | rule | posting.title: “Software Engineer - Machine Learning” |
| TOPIC: The posting mentions python ('python'). | **supported** | rule | posting.description: “Proficiency in Python and familiarity with ML libraries like PyTorch, TensorFlow, Scikit-learn, Spark MLlib, or XGBoost.” |
| DUTY: The role itself involves python work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Proficiency in Python and familiarity with ML libraries like PyTorch, TensorFlow, Scikit-learn, Spark MLlib, or XGBoost.” |
| TOPIC: The posting mentions llm ('generative ai'). | **supported** | rule | posting.description: “Design, build, and productionize ML models for Search, Discovery, Ranking, Retrieval-Augmented Generation (RAG), and generative AI features.” |
| DUTY: The role itself involves llm work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Design, build, and productionize ML models for Search, Discovery, Ranking, Retrieval-Augmented Generation (RAG), and generative AI features.” |
| TOPIC: The posting mentions ml ('machine learning'). | **supported** | rule | posting.title: “Software Engineer - Machine Learning” |
| DUTY: The role itself involves ml work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Design, build, and productionize ML models for Search, Discovery, Ranking, Retrieval-Augmented Generation (RAG), and generative AI features.” |
| TOPIC: The posting mentions evaluation ('evaluation'). | **supported** | rule | posting.description: “Build and maintain scalable data pipelines to collect high-quality training and evaluation datasets, including annotation systems and human-in-the-loop workflows.” |
| DUTY: The role itself involves evaluation work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Build and maintain scalable data pipelines to collect high-quality training and evaluation datasets, including annotation systems and human-in-the-loop workflows.” |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule (FILTER.md §2 C1) | posting.description: “5+ years of industry experience in software engineering, with 3+ years focused on applied machine learning or AI.” ('5 years' (N >= 2))<br>posting.description: “5+ years of industry experience in software engineering, with 3+ years focused on applied machine learning or AI.” ('3 years' (N >= 2)) |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “San Francisco, CA • New York, NY • United States” |

## `greenhouse:figma:6233043004`: AI Engineer, Internal Tools

- score: `R 4 + S 0 + T 4 + E 0 + Y -1 = 7` → keep · location: 'San Francisco, CA • New York, NY • United States'
- Aditya: **yes (Building internal AI tools aligns directly with her agent experience.)**

| claim | label | by | field: quote |
|---|---|---|---|
| ROLE: The title names a R-core role ('ai engineer'). | **supported** | rule | posting.title: “AI Engineer, Internal Tools” |
| TOPIC: The posting mentions llm ('llms'). | **supported** | rule | posting.description: “Design, build, and productionize AI agents, assistants, and workflow automations that solve real business problems using LLMs, tool calling, RAG, structured outputs, agent frameworks, MCP, APIs, and enterprise data” |
| DUTY: The role itself involves llm work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Design, build, and productionize AI agents, assistants, and workflow automations that solve real business problems using LLMs, tool calling, RAG, structured outputs, agent frameworks, MCP, APIs, and enterprise data” |
| TOPIC: The posting mentions agents ('agent'). | **supported** | rule | posting.description: “Design, build, and productionize AI agents, assistants, and workflow automations that solve real business problems using LLMs, tool calling, RAG, structured outputs, agent frameworks, MCP, APIs, and enterprise data” |
| DUTY: The role itself involves agents work. | **supported** | Claude Code (reading), 2026-11-25 | posting.description: “Design, build, and productionize AI agents, assistants, and workflow automations that solve real business problems using LLMs, tool calling, RAG, structured outputs, agent frameworks, MCP, APIs, and enterprise data” |
| TOPIC: The posting mentions evaluation ('evaluation'). | **supported** | rule | posting.description: “Hands-on experience building applications with LLMs, agents, retrieval-augmented generation, function calling, schema-constrained outputs, or evaluation frameworks” |
| DUTY: The role itself involves evaluation work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “Hands-on experience building applications with LLMs, agents, retrieval-augmented generation, function calling, schema-constrained outputs, or evaluation frameworks” — evaluation frameworks is one option in an 'or' list |
| TOPIC: The posting mentions cloud ('aws'). | **supported** | rule | posting.description: “Knowledge of AWS Bedrock, AgentCore, OpenAI, Anthropic, or similar AI platforms” |
| DUTY: The role itself involves cloud work. | **insufficient** | Claude Code (reading), 2026-11-25 | posting.description: “Knowledge of AWS Bedrock, AgentCore, OpenAI, Anthropic, or similar AI platforms” — AWS Bedrock is one of several platforms in an 'or' list |
| LEVEL: The role is open to someone with Priya's experience (under 1 year full-time). | **contradicted** | rule (FILTER.md §2 C1) | posting.description: “5+ years of software engineering experience building production applications, integrations, backend systems, or AI-powered products” ('5 years' (N >= 2)) |
| LOCATION: The role is in Boston or remote within the US. | **contradicted** | rule (FILTER.md §2) | posting.location: “San Francisco, CA • New York, NY • United States” |
