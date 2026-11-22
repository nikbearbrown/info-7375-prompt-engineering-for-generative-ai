# Prior art for Part 2 — researched by a Claude Code subagent, 2026-11-21

Method (written by the subagent, not the student): every page below was read on 2026-11-21. Pages that allowed it were read as raw HTML. uscis.gov and jobscan.co refused scripted reads, so they were read with a web-fetch tool and then checked as plain page text in a browser pane. There was no sign-in, no form, no account and no personal data. The only search was one generic job-title search (*machine learning engineer*, 2025) on h1bdata.info. Text in double quotation marks is copied from the named page, was matched against that page's text, and is 15 words or fewer. *Not mentioned on the pages read* means only that. It is not evidence that a product or paper lacks the feature.

## USCIS H-1B Employer Data Hub  (category: sponsorship-history lookup, official U.S. government)
- URL: hub page https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub ; companion page https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub/understanding-our-h-1b-employer-data-hub
- Accessed: 2026-11-21 18:43 ET (first read of both pages); quotes re-checked in a browser 18:46–18:47 ET and 18:54 ET
- What it produces (from its own page): employer-level counts of USCIS decisions on H-1B petitions, fiscal year 2009 through fiscal year 2026 (quarter 4), downloadable as Excel or CSV. The hub has "data on the first decisions USCIS makes on petitions for initial and continuing employment" (hub page). Data can be "queried by fiscal year, employer name, city, state, zip code, and NAICS code" (hub page). Counts are "aggregated by distinct completion fiscal year, two digit NAICS code, tax ID", plus state, city and ZIP code (companion page). Stated limits: "The approval and denial data in the data hub reflects USCIS’ first decision." (companion page). Appeals and revocations are excluded. State, city and ZIP code come from the employer's mailing address, which is "not necessarily the beneficiary(ies) work location" (companion page).
- What its page says about:
  - (a) required vs preferred: not mentioned on the pages read.
  - (b) quoting the posting's sentences: not mentioned on the pages read.
  - (c) sponsorship for a specific posting: not mentioned on the pages read. The counts are per employer. Job title is not among the query fields the hub page lists, and the companion page mentions job titles only inside two glossary definitions, about a change in job title. The companion page says an employer needs a certified Labor Condition Application from the Department of Labor before filing Form I-129, and that hub data come from Form I-129 fields or adjudicative decisions.
  - (d) a human approval step: not mentioned on the pages read.
- Result reported (research only): n/a (not research).
- Confidence: high. These are official government pages. The main text of both pages was read in full, and each quote was checked against the page text in a browser.

## h1bdata.info  (category: sponsorship-history lookup, third-party site built on Department of Labor LCA disclosure data)
- URL: homepage https://h1bdata.info/ ; example search page https://h1bdata.info/index.php?em=&job=machine+learning+engineer&city=&year=2025
- Accessed: 2026-11-21 18:44 ET
- What it produces (from its own page): the homepage says the site indexes the Department of Labor's Labor Condition Application (LCA) disclosure data. It explains that an employer must file an LCA with the Department of Labor before filing an H-1B petition with USCIS. The search form takes an employer, a job title, a city and a year. The example job-title search listed one row per record, with the columns EMPLOYER, JOB TITLE, BASE SALARY, LOCATION, SUBMIT DATE and START DATE. The homepage says it has indexed more than 3.8 million records between April 2016 and June 2026.
- What its page says about:
  - (a) required vs preferred: not mentioned on the pages read.
  - (b) quoting the posting's sentences: not mentioned on the pages read.
  - (c) sponsorship for a specific posting: not mentioned on the pages read. The records are LCA filings, searchable by job title. The pages read do not link a record to any job posting, and the homepage warns: "DOL disclosure data does not indicate the employer's intended use for the LCA." (homepage)
  - (d) a human approval step: not mentioned on the pages read.
- Result reported (research only): n/a (not research).
- Confidence: high for what the pages say. They were read as raw HTML, and the quote was checked character for character. This is a third-party site, and its records were not compared with the Department of Labor's own files.

## Jobscan  (category: résumé-to-posting match scorer, commercial)
- URL: homepage https://www.jobscan.co/ ; tutorial https://www.jobscan.co/jobscan-tutorial
- Accessed: 2026-11-21 18:44 ET (homepage) and 18:45 ET (tutorial); both re-checked in a browser 18:47 ET, and the homepage quote again 18:54 ET
- What it produces (from its own page): a match rate (the tutorial also calls it a Match Score) for a résumé compared with a job description the user pastes in. The homepage says Jobscan shows the keywords and skills the résumé is missing. The homepage lists what the match rate is based on, in order: hard skills; education level (only when the job description includes an advanced degree); job title; soft skills; other keywords. It recommends a 75% match rate. The tutorial says *predicted skills* (common skills in the field that are not in the pasted posting) do not affect the match rate.
- What its page says about:
  - (a) required vs preferred: not mentioned on the pages read. The match-rate priorities are skill types, and neither page uses the words required or preferred about qualifications.
  - (b) quoting the posting's sentences: the tutorial describes a Highlighted Skills section that shows every use of a chosen keyword, highlighted in both the résumé and the job description. Clicking a skill shows the context where it is used in both. The pages read do not describe quoting whole requirement sentences, or checking that a quote is really in the posting.
  - (c) sponsorship for a specific posting: not mentioned on the pages read. Neither page mentions visas or sponsorship.
  - (d) a human approval step: yes, for its Auto Apply feature: "Auto-apply with your resume. You review every one before it's sent." (homepage). The tutorial also says each AI résumé suggestion can be accepted or rejected with one click.
- Result reported (research only): n/a (not research).
- Confidence: high for what the pages say. The main text was read twice, and the quote was checked against the page text in a browser. These are marketing and tutorial pages. The product itself was not tried, and its features may differ by plan or change over time.

## SkillSpan: Hard and Soft Skill Extraction from English Job Postings — Zhang, Jensen, Sonniks and Plank, NAACL 2022  (category: published research, span-level skill extraction)
- URL: abstract page https://aclanthology.org/2022.naacl-main.366/ ; arXiv full text https://arxiv.org/html/2204.12811
- Accessed: 2026-11-21 18:45 ET (abstract page; abstract re-read as raw HTML 18:46 ET); arXiv full text 18:48 ET
- What it produces (from its own page): a skill-extraction dataset, "a novel SE dataset consisting of 14.5K sentences and over 12.5K annotated spans" (abstract page). Domain experts annotated it for hard and soft skills. The authors release their annotation guidelines and report baseline models.
- What its page says about:
  - (a) required vs preferred: not mentioned in the abstract. The annotation guidelines in the arXiv full text say skills are annotated in all such sections, naming requirements, good-to-haves and optionals. The pages read describe no separate required-vs-preferred label.
  - (b) quoting the posting's sentences: the labels are spans of text inside job-posting sentences (abstract page). The pages read do not describe showing those sentences to a job seeker.
  - (c) sponsorship for a specific posting: not mentioned on the pages read.
  - (d) a human approval step: not mentioned on the pages read. The human role described is expert annotation of the data.
- Result reported (research only): the abstract reports a BERT baseline and experiments with long-span models, continued pre-training on job postings, and multi-task learning. Domain-adapted models significantly outperformed non-adapted ones, and single-task learning outperformed multi-task learning. The abstract gives no single headline score, so none is given here.
- Confidence: high. It is a peer-reviewed conference paper, and the abstract was read word for word from the ACL Anthology. The guideline detail comes from the arXiv full text, whose arXiv page says it was accepted to NAACL 2022.

## Rethinking Skill Extraction in the Job Market Domain using Large Language Models — Nguyen, Zhang, Montariol and Bosselut, NLP4HR workshop 2024  (category: published research, LLM-based skill extraction)
- URL: abstract page https://aclanthology.org/2024.nlp4hr-1.3/ ; arXiv v1 full text https://arxiv.org/html/2402.03832
- Accessed: 2026-11-21 18:45 ET (abstract page; abstract re-read as raw HTML 18:46 ET); arXiv full text 18:48 ET
- What it produces (from its own page): a test of few-shot, in-context prompting of large language models for skill extraction, on a benchmark of six skill-extraction datasets that the authors uniformized (abstract page). The full text says GPT-3.5-turbo was used for all experiments, with GPT-4 on a subset of samples, and that the six datasets cover four languages.
- What its page says about:
  - (a) required vs preferred: not mentioned on the pages read. The full text's prompt template asks for the skills required from the candidate, but no required-vs-preferred label is described.
  - (b) quoting the posting's sentences: a relevant finding in the full text. Under a looser matching metric, recall was much higher. The authors conclude that the models can locate skills within a sentence but "fail to capture the exact sequence" (arXiv full text).
  - (c) sponsorship for a specific posting: not mentioned on the pages read.
  - (d) a human approval step: not mentioned on the pages read.
- Result reported (research only): the abstract says the LLMs were not on par with traditional supervised models in performance, but handled syntactically complex skill mentions better. The full text adds that the drop from supervised models was significant on every dataset except one (Fijo, where GPT-3.5 was comparable), with up to 50% decreases in F1.
- Confidence: high for the abstract, read word for word from the ACL Anthology. Medium for the full-text details, which come from arXiv v1 (February 2024) and were not compared with the final ACL PDF.

## Enhancing Talent Employment Insights Through Feature Extraction with LLM Finetuning — Thakrar and Young, arXiv, January 2025  (category: published research, LLM-based requirement extraction)
- URL: abstract page https://arxiv.org/abs/2501.07663 ; full text https://arxiv.org/html/2501.07663v1
- Accessed: 2026-11-21 18:46 ET (re-checked 18:53 ET; quote re-checked 18:54 ET)
- What it produces (from its own page): the abstract describes a pipeline (semantic chunking, retrieval-augmented generation and fine-tuned DistilBERT models). It extracts job features from 1.2 million job postings provided by AdeptID, including remote work, pay structure, educational requirements and work-experience preferences. The full text describes structured output fields, such as a true/false experience_required field, experience_minimum_years, and an education requirement level. It says the paper was written in July 2024 for a Georgia Tech practicum course sponsored by AdeptID.
- What its page says about:
  - (a) required vs preferred: yes, directly. The full text says the original data did not show whether years of experience were required or preferred. So the output flags whether experience is required, and asks whether the education level is required or preferred: "This helps applicants understand true qualifications versus preferences." (full text)
  - (b) quoting the posting's sentences: not mentioned on the pages read. The output described is a set of structured fields, not quoted sentences.
  - (c) sponsorship for a specific posting: not mentioned on the pages read. The only sponsor the pages mention is the course sponsor, AdeptID.
  - (d) a human approval step: not mentioned on the pages read.
- Result reported (research only): the abstract claims significant improvements on variables that are often mislabeled or overlooked, but gives no numbers. In the full text, Table 2 (accuracy per sub-variable, % correct) lists Experience Required 74.2 and Education Required 73.5. The paper says the test-set ground truth was based on the output of a larger LLM. In a separate check of 10 postings (5 real, 5 written by the authors), 4 were correct on all variables, and 3 of those 4 were author-written.
- Confidence: medium. The arXiv page lists no journal or conference. The paper says it was written for a course practicum, and its main accuracy figures are measured against another LLM's output.

## Safe one-line summaries for narration
- USCIS H-1B Employer Data Hub: The official USCIS H-1B Employer Data Hub reports first-decision approval and denial counts by employer and fiscal year.
- h1bdata.info: One site built on Labor Department disclosure data lists past filings with employer, job title, salary and location.
- Jobscan: Jobscan scores a résumé against a posting and lists missing keywords; its Auto Apply says users review each application first.
- SkillSpan: The SkillSpan dataset marks hard and soft skills as text spans in about 14,500 English job-posting sentences.
- Nguyen et al., 2024: A 2024 study reported prompted large language models were not on par with supervised models for skill extraction.
- Thakrar and Young, 2025: A 2025 arXiv paper used language models to flag whether experience and education in job postings were required or preferred.
