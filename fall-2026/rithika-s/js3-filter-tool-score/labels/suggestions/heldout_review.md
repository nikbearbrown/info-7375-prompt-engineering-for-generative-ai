# heldout: Claude Code suggestions for review

AUTOMATED SUGGESTIONS, NOT REVIEWED BY A HUMAN. Each verdict below was proposed by Claude Code from the blind sheet text only, using labels/LABELING_RUBRIC.md (sha256 55829cfef808...). They become your verdicts only after you review them in the CSV.

Counts: relevant 3, not 19, unsure 2.

## Borderline cases (review these first)

- row 1 `1bb1f351-41a2-43a5-bac1-259859886cb3` Software Engineer, GTM Growth Engineering: **unsure** (medium). Applied-AI product engineering: relevant if the role means building LLM features (close to Priya's agent work), not if it is mostly GTM web product.
- row 2 `2b5e8e15-7952-4170-a927-2ad68e318ed6` Software Engineer, Database Systems: **not** (low). Infrastructure with a partial ML link: a reader who counts the RAG vector database as an ML data platform would say relevant.
- row 9 `d8b894e3-c399-4303-a708-3cef8ff5c1a2` Forward Deployed Engineer (FDE), Healthcare - SF: **not** (low). Customer-facing role with substantial ML deployment and evaluation work; LABELING_RULE.md says customer-facing is not, but the work is close to Priya's inference/eval experience.
- row 13 `2a931dd1-5002-47d1-a367-ec1a19ef7e9e` Forward Deployed Engineer (FDE), Healthcare - NYC: **not** (low). Should be decided the same way as row 9 (same role, different city).
- row 14 `823a05bf-33fb-4d94-9dd8-571723d27b1a` Software Engineer, Infrastructure - Core Experimentation : **not** (low). Experimentation/analytics platform with a partial ML-evaluation link; arguably a data platform that model work runs on.
- row 15 `7613aca3-9dd8-41cd-b114-06ef4de967a9` Software Engineer, Cooperative AI: **relevant** (medium). Applied LLM application engineering: relevant under the rubric's deploying/serving clause, but a strict model-building reading could say unsure.
- row 20 `8220836002` Staff Fullstack Engineer, Agentic Applications: **unsure** (medium). Agentic applications are close to Priya's LangGraph agent work, but the posting reads as fullstack internal tools; also check whether technical leader means manager.
- row 23 `8200692002` Staff Software Engineer - Ingestion: **relevant** (medium). Data platform versus ML: relevant only because LABELING_RULE.md counts data platforms and pipelines.
- row 24 `9ddb1bd1-3ee0-4350-88f7-3710057b8c93` Forward Deployed Engineer - Paris: **not** (low). Same question as rows 9 and 13: is forward-deployed model deployment customer-facing (not) or ML deployment (relevant)?

## All postings

### row 1: Software Engineer, GTM Growth Engineering

- id: `1bb1f351-41a2-43a5-bac1-259859886cb3` | board: openai | batch 1
- suggested verdict: **unsure** (confidence medium)
- CSV reason: AI-powered GTM product work not model building
- justification: The team builds AI-native products for go-to-market and marketing workflows; the text mixes product craft with applied AI, and the excerpt stops before saying whether the engineer builds or evaluates models or mainly builds product surfaces.
- evidence: "builds AI-native products and systems that help OpenAI's go-to-market and B2B marketing organizations" / "Our work combines product craft, applied AI, reliable systems, and thoughtful operational design."
- uncertainty: Excerpt cut mid-sentence at the role description; amount of hands-on LLM work unknown.

### row 2: Software Engineer, Database Systems

- id: `2b5e8e15-7952-4170-a927-2ad68e318ed6` | board: openai | batch 1
- suggested verdict: **not** (confidence low)
- CSV reason: core C++ database engine work
- justification: The main work is the core distributed database engine (C++, query execution, indexing); the database does serve vector search and RAG, but the shown role is database-engine engineering rather than ML or data-pipeline building.
- evidence: "our core engine is written in C++" / "you'll contribute to the core database engine, driving improvements across ingestion, query execution, indexin" / "vector database that powers all vector search and retrieval augmented generation (RAG) at OpenAI"
- uncertainty: The rubric counts data platforms ML runs on; a vector database for RAG could be read that way.

### row 3: AI Support Engineer, Government - San Francisco, CA

- id: `48993416-b5f5-4c3f-b7c8-b8ca7c2395e0` | board: openai | batch 1
- suggested verdict: **not** (confidence high)
- CSV reason: customer support role
- justification: Sits in User Operations and resolves customer issues and adoption questions; this is a customer-facing support role, not ML building.
- evidence: "OpenAI’s User Operations team shepherds our customers’ adoption of AI" / "We resolve complex issues, provide technical guidance, and support customers"
- uncertainty: none; no clearance is mentioned in the excerpt, so the Government label played no part.

### row 4: Account Director, Manufacturing- Tokyo

- id: `772faf37-f0a0-4ea2-9f94-f9ea2c4a8914` | board: openai | batch 1
- suggested verdict: **not** (confidence high)
- CSV reason: sales account role
- justification: An account director on the Go To Market sales team helping customers adopt products; sales, not engineering.
- evidence: "Our Sales team has a unique mission to help customers understand the deep impact"
- uncertainty: none

### row 5: Operations Analyst, User Safety & Risk Operations

- id: `daabc150-f22c-421e-b30d-1a50fb4cede3` | board: openai | batch 1
- suggested verdict: **not** (confidence high)
- CSV reason: safety operations analyst
- justification: A senior operations analyst turning abuse and fraud risks into operational processes; operations work with no model or pipeline building described.
- evidence: "We are seeking a Senior Operations Analyst to take on complex, ambiguous safety and risk problems"
- uncertainty: none

### row 6: Head of Finance - Data Centers

- id: `144b12f3-5821-4727-a266-b5ed9ff46fd2` | board: openai | batch 1
- suggested verdict: **not** (confidence high)
- CSV reason: finance leadership role
- justification: Finance leader for data center investments: budgets, capital forecasting and investment cases. Finance and a head-of role.
- evidence: "you will be the finance leader for OpenAI’s self-built data center efforts" / "forecasting capital needs, managing construction budgets"
- uncertainty: none

### row 7: Android Engineer, Applied Foundations 

- id: `6202038a-323b-43ce-ae10-534acba4145c` | board: openai | batch 1
- suggested verdict: **not** (confidence high)
- CSV reason: Android mobile product engineering
- justification: Senior Android engineer building sign-up, account, payments and safety flows in the mobile apps; mobile product work, not ML.
- evidence: "building the core mobile experiences that power how users sign up, manage their account, family features, pay for services"
- uncertainty: none

### row 8: Staff Software Engineer - Security Infrastructure

- id: `7994759002` | board: databricks | batch 1
- suggested verdict: **not** (confidence medium)
- CSV reason: security infrastructure engineering
- justification: Title places the role in security infrastructure under Trust & Safety; the excerpt is company boilerplate and mentions the ML platform only as the product being secured.
- evidence: "Staff Software Engineer - Security Infrastructure" / "Trust & Safety has the mission to build the most trusted data analytics and ML platform"
- uncertainty: Excerpt ends before the role's duties, so the verdict rests mainly on the title.

### row 9: Forward Deployed Engineer (FDE), Healthcare - SF

- id: `d8b894e3-c399-4303-a708-3cef8ff5c1a2` | board: openai | batch 2
- suggested verdict: **not** (confidence low)
- CSV reason: forward-deployed customer role
- justification: The rubric puts forward-deployed roles under customer-facing, and this one is built around healthcare customer engagements; but the shown duties are hands-on model deployment, evaluation and productionization, so it is a close call.
- evidence: "partners with healthcare organizations to deploy production AI systems" / "to own end-to-end deployments of our models within healthcare organizations" / "implementation, evaluation, productionization, and handoff"
- uncertainty: How much of the job is building versus customer discovery and handoff is not stated in the excerpt.

### row 10: Senior Solutions Architect - Digital Natives

- id: `8905967002` | board: databricks | batch 2
- suggested verdict: **not** (confidence high)
- CSV reason: solutions architect customer role
- justification: A solutions architect owning executive relationships and consumption strategy for complex customer engagements; customer-facing technical sales.
- evidence: "responsible for the organisation's most complex customer engagements" / "You drive consumption strategy, own executive-level relationships"
- uncertainty: none

### row 11: Delivery Solutions Architect - Public Sector (DOW, DHS, Intelligence Community)

- id: `8899462002` | board: databricks | batch 2
- suggested verdict: **not** (confidence high)
- CSV reason: customer delivery architect role
- justification: Works with sales and field engineering to grow customers' platform usage; customer-facing delivery role. The posting also requires access to classified information.
- evidence: "You will collaborate with our sales and field engineering teams to accelerate the adoption and growth of the Databricks Platform" / "U.S. citizenship is required to access classified information"
- uncertainty: The excerpt never uses the word clearance; the not verdict stands on the customer-facing role alone.

### row 12: Systems Software Engineer, BMC & Management Plane

- id: `21229750-8bd1-4134-a20e-2a8922b88806` | board: openai | batch 2
- suggested verdict: **not** (confidence high)
- CSV reason: embedded hardware management software
- justification: BMC firmware and embedded Linux services that monitor server and accelerator hardware; hardware systems software, even though the hardware serves AI workloads.
- evidence: "with a focus on BMC software and embedded Linux services for server and accelerator manageability" / "software that monitors hardware health"
- uncertainty: none

### row 13: Forward Deployed Engineer (FDE), Healthcare - NYC

- id: `2a931dd1-5002-47d1-a367-ec1a19ef7e9e` | board: openai | batch 2
- suggested verdict: **not** (confidence low)
- CSV reason: forward-deployed customer role
- justification: Same NYC-based healthcare FDE role as the SF posting: the job is defined by customer deployments with payers and providers, which the rubric counts as customer-facing, while still involving real model evaluation and productionization.
- evidence: "own end-to-end deployments of our models within healthcare organizations, including payers, providers, health systems" / "You will lead technical discovery, architecture, implementation, evaluation, productionization"
- uncertainty: Text is nearly identical to row 9; the split between building and client work is not given.

### row 14: Software Engineer, Infrastructure - Core Experimentation 

- id: `823a05bf-33fb-4d94-9dd8-571723d27b1a` | board: openai | batch 2
- suggested verdict: **not** (confidence low)
- CSV reason: product experimentation infrastructure
- justification: The Statsig team builds experimentation, rollout, feature-config and analytics infrastructure for every product; model changes are one of many things it evaluates, so the main work reads as product-experimentation infrastructure rather than ML.
- evidence: "owns the experimentation, rollout, dynamic configuration, and analytics infrastructure" / "evaluate product and model changes in production"
- uncertainty: Priya's resume includes an A/B framework for LLM evaluation, which this platform resembles; the excerpt ends before the role's own duties.

### row 15: Software Engineer, Cooperative AI

- id: `7613aca3-9dd8-41cd-b114-06ef4de967a9` | board: openai | batch 2
- suggested verdict: **relevant** (confidence medium)
- CSV reason: builds AI-powered knowledge system
- justification: The team builds an AI-powered knowledge system on top of OpenAI's models to automate operations; that is LLM application building, the closest match to Priya's agent and routing work.
- evidence: "We are building an AI powered knowledge system that evolves and learns" / "We leverage our state of the art models, technologies, and products"
- uncertainty: It is applied LLM systems work rather than training models, and the excerpt does not list the engineer's own tasks.

### row 16: Revenue Operations Manager

- id: `4740043005` | board: scaleai | batch 2
- suggested verdict: **not** (confidence high)
- CSV reason: revenue operations role
- justification: Owns go-to-market measurement and pipeline diagnosis; explicitly individual-contributor, but revenue operations, not engineering.
- evidence: "you will own the measurement layer of our go-to-market engine" / "This is an individual contributor role with a wide mandate"
- uncertainty: none

### row 17: Data Scientist, Ads Demand

- id: `1eb32675-b1a0-4c0a-9b57-19ceab07e9e0` | board: openai | batch 3
- suggested verdict: **not** (confidence high)
- CSV reason: ads measurement and analytics
- justification: Defines metrics, benchmarks and diagnostic frameworks for ads demand with sales and product leadership; analysis and measurement, with no model or pipeline building shown.
- evidence: "you will build the measurement and insight foundation for understanding demand health" / "Define the North Star metrics, diagnostic framework, and measurement strategy"
- uncertainty: none

### row 18: Financial Systems Engineer

- id: `ac43a452-1f50-42a2-816e-f920fdb51823` | board: openai | batch 3
- suggested verdict: **not** (confidence high)
- CSV reason: Oracle finance systems engineering
- justification: Builds Oracle Fusion financial systems and accounting integrations; requires Oracle Financials and accounting process knowledge, unrelated to ML.
- evidence: "support critical accounting processes across Oracle Fusion Cloud" / "This role requires deep Oracle Financials expertise"
- uncertainty: none

### row 19: Software Engineer, Platform Systems

- id: `5e4ed6d1-2417-4bf5-bae0-905931c488e3` | board: openai | batch 3
- suggested verdict: **relevant** (confidence high)
- CSV reason: model training infrastructure
- justification: The team writes the core model training software and infrastructure for training flagship models on large supercomputers; ML infrastructure is the main work.
- evidence: "We build the engineering and research infrastructure required to train OpenAI’s flagship models" / "Our team develops core model training software"
- uncertainty: Deep distributed-systems work (collective communication, parallelism) is a stretch from Priya's experience, but fit level is not a rubric criterion.

### row 20: Staff Fullstack Engineer, Agentic Applications

- id: `8220836002` | board: databricks | batch 3
- suggested verdict: **unsure** (confidence medium)
- CSV reason: internal AI apps with fullstack focus
- justification: Builds internal end-to-end applications with AI-powered capabilities for running the business; the title says fullstack and the excerpt is about roadmap and tech leadership, so it is unclear whether agent/LLM building is the main work.
- evidence: "build resilient, in-house platforms and AI-powered capabilities" / "delivering end-to-end applications that power our business"
- uncertainty: The excerpt ends at a tech-lead sentence; it says the person is technical leader for a team of software engineers, which may or may not mean people management.

### row 21: Sr Staff Technical Program Manager- Security

- id: `8818577002` | board: databricks | batch 3
- suggested verdict: **not** (confidence high)
- CSV reason: security program management
- justification: A technical program manager running company-wide security programs; program management, not ML engineering.
- evidence: "We are seeking a Senior Staff Technical Program Manager to own and lead a company-wide portfolio of security programs"
- uncertainty: none

### row 22: Contracts Manager

- id: `4745295005` | board: scaleai | batch 3
- suggested verdict: **not** (confidence high)
- CSV reason: legal contracts role
- justification: Reviews, drafts and negotiates agreements as part of the legal team; legal work.
- evidence: "the legal department by working closely with business and legal teams to review, draft, and negotiate agreements"
- uncertainty: none

### row 23: Staff Software Engineer - Ingestion

- id: `8200692002` | board: databricks | batch 3
- suggested verdict: **relevant** (confidence medium)
- CSV reason: data ingestion platform engineering
- justification: Builds Lakeflow Connect ingestion connectors that bring data into the Lakehouse for data and AI workflows; data-platform pipeline engineering, which the rule counts.
- evidence: "Ingesting data into the Lakehouse is a strategic area of investment for Databricks and a key enabler for Data and AI workflows" / "providing ready-to-use, point-and-click connectors"
- uncertainty: Connector work may be closer to product integration engineering than ML; the excerpt stops before the engineer's duties.

### row 24: Forward Deployed Engineer - Paris

- id: `9ddb1bd1-3ee0-4350-88f7-3710057b8c93` | board: openai | batch 3
- suggested verdict: **not** (confidence low)
- CSV reason: forward-deployed customer role
- justification: A Paris FDE leading frontier-model deployments alongside strategic customers and partnering directly with their teams; customer-facing by the rubric, though it includes system design, build and eval-driven feedback.
- evidence: "lead complex end-to-end deployments of frontier models in production alongside our most strategic customers" / "eval-driven feedback that changes product and model roadmaps"
- uncertainty: The share of build work versus customer scoping is not stated.
