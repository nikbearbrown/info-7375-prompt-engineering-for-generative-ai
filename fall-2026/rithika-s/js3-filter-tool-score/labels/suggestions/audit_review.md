# audit: Claude Code suggestions for review

AUTOMATED SUGGESTIONS, NOT REVIEWED BY A HUMAN. Each verdict below was proposed by Claude Code from the blind sheet text only, using labels/LABELING_RUBRIC.md (sha256 55829cfef808...). They become your verdicts only after you review them in the CSV.

Counts: relevant 8, not 37, unsure 5.

## Borderline cases (review these first)

- row 2 `3254f6a7-6353-4a77-beec-f37b832c99ae` Applied AI Engineer, API Platform, Digital Natives: **not** (low). Customer-facing role with hands-on LLM application building; title is a direct Priya target keyword.
- row 5 `7654349002` Staff Software Engineer (Money): **unsure** (medium). Open the posting: if the team is Mosaic AI model serving or training this is relevant, if it is billing or payments it is not.
- row 8 `8716192002` Sr. Developer Advocate, AI and Machine Learning: **not** (medium). Outward-facing role that requires real ML practice; not under the rubric, but a reader focused on skills match could disagree.
- row 10 `eacbd123-83fb-42c6-a5d5-e914b8e135b8` Applied AI Engineer, Startups : **not** (low). Same question as audit row 2: Applied AI Engineer title with a customer-advisory description.
- row 17 `4720573005` Frontier Agents Engineer (Applied AI): **relevant** (medium). If the role turns out to be client delivery like an FDE, the rubric would make it not.
- row 18 `8093293002` Staff Software Engineer - Backend : **not** (medium). Infrastructure with an unknown ML link; unsure would also be defensible.
- row 20 `4660340005` Machine Learning Fellow - Human Frontier Collective: **not** (medium). Title contains a target keyword; the role reads as an expert-network fellowship.
- row 23 `1c516e9f-c97d-4a40-8529-9871dac615a5` Research Engineer / Research Scientist- Post Training: **relevant** (medium). Research engineer/scientist: relevant under the rubric, but the research emphasis may be a stretch for Priya.
- row 24 `7934782002` Senior Software Engineer - Ingestion: **relevant** (medium). Data platform rather than ML; decide together with held-out row 23 (the Staff version of this role).
- row 26 `8878946002` Evergreen - AI Engineer, AI FDE: **not** (low). Title is a Priya target keyword and the work is ML pipelines, but for customers; same question as the FDE and Applied AI Engineer rows.
- row 27 `8617901002` Sr Software Engineer- CXI: **unsure** (medium). Could be an LLM application platform (relevant) or backend workflow services (not); open the full posting.
- row 28 `872ca3d0-c8c0-4585-9a34-7f9ed6b4dbf9` Research Engineer/Research Scientist- Post Training, Model Experience: **relevant** (medium). Research engineer/scientist clause; treat consistently with audit row 23.
- row 29 `74842880-e750-4664-9e2e-83b4c96c5a03` Principal Software Engineer, Full Stack — Codex: **unsure** (medium). Mixed full-stack product role; relevant only if agent and prompt work dominates.
- row 31 `8784103002` Sr. Specialist Solutions Architect -AI&ML Engineer: **not** (medium). Customer-facing role with substantial ML architecture; title includes ML Engineer.
- row 34 `4688021005` Finance Systems Integration Lead: **unsure** (medium). Internal business-systems role with agentic workflows similar to Priya's agent work; could go relevant or not.
- row 36 `087aa4f5-1192-413a-ba34-3ae324cf90e5` Applied AI Engineer, Enterprise - EDU: **not** (low). Applied AI Engineer customer role; decide with audit rows 2 and 10.
- row 37 `7472e486-0aa6-4f9d-86da-2105a42b2dce` Forward Deployed Engineer (FDE) - AI Infra - SF: **not** (low). Forward-deployed ML-infrastructure work; the strongest case among the FDE rows for relevant.
- row 41 `c8d3feee-2b6a-4ef7-b8c0-90bbd1381c1f` Applied AI Engineer, Codex: **not** (medium). Applied AI Engineer title on a customer-adoption role; less ML building than the other Applied AI rows.
- row 43 `cc434f5b-dc0b-42fd-97ec-e0171545c6e9` Research Engineer, Privacy: **not** (medium). Research engineer in privacy with a possible but unstated link to model training data.
- row 44 `8592928002` Sr. Forward Deployed Engineer (FDE) - Financial Services: **not** (low). The clearest test of the customer-facing rule: hands-on data and AI building for clients.
- row 45 `8133691002` Software Engineer - New Grad (2027 Start) - Aarhus: **unsure** (medium). Generic platform role with unknown team; compare with audit row 18, which I marked not because its shown duties were generic backend.
- row 46 `840963bb-7b1a-4021-91a0-40baf71b7e20` Applied AI Engineer, Startups (Codex): **not** (low). Applied AI Engineer with an evaluation component; decide with audit rows 2, 10 and 36.
- row 47 `2796d32a-9f7c-4008-a2c5-50dd53b0f2fe` Data Engineer, Core Experimentation: **relevant** (low). Data engineering versus experimentation analytics; held-out row 14 (Software Engineer on the same team) was marked not, so decide both together.
- row 49 `8892970002` Lead Solutions Architect - Generative AI (EMEA Emerging DNB): **not** (medium). Customer-facing LLM specialist; decide with audit row 31.
- row 50 `8592952002` Sr. Forward Deployed Engineer (FDE) - Financial Services: **not** (low). Duplicate of audit row 44 in another city; give both the same verdict.

## All postings

### row 1: Strategic Core Account Executive - Retail 

- id: `8458710002` | board: databricks | batch 1
- suggested verdict: **not** (confidence high)
- CSV reason: enterprise sales role
- justification: An account executive running go-to-market campaigns and closing deals in Fortune 500 retail accounts; sales.
- evidence: "you are a sales professional experienced in leading go-to-market campaigns in Fortune 500 accounts"
- uncertainty: none

### row 2: Applied AI Engineer, API Platform, Digital Natives

- id: `3254f6a7-6353-4a77-beec-f37b832c99ae` | board: openai | batch 1
- suggested verdict: **not** (confidence low)
- CSV reason: customer advisory applied AI role
- justification: Despite the AI Engineer title, the team describes itself as a trusted advisor to API customers and the role partners with customer product teams to ship their AI features; the rubric treats that as customer-facing, though it involves building agentic features with frontier models.
- evidence: "We act as a trusted advisor and thought partner for our API customers" / "turn frontier model capabilities into new features and agentic experiences"
- uncertainty: The excerpt does not say how much code the engineer writes versus advising; the title matches Priya's target title exactly.

### row 3: Executive in Residence, Cyber

- id: `6384df1b-c2e0-4265-ad9b-d4a7bca706d6` | board: openai | batch 1
- suggested verdict: **not** (confidence high)
- CSV reason: cybersecurity executive outreach role
- justification: Seeks a CISO-level security executive to be an industry voice and speaker for customers; executive outreach, not engineering.
- evidence: "OpenAI is seeking an accomplished CISO/CSO or equivalent cybersecurity executive" / "You will combine invited speaking and executive engagement"
- uncertainty: none

### row 4: Applied AI Architect - Tokyo

- id: `57cfe1d3-27b6-4761-909c-fec7829e9227` | board: openai | batch 1
- suggested verdict: **not** (confidence high)
- CSV reason: customer technical owner role
- justification: Senior technical owner for a portfolio of customers and counterpart to their leadership, working with Sales; a customer-facing architect role.
- evidence: "you will be the senior technical owner for a named portfolio of customers and the primary technical counterpart to their leadership teams"
- uncertainty: none

### row 5: Staff Software Engineer (Money)

- id: `7654349002` | board: databricks | batch 1
- suggested verdict: **unsure** (confidence medium)
- CSV reason: boilerplate only and team unclear
- justification: The excerpt is company boilerplate followed by a Mosaic AI product paragraph; the title only says Money, and nothing shown states what this engineer builds.
- evidence: "Staff Software Engineer (Money)" / "Databricks Mosaic AI offers a unique data-centric approach to building enterprise-quality, Machine Learning and Generative AI solutions"
- uncertainty: The Mosaic AI paragraph may describe the team or may be general company context; Money could mean billing or something else, which I did not assume.

### row 6: Software Engineer, Foundations Search

- id: `40ed6975-ef61-4807-b748-37c2fa2b76c7` | board: openai | batch 1
- suggested verdict: **relevant** (confidence medium)
- CSV reason: retrieval systems for frontier models
- justification: The Search team in Foundations builds agentic search by co-designing model-system interfaces with serving, indexing and retrieval, and large-scale indexing systems that models reason over; ML serving and retrieval infrastructure.
- evidence: "building agentic search by co-designing model–system interfaces with the core search stack (serving, indexing, retrieval)" / "develops large-scale systems that transform and index vast corpora, enabling models to reason over"
- uncertainty: Sits in a research organization; the engineer's own duties are past the excerpt.

### row 7: Hardware Operations Engineer

- id: `b9a4a809-a965-4dbe-aeef-6ce1593903dd` | board: openai | batch 1
- suggested verdict: **not** (confidence high)
- CSV reason: data center hardware operations
- justification: Keeps compute hardware reliable and available across AI campuses with data center operations partners; hardware operations rather than ML or data-platform software.
- evidence: "The Hardware Operations team is responsible for ensuring the reliability, availability, and lifecycle health of OpenAI’s compute infrastructure"
- uncertainty: none

### row 8: Sr. Developer Advocate, AI and Machine Learning

- id: `8716192002` | board: databricks | batch 1
- suggested verdict: **not** (confidence medium)
- CSV reason: developer advocacy community role
- justification: Developer advocacy aimed at building trust and recognition in the AI practitioner community and attending meetups; it asks for hands-on GenAI, agents and MLOps practice, but the job itself is outreach.
- evidence: "depends on building trust and recognition within an ever-growing community" / "Are you a hands-on practitioner in generative AI, agents, and MLOps"
- uncertainty: Advocates often build demos and sample code; the excerpt stops before the duties.

### row 9: Manager, Forward Deployed Engineering - Munich

- id: `5d5b2256-ee0f-4ba6-a983-d62d0d70515d` | board: openai | batch 2
- suggested verdict: **not** (confidence high)
- CSV reason: manages forward-deployed team
- justification: A people manager who leads and grows the Munich FDE team through customer deployments; management and customer-facing.
- evidence: "As a foundational FDE manager, you’ll lead FDE through high-stakes, ambiguous customer deployments" / "You’ll grow a team"
- uncertainty: none

### row 10: Applied AI Engineer, Startups 

- id: `eacbd123-83fb-42c6-a5d5-e914b8e135b8` | board: openai | batch 2
- suggested verdict: **not** (confidence low)
- CSV reason: startup customer advisory role
- justification: Guides startup customers through ideation, development and delivery of GenAI applications as a trusted advisor; business-minded and customer-facing by the rubric, with real technical depth expected.
- evidence: "We act as a trusted advisor and thought partner for our customers" / "We are seeking a technically proficient, business-minded Applied AI Engineer" / "guiding them through ideation, development, delivery"
- uncertainty: Whether the engineer builds alongside customers or mainly advises is not stated in the excerpt.

### row 11: Manager, Delivery Solutions Architects

- id: `8801844002` | board: databricks | batch 2
- suggested verdict: **not** (confidence high)
- CSV reason: manages post-sales architects
- justification: Builds and leads a team of delivery solution architects responsible for post-sales customer success; people management in a customer-facing function.
- evidence: "You will build and lead a team of Delivery Solution Architects (DSAs) responsible for the post-sales success of Databricks' customers"
- uncertainty: none

### row 12: Strategic Core Account Executive - Retail

- id: `8903091002` | board: databricks | batch 2
- suggested verdict: **not** (confidence high)
- CSV reason: account executive sales role
- justification: Strategic account executive in Germany reporting to enterprise sales leadership, focused on closing new business with one large retail/OEM client.
- evidence: "you will focus on building relationships and closing new business opportunities" / "Reporting to our Senior Director of Enterprise Sales"
- uncertainty: none

### row 13: GTM Strategy & Planning

- id: `41408133-b45f-4c7b-a0df-c050f16d92de` | board: openai | batch 2
- suggested verdict: **not** (confidence high)
- CSV reason: revenue strategy and planning
- justification: Sits in Revenue Operations shaping financial targets, capacity plans and investment decisions for the sales organization; business strategy, not engineering.
- evidence: "The GTM Strategy & Planning team sits within Revenue Operations" / "translating company ambitions into actionable growth strategies, financial targets, capacity plans"
- uncertainty: none

### row 14: Applied AI Architect, Healthcare & Life Sciences

- id: `1baad891-43b8-4e2a-9e6c-f68741e718a4` | board: openai | batch 2
- suggested verdict: **not** (confidence high)
- CSV reason: healthcare customer architect role
- justification: Technical owner for a portfolio of healthcare and life-sciences customers and counterpart to their leadership; customer-facing architecture.
- evidence: "you will be the senior technical owner for a named portfolio of Healthcare & Life Sciences customers"
- uncertainty: none

### row 15: Product Engagement Manager, User Operations

- id: `bbf8d3b8-2f8f-49f8-9f35-73c7847647f7` | board: openai | batch 2
- suggested verdict: **not** (confidence high)
- CSV reason: manages support launch specialists
- justification: Leads a team of product engagement specialists in the support organization to run product launches; support operations and people management.
- evidence: "you will lead a team of Product Engagement Specialists responsible for ensuring smooth, successful product launches"
- uncertainty: none

### row 16: Staff Product Designer, Enterprise

- id: `4735360005` | board: scaleai | batch 2
- suggested verdict: **not** (confidence high)
- CSV reason: product design role
- justification: Designs user flows, wireframes and prototypes for enterprise AI web applications; product design, not engineering.
- evidence: "Design end to end user flows, wireframes, high-fidelity mockups, and interactive prototypes for desktop web applications"
- uncertainty: none

### row 17: Frontier Agents Engineer (Applied AI)

- id: `4720573005` | board: scaleai | batch 3
- suggested verdict: **relevant** (confidence medium)
- CSV reason: builds production AI agents
- justification: Title and text centre on building production AI agents with new foundation models and agent architectures, which is LLM application building close to Priya's agent work.
- evidence: "Frontier Agents Engineer (Applied AI)" / "build production AI agents that automate complex workflows" / "building AI systems that reliably solve real-world problems"
- uncertainty: The excerpt is about Scale and the opportunity, not the engineer's duties; the agents are built with client organizations, so some customer-delivery work is possible.

### row 18: Staff Software Engineer - Backend 

- id: `8093293002` | board: databricks | batch 3
- suggested verdict: **not** (confidence medium)
- CSV reason: generic backend distributed systems
- justification: After the company boilerplate the only duty shown is leading complex distributed systems across services; nothing ties this backend role to ML or to data pipelines.
- evidence: "Lead the design and implementation of complex, high-impact distributed systems that span multiple services or teams"
- uncertainty: The team is not named, and any Databricks backend team could touch the data platform.

### row 19: Strategist, Qatar

- id: `4607930005` | board: scaleai | batch 3
- suggested verdict: **not** (confidence high)
- CSV reason: public sector business development
- justification: Grows the public-sector business in Qatar by winning opportunities and running a go-to-market strategy; business development.
- evidence: "you’ll be responsible for growing the Global Public Sector business unit" / "You will develop and execute on a go to market strategy for customer acquisition"
- uncertainty: none

### row 20: Machine Learning Fellow - Human Frontier Collective

- id: `4660340005` | board: scaleai | batch 3
- suggested verdict: **not** (confidence medium)
- CSV reason: expert network fellowship not engineering job
- justification: Membership in an expert network of mostly doctorate-holding researchers who take part in selected projects and publish; not an engineering role building ML systems, despite the Machine Learning title.
- evidence: "We bring together researchers, academics, and domain leaders across 70+ fields – over 90% of members hold doctorates" / "the network itself, participation in selected AI/ML projects, and opportunities to publish"
- uncertainty: The excerpt does not say what a fellow actually does day to day or whether it is a job at all.

### row 21: Software Engineer, Research - Human Data

- id: `4d6a5951-9838-434c-830a-22cb938ea228` | board: openai | batch 3
- suggested verdict: **relevant** (confidence high)
- CSV reason: human feedback platforms for model training
- justification: Engineers build the platforms, tools and infrastructure for human-feedback data that OpenAI uses to train its models; ML data-platform work feeding training.
- evidence: "The Human Data engineering team creates the systems that enable scalable, high-quality human feedback" / "These systems are essential to how OpenAI trains and improves its most advanced models"
- uncertainty: none

### row 22: Startup Core Account Executive

- id: `8899929002` | board: databricks | batch 3
- suggested verdict: **not** (confidence high)
- CSV reason: startup sales role
- justification: An account executive selling to start-up and mid-market accounts under a consumption sales process; sales.
- evidence: "you come with relevant experience selling to Start-up and Mid-Market accounts"
- uncertainty: none

### row 23: Research Engineer / Research Scientist- Post Training

- id: `1c516e9f-c97d-4a40-8529-9871dac615a5` | board: openai | batch 3
- suggested verdict: **relevant** (confidence medium)
- CSV reason: post-training model development
- justification: The Post Training team trains and improves pre-trained models for deployment, and the role researches and develops model improvements with strong ML engineering skills; model training is the main work.
- evidence: "The Post Training team is responsible for training and improving pre-trained models" / "We're looking for individuals with strong ML engineering skills and research experience"
- uncertainty: Research-heavy role; research experience is asked for, which I did not treat as a criterion.

### row 24: Senior Software Engineer - Ingestion

- id: `7934782002` | board: databricks | batch 3
- suggested verdict: **relevant** (confidence medium)
- CSV reason: data ingestion platform engineering
- justification: Senior-level role on Lakeflow Connect, the ingestion connectors that load enterprise data into the Lakehouse for data and AI workflows; data-pipeline platform work.
- evidence: "Ingesting data into the Lakehouse is a strategic area of investment for Databricks" / "Lakeflow Connect is looking to solve this problem by providing ready-to-use, point-and-click connectors"
- uncertainty: Connector engineering may be integration work more than ML; the excerpt ends before the duties.

### row 25: Strategic Core Account Executive - CMEG - Telco 

- id: `8431459002` | board: databricks | batch 4
- suggested verdict: **not** (confidence high)
- CSV reason: telco enterprise sales
- justification: Enterprise account executive for telecom Fortune 500 accounts, leading go-to-market campaigns and deals; sales.
- evidence: "you are a sales professional experienced in leading go-to-market campaigns in Fortune 500 accounts, specificlaly in the TELCO space"
- uncertainty: none

### row 26: Evergreen - AI Engineer, AI FDE

- id: `8878946002` | board: databricks | batch 4
- suggested verdict: **not** (confidence low)
- CSV reason: customer-facing ML professional services
- justification: The team calls itself customer-facing and delivers professional-services engagements helping customers build and productionize ML and LLM pipelines; real ML work, but delivered as client services, which the rubric counts as customer-facing.
- evidence: "is a highly specialized customer-facing ML team at Databricks" / "We deliver professional services engagements to help our customers build, scale, and optimize ML pipelines"
- uncertainty: Evergreen suggests a standing requisition; the share of hands-on building is not stated.

### row 27: Sr Software Engineer- CXI

- id: `8617901002` | board: databricks | batch 4
- suggested verdict: **unsure** (confidence medium)
- CSV reason: AI-native workflow platform backend unclear
- justification: A backend engineer who will architect an AI-native vertical workflow platform for customer experience intelligence; the excerpt cuts off before saying whether that means building ML or LLM components or conventional backend services.
- evidence: "As a Sr. Backend Software Engineer for Customer Experience Intelligence (CXI ) , you will architect and deliver Databricks' AI-native vertical workflow platform"
- uncertainty: Only one sentence describes the role; AI-native is not defined in the shown text.

### row 28: Research Engineer/Research Scientist- Post Training, Model Experience

- id: `872ca3d0-c8c0-4585-9a34-7f9ed6b4dbf9` | board: openai | batch 4
- suggested verdict: **relevant** (confidence medium)
- CSV reason: post-training evals and reward models
- justification: Model Experience turns desired ChatGPT behavior into the model through human data, evaluations, reward models and post-training; model training and evaluation work, close to Priya's LLM evaluation experience.
- evidence: "turn that vision into real model behavior through human data, evaluations, reward models, and post-training"
- uncertainty: Part of the team's work is research and model design; the engineer's own tasks are past the excerpt.

### row 29: Principal Software Engineer, Full Stack — Codex

- id: `74842880-e750-4664-9e2e-83b4c96c5a03` | board: openai | batch 4
- suggested verdict: **unsure** (confidence medium)
- CSV reason: product leadership with partial agent work
- justification: A product-oriented technical leadership role across UI, developer tooling, orchestration, agent and prompt design, backend and cloud for Codex; agent work is one strand among many, so ML is not clearly the main work.
- evidence: "agent and prompt design, backend systems, and cloud infrastructure" / "This is a highly product-oriented technical leadership role"
- uncertainty: It says the person leads execution across multiple engineers; whether that is people management is not stated.

### row 30: VC Partnerships Manager

- id: `83ac3381-99c0-46a0-897c-abcd8699b466` | board: openai | batch 4
- suggested verdict: **not** (confidence high)
- CSV reason: venture partnerships role
- justification: Manages venture-capital partnerships on the Startups go-to-market team; partnerships, not engineering.
- evidence: "seeking a highly motivated and experienced VC Partnerships Manager to join our Startups Go To Market team"
- uncertainty: none

### row 31: Sr. Specialist Solutions Architect -AI&ML Engineer

- id: `8784103002` | board: databricks | batch 4
- suggested verdict: **not** (confidence medium)
- CSV reason: ML specialist solutions architect
- justification: The trusted ML and AI expert to customers and field engineering, guiding customers' production ML architectures with solution architects; deep ML content but a solutions-architecture role.
- evidence: "you will be the trusted technical ML & AI expert to both Databricks customers and the Field Engineering organization" / "Architect production level ML & AI workloads for customers"
- uncertainty: Specialist SAs can be hands-on; the excerpt emphasizes guiding customers.

### row 32: Solutions Architect - Manufacturing

- id: `8661758002` | board: databricks | batch 4
- suggested verdict: **not** (confidence high)
- CSV reason: pre-sales solutions architect
- justification: Pre-sales solutions architect working with the account executive on technical strategy, value selling and proofs-of-concept for large accounts.
- evidence: "We are looking for experienced pre-sales professionals" / "You will lean upon your solid background in value selling, technical account management"
- uncertainty: none

### row 33: Solutions Architect - Communications, Media, Entertainment and Games

- id: `8755492002` | board: databricks | batch 5
- suggested verdict: **not** (confidence high)
- CSV reason: customer solutions architect
- justification: Owns technical strategy and platform adoption for media and games accounts as a trusted advisor to customer architects; solutions architecture.
- evidence: "owning architecture discussions, driving platform adoption, and serving as a trusted advisor to customer technical leads and architects"
- uncertainty: none

### row 34: Finance Systems Integration Lead

- id: `4688021005` | board: scaleai | batch 5
- suggested verdict: **unsure** (confidence medium)
- CSV reason: internal integrations with some agent work
- justification: Builds integrations, automations and AI agents for finance, people and recruiting workflows; agentic workflows are named, but so are traditional system integrations, and the excerpt does not say which dominates.
- evidence: "help design and develop integrations, automations, and AI agents that streamline workflows across Finance, Accounting, People, and Recruiting" / "from traditional system integrations to intelligent agent-driven workflows"
- uncertainty: Whether Lead means people management is not stated; the balance of agent work versus integration plumbing is unknown.

### row 35: Public Sector Lead, Defence & Security

- id: `4736243005` | board: scaleai | batch 5
- suggested verdict: **not** (confidence medium)
- CSV reason: defence public sector business lead
- justification: The excerpt describes Scale's defence market and the pressure on UK Defence to adopt AI, framing a public-sector lead for that market; a business role, not engineering.
- evidence: "Public Sector Lead, Defence & Security" / "Defence is under pressure to adopt AI at pace"
- uncertainty: The excerpt ends before the duties; no clearance is mentioned in the shown text, so that played no part.

### row 36: Applied AI Engineer, Enterprise - EDU

- id: `087aa4f5-1192-413a-ba34-3ae324cf90e5` | board: openai | batch 5
- suggested verdict: **not** (confidence low)
- CSV reason: education customer technical partner
- justification: Serves as a technical partner to universities, working directly with their engineering and transformation teams to get AI use cases into production; customer-facing per the rubric, with real production-system work.
- evidence: "you will serve as a technical partner to leading organizations including universities and other educational institutions" / "We work directly with customers’ engineering, product, security, and transformation teams"
- uncertainty: Hands-on share is not stated; title matches Priya's target title.

### row 37: Forward Deployed Engineer (FDE) - AI Infra - SF

- id: `7472e486-0aa6-4f9d-86da-2105a42b2dce` | board: openai | batch 5
- suggested verdict: **not** (confidence low)
- CSV reason: forward-deployed AI infra customer role
- justification: Embeds with customers on optimization problems across semiconductors and AI infrastructure, writing software and running experiments on their workloads and hardware; strong ML-infrastructure content, but the job is defined by customer embedding.
- evidence: "You will embed with customers where model performance matters" / "You will write and debug software, run experiments against real workloads and hardware"
- uncertainty: This FDE variant is more hands-on and infrastructure-focused than the others.

### row 38: Applied AI Engineer, Codex Core Agent

- id: `577e6673-0a4a-491b-9a0d-facbdd3bdf3c` | board: openai | batch 5
- suggested verdict: **relevant** (confidence high)
- CSV reason: improves the Codex agent in production
- justification: An internal team that builds the Codex agent's core loop, its token, latency and cost envelope, and the feedback loops that turn usage into better models; LLM agent engineering and serving, not customer work.
- evidence: "The Codex Core Agent team builds the kernel of Codex" / "the feedback loops that turn real-world usage into better models and better agent behavior over time"
- uncertainty: none

### row 39: Electrical Commissioning Lead

- id: `4d0b1eb5-ea5d-460b-8fe6-23c45b0703f5` | board: openai | batch 5
- suggested verdict: **not** (confidence high)
- CSV reason: electrical commissioning for facilities
- justification: Plans and oversees electrical commissioning and test execution for a data center project on site; facilities engineering.
- evidence: "owns electrical commissioning planning, readiness, quality coordination, and test execution oversight for the project"
- uncertainty: none

### row 40: Senior Solutions Architect - Lakebase

- id: `8567991002` | board: databricks | batch 5
- suggested verdict: **not** (confidence high)
- CSV reason: go-to-market product solutions architect
- justification: Part of a go-to-market team positioning the Lakebase product with clients alongside account teams to grow adoption; customer-facing.
- evidence: "They are part of a global go-to-market team mandate" / "provide compelling reasons for clients to adopt and grow the usage of the given product"
- uncertainty: none

### row 41: Applied AI Engineer, Codex

- id: `c8d3feee-2b6a-4ef7-b8c0-90bbd1381c1f` | board: openai | batch 6
- suggested verdict: **not** (confidence medium)
- CSV reason: Codex customer adoption partner
- justification: Helps customer engineering teams adopt and integrate Codex as a trusted technical partner and power user of AI coding tools; customer adoption work rather than building models or ML systems.
- evidence: "The Applied AI Engineering (Codex) team helps customers adopt OpenAI's coding tools" / "We act as trusted technical partners, guiding engineering teams"
- uncertainty: It does involve prototyping AI workflows with customers.

### row 42: Strategic Finance, Compute

- id: `b4196174-9cc3-487d-9d21-848bc283b80f` | board: openai | batch 6
- suggested verdict: **not** (confidence high)
- CSV reason: compute finance and FP&A
- justification: A finance generalist doing FP&A, investment analysis and planning for the compute portfolio; finance.
- evidence: "This is a finance generalist role that includes core FP&A responsibilities"
- uncertainty: none

### row 43: Research Engineer, Privacy

- id: `cc434f5b-dc0b-42fd-97ec-e0171545c6e9` | board: openai | batch 6
- suggested verdict: **not** (confidence medium)
- CSV reason: privacy engineering for user data
- justification: Privacy engineering across products that handle user data: production services, privacy-preserving techniques and tooling for responsible data use; the shown main work is privacy and security, not ML building.
- evidence: "Our focus is on all OpenAI products and systems handling user data" / "develop novel privacy-preserving techniques"
- uncertainty: Privacy-preserving techniques could apply to training data, but the excerpt does not say so.

### row 44: Sr. Forward Deployed Engineer (FDE) - Financial Services

- id: `8592928002` | board: databricks | batch 6
- suggested verdict: **not** (confidence low)
- CSV reason: customer-facing forward-deployed builder
- justification: Builds and productionizes data and AI systems for financial-services customers and calls itself a hands-on, customer-facing role; it spans data engineering and AI, but the rubric counts customer-facing as not.
- evidence: "you will work with customers to build and productionize solutions to their data & AI challenges" / "This is a hands-on, customer-facing role for builders"
- uncertainty: Hands-on data engineering and AI building is explicit, which makes the customer-facing rule the only reason for not.

### row 45: Software Engineer - New Grad (2027 Start) - Aarhus

- id: `8133691002` | board: databricks | batch 6
- suggested verdict: **unsure** (confidence medium)
- CSV reason: new grad team not specified
- justification: A new-grad software engineer who will build infrastructure and products for the Databricks platform, hired across teams; the shown text does not say whether the placement involves ML or data pipelines.
- evidence: "you will work with our engineering team to build infrastructure and products for the Databricks platform"
- uncertainty: Team placement is unknown; a 2027 start date and Aarhus location were not used as criteria.

### row 46: Applied AI Engineer, Startups (Codex)

- id: `840963bb-7b1a-4021-91a0-40baf71b7e20` | board: openai | batch 6
- suggested verdict: **not** (confidence low)
- CSV reason: startup advisory with eval feedback
- justification: Trusted advisor to startup founders and developers using Codex, while feeding insights into evaluation systems and model behavior; customer-facing first, with a real model-quality component.
- evidence: "We are trusted advisors to, and thought partners with, startups" / "turn those insights into evaluation systems, product improvements, and better model behavior"
- uncertainty: The evaluation-systems work is close to Priya's LLM evaluation experience; its share of the role is not stated.

### row 47: Data Engineer, Core Experimentation

- id: `2796d32a-9f7c-4008-a2c5-50dd53b0f2fe` | board: openai | batch 6
- suggested verdict: **relevant** (confidence low)
- CSV reason: data engineer on experimentation data platform
- justification: A data engineer on the Statsig experimentation platform working across data infrastructure and analytics; the rule counts data platforms and pipelines, though the team frames the hire as an experimentation expert.
- evidence: "Data Engineer, Core Experimentation" / "The team operates at the intersection of experimentation methodology, data infrastructure, causal inference, and product analytics"
- uncertainty: The excerpt asks for experimentation experts, which may mean statistics more than pipelines.

### row 48: Director, Lakebase Sales Specialists (Central region)

- id: `8567843002` | board: databricks | batch 6
- suggested verdict: **not** (confidence high)
- CSV reason: sales director managing specialists
- justification: Directs a regional team of sales specialists growing the Lakebase business; sales leadership and people management.
- evidence: "to lead a regional team of specialists across the Central region responsible for growing the Databricks Lakebase business"
- uncertainty: none

### row 49: Lead Solutions Architect - Generative AI (EMEA Emerging DNB)

- id: `8892970002` | board: databricks | batch 7
- suggested verdict: **not** (confidence medium)
- CSV reason: GenAI customer-facing solutions architect
- justification: The go-to GenAI and LLM expert for account teams and digital-native customers, described as a customer-facing individual contributor; strong LLM content in a solutions-architect role.
- evidence: "You will be the go-to expert our Account Teams and customers turn to when a GenAI or LLM use case needs to move from an ambitious idea to a production-grade reality" / "This is a highly technical, customer-facing individual contrib"
- uncertainty: Travel across Europe and the France location were not used.

### row 50: Sr. Forward Deployed Engineer (FDE) - Financial Services

- id: `8592952002` | board: databricks | batch 7
- suggested verdict: **not** (confidence low)
- CSV reason: customer-facing forward-deployed builder
- justification: The Washington, D.C. listing of the same financial-services FDE role as audit row 44 (same requisition CSQ327R59): hands-on data and AI building for clients, labeled customer-facing.
- evidence: "CSQ327R59" / "This is a hands-on, customer-facing role for builders who thrive at the intersection of technology and business impact"
- uncertainty: Same as row 44.
