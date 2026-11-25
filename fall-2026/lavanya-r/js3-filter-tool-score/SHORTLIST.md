# SHORTLIST.md — the source-grounded shortlist (Chapter 7)

**The shortlist** is the 10 highest-scoring postings kept by FILTER.md v1.1, out of 115 kept; ties are broken by key.

**How each posting was labelled** (2026-11-24):
1. **Claims.** `agent/shortlist.py` turns the filter's justification into claims. There is one claim per thing the filter matched: role word, each topic word, each résumé skill, and the US location. Two more claims cover what the filter only implies: experience and sponsorship. That makes **113 claims** in total.
2. **Labels.** Claude labelled every claim, with one `claude -p` call per posting (model reported as `claude-sonnet-5-5`, tools disabled, run from a folder outside this repo). Each label is supported, contradicted or insufficient, with an exact quote. The prompt is in `agent/shortlist.py` (`PROMPT`), and every raw reply is saved in `out/shortlist/`.
3. **Mechanical check.** `agent/evidence.py` re-checked every label (FILTER.md §2). A "supported" or "contradicted" label stands only if its quote is found character for character in the posting. Otherwise it becomes "insufficient". 11 tests cover this, including wrong version W5.

**Results: 72 supported · 3 contradicted · 38 insufficient**, out of 113.

| Claim type | supported | contradicted | insufficient |
|---|---|---|---|
| role word in the title | 10 | 0 | 0 |
| topic word in the text | 28 | 0 | 13 |
| résumé skill in the text | 19 | 0 | 13 |
| US location | 10 | 0 | 0 |
| open to < 1 year of experience | 5 | 3 | 2 |
| will sponsor a US visa | 0 | 0 | **10** |

**The checker's first pass had a bug.** On its first run, the checker overrode 8 of Claude's "supported" labels as "quote not found". The quotes were correct: they began with `Title:` or `Location:`, exactly as my labelling prompt shows the posting, but the checker's copy of the posting didn't have those prefixes. I fixed the checker to compare against the posting exactly as the prompt shows it, and added a test (`test_quote_may_include_the_prompts_field_labels`). The output before the fix is in `logs/js3-06-shortlist-check-before-fix.md`. After the fix, every one of Claude's quotes was found in its posting. **That does not mean every quote *says* its claim.** Only the quote's presence is checked mechanically. Whether the quote makes the claim is Claude's judgement, and I checked a sample of those by hand (section 4).

## 1. Relevance is not entailment

The filter **matched these words**, so the postings are relevant to them. But the posting text does **not support** the claim that the word stands for.

**(a) The Databricks company footer.** Every one of the 890 Databricks postings ends with the same "About Databricks" paragraph. It contains "…build and scale data and AI apps, analytics and **agents**…", "…and **Unity Catalog**", and the word **Databricks** itself.
- So the filter gave every Databricks posting points for the topic word "agents" and the skills "Databricks" and "Unity Catalog", whatever the job is.
- In shortlist #1 (Data Science Intern (2027 Start)), Claude labelled "The role uses Unity Catalog" and "The day-to-day work involves agents" **insufficient**. The words appear only in that footer.
- When the footer is removed, **5 postings drop from keep to reject**, and one becomes "cannot tell" because too little text is left. This is the strongest **false friend** I found. It was found here, after the audit, so it is not fixed in FILTER.md v1.1. It is recorded as deferred change X5 in FILTER.md's Changes table and AUDIT.md §3–4 (`python3 -B audit/measure.py --footer`).

**(b) A top-scored posting that excludes Priya.** Shortlist #2, AI Engineer – Forward Deployed Engineering (AI FDE), scores 9 of 9. Its title has "AI", its text has LLM/ML words, and Priya's skills are there. But the posting says: *"It is not intended for internship, new graduate, or entry-level applicants."* The claim "open to someone with less than one year of full-time experience" is **contradicted**. Every word matched, and the posting still rules her out.

**(c) "Inference" in a statistics sense.** In #1 the topic word "inference" matched "causal **inference** modeling", and in #6 it matched "Bayesian **inference**". These are statistics, not the model-inference work S2 was meant to find. Claude labelled both claims insufficient.

## 2. The abstention rule

FILTER.md §2 says the agent answers "**I cannot tell**":
- **E1:** the text is under 200 characters;
- **E2:** the posting is silent on the question;
- **E3:** the posting's own quotes conflict;
- **E4:** the only support is from outside the posting. The quote check enforces E4.

**What it did here:**
- **Sponsorship:** "I cannot tell" for **all 10**. No shortlisted posting says whether it sponsors visas, so the agent never claims that one does.
- **Experience:** "no" for 3 (#2, #3, #7, each with a contradicting quote), "I cannot tell" for 2 (#1, #4), and "yes" for 5.

## 3. A counterexample that exposes the rule's limits

The 5 "yes" answers on experience are all **internships**: #5, #6, #8, #9 and #10.
- Each is "supported" by a real quote, such as #8's *"Pursuing a bachelor's or master's in computer science or a related engineering field graduating in Fall 2027 or Spring 2028"*. That quote does show the job is open to someone with under a year of experience.
- **But Priya graduated in December 2025, so she is not eligible for any of them.**
- The abstention rule only asks whether the posting **speaks to the claim**. It cannot notice that the claim was the wrong question. Here the claim was about years of experience, when the real gate is current enrolment.
- So the agent answered a confident, quote-backed "yes" where the right answer for Priya is "no". The rule abstains when evidence is missing, not when the question is wrong.

**My own verdict on #5 shows the same gap.** #5 is sheet item 47 in the audit, which I marked **y**. I recorded that verdict as given and did not change it after seeing this.

## 4. My hand check of Claude's labels

On 2026-11-24 I checked 3 of Claude's 113 labels by hand. Claude chose which 3 to show me, to cover each label type.

| Posting | Claim | Claude's label | My answer |
|---|---|---|---|
| #3 Specialist Solutions Architect – AI/ML | The role uses MLflow. | supported ("…guardrails, using MLflow") | **agree** |
| #2 AI Engineer – Forward Deployed Engineering (AI FDE) | Open to someone with less than one year of experience. | contradicted ("It is not intended for internship, new graduate, or entry-level applicants.") | **agree**. My first answer was "disagree". I changed it after Claude restated what each label means. Both answers are recorded here. |
| #1 Data Science Intern (2027 Start) | The role uses Unity Catalog. | insufficient (the words are only in the company footer) | **disagree**: a Databricks job will use Unity Catalog, so I'd call it supported |

**On the disagreement:** Claude's label follows my own evidence rule. FILTER.md §2 says a quote must say the claim, and E4 says no support from outside the posting. My answer rests on what I expect of a Databricks job, not on the posting's text. So my judgement and my written rule disagree here. I haven't resolved it. I also didn't check the other 110 labels by hand.

## 5. Every claim and its label

Generated by `python3 -B -m agent.shortlist --table`.

### 1. Data Science Intern (2027 Start) (databricks), score 9

Labelled by Claude (sonnet, `claude -p`) at 2026-11-25T04:38:24+00:00; re-checked by `agent/evidence.py`. Agent's answer: experience **I cannot tell**, sponsorship **I cannot tell**.

| # | Claim | Claude's label | Quote | Final label | Check |
|---|---|---|---|---|---|
| 1 | The job is a Intern role. | supported | Title: Data Science Intern (2027 Start) | **supported** | quote found in the posting |
| 2 | The day-to-day work involves machine learning. | supported | Experience with multiple statistical data analysis and machine learning methods such as generalized linear regression, regression and classification trees, unsupervised learning methods, causal inference, stochastic processes, time series forecasting | **supported** | quote found in the posting |
| 3 | The day-to-day work involves inference. | insufficient |  | **insufficient** | labelled insufficient |
| 4 | The day-to-day work involves agents. | insufficient |  | **insufficient** | labelled insufficient |
| 5 | The role uses Python, which Priya has shipped with. | supported | Proven ability to work with data in SQL and Python | **supported** | quote found in the posting |
| 6 | The role uses SQL, which Priya has shipped with. | supported | Proven ability to work with data in SQL and Python | **supported** | quote found in the posting |
| 7 | The role uses Databricks, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 8 | The role uses Unity Catalog, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 9 | The job can be done in the US (Mountain View, California). | supported | We are hiring for the Mountain View & San Francisco offices. | **supported** | quote found in the posting |
| 10 | The job is open to someone with less than one year of full-time experience. | insufficient |  | **insufficient** | labelled insufficient |
| 11 | The employer will sponsor a US work visa. | insufficient |  | **insufficient** | labelled insufficient |

### 2. AI Engineer – Forward Deployed Engineering (AI FDE) (databricks), score 9

Labelled by Claude (sonnet, `claude -p`) at 2026-11-25T04:38:31+00:00; re-checked by `agent/evidence.py`. Agent's answer: experience **no**, sponsorship **I cannot tell**.

| # | Claim | Claude's label | Quote | Final label | Check |
|---|---|---|---|---|---|
| 1 | The job is a AI role. | supported | AI Engineer – Forward Deployed Engineering (AI FDE) | **supported** | quote found in the posting |
| 2 | The day-to-day work involves LLM. | supported | designing, building, and deploying production GenAI and LLM applications at scale | **supported** | quote found in the posting |
| 3 | The day-to-day work involves machine learning. | supported | leveraging common machine learning and data science tools, i.e. pandas, scikit-learn, PyTorch, etc. | **supported** | quote found in the posting |
| 4 | The day-to-day work involves evaluation. | supported | Expertise in deploying production-grade GenAI applications, including evaluation and optimizations | **supported** | quote found in the posting |
| 5 | The day-to-day work involves fine-tuning. | supported | Experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc. | **supported** | quote found in the posting |
| 6 | The day-to-day work involves RAG. | supported | Experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc. | **supported** | quote found in the posting |
| 7 | The day-to-day work involves agents. | supported | Experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc. | **supported** | quote found in the posting |
| 8 | The role uses Databricks, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 9 | The role uses Unity Catalog, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 10 | The role uses AWS, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 11 | The job can be done in the US (United States). | supported | Location: United States; Remote - California | **supported** | quote found in the posting |
| 12 | The job is open to someone with less than one year of full-time experience. | contradicted | It is not intended for internship, new graduate, or entry-level applicants. | **contradicted** | quote found in the posting |
| 13 | The employer will sponsor a US work visa. | insufficient |  | **insufficient** | labelled insufficient |

### 3. Specialist Solutions Architect - AI/ML (Healthcare & Life Sciences) (databricks), score 9

Labelled by Claude (sonnet, `claude -p`) at 2026-11-25T04:38:38+00:00; re-checked by `agent/evidence.py`. Agent's answer: experience **no**, sponsorship **I cannot tell**.

| # | Claim | Claude's label | Quote | Final label | Check |
|---|---|---|---|---|---|
| 1 | The job is a AI / ML role. | supported | Specialist Solutions Architect - AI/ML (Healthcare & Life Sciences) | **supported** | quote found in the posting |
| 2 | The day-to-day work involves LLM. | supported | including LLMs, RAG, agent frameworks, tool calling and MCP, prompt and context engineering, fine-tuning, evaluation and guardrails | **supported** | quote found in the posting |
| 3 | The day-to-day work involves machine learning. | supported | Bring machine learning in where it fits, such as risk, fraud and forecasting models that work alongside generative AI and agents | **supported** | quote found in the posting |
| 4 | The day-to-day work involves evaluation. | supported | Set up evaluation, tracing and monitoring for AI quality, cost and latency, including LLM judges, human feedback and guardrails, using MLflow | **supported** | quote found in the posting |
| 5 | The day-to-day work involves MLOps. | insufficient |  | **insufficient** | labelled insufficient |
| 6 | The day-to-day work involves fine-tuning. | insufficient |  | **insufficient** | labelled insufficient |
| 7 | The day-to-day work involves RAG. | supported | architecting generative AI applications and agents with retrieval-augmented generation (RAG), fine-tuned or open foundation models, and the data platforms behind them | **supported** | quote found in the posting |
| 8 | The day-to-day work involves agents. | supported | Build agents for Payer and Provider workflows such as medical coding, utilization review and member and patient service | **supported** | quote found in the posting |
| 9 | The role uses Python, which Priya has shipped with. | supported | Production programming experience in SQL and Python, Scala or Java | **supported** | quote found in the posting |
| 10 | The role uses SQL, which Priya has shipped with. | supported | Production programming experience in SQL and Python, Scala or Java | **supported** | quote found in the posting |
| 11 | The role uses Databricks, which Priya has shipped with. | supported | turn that data into AI on Databricks that is accurate, governed and ready for production. | **supported** | quote found in the posting |
| 12 | The role uses Unity Catalog, which Priya has shipped with. | supported | meet HIPAA and PHI requirements through governance with Unity Catalog | **supported** | quote found in the posting |
| 13 | The role uses MLflow, which Priya has shipped with. | supported | Set up evaluation, tracing and monitoring for AI quality, cost and latency, including LLM judges, human feedback and guardrails, using MLflow | **supported** | quote found in the posting |
| 14 | The job can be done in the US (United States). | supported | Location: United States; Boston, Massachusetts | **supported** | quote found in the posting |
| 15 | The job is open to someone with less than one year of full-time experience. | contradicted | 5+ years of hands-on experience in a technical role, with recent hands-on work building generative AI applications or agents | **contradicted** | quote found in the posting |
| 16 | The employer will sponsor a US work visa. | insufficient |  | **insufficient** | labelled insufficient |

### 4. AI Engineer – Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus) (databricks), score 9

Labelled by Claude (sonnet, `claude -p`) at 2026-11-25T04:38:47+00:00; re-checked by `agent/evidence.py`. Agent's answer: experience **I cannot tell**, sponsorship **I cannot tell**.

| # | Claim | Claude's label | Quote | Final label | Check |
|---|---|---|---|---|---|
| 1 | The job is a AI role. | supported | The AI Forward Deployed Engineering (AI FDE) team is a highly specialized customer-facing AI team at Databricks. | **supported** | quote found in the posting |
| 2 | The day-to-day work involves machine learning. | supported | leveraging common machine learning and data science tools, i.e. pandas, scikit-learn, PyTorch, etc. | **supported** | quote found in the posting |
| 3 | The day-to-day work involves evaluation. | supported | Expertise in deploying production-grade GenAI applications, including evaluation and optimizations | **supported** | quote found in the posting |
| 4 | The day-to-day work involves fine-tuning. | supported | Experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc., with tools such as HuggingFace, LangChain, and DSPy | **supported** | quote found in the posting |
| 5 | The day-to-day work involves RAG. | supported | Experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc., with tools such as HuggingFace, LangChain, and DSPy | **supported** | quote found in the posting |
| 6 | The day-to-day work involves agents. | supported | Experience building GenAI applications, including RAG, multi-agent systems, Text2SQL, fine-tuning, etc., with tools such as HuggingFace, LangChain, and DSPy | **supported** | quote found in the posting |
| 7 | The role uses Databricks, which Priya has shipped with. | supported | [Preferred] Experience using the Databricks Intelligence Platform and Apache Spark™ to process large-scale distributed datasets | **supported** | quote found in the posting |
| 8 | The role uses Unity Catalog, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 9 | The role uses AWS, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 10 | The job can be done in the US (Maryland). | supported | Location: Maryland; Virginia; Washington, D.C.; Remote - Washington D.C. | **supported** | quote found in the posting |
| 11 | The job is open to someone with less than one year of full-time experience. | insufficient |  | **insufficient** | labelled insufficient |
| 12 | The employer will sponsor a US work visa. | insufficient |  | **insufficient** | labelled insufficient |

### 5. AI Engineering Intern, Operational Safety [Summer 2027] (zoox), score 9

Labelled by Claude (sonnet, `claude -p`) at 2026-11-25T04:38:52+00:00; re-checked by `agent/evidence.py`. Agent's answer: experience **yes**, sponsorship **I cannot tell**.

| # | Claim | Claude's label | Quote | Final label | Check |
|---|---|---|---|---|---|
| 1 | The job is a AI / Intern role. | supported | AI Engineering Intern, Operational Safety [Summer 2027] | **supported** | quote found in the posting |
| 2 | The day-to-day work involves LLM. | supported | Experience building with LLMs or machine learning models (prompting, evaluation, classification), through coursework, projects, or prior work | **supported** | quote found in the posting |
| 3 | The day-to-day work involves machine learning. | supported | Experience building with LLMs or machine learning models (prompting, evaluation, classification), through coursework, projects, or prior work | **supported** | quote found in the posting |
| 4 | The day-to-day work involves evaluation. | supported | Evaluate your workflows against real safety data, measure accuracy, and refine them based on what you find. | **supported** | quote found in the posting |
| 5 | The role uses Python, which Priya has shipped with. | supported | Proficiency in Python, including data analysis and scripting to automate workflows | **supported** | quote found in the posting |
| 6 | The role uses SQL, which Priya has shipped with. | supported | Strong SQL and data skills; comfort querying and analyzing large datasets (e.g. Databricks) | **supported** | quote found in the posting |
| 7 | The role uses Databricks, which Priya has shipped with. | supported | Strong SQL and data skills; comfort querying and analyzing large datasets (e.g. Databricks) | **supported** | quote found in the posting |
| 8 | The job can be done in the US (Foster City, CA). | supported | Ability to relocate to the Bay Area, California, for the duration of the internship | **supported** | quote found in the posting |
| 9 | The job is open to someone with less than one year of full-time experience. | supported | Currently working towards a B.S., M.S., Ph.D., or advanced degree in a relevant engineering program | **supported** | quote found in the posting |
| 10 | The employer will sponsor a US work visa. | insufficient |  | **insufficient** | labelled insufficient |

### 6. Data Scientist Intern [Summer 2027] (zoox), score 9

Labelled by Claude (sonnet, `claude -p`) at 2026-11-25T04:38:59+00:00; re-checked by `agent/evidence.py`. Agent's answer: experience **yes**, sponsorship **I cannot tell**.

| # | Claim | Claude's label | Quote | Final label | Check |
|---|---|---|---|---|---|
| 1 | The job is a Intern role. | supported | Data Scientist Intern [Summer 2027] | **supported** | quote found in the posting |
| 2 | The day-to-day work involves LLM. | insufficient |  | **insufficient** | labelled insufficient |
| 3 | The day-to-day work involves machine learning. | supported | Formulate and build statistical and machine learning models to evaluate system performance and analyze rare, high-consequence safety events. | **supported** | quote found in the posting |
| 4 | The day-to-day work involves evaluation. | supported | Formulate and build statistical and machine learning models to evaluate system performance and analyze rare, high-consequence safety events. | **supported** | quote found in the posting |
| 5 | The day-to-day work involves inference. | insufficient |  | **insufficient** | labelled insufficient |
| 6 | The day-to-day work involves agents. | insufficient |  | **insufficient** | labelled insufficient |
| 7 | The role uses Python, which Priya has shipped with. | supported | Process and analyze large-scale datasets using SQL, Python, or distributed data frameworks (Spark/Databricks) | **supported** | quote found in the posting |
| 8 | The role uses SQL, which Priya has shipped with. | supported | Process and analyze large-scale datasets using SQL, Python, or distributed data frameworks (Spark/Databricks) | **supported** | quote found in the posting |
| 9 | The role uses Databricks, which Priya has shipped with. | supported | Process and analyze large-scale datasets using SQL, Python, or distributed data frameworks (Spark/Databricks) | **supported** | quote found in the posting |
| 10 | The job can be done in the US (Foster City, CA). | supported | Foster City, CA | **supported** | quote found in the posting |
| 11 | The job is open to someone with less than one year of full-time experience. | supported | Currently pursuing a Master's or Ph.D. in Statistics, Data Science, Machine Learning, Computer Science, or a related quantitative engineering/scientific discipline. | **supported** | quote found in the posting |
| 12 | The employer will sponsor a US work visa. | insufficient |  | **insufficient** | labelled insufficient |

### 7. Partner Applied AI Engineer, Oracle and Cloud ISV (openai), score 8

Labelled by Claude (sonnet, `claude -p`) at 2026-11-25T04:39:05+00:00; re-checked by `agent/evidence.py`. Agent's answer: experience **no**, sponsorship **I cannot tell**.

| # | Claim | Claude's label | Quote | Final label | Check |
|---|---|---|---|---|---|
| 1 | The job is a AI role. | supported | The Applied AI Engineering team helps developers and enterprises deploy generative AI safely and effectively. | **supported** | quote found in the posting |
| 2 | The day-to-day work involves LLM. | supported | practical experience with APIs, retrieval, tool use, LLM evaluation, and secure cloud deployments. | **supported** | quote found in the posting |
| 3 | The day-to-day work involves evaluation. | supported | Put evaluation, observability, and deployment practices in place to measure quality, safety, reliability, latency, cost, and real workload usage. | **supported** | quote found in the posting |
| 4 | The day-to-day work involves inference. | insufficient |  | **insufficient** | labelled insufficient |
| 5 | The day-to-day work involves agents. | supported | GPT-powered applications and agents with Mosaic AI Model Serving, Agent Bricks, and Databricks Apps. | **supported** | quote found in the posting |
| 6 | The role uses Python, which Priya has shipped with. | supported | Can build in Python or a comparable language | **supported** | quote found in the posting |
| 7 | The role uses Databricks, which Priya has shipped with. | supported | you will work with Oracle Cloud, Snowflake, and Databricks to help customers adopt OpenAI. | **supported** | quote found in the posting |
| 8 | The job can be done in the US (San Francisco). | supported | Location: San Francisco | **supported** | quote found in the posting |
| 9 | The job is open to someone with less than one year of full-time experience. | contradicted | We are looking for an experienced technical leader | **contradicted** | quote found in the posting |
| 10 | The employer will sponsor a US work visa. | insufficient |  | **insufficient** | labelled insufficient |

### 8. Product Management Intern (Summer 2027) (databricks), score 8

Labelled by Claude (sonnet, `claude -p`) at 2026-11-25T04:39:11+00:00; re-checked by `agent/evidence.py`. Agent's answer: experience **yes**, sponsorship **I cannot tell**.

| # | Claim | Claude's label | Quote | Final label | Check |
|---|---|---|---|---|---|
| 1 | The job is a Intern role. | supported | Title: Product Management Intern (Summer 2027) | **supported** | quote found in the posting |
| 2 | The day-to-day work involves machine learning. | insufficient |  | **insufficient** | labelled insufficient |
| 3 | The day-to-day work involves agents. | insufficient |  | **insufficient** | labelled insufficient |
| 4 | The role uses Python, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 5 | The role uses SQL, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 6 | The role uses Databricks, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 7 | The role uses Unity Catalog, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 8 | The job can be done in the US (Bellevue, Washington). | supported | This is a 12 week paid summer internship program in either San Francisco, CA, Mountain View, CA, or Bellevue, WA. | **supported** | quote found in the posting |
| 9 | The job is open to someone with less than one year of full-time experience. | supported | Pursuing a bachelor's or master's in computer science or a related engineering field graduating in Fall 2027 or Spring 2028 | **supported** | quote found in the posting |
| 10 | The employer will sponsor a US work visa. | insufficient |  | **insufficient** | labelled insufficient |

### 9. Systems & Safety Engineering Intern [Summer 2027] (zoox), score 8

Labelled by Claude (sonnet, `claude -p`) at 2026-11-25T04:39:17+00:00; re-checked by `agent/evidence.py`. Agent's answer: experience **yes**, sponsorship **I cannot tell**.

| # | Claim | Claude's label | Quote | Final label | Check |
|---|---|---|---|---|---|
| 1 | The job is a Intern role. | supported | Systems & Safety Engineering Intern [Summer 2027] | **supported** | quote found in the posting |
| 2 | The day-to-day work involves LLM. | supported | Hands-on experience using modern AI tools and agents (LLM assistants, prompt pipelines, coding agents) in engineering or research | **supported** | quote found in the posting |
| 3 | The day-to-day work involves machine learning. | insufficient |  | **insufficient** | labelled insufficient |
| 4 | The day-to-day work involves RAG. | insufficient |  | **insufficient** | labelled insufficient |
| 5 | The day-to-day work involves agents. | insufficient |  | **insufficient** | labelled insufficient |
| 6 | The role uses Python, which Priya has shipped with. | supported | Develop Python-based automation and data analysis scripts to extract metrics, validate system requirements, and automate safety analysis workflows. | **supported** | quote found in the posting |
| 7 | The role uses SQL, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 8 | The job can be done in the US (Foster City, CA). | supported | Location: Foster City, CA | **supported** | quote found in the posting |
| 9 | The job is open to someone with less than one year of full-time experience. | supported | Currently working towards a B.S., M.S., Ph.D., or advanced degree in Systems Engineering, Computer Science, Electrical Engineering, Robotics, Mechanical Engineering, or a related discipline. | **supported** | quote found in the posting |
| 10 | The employer will sponsor a US work visa. | insufficient |  | **insufficient** | labelled insufficient |

### 10. Data Science Intern [Summer 2027] (zoox), score 8

Labelled by Claude (sonnet, `claude -p`) at 2026-11-25T04:39:21+00:00; re-checked by `agent/evidence.py`. Agent's answer: experience **yes**, sponsorship **I cannot tell**.

| # | Claim | Claude's label | Quote | Final label | Check |
|---|---|---|---|---|---|
| 1 | The job is a Intern role. | supported | Data Science Intern [Summer 2027] | **supported** | quote found in the posting |
| 2 | The day-to-day work involves machine learning. | supported | Test new frameworks and algorithms to improve model performance | **supported** | quote found in the posting |
| 3 | The day-to-day work involves evaluation. | supported | You will work on fleet metrics, behavior analysis, and performance evaluation of our autonomous vehicles. | **supported** | quote found in the posting |
| 4 | The role uses Python, which Priya has shipped with. | supported | Proficiency in Python and SQL | **supported** | quote found in the posting |
| 5 | The role uses SQL, which Priya has shipped with. | supported | Proficiency in Python and SQL | **supported** | quote found in the posting |
| 6 | The role uses Databricks, which Priya has shipped with. | insufficient |  | **insufficient** | labelled insufficient |
| 7 | The job can be done in the US (Foster City, CA). | supported | Location: Foster City, CA; Boston, MA | **supported** | quote found in the posting |
| 8 | The job is open to someone with less than one year of full-time experience. | supported | Currently working towards a B.S., M.S., Ph.D., or advanced degree in data science, statistics, computer science, or a related engineering program | **supported** | quote found in the posting |
| 9 | The employer will sponsor a US work visa. | insufficient |  | **insufficient** | labelled insufficient |
