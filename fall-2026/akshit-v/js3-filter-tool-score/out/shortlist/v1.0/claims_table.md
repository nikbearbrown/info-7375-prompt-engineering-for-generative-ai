# Every shortlist claim (v1.0), labeled

`checker` = a fresh Claude session given only the posting text and the claims (prompts/check_v1.md), after the code's verbatim check. `mine` = my blind hand check (labels/claim_checks_v1.0.csv), which under E4 stands.

## 1. Software Engineer - Data Infrastructure (greenhouse:figma)
`greenhouse:figma:5551686004` · https://boards.greenhouse.io/figma/jobs/5551686004?gh_jid=5551686004

- answer with the checker's labels: **relevant** (A2: both core claims are supported by quoted text)
- answer with my labels (E4, in force): **relevant** (A2: both core claims are supported by quoted text)

| # | kind | claim | quote | checker | mine | checker's reason |
|---|---|---|---|---|---|---|
| 1 | core_work | The posting says the main work is designing and building large-scale distributed data systems that power analytics, AI/ML, and business intelligence. | Design and build large-scale distributed data systems that power analytics, AI/ML, and business intelligence across Fig… | supported | supported | This is the first item under 'What you'll do at Figma', which describes the role's day-to-day work. |
| 2 | level | The posting asks for 5+ years of backend or infrastructure engineering experience, including designing and building distributed data infrastructure at scale. | 5+ years of backend or infrastructure engineering experience, including designing and building distributed data infrast… | supported | supported | The qualifications list, introduced by 'We'd love to hear from you if you have', includes this exact item. |
| 3 | employment | The posting says this is a full-time role, based at a US hub or remote in the United States. | This is a full-time role that can be held from one of our US hubs or remotely in the United States. | supported | supported | The posting says outright that this is a full-time role that can be held from a US hub or remotely in the Uni… |
| 4 | has | The posting requires 5+ years of backend or infrastructure engineering experience. The résumé shows about five years of data engineering, from 2019-07 to 2024-… | 5+ years of backend or infrastructure engineering experience | insufficient | supported | The posting lists the 5+ years under 'We'd love to hear from you if you have' and never states it is required… |
| 5 | has | The posting requires strong expertise in batch and streaming processing technologies such as Spark, Kafka, or Airflow. The résumé lists Spark, Kafka, and Airfl… | Strong expertise in batch and streaming data processing technologies such as Spark, Flink, Kafka, or Airflow/Dagster | insufficient | supported | The posting lists this expertise under 'We'd love to hear from you if you have' without stating it is require… |
| 6 | lacks | The posting asks for experience mentoring engineers. The résumé does not mention any mentoring. | Experience mentoring engineers and fostering a culture of learning and technical excellence | insufficient | supported | The posting does ask for mentoring experience, but it contains no résumé, so the claim that the résumé lacks … |
| 7 | has | The posting lists familiarity with its stack as a plus, not a requirement. The résumé covers Python, SQL, dbt, Spark, Kafka, and Snowflake, but not Golang or D… | Familiarity with our stack, including Golang, Python, SQL, frameworks such as dbt, and technologies like Spark, Kafka, … | insufficient | supported | The posting does list stack familiarity under 'While it's not required, it's an added plus', but it contains … |

## 2. Data Engineer (ashby:snowflake)
`ashby:snowflake:1af751fb-d53e-43b0-a3bc-6fcc4004cafb` · https://jobs.ashbyhq.com/snowflake/1af751fb-d53e-43b0-a3bc-6fcc4004cafb

- answer with the checker's labels: **relevant** (A2: both core claims are supported by quoted text)
- answer with my labels (E4, in force): **relevant** (A2: both core claims are supported by quoted text)

| # | kind | claim | quote | checker | mine | checker's reason |
|---|---|---|---|---|---|---|
| 8 | core_work | The posting says the main work is building and maintaining production data pipelines and models on Snowflake, from ingestion through transformation and consump… | Build and maintain production data pipelines and models on Snowflake, from ingestion through transformation and consump… | supported | supported | This is the first bullet under 'AS A DATA ENGINEER AT SNOWFLAKE, YOU WILL:', which describes the role's day-t… |
| 9 | level | The posting asks for 3+ years of hands-on production data pipeline or data model experience. It does not mention people management. | 3+ years of hands-on experience building data pipelines or data models in a production environment | supported | supported | The qualifications list states 3+ years of hands-on production pipeline or model experience, and the posting … |
| 10 | employment | The posting lists the employment type as full-time. | employment type: FullTime | supported | supported | The posting states 'employment type: FullTime'. |
| 11 | has | The posting requires working knowledge of dbt and an orchestration tool such as Apache Airflow. The résumé lists both dbt and Airflow. | Working knowledge of dbt and an orchestration tool such as Apache Airflow | insufficient | supported | The posting does list working knowledge of dbt and an orchestration tool like Airflow as a qualification, but… |
| 12 | has | The posting requires hands-on experience with a cloud data warehouse, ideally Snowflake. The résumé shows dbt and SQL work in Snowflake. | Hands-on experience with a cloud data warehouse, ideally Snowflake | insufficient | supported | The posting does list hands-on cloud data warehouse experience, ideally Snowflake, but no résumé is provided,… |
| 13 | has | The posting requires strong SQL and working Python skills. The résumé lists both SQL and Python. | Strong SQL and working Python skills, including basic query tuning and schema design | insufficient | supported | The posting does list strong SQL and working Python skills, but no résumé is provided, so the claim that the … |
| 14 | lacks | The posting requires an understanding of dimensional modelling concepts. The résumé does not explicitly mention dimensional modelling. | Understanding of dimensional modelling concepts | insufficient | supported | The posting does list an understanding of dimensional modelling concepts, but no résumé is provided, so the c… |

## 3. Backend Engineer - Data Platform (lever:spotify)
`lever:spotify:186b763a-2a61-4563-8813-ff6b40c9c8a7` · https://jobs.lever.co/spotify/186b763a-2a61-4563-8813-ff6b40c9c8a7

- answer with the checker's labels: **cannot_tell** (A2: core claim 'level' is not supported by the posting text)
- answer with my labels (E4, in force): **relevant** (A2: both core claims are supported by quoted text)

| # | kind | claim | quote | checker | mine | checker's reason |
|---|---|---|---|---|---|---|
| 15 | core_work | The posting says the main work is backend engineering for data management: building and operating the services and APIs behind the data catalog, lineage and pu… | Design, build and operate the backend services and APIs behind our data catalog, lineage and publishing systems | supported | supported | Under 'What You'll Do', the posting says the role will design, build and operate the backend services and API… |
| 16 | level | The posting does not say how many years of experience are required, what seniority level the role is, or whether it involves managing people. | *(no quote)* | insufficient | supported | E3: no quote |
| 17 | employment | The posting lists the employment type as permanent. It does not explicitly say full-time. | employment type: Permanent | supported | supported | The posting gives the employment type as 'Permanent' and never mentions full-time or part-time. |
| 18 | lacks | The posting requires solid experience building and running production backend services and APIs in Java. The résumé lists Python, SQL, Spark, Airflow, Kafka, d… | You have solid experience building and running backend services and APIs in production with Java | supported | supported | The 'Who You Are' section states that candidates have solid experience building and running production backen… |
| 19 | has | The posting asks for comfort with SQL and experience with data pipelines or a cloud data warehouse such as Snowflake. The résumé shows SQL, pipeline building, … | You're comfortable with SQL and have worked with data pipelines or a cloud data warehouse such as BigQuery, Snowflake o… | supported | supported | The posting asks for comfort with SQL and experience with data pipelines or a cloud data warehouse, and it na… |
| 20 | has | The posting lists hands-on experience with batch or streaming frameworks such as Spark as a plus. The résumé shows Spark batch and streaming pipelines. | Hands-on experience with batch or streaming frameworks like Beam, Flink or Spark is a plus. | supported | supported | The posting calls hands-on experience with Beam, Flink or Spark 'a plus', which matches the claim; the résumé… |
| 21 | lacks | The posting says the role is based in Stockholm or London. The résumé lists only US locations and says the job seeker needs sponsorship. | This role is based in Stockholm or London. | supported | supported | The posting states that the role is based in Stockholm or London; the résumé and sponsorship details cannot b… |

## 4. Senior Solution Engineer (ashby:snowflake)
`ashby:snowflake:a040adc3-9592-49cb-84db-27fcc8ede438` · https://jobs.ashbyhq.com/snowflake/a040adc3-9592-49cb-84db-27fcc8ede438

- answer with the checker's labels: **relevant** (A2: both core claims are supported by quoted text)
- answer with my labels (E4, in force): **relevant** (A2: both core claims are supported by quoted text)

| # | kind | claim | quote | checker | mine | checker's reason |
|---|---|---|---|---|---|---|
| 22 | core_work | The posting says the main work is pre-sales solution engineering: working with the sales team and channel partners to understand customers' data challenges, de… | work directly with the sales team and channel partners to understand the data challenges of our customers | supported | supported | The role description says the person will work directly with the sales team and channel partners to understan… |
| 23 | level | The posting says the role is senior and requires 7–8 years of industry experience, including at least 5 years in pre-sales or solutions architecture focused on… | 7–8 years of industry experience, with a minimum of 5 years in a pre-sales or solutions architecture role focused on da… | supported | supported | The title is Senior Solution Engineer, the day-one requirements state 7–8 years of industry experience with a… |
| 24 | employment | The posting says the role is full-time. | employment type: FullTime | supported | supported | The posting lists the employment type as FullTime. |
| 25 | lacks | The posting requires at least 5 years in a pre-sales or solutions architecture role focused on data platforms. The résumé shows only data engineering roles and… | a minimum of 5 years in a pre-sales or solutions architecture role focused on data platforms | supported | supported | The day-one requirements state a minimum of 5 years in a pre-sales or solutions architecture role focused on … |
| 26 | lacks | The posting requires 7–8 years of industry experience. The résumé shows about 5 years (2019-07 to 2024-08). | 7–8 years of industry experience | supported | supported | The day-one requirements state 7–8 years of industry experience; the résumé part cannot be checked against th… |
| 27 | has | The posting requires broad experience with the modern data stack, including dbt, Spark, Kafka, and Airflow. The résumé lists dbt, Spark, Kafka, Airflow, and AW… | ETL/ELT tools (dbt, Fivetran, Informatica, Spark), streaming platforms (Kafka, Kinesis), orchestration (Airflow, dbt Cl… | supported | supported | The day-one requirements list broad modern data stack experience, including dbt, Spark, Kafka, and Airflow; t… |
| 28 | has | The posting requires a university degree in data science or a related field. The résumé shows a completed M.S. in Data Science. | University degree in computer science, data science, engineering, mathematics or a related field | contradicted | supported | The posting accepts equivalent practical experience in place of a degree, so a degree is not strictly require… |

## 5. Senior Solution Engineer (ashby:snowflake)
`ashby:snowflake:a2c9754a-80d0-45fe-82a5-3f272c44c24e` · https://jobs.ashbyhq.com/snowflake/a2c9754a-80d0-45fe-82a5-3f272c44c24e

- answer with the checker's labels: **relevant** (A2: both core claims are supported by quoted text)
- answer with my labels (E4, in force): **relevant** (A2: both core claims are supported by quoted text)

| # | kind | claim | quote | checker | mine | checker's reason |
|---|---|---|---|---|---|---|
| 29 | core_work | The posting says the main work is working with the sales team and channel partners to understand customers' data challenges, deliver data-driven demonstrations… | work directly with the sales team and channel partners to understand the data challenges of our customers | supported | supported | The 'In this role you will' sentence says the role works with sales and channel partners to understand custom… |
| 30 | level | The posting says the role is senior and asks for 3–8 years of industry experience in a pre-sales or solutions architecture role. It does not mention managing p… | 3–8 years of industry experience, in a pre-sales or solutions architecture role focused on data platforms | supported | supported | The title is Senior Solution Engineer, the day-one requirements list 3–8 years of pre-sales or solutions arch… |
| 31 | employment | The posting says the role is full-time. | employment type: FullTime | supported | supported | The posting lists 'employment type: FullTime'. |
| 32 | lacks | The posting requires experience in a pre-sales or solutions architecture role. The résumé shows only data engineering roles, with no pre-sales or solutions arc… | in a pre-sales or solutions architecture role focused on data platforms | supported | supported | The day-one requirements state 3–8 years of experience in a pre-sales or solutions architecture role; the rés… |
| 33 | lacks | The posting requires the candidate to be located in North Carolina or South Carolina. Neither state is among the résumé's listed locations. | Location Requirement: Must be in North Carolina or South Carolina. | supported | supported | The posting states 'Location Requirement: Must be in North Carolina or South Carolina.'; the résumé part of t… |
| 34 | has | The posting requires deep hands-on expertise with SQL, Python, and cloud data warehouse architectures. The résumé lists SQL, Python, and Snowflake work. | Deep hands-on expertise with SQL, Python, and cloud data warehouse / data lakehouse architectures | supported | supported | The day-one requirements include deep hands-on expertise with SQL, Python, and cloud data warehouse / data la… |
| 35 | has | The posting requires broad modern data stack experience, including ETL/ELT tools such as dbt and Spark, streaming such as Kafka, and orchestration such as Airf… | ETL/ELT tools (dbt, Fivetran, Informatica, Spark), streaming platforms (Kafka, Kinesis), orchestration (Airflow, dbt Cl… | supported | supported | The day-one requirements include broad modern data stack experience naming dbt, Spark, Kafka, and Airflow; th… |

## 6. Technical Architect (ashby:snowflake)
`ashby:snowflake:8ca0b89c-45ee-4891-8db0-c7588661986c` · https://jobs.ashbyhq.com/snowflake/8ca0b89c-45ee-4891-8db0-c7588661986c

- answer with the checker's labels: **relevant** (A2: both core claims are supported by quoted text)
- answer with my labels (E4, in force): **relevant** (A2: both core claims are supported by quoted text)

| # | kind | claim | quote | checker | mine | checker's reason |
|---|---|---|---|---|---|---|
| 36 | core_work | The posting says the main work is working hands-on with customer and partner teams to design, build, and launch Snowflake data solutions. | work hands-on with customer and partner teams to design, build, and launch data solutions that solve real business prob… | supported | supported | The role description says the Technical Architect will work hands-on with customer and partner teams to desig… |
| 37 | level | The posting asks for 5+ years in a customer-facing technical role and 8+ years of overall technology experience. It does not mention people management. | 5+ years of experience in a customer-facing technical role such as consulting, data engineering, or solutions architect… | supported | supported | The qualifications state 5+ years in a customer-facing technical role with 8+ years of overall technology exp… |
| 38 | employment | The posting says the role is full-time. | employment type: FullTime | supported | supported | The posting lists the employment type as FullTime. |
| 39 | lacks | The posting requires 8+ years of overall technology experience. The résumé shows about 5 years (2019-07 to 2024-08). | With 8+ years of overall Technology experience | supported | supported | The ideal-candidate requirements list 8+ years of overall technology experience; the résumé detail cannot be … |
| 40 | lacks | The posting says the role is based in Singapore. The résumé lists only US locations and says the job seeker needs sponsorship. | As a Technical Architect based in Singapore | supported | supported | The posting states the role is based in Singapore (Location: SG-Singapore); the résumé and sponsorship detail… |
| 41 | has | The posting requires strong hands-on SQL and Python skills. The résumé lists both and shows pipeline work in Python and SQL. | Strong hands-on skills in SQL and Python building data intensive use cases | supported | supported | The ideal-candidate requirements list strong hands-on skills in SQL and Python; the résumé detail cannot be c… |
| 42 | has | The posting requires experience with ETL/ELT and orchestration tools such as dbt or Airflow. The résumé shows both dbt and Airflow. | Experience with ETL/ELT and orchestration tools such as dbt, Informatica, Matillion, Fivetran, or Airflow | supported | supported | The ideal-candidate requirements list experience with ETL/ELT and orchestration tools including dbt and Airfl… |

## 7. Data & Integration Engineer, Business Systems (greenhouse:figma)
`greenhouse:figma:6233040004` · https://boards.greenhouse.io/figma/jobs/6233040004?gh_jid=6233040004

- answer with the checker's labels: **relevant** (A2: both core claims are supported by quoted text)
- answer with my labels (E4, in force): **relevant** (A2: both core claims are supported by quoted text)

| # | kind | claim | quote | checker | mine | checker's reason |
|---|---|---|---|---|---|---|
| 43 | core_work | The posting says the main work is building reliable integrations and data pipelines across business systems such as Salesforce, NetSuite, Workday, and Snowflak… | We partner with teams across Finance, GTM, People, and Engineering to build reliable integrations and data pipelines ac… | supported | supported | The quote describes the Integration Engineering team this role joins, and the duties list confirms the role d… |
| 44 | level | The posting asks for 5+ years of relevant engineering experience covering both enterprise integrations and production data pipelines. | 5+ years of relevant engineering experience, including hands-on delivery of both enterprise integrations and production… | supported | supported | This item is in the main qualifications list, which is set apart from the 'not required' plus list, and it st… |
| 45 | employment | The posting says this is a full-time role, held from a US hub or remotely in the United States. | This is a full time role that can be held from one of our US hubs or remotely in the United States. | supported | supported | The posting states the role is full time and can be held from a US hub or remotely in the United States. |
| 46 | has | The posting requires experience with Snowflake or a comparable cloud data warehouse, including data modeling. The résumé lists Snowflake and building dbt model… | Experience with Snowflake or a comparable cloud data warehouse, including data modeling, incremental processing, and qu… | supported | supported | The main qualifications list asks for experience with Snowflake or a comparable cloud data warehouse, includi… |
| 47 | has | The posting requires hands-on proficiency in query languages and programming for data transformation and pipelines. The résumé lists SQL and Python used for pi… | Hands-on proficiency in query languages and programming for data transformation, pipeline development, and automation | supported | supported | The main qualifications list asks for hands-on proficiency in query languages and programming for data transf… |
| 48 | lacks | The posting requires strong experience building and supporting API-led integrations. The résumé shows data pipeline work but no API or enterprise application i… | Strong experience building and supporting API-led integrations, with an understanding of API design, authentication, as… | supported | supported | The main qualifications list asks for strong experience building and supporting API-led integrations; the rés… |

## 8. Data Platform Engineer (greenhouse:figma)
`greenhouse:figma:6201407004` · https://boards.greenhouse.io/figma/jobs/6201407004?gh_jid=6201407004

- answer with the checker's labels: **relevant** (A2: both core claims are supported by quoted text)
- answer with my labels (E4, in force): **relevant** (A2: both core claims are supported by quoted text)

| # | kind | claim | quote | checker | mine | checker's reason |
|---|---|---|---|---|---|---|
| 49 | core_work | The posting says the main work is building and evolving the shared data platform that powers analytics, Data Science, and data-driven product development. | Build and evolve the shared data platform that powers analytics, Data Science, and data-driven product development at F… | supported | supported | The quote is the first bullet under 'What you'll do at Figma', which describes the role's day-to-day work. |
| 50 | level | The posting asks for 5+ years of experience building and operating production data platforms, developer infrastructure, or distributed systems. It does not men… | 5+ years of experience building and operating production data platforms, developer infrastructure, or distributed syste… | supported | supported | The qualifications list asks for exactly this experience, and nothing in the posting mentions people manageme… |
| 51 | employment | The posting says this is a full-time role, held from a US hub or remotely in the United States. | This is a full-time role that can be held from one of our US hubs or remotely in the United States. | supported | supported | The posting says the role is full-time and can be held from a US hub or remotely in the United States. |
| 52 | has | The posting requires 5+ years of experience building and operating production data platforms. The résumé shows about 5 years of data engineering work (2019-07 … | 5+ years of experience building and operating production data platforms | insufficient | supported | The posting lists 5+ years under 'We'd love to hear from you if you have', but it contains no résumé, so the … |
| 53 | has | The posting requires strong software engineering skills in Python or similar. The résumé lists Python and Python pipeline work. | Strong software engineering skills (Python or similar), with experience designing reliable and scalable systems | insufficient | supported | The posting lists strong Python or similar skills as a desired qualification, but the résumé content the clai… |
| 54 | has | The posting asks for experience with cloud data warehouses, transformation frameworks, and workflow orchestrators. The résumé lists Snowflake, dbt, and Airflow. | cloud data warehouses, transformation frameworks, workflow orchestrators | insufficient | supported | The posting does name cloud data warehouses, transformation frameworks, and workflow orchestrators, but the c… |
| 55 | lacks | The posting asks for experience with infrastructure as code and observability tools. The résumé does not list either. | infrastructure as code, and observability tools | insufficient | supported | The posting does mention infrastructure as code and observability tools, but whether the résumé lists them ca… |

## 9. Backend Engineer - Data Platform (lever:spotify)
`lever:spotify:926149ab-6999-4058-b35d-41e302b70e05` · https://jobs.lever.co/spotify/926149ab-6999-4058-b35d-41e302b70e05

- answer with the checker's labels: **relevant** (A2: both core claims are supported by quoted text)
- answer with my labels (E4, in force): **relevant** (A2: both core claims are supported by quoted text)

| # | kind | claim | quote | checker | mine | checker's reason |
|---|---|---|---|---|---|---|
| 56 | core_work | The posting says the main work is building the foundations of an Iceberg-based lakehouse, migrating pipelines onto it, and owning BigQuery operations at Spotif… | Help build the foundations that let data workflows read and write Iceberg tables directly | supported | supported | The quoted sentence and the surrounding 'What You'll Do' section describe building the Iceberg lakehouse foun… |
| 57 | level | The posting does not state a number of years, a seniority title, or people management. It asks only for solid experience building and operating production back… | You have solid experience building and operating backend services in production with Java or Scala. | supported | supported | The quote asks for solid production backend experience, and the posting states no year count, seniority title… |
| 58 | employment | The posting lists the employment type as Permanent. It does not explicitly say full-time or part-time. | employment type: Permanent | supported | supported | The posting lists 'employment type: Permanent' and never says full-time or part-time. |
| 59 | lacks | The posting requires production backend experience in Java or Scala. The résumé lists Python and SQL but neither Java nor Scala. | You have solid experience building and operating backend services in production with Java or Scala. | insufficient | supported | The posting does require production backend experience in Java or Scala, but it contains no résumé, so the ré… |
| 60 | lacks | The posting requires comfort with GCP and Kubernetes. The résumé lists AWS but not GCP or Kubernetes. | You're comfortable on GCP and Kubernetes. | insufficient | supported | The posting does ask for comfort on GCP and Kubernetes, but it contains no résumé, so the résumé part cannot … |
| 61 | has | The posting asks for experience with Spark or a cloud data warehouse such as Snowflake. The résumé lists both Spark and Snowflake. | You've worked with Apache Iceberg or JVM-based processing frameworks like Spark, Beam or Flink, or with a cloud data wa… | insufficient | supported | The posting does list Spark or a warehouse like Snowflake among acceptable experience, but it contains no rés… |
| 62 | lacks | The posting says the role is based in London or Stockholm. The résumé lists only US locations and Remote (US). | This role is based in London or Stockholm. | insufficient | supported | The posting does say the role is based in London or Stockholm, but it contains no résumé, so the résumé part … |

## 10. Software Engineer - SnowConvert AI (ashby:snowflake)
`ashby:snowflake:2a928b93-a5d4-4285-a92c-032fb389faa2` · https://jobs.ashbyhq.com/snowflake/2a928b93-a5d4-4285-a92c-032fb389faa2

- answer with the checker's labels: **cannot_tell** (A2: core claim 'level' is not supported by the posting text)
- answer with my labels (E4, in force): **relevant** (A2: both core claims are supported by quoted text)

| # | kind | claim | quote | checker | mine | checker's reason |
|---|---|---|---|---|---|---|
| 63 | core_work | The posting says the main work is building the code conversion foundations that AI agents use to migrate applications to Snowflake. | Develop the foundations that AI agents rely on for fast, consistent code conversion | supported | supported | The responsibilities say to 'Develop the foundations that AI agents rely on for fast, consistent code convers… |
| 64 | level | The posting does not say how many years of experience are required, what seniority level the role is, or whether it involves people management. | *(no quote)* | insufficient | supported | E3: no quote |
| 65 | employment | The posting says the role is full-time. | employment type: FullTime | supported | supported | The posting states 'employment type: FullTime'. |
| 66 | lacks | The posting asks for hands-on experience building agentic AI applications, and the résumé does not show this. | Hands-on experience building agentic AI applications, especially in domains such as computer control or code gen. | insufficient | supported | The posting does list agentic AI experience under the ideal candidate, but it contains no résumé, so it canno… |
| 67 | lacks | The posting asks for contributions to open-source agentic frameworks such as LangChain or AutoGen, and the résumé does not show this. | Track record of contributions to open-source agentic frameworks such as LangChain, AutoGen, etc. | insufficient | supported | The posting does list open-source agentic framework contributions under the ideal candidate, but it contains … |
| 68 | has | The posting strongly desires proficiency in Spark, Airflow, dbt, or Kafka, and the résumé lists all four. | Proficiency in Spark, Airflow, dbt, Kafka or other data engineering tools. | insufficient | supported | The posting does list Spark, Airflow, dbt, or Kafka under 'Strongly desired', but it contains no résumé, so i… |
| 69 | has | The posting strongly desires an understanding of ETL and ELT pipelines, and the résumé shows building pipelines and maintaining ETL jobs. | Strong understanding of big data transformation, ETL, and ELT pipelines. | insufficient | supported | The posting does list ETL/ELT understanding under 'Strongly desired', but it contains no résumé, so it cannot… |

