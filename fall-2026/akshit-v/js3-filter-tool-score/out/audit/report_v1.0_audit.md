# Audit report: filter v1.0 vs my hand labels (audit sets)

Sample drawn with seed 20261124 from the v1.0 verdicts (FILTER.md section 5). A posting counts as an error when keep != (hand label == relevant).

- **audit_reject_random**: labeled 30/30; wrong 12/30 = 40% (95% CI 23%–59%); kept under v1.0: 0
- **audit_close**: labeled 10/10; wrong 5/10 = 50% (95% CI 19%–81%); kept under v1.0: 5
- **audit_kept_random**: labeled 10/10; wrong 0/10 = 0% (95% CI 0%–31%); kept under v1.0: 10

## What 30 random rejects can and cannot say

- 12 of 30 random v1.0 rejects were postings I labeled relevant.
- 95% exact interval for the reject error rate: 22.7% to 59.4%.
- Scaled to all 689 v1.0 rejects: between about 156 and 409 relevant postings could be among them. The sample cannot tell those apart.
- The sample is random over rejects, so it says almost nothing about rare kinds of reject: a kind that is 3% of rejects has a 40% chance of not appearing in 30 draws at all.

## Every disagreement, with the words that moved the score

### [audit_reject_random] Software Engineer - Trust & Platform Security (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 0 (none) + skills 3 (Python, SQL, AWS) = 3, below 6
- my label: **relevant**: partial match
- id `ashby:snowflake:2887def2-f6d8-44fb-b6c4-976329de7d5f`
  - skill **Python**: "… Loss Prevention (DLP) concepts   - Solid coding skills in SQL, Java, Python and exposure to building distributed or backend systems and wil…"
  - skill **SQL**: "…es, or Data Loss Prevention (DLP) concepts   - Solid coding skills in SQL, Java, Python and exposure to building distributed or backend syst…"
  - skill **AWS**: "… for full stack exposure   - Familiarity with cloud platforms such as AWS, GCP, or Azure, and their security or networking controls   - Eage…"

### [audit_reject_random] Staff  Software Engineer - Database Engineering (ashby:snowflake)
- filter: **reject**, disqualified by title:Staff; [role 0 (none) + topics 1 (T2 storage) + skills 0 (none) = 1]
- my label: **relevant**: skillset matches
- id `ashby:snowflake:30e214f2-5853-4014-8def-c4284c0e99f8`
  - topic **T2 storage: data warehousing**: "…d data processing algorithms to maintain Snowflake's industry-leading data warehousing capabilities.   - Design, develop, and support a peta…"

### [audit_reject_random] Staff Software Engineer - Metadata (ashby:snowflake)
- filter: **reject**, disqualified by title:Staff; [role 0 (none) + topics 0 (none) + skills 1 (AWS) = 1]
- my label: **relevant**: some skills matches
- id `ashby:snowflake:67057ad9-3f52-4f54-80c6-20a1ea026db4`
  - skill **AWS**: "…a, catalogs, or query compilation.   - Experience running services on AWS, Azure, or GCP.  Snowflake is growing fast, and we’re scaling our …"

### [audit_reject_random] Engineering Manager (ashby:snowflake)
- filter: **reject**, disqualified by title:Manager; [role 0 (none) + topics 1 (T4 orchestration) + skills 1 (AWS) = 2]
- my label: **relevant**: skillset matches
- id `ashby:snowflake:906a4bc8-b5f6-4a35-bf97-fa6d9e694893`
  - topic **T4 orchestration: orchestration**: "…trong technical leadership across both the Postgres dataplane and the orchestration/control plane required to deliver a managed service (HA,…"
  - skill **AWS**: "…ices in production.   - Significant experience in cloud environments (AWS, Azure, and/or GCP) and building services with high availability a…"

### [audit_reject_random] Principal Engineer (ashby:snowflake)
- filter: **reject**, disqualified by title:Principal; [role 0 (none) + topics 0 (none) + skills 1 (Python) = 1]
- my label: **relevant**: partial match
- id `ashby:snowflake:a265dbe7-bf24-4443-b54e-8da34ab5adad`
  - skill **Python**: "…e requires a rare combination: deep hands-on engineering expertise in Python/container runtimes, a systems architect's instinct for platform…"

### [audit_reject_random] Senior Software Engineer, Enterprise Team (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T2 storage) + skills 1 (Python) = 2, below 6
- my label: **relevant**: required skills are matching with the candidate skills
- id `ashby:snowflake:b29ce51b-a6b7-43af-81ce-3fe882913cc4`
  - topic **T2 storage: lakehouse**: "…and store logs, metrics, traces, and events on an open, scalable data lakehouse, using open formats like Apache Iceberg, at dramatically low…"
  - skill **Python**: "…iciency in one or more server-side languages such as Go, Java, Scala, Python, or similar   - Ability to work independently and take ownershi…"

### [audit_reject_random] Partner Development Manager (ashby:snowflake)
- filter: **reject**, disqualified by title:Manager; [role 0 (none) + topics 0 (none) + skills 0 (none) = 0]
- my label: **relevant**: partial match
- id `ashby:snowflake:da15dcf5-67fc-4217-9cb9-fd6839d94eee`

### [audit_reject_random] Enterprise Account Executive (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 0 (none) + skills 0 (none) = 0, below 6
- my label: **relevant**: partial match
- id `ashby:snowflake:e3468d58-d62b-4633-b7cd-54e0a2e90e5c`

### [audit_reject_random] Product Manager, AI Growth (greenhouse:figma)
- filter: **reject**, disqualified by title:Manager; [role 0 (none) + topics 0 (none) + skills 0 (none) = 0]
- my label: **relevant**: partial match
- id `greenhouse:figma:5989185004`

### [audit_reject_random] Applied Data Researcher (greenhouse:figma)
- filter: **reject**, role 0 (none) + topics 0 (none) + skills 5 (Python, SQL, dbt, Snowflake, AWS) = 5, below 6
- my label: **relevant**: partial match
- id `greenhouse:figma:6238480004`
  - skill **Python**: "…g evals, labeling, and agentic workflows Fluent programming skills in Python or a comparable language, plus SQL, and a record of independent…"
  - skill **SQL**: "…ws Fluent programming skills in Python or a comparable language, plus SQL, and a record of independently building, debugging, testing, and r…"
  - skill **dbt**: "… infrastructure experience; familiarity with Snowflake, AWS, Dagster, dbt, or Hex is useful, but no particular vendor or framework is requir…"
  - skill **Snowflake**: "…urce tools Cloud and data infrastructure experience; familiarity with Snowflake, AWS, Dagster, dbt, or Hex is useful, but no particular vend…"
  - skill **AWS**: "…Cloud and data infrastructure experience; familiarity with Snowflake, AWS, Dagster, dbt, or Hex is useful, but no particular vendor or frame…"

### [audit_reject_random] Researcher, AI Evaluations (greenhouse:figma)
- filter: **reject**, role 0 (none) + topics 0 (none) + skills 0 (none) = 0, below 6
- my label: **relevant**: partial match
- id `greenhouse:figma:6242701004`

### [audit_reject_random] Senior Machine Learning Engineering Manager - Content Platform (lever:spotify)
- filter: **reject**, disqualified by title:Manager; [role 0 (none) + topics 0 (none) + skills 0 (none) = 0]
- my label: **relevant**: partial match
- id `lever:spotify:bc70c9af-212e-48d5-b00b-eab26e4c0658`

### [audit_close] Solutions Architect (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T1 pipelines) + skills 4 (Python, SQL, Spark, AWS) = 5, below 6
- my label: **relevant**: partial match
- id `ashby:snowflake:440ec976-a307-4575-abab-554aef8151a4`
  - topic **T1 pipelines: ETL**: "…  - Understanding of complete data analytics stack and workflow, from ETL to data platform design to BI and analytics tools   - Deep underst…"
  - skill **Python**: "…utions   - Hands-on experience in a technical role leveraging SQL and Python (optionally Java or Spark) to build, operate and maintain data …"
  - skill **SQL**: "… ETL solutions   - Hands-on experience in a technical role leveraging SQL and Python (optionally Java or Spark) to build, operate and mainta…"
  - skill **Spark**: "…nce in a technical role leveraging SQL and Python (optionally Java or Spark) to build, operate and maintain data analytics solutions   - Ext…"
  - skill **AWS**: "…ecuting technical projects   - Application Development experience   - AWS, Google or Microsoft Cloud certification(s)   - Snowflake Snowpro …"

### [audit_close] Senior Solution Engineer - GCC (ashby:snowflake)
- filter: **keep**, role 0 (none) + topics 3 (T1 pipelines, T2 storage, T3 modeling) + skills 3 (Python, SQL, AWS) = 6 >= 6
- my label: **not_relevant**: requires more number of experience than what candidate has
- id `ashby:snowflake:9d29d7a3-e42b-4a47-adc7-896eb60ffbc7`
  - topic **T1 pipelines: ETL**: "…road range of skills and experience ranging from data architecture to ETL/ELT, data science, security, performance analysis, analytics, etc.…"
  - topic **T2 storage: data warehouse**: "…lent experience   - Strong competency on modern data stacks, ETL/ELT, data warehouse/lake, data science and data apps   - Outstanding skills…"
  - topic **T3 modeling: Data modeling**: "…ud Provider Experience -  Amazon AWS/Microsoft Azure/Google Cloud   - Data modeling and data architecture experience   - Experience selling …"
  - skill **Python**: "…or using presentations and demos.   - Hands-on expertise with SQL and Python   - Experience working with large global accounts, GSIs and/or …"
  - skill **SQL**: "…teboard or using presentations and demos.   - Hands-on expertise with SQL and Python   - Experience working with large global accounts, GSIs…"
  - skill **AWS**: "…leau, PowerBI, Metabase etc).   - Cloud Provider Experience -  Amazon AWS/Microsoft Azure/Google Cloud   - Data modeling and data architectu…"

### [audit_close] Account Engineer (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T4 orchestration) + skills 4 (Python, SQL, dbt, AWS) = 5, below 6
- my label: **relevant**: skillset matches
- id `ashby:snowflake:c8604e76-c715-4709-b46e-26639c35649e`
  - topic **T4 orchestration: orchestration**: "…perience in Python, Java or Scala, and experience with dbt, CI/CD and orchestration tools.   - Daily use of AI-powered development tools and…"
  - skill **Python**: "…ns)   - SnowPro Advanced certification.   - Programming experience in Python, Java or Scala, and experience with dbt, CI/CD and orchestratio…"
  - skill **SQL**: "… of related experience, including time in a customer-facing role.   - SQL and Data Architecture: Strong hands-on SQL and data architecture e…"
  - skill **dbt**: "… Programming experience in Python, Java or Scala, and experience with dbt, CI/CD and orchestration tools.   - Daily use of AI-powered develo…"
  - skill **AWS**: "…ern Data Stack: Solid knowledge of at least one major cloud platform (AWS, Azure or Google Cloud).   - Delivery: Project management skills t…"

### [audit_close] Associate Solution Engineer (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T4 orchestration) + skills 4 (Python, SQL, Spark, dbt) = 5, below 6
- my label: **relevant**: skillset matches
- id `ashby:snowflake:ffa41b67-69ab-4086-b025-60dcb8bce489`
  - topic **T4 orchestration: orchestration**: "… modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)    - Experience with data science and …"
  - skill **Python**: "…   PREFERRED (BUT NOT REQUIRED) TO HAVE:   - Hands on experience with Python    - Experience working with modern data technology (e.g. dbt, …"
  - skill **SQL**: "…re, data analytics and cloud technology    - Hands on experience with SQL   - Ability to solve customer specific business problems and apply…"
  - skill **Spark**: "…Python    - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)    …"
  - skill **dbt**: "…with Python    - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.…"

### [audit_close] Technical Operations & Insights Analyst (greenhouse:figma)
- filter: **reject**, role 0 (none) + topics 1 (T3 modeling) + skills 4 (Python, SQL, dbt, Snowflake) = 5, below 6
- my label: **relevant**: skillset matches
- id `greenhouse:figma:6249978004`
  - topic **T3 modeling: data models**: "…cial partners Use SQL and Python or R to build reproducible analyses, data models, and reporting. Use git, peer review, and responsible AI-a…"
  - skill **Python**: "…ns, and ownership with operational and financial partners Use SQL and Python or R to build reproducible analyses, data models, and reporting…"
  - skill **SQL**: "…exclusions, and ownership with operational and financial partners Use SQL and Python or R to build reproducible analyses, data models, and r…"
  - skill **dbt**: "…ience, service operations, or cost-to-serve analytics Experience with dbt, Snowflake, Hex, or comparable analytical toolsets Experiment desi…"
  - skill **Snowflake**: "…, service operations, or cost-to-serve analytics Experience with dbt, Snowflake, Hex, or comparable analytical toolsets Experiment design, a…"

## Each counted term across the labeled postings

| term | matched in | of those, labeled relevant |
|---|---:|---:|
| skill:Python | 25 | 20 |
| skill:SQL | 23 | 18 |
| skill:AWS | 17 | 14 |
| skill:dbt | 13 | 12 |
| skill:Spark | 11 | 11 |
| topic:orchestration | 9 | 8 |
| topic:etl | 8 | 6 |
| topic:data warehouse | 7 | 5 |
| skill:Snowflake | 6 | 5 |
| topic:data modeling | 6 | 4 |
| topic:data quality | 6 | 6 |
| topic:data warehousing | 6 | 1 |
| topic:data pipelines | 5 | 4 |
| topic:streaming | 4 | 3 |
| skill:Airflow | 3 | 3 |
| topic:data models | 3 | 3 |
| role:Data Platform | 2 | 2 |
| skill:Kafka | 2 | 2 |
| topic:data warehouses | 2 | 2 |
| topic:lakehouse | 2 | 2 |
| role:Data Engineer | 1 | 1 |
| role:Data Infrastructure | 1 | 1 |
| topic:data lake | 1 | 0 |
| topic:data pipeline | 1 | 1 |
