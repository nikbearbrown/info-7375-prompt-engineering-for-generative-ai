# Audit report: filter v1.0 vs my hand labels (heldout sets)

Sample drawn with seed 20261124 from the v1.0 verdicts (FILTER.md section 5). A posting counts as an error when keep != (hand label == relevant).

- **heldout_reject**: labeled 15/15; wrong 6/15 = 40% (95% CI 16%–68%); kept under v1.0: 0
- **heldout_kept_or_close**: labeled 15/15; wrong 10/15 = 67% (95% CI 38%–88%); kept under v1.0: 4

## Every disagreement, with the words that moved the score

### [heldout_reject] Sr Product Marketing Manager, Media, Entertainment and Advertising (ashby:snowflake)
- filter: **reject**, disqualified by title:Manager; [role 0 (none) + topics 1 (T4 orchestration) + skills 0 (none) = 1]
- my label: **relevant**: partial match
- id `ashby:snowflake:5220aae8-7fd1-4374-8b8f-4f27f8573791`
  - topic **T4 orchestration: orchestration**: "…ategy with execution. The successful candidate will thrive on program orchestration, enablement at scale, and surfacing regional insights to…"

### [heldout_reject] Senior Software Engineer - Elastic Global Services (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 0 (none) + skills 0 (none) = 0, below 6
- my label: **relevant**: candidate skills matches the skillset
- id `ashby:snowflake:829e9786-6661-4134-b7cd-aef3bed75c1c`

### [heldout_reject] Strategic Account Executive, Majors Acquisition (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T2 storage) + skills 0 (none) = 1, below 6
- my label: **relevant**: partial match
- id `ashby:snowflake:cdebc456-bb4f-4cc7-84fc-dccb8499a8f6`
  - topic **T2 storage: Data Warehousing**: "…mplex sales strategies and tactics within one of the following spaces Data Warehousing, Business Intelligence, Data Science and/or AI/ML   -…"

### [heldout_reject] Software Engineer - Distributed Systems (greenhouse:figma)
- filter: **reject**, role 0 (none) + topics 2 (T4 orchestration, T5 streaming) + skills 3 (Python, Kafka, AWS) = 5, below 6
- my label: **relevant**: skillset matches
- id `greenhouse:figma:5552549004`
  - topic **T4 orchestration: orchestration**: "… a variety of teams. Whether you’re passionate about storage, compute orchestration, developer tooling, networking, or real-time data system…"
  - topic **T5 streaming: streaming**: "…Architect and evolve distributed systems including storage platforms, streaming infrastructure, and compute orchestration Improve developer …"
  - skill **Python**: "…tainer orchestration Proficiency in languages such as Go, TypeScript, Python, Rust, or Ruby Strong system design skills and a track record o…"
  - skill **Kafka**: "…., Postgres, Redis, S3, DynamoDB) or operating streaming systems like Kafka Background in traffic management, DDoS mitigation, or service me…"
  - skill **AWS**: "…, and eventual convergence Experience with cloud-native environments (AWS, GCP, or Azure), infrastructure-as-code, and container orchestrati…"

### [heldout_reject] Account Executive, SMB (Berlin, Germany) (greenhouse:figma)
- filter: **reject**, role 0 (none) + topics 0 (none) + skills 0 (none) = 0, below 6
- my label: **relevant**: partial match
- id `greenhouse:figma:5985397004`

### [heldout_reject] Manager, Software Engineering - External Platform (greenhouse:figma)
- filter: **reject**, disqualified by title:Manager; [role 0 (none) + topics 0 (none) + skills 0 (none) = 0]
- my label: **relevant**: skillset matches
- id `greenhouse:figma:6224661004`

### [heldout_kept_or_close] Lead Forward Deployed Engineer - Migration (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 4 (T1 pipelines, T2 storage, T3 modeling, T7 quality) + skills 1 (Python) = 5, below 6
- my label: **relevant**: lot of skills matches
- id `ashby:snowflake:0f2d263b-37c1-4e5c-92b7-007818fbc0d5`
  - topic **T1 pipelines: data pipelines**: "…eporting/BI integration.   - Platform Implementation: Design scalable data pipelines and modern data architectures on Snowflake. Ensure data…"
  - topic **T2 storage: data warehousing**: "…loping AI/ML applications.   - Strong understanding of data modeling, data warehousing & data lake concepts, and cloud data platforms.   - A…"
  - topic **T3 modeling: data modeling**: "…ience with developing AI/ML applications.   - Strong understanding of data modeling, data warehousing & data lake concepts, and cloud data p…"
  - topic **T7 quality: data quality**: "…ble data pipelines and modern data architectures on Snowflake. Ensure data quality, integrity, and efficient processing within the customer'…"
  - skill **Python**: "…kills.   - Proficiency in programming and scripting languages such as Python, Go, Java or C++.   - Experience with developing AI/ML applicat…"

### [heldout_kept_or_close] Solution Engineer (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T4 orchestration) + skills 4 (Python, SQL, Spark, dbt) = 5, below 6
- my label: **relevant**: partial relevant
- id `ashby:snowflake:5a4332ce-2131-4d7b-b251-956d382fd3da`
  - topic **T4 orchestration: orchestration**: "… modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)   - Solution engineering/solution arch…"
  - skill **Python**: "…    Preferred (but not required) to have:  · Hands on experience with Python  · Experience with AI, data science and machine learning techno…"
  - skill **SQL**: "…ure, data analytics and cloud technology   - Hands on experience with SQL   - Ability to solve customer specific business problems and apply…"
  - skill **Spark**: "…o have:   - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)   -…"
  - skill **dbt**: "…you to have:   - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.…"

### [heldout_kept_or_close] Solution Engineer (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 2 (T1 pipelines, T2 storage) + skills 3 (Python, SQL, Spark) = 5, below 6
- my label: **relevant**: partial match
- id `ashby:snowflake:737e26ff-7ac1-493e-8385-868093ec4b78`
  - topic **T1 pipelines: ETL**: "… of experience within Large-scale Database/Data Warehouse technology, ETL, and modern AI/ML frameworks.   - Hands-on expertise with SQL and …"
  - topic **T2 storage: Data Warehouse**: "…ness value.   - Broad range of experience within Large-scale Database/Data Warehouse technology, ETL, and modern AI/ML frameworks.   - Hands…"
  - skill **Python**: "… AI/ML frameworks.   - Hands-on expertise with SQL and SQL analytics (Python or R experience for data science is a plus).   - The ability to…"
  - skill **SQL**: "…nology, ETL, and modern AI/ML frameworks.   - Hands-on expertise with SQL and SQL analytics (Python or R experience for data science is a pl…"
  - skill **Spark**: "…Microsoft Fabric, Cloudera, BigQuery, Analytics Open Source projects: Spark, Trino, Cassandra, Hive, among others.   - Outstanding presentin…"

### [heldout_kept_or_close] Commercial Solution Engineer - Expansion (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T4 orchestration) + skills 4 (Python, SQL, Spark, dbt) = 5, below 6
- my label: **relevant**: candidate skills matches with the required skillset
- id `ashby:snowflake:86e9ce4d-7288-43ac-8d62-45ea073a72d1`
  - topic **T4 orchestration: orchestration**: "… modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)    - Experience with data science and …"
  - skill **Python**: "…NOT REQUIRED) TO HAVE:   - Dutch-speaker   - Hands on experience with Python    - Experience working with modern data technology (e.g. dbt, …"
  - skill **SQL**: "…re, data analytics and cloud technology    - Hands on experience with SQL   - Ability to solve customer specific business problems and apply…"
  - skill **Spark**: "…Python    - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)    …"
  - skill **dbt**: "…with Python    - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.…"

### [heldout_kept_or_close] Senior Solution Engineer (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T4 orchestration) + skills 4 (Python, SQL, Spark, dbt) = 5, below 6
- my label: **relevant**: partial match
- id `ashby:snowflake:88d996f4-08db-407c-8859-ca7912e59fbc`
  - topic **T4 orchestration: orchestration**: "… modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)   - Experience with AI, data science a…"
  - skill **Python**: "…   PREFERRED (BUT NOT REQUIRED) TO HAVE:   - Hands on experience with Python   - Experience working with modern data technology (e.g. dbt, s…"
  - skill **SQL**: "…ure, data analytics and cloud technology   - Hands on experience with SQL   - Ability to solve customer specific business problems and apply…"
  - skill **Spark**: "… Python   - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)   -…"
  - skill **dbt**: "… with Python   - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.…"

### [heldout_kept_or_close] Technical Architect (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T1 pipelines) + skills 4 (Python, SQL, Spark, AWS) = 5, below 6
- my label: **relevant**: partial match
- id `ashby:snowflake:ccc6c304-07da-46cf-95da-877eed922e11`
  - topic **T1 pipelines: ETL**: "…らえ、自らプロジェクトの進め方を提案・推進できる能力   - 技術者層・経営層を問わず、優れたプレゼンテーションやデモを行える能力   - ETL からデータプラットフォームの設計、BI および分析ツールまでの完全なデータ分析スタックとワークフローの理解   - データベース、デ…"
  - skill **Python**: "…ータベース、データウェアハウス、データ処理に関する設計、実装スキル   - SQL および SQL アナリティクスの豊富な実務経験   - Python、Ruby、Perl、Bashなどのスクリプトの経験   - 顧客と現地で作業するための能力と柔軟性。必要に応じて出張が可能であ…"
  - skill **SQL**: "…ルまでの完全なデータ分析スタックとワークフローの理解   - データベース、データウェアハウス、データ処理に関する設計、実装スキル   - SQL および SQL アナリティクスの豊富な実務経験   - Python、Ruby、Perl、Bashなどのスクリプトの経験   - 顧…"
  - skill **Spark**: "…edshift, Netezza, Exadata, Teradata など）の知識と設計・実装の経験   - 大規模データ処理ツール（例：Spark, Hadoop, HBase）の経験と知識   - BIやデータ探索ツール（例: Tableau, Sigma, Qlik, O…"
  - skill **AWS**: "…）についての理解と経験   - カスタムおよびパッケージ化されたツールを使用したETLパイプラインの実装経験   - パブリッククラウド（ AWS, Microsoft Azure, Google Cloud Platformなど）を使用したシステムの設計・構築の経験と知識   …"

### [heldout_kept_or_close] Senior Solution Engineer - Acquisition (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T4 orchestration) + skills 4 (Python, SQL, Spark, dbt) = 5, below 6
- my label: **relevant**: partial match
- id `ashby:snowflake:db45108c-5665-487f-82f5-53f93126b6b2`
  - topic **T4 orchestration: orchestration**: "… modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)   - Experience with AI, data science a…"
  - skill **Python**: "…   PREFERRED (BUT NOT REQUIRED) TO HAVE:   - Hands on experience with Python   - Experience working with modern data technology (e.g. dbt, s…"
  - skill **SQL**: "…ure, data analytics and cloud technology   - Hands on experience with SQL   - Ability to solve customer specific business problems and apply…"
  - skill **Spark**: "… Python   - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.)   -…"
  - skill **dbt**: "… with Python   - Experience working with modern data technology (e.g. dbt, spark, containers, devops tooling, orchestration tools, git, etc.…"

### [heldout_kept_or_close] Solution Engineer - GCC (FSI) (ashby:snowflake)
- filter: **keep**, role 0 (none) + topics 3 (T1 pipelines, T2 storage, T3 modeling) + skills 3 (Python, SQL, AWS) = 6 >= 6
- my label: **not_relevant**: requires lots of work experience
- id `ashby:snowflake:dd74b9e7-ebed-4d23-94d0-1fbb4d90b180`
  - topic **T1 pipelines: ETL**: "…road range of skills and experience ranging from data architecture to ETL/ELT, data science, security, performance analysis, analytics, etc.…"
  - topic **T2 storage: data warehouse**: "…lent experience   - Strong competency on modern data stacks, ETL/ELT, data warehouse/lake, data science and data apps   - Outstanding skills…"
  - topic **T3 modeling: Data modeling**: "…ud Provider Experience -  Amazon AWS/Microsoft Azure/Google Cloud   - Data modeling and data architecture experience   - Experience selling …"
  - skill **Python**: "…or using presentations and demos.   - Hands-on expertise with SQL and Python   - Experience working with large global accounts, GSIs and/or …"
  - skill **SQL**: "…teboard or using presentations and demos.   - Hands-on expertise with SQL and Python   - Experience working with large global accounts, GSIs…"
  - skill **AWS**: "…leau, PowerBI, Metabase etc).   - Cloud Provider Experience -  Amazon AWS/Microsoft Azure/Google Cloud   - Data modeling and data architectu…"

### [heldout_kept_or_close] Data Engineering Solutions Specialist (ashby:snowflake)
- filter: **reject**, role 4 (Data Engineering) + topics 1 (T2 storage) + skills 0 (none) = 5, below 6
- my label: **relevant**: skillset matches
- id `ashby:snowflake:ecd08904-f188-4336-bf8c-f75f97df1a02`
  - role **Data Engineering**: title: "Data Engineering Solutions Specialist"
  - topic **T2 storage: Data Lake**: "… the successful customer adoption of Snowflake’s Data Engineering and Data Lake capabilities.  Responsibilities:   - Achieve pipeline genera…"

### [heldout_kept_or_close] Senior Solution Engineer, Partnerships - Brazil (ashby:snowflake)
- filter: **reject**, role 0 (none) + topics 1 (T1 pipelines) + skills 4 (SQL, Spark, Kafka, AWS) = 5, below 6
- my label: **relevant**: skillset matches
- id `ashby:snowflake:f5f6e36e-4e6f-49ec-938c-396d038b41e7`
  - topic **T1 pipelines: data pipelines**: "…ise in developing and deploying PySpark or Scala and SQL to build ELT/data pipelines into production environments. Staying current with the …"
  - skill **SQL**: "…l hands on expertise in developing and deploying PySpark or Scala and SQL to build ELT/data pipelines into production environments. Staying …"
  - skill **Spark**: "…pelines into production environments. Staying current with the latest Spark updates and best practices   - Hands on experience in designing …"
  - skill **Kafka**: "…in designing and building highly scalable data pipelines using Spark, Kafka to ingest data from various systems.   - Experience with integra…"
  - skill **AWS**: "… DevOps and CI/CD processes and tools, such as Azure DevOps, Jenkins, AWS CodePipeline, and Google Cloud Build   - Strong experience with ma…"

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
