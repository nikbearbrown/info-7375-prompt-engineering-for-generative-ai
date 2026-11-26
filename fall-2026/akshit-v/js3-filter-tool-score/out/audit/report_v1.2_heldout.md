# Audit report: filter v1.2 vs my hand labels (heldout sets)

Sample drawn with seed 20261124 from the v1.0 verdicts (FILTER.md section 5). A posting counts as an error when keep != (hand label == relevant).

- **heldout_reject**: labeled 15/15; wrong 6/15 = 40% (95% CI 16%–68%); kept under v1.2: 2
- **heldout_kept_or_close**: labeled 15/15; wrong 3/15 = 20% (95% CI 4%–48%); kept under v1.2: 15

## Every disagreement, with the words that moved the score

### [heldout_reject] Sr Product Marketing Manager, Media, Entertainment and Advertising (ashby:snowflake)
- filter: **reject**, disqualified by title:Manager; [role 0 (none) + topics 1 (T4 orchestration) + skills 0 (none) = 1]
- my label: **relevant**: partial match
- id `ashby:snowflake:5220aae8-7fd1-4374-8b8f-4f27f8573791`
  - topic **T4 orchestration: orchestration**: "…ategy with execution. The successful candidate will thrive on program orchestration, enablement at scale, and surfacing regional insights to…"

### [heldout_reject] Senior Solution Engineer - Expansion (ashby:snowflake)
- filter: **keep**, role 0 (none) + topics 1 (T4 orchestration) + skills 4 (Python, SQL, Spark, dbt) = 5 >= 5
- my label: **not_relevant**: not data engineer role
- id `ashby:snowflake:7d56d42e-4157-47df-81b3-d5e2f5abacde`
  - topic **T4 orchestration: orchestration**: "… modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)   - Experience with AI, data science a…"
  - skill **Python**: "…   PREFERRED (BUT NOT REQUIRED) TO HAVE:   - Hands on experience with Python   - Experience working with modern data technology (e.g. dbt, s…"
  - skill **SQL**: "…ure, data analytics and cloud technology   - Hands on experience with SQL   - Ability to solve customer specific business problems and apply…"
  - skill **Spark**: "… Python   - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)   -…"
  - skill **dbt**: "… with Python   - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.…"

### [heldout_reject] Senior Software Engineer - Elastic Global Services (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 0 (none) + skills 0 (none) = 0, below 5
- my label: **relevant**: candidate skills matches the skillset
- id `ashby:snowflake:829e9786-6661-4134-b7cd-aef3bed75c1c`

### [heldout_reject] Strategic Account Executive, Majors Acquisition (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T2 storage) + skills 0 (none) = 1, below 5
- my label: **relevant**: partial match
- id `ashby:snowflake:cdebc456-bb4f-4cc7-84fc-dccb8499a8f6`
  - topic **T2 storage: Data Warehousing**: "…mplex sales strategies and tactics within one of the following spaces Data Warehousing, Business Intelligence, Data Science and/or AI/ML   -…"

### [heldout_reject] Account Executive, SMB (Berlin, Germany) (greenhouse:figma)
- filter: **reject**, role 0 (none) + topics 0 (none) + skills 0 (none) = 0, below 5
- my label: **relevant**: partial match
- id `greenhouse:figma:5985397004`

### [heldout_reject] Manager, Software Engineering - External Platform (greenhouse:figma)
- filter: **reject**, disqualified by title:Manager; [role 0 (none) + topics 0 (none) + skills 0 (none) = 0]
- my label: **relevant**: skillset matches
- id `greenhouse:figma:6224661004`

### [heldout_kept_or_close] Account Engineer (ashby:snowflake)
- filter: **keep**, role 0 (none) + topics 1 (T4 orchestration) + skills 4 (Python, SQL, dbt, AWS) = 5 >= 5
- my label: **not_relevant**: no dutch language speaking skills
- id `ashby:snowflake:2d84b26c-fd1c-414b-b321-39369bc6ddb6`
  - topic **T4 orchestration: orchestration**: "…perience in Python, Java or Scala, and experience with dbt, CI/CD and orchestration tools.   - Daily use of AI-powered development tools and…"
  - skill **Python**: "…ns)   - SnowPro Advanced certification.   - Programming experience in Python, Java or Scala, and experience with dbt, CI/CD and orchestratio…"
  - skill **SQL**: "… of related experience, including time in a customer-facing role.   - SQL and Data Architecture: Strong hands-on SQL and data architecture e…"
  - skill **dbt**: "… Programming experience in Python, Java or Scala, and experience with dbt, CI/CD and orchestration tools.   - Daily use of AI-powered develo…"
  - skill **AWS**: "…ern Data Stack: Solid knowledge of at least one major cloud platform (AWS, Azure or Google Cloud).   - Delivery: Project management skills t…"

### [heldout_kept_or_close] Solution Engineer - GCC (FSI) (ashby:snowflake)
- filter: **keep**, role 0 (none) + topics 3 (T1 pipelines, T2 storage, T3 modeling) + skills 3 (Python, SQL, AWS) = 6 >= 5
- my label: **not_relevant**: requires lots of work experience
- id `ashby:snowflake:dd74b9e7-ebed-4d23-94d0-1fbb4d90b180`
  - topic **T1 pipelines: ETL**: "…road range of skills and experience ranging from data architecture to ETL/ELT, data science, security, performance analysis, analytics, etc.…"
  - topic **T2 storage: data warehouse**: "…lent experience   - Strong competency on modern data stacks, ETL/ELT, data warehouse/lake, data science and data apps   - Outstanding skills…"
  - topic **T3 modeling: Data modeling**: "…ud Provider Experience -  Amazon AWS/Microsoft Azure/Google Cloud   - Data modeling and data architecture experience   - Experience selling …"
  - skill **Python**: "…or using presentations and demos.   - Hands-on expertise with SQL and Python   - Experience working with large global accounts, GSIs and/or …"
  - skill **SQL**: "…teboard or using presentations and demos.   - Hands-on expertise with SQL and Python   - Experience working with large global accounts, GSIs…"
  - skill **AWS**: "…leau, PowerBI, Metabase etc).   - Cloud Provider Experience -  Amazon AWS/Microsoft Azure/Google Cloud   - Data modeling and data architectu…"

### [heldout_kept_or_close] Commercial Solutions Engineer - Acquisition (ashby:snowflake)
- filter: **keep**, role 0 (none) + topics 1 (T4 orchestration) + skills 4 (Python, SQL, Spark, dbt) = 5 >= 5
- my label: **not_relevant**: not data engineer role
- id `ashby:snowflake:f86b9707-4718-43ed-99b8-29913a9118fd`
  - topic **T4 orchestration: orchestration**: "… modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)    - Experience with data science and …"
  - skill **Python**: "…   PREFERRED (BUT NOT REQUIRED) TO HAVE:   - Hands on experience with Python    - Experience working with modern data technology (e.g. dbt, …"
  - skill **SQL**: "…re, data analytics and cloud technology    - Hands on experience with SQL   - Ability to solve customer specific business problems and apply…"
  - skill **Spark**: "…Python    - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)    …"
  - skill **dbt**: "…with Python    - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.…"

## Each counted term across the labeled postings

| term | matched in | of those, labeled relevant |
|---|---:|---:|
| skill:SQL | 16 | 10 |
| skill:Python | 15 | 11 |
| skill:Spark | 13 | 10 |
| topic:orchestration | 10 | 7 |
| skill:dbt | 9 | 6 |
| skill:AWS | 8 | 5 |
| topic:etl | 7 | 4 |
| topic:data warehouse | 5 | 2 |
| skill:Kafka | 3 | 3 |
| topic:data pipelines | 3 | 3 |
| topic:data warehousing | 3 | 3 |
| topic:streaming | 3 | 3 |
| skill:Airflow | 2 | 2 |
| topic:data modeling | 2 | 1 |
| topic:data quality | 2 | 2 |
| role:Data Engineering | 1 | 1 |
| topic:data lake | 1 | 1 |
| topic:data models | 1 | 1 |
