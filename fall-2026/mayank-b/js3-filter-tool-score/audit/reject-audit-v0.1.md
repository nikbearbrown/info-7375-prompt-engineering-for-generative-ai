# Reject audit, filter v0.1

Filter run `runs/2026-11-26T02-20-53Z-filter-v0.1` on corpus `runs/2026-11-26T02-20-27Z-content` (raw SHA-256 per board in its run.json). Seed 7375. Pools: {'kept': 76, 'close': 42, 'rejects': 874, 'cannot_tell': 0, 'all': 950}. Draw: 30 uniform random rejects, the close calls (score 2; all, or a seeded 15), 10 random kept. The held-out postings are excluded.

For each posting: **My verdict** = what Priya should get (`keep` / `reject` / `cannot tell`), judged from the original posting. **False friend** = a word that matched for the wrong reason (for example `pipeline` meaning a sales pipeline). Claude Code never fills these lines.

## Part: random-rejects (30)

### R01 · greenhouse/anthropic · 5391004008

**Manager, Technical Deployment (Financial Services)** · New York City, NY · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5391004008)

Filter v0.1: **reject**. exclude word in title: 'Manager'. Score 3. Role word: -. Exclude word: Manager. Location: pass (New York City, NY).
Topic words: `llm`, `evaluation` (×2), `agents` (×2)

> `llm` → …e environments, ideally including embedded or forward-deployed teams working at client sites. Have delivered AI, ML, or LLM-based agentic solutions into production. You understand solution patterns, integration approaches, and what breaks i…
> `evaluation` → …own engagement portfolio health across your vertical. You set the bar for delivery quality and build the playbooks and evaluation frameworks that let the practice scale. Your work will directly influence Anthropic's product direction and e…
> `agents` → …ents, ideally including embedded or forward-deployed teams working at client sites. Have delivered AI, ML, or LLM-based agentic solutions into production. You understand solution patterns, integration approaches, and what breaks in real env…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “Have 8+ years leading enterprise AI/ML delivery, whether you came up as a founder, engineer, data scientist, or researcher who has mo” · “ved into deployments, with at least 3 years directly managing people who owned delivery outcomes”

<details><summary>Posting text (excerpt)</summary>

Responsibilities 

 
 Hire, develop, and retain a team of TDLs embedded in Financial Services engagements. Set a high bar for delivery judgment, technical fluency, and customer presence, and run the interviews that hold it.

 Manage each TDL directly: regular 1:1s, clear expectations, direct feedback, and a growth plan. Build a bench that runs engagements well without you in the room.

 Own portfolio health across the vertical. Track which engagements are on track, at risk, or closing out, and intervene early when delivery drifts. Run engagement quality reviews with your team.

 Own customer outcomes across the portfolio. Hold the executive relationship with customer sponsors, run steering committees, and represent Anthropic's credibility with senior business, risk, and engineering leaders.

 Make the staffing call for each engagement. Work with FDE managers to match TDLs and engineers t…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R02 · greenhouse/anthropic · 5390754008

**Applied AI Engineer, Enterprise** · Paris, France · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5390754008)

Filter v0.1: **reject**. location is not one Priya accepts. Score 3. Role word: AI Engineer. Exclude word: -. Location: fail.
Topic words: `llm` (×2), `evaluation` (×9), `agents` (×6)

> `llm` → …'ingénierie, de sécurité, juridique et des achats Une expérience en production avec des applications propulsées par des LLM, incluant le prompting, l'ingénierie du contexte, les architectures d'agents, les cadres d'évaluation et le déploiem…
> `evaluation` → …t and trusted technical advisor for your customers, advising their engineering teams on architecture, agent design, and evaluation, and working with the C-level and senior executives who sponsor these programmes to show the business value C…
> `agents` → …re technique de confiance de vos clients, en conseillant leurs équipes d'ingénierie sur l'architecture, la conception d'agents et l'évaluation, et en travaillant avec les dirigeants et les cadres supérieurs qui sponsorisent ces programmes p…

False-friend check:
> `training`: …UR 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “6+ years of experience as a Software Engineer, Solutions Architect, Forward Deployed Engineer, or technical founder”

<details><summary>Posting text (excerpt)</summary>

About the role 

 As an Applied AI Engineer on our Enterprise team, your role is to guide some of France's largest businesses to the frontier of AI and help them deploy Claude into their operations, their products, and their ways of working. You will become the go-to Claude Platform specialist and trusted technical advisor for your customers, advising their engineering teams on architecture, agent design, and evaluation, and working with the C-level and senior executives who sponsor these programmes to show the business value Claude can create and help them reach a confident decision to build on Claude.

 Enterprise deals are different. Procurement cycles are longer, more stakeholders are involved, and success depends on being able to connect the technical work to the outcomes the boardroom cares about. You will be as comfortable advising an engineering team on evaluation and architectur…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R03 · ashby/notion · b06005d2-e24b-467b-b7ea-783bac7366da

**Commercial Outcomes Architect** · Tokyo, Japan  · [original posting](https://jobs.ashbyhq.com/notion/b06005d2-e24b-467b-b7ea-783bac7366da)

Filter v0.1: **reject**. location is not one Priya accepts. Score 1. Role word: -. Exclude word: -. Location: fail.
Topic words: `agents` (×2)

> `agents` → WHO WE ARE Notion is the collaborative AI workspace where teams and agents think together https://www.youtube.com/watch?v=vkpYpWfEK5s. We're building one place where your knowledge, projects, meetings, and AI tools live side by side, so wor…

False-friend check:
> `pipeline`: …deliver outcomes with Notion

 - Contribute directly to NRR with predictable renewal and expansion pipeline and proactive product adoption for your book of business

 - Partner closely with Solutions…

Experience lines in the text: “- 5+ years of experience driving customer adoption, value realization, renewals, or expansion within a B2B software environment”

<details><summary>Posting text (excerpt)</summary>

WHO WE ARE

Notion is the collaborative AI workspace where teams and agents think together https://www.youtube.com/watch?v=vkpYpWfEK5s. We're building one place where your knowledge, projects, meetings, and AI tools live side by side, so work is faster, clearer, and less fragmented. Millions of individuals, small teams, and large companies run their work on Notion.



Notinos (our employees) are customer zero in bringing this future of work to life. We care about craft, building things that last, and the belief that great work is still fundamentally human. Our goal isn’t to ship the next feature. Each and every team of Notinos is working to set the standard for how humans work together in the AI era. From building a business’s system of record to making and managing AI agents to automating away the busy work, we care deeply about giving our customers more time for their life’s work.…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R04 · greenhouse/anthropic · 5454142008

**Manager, Sales Development, Enterprise** · San Francisco, CA | New York City, NY · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5454142008)

Filter v0.1: **reject**. exclude word in title: 'Manager'. Score 2. Role word: -. Exclude word: Manager. Location: pass (San Francisco, CA).
Topic words: `llm`, `machine learning`

> `llm` → …executive-level stakeholders An understanding of Anthropic’s products, ecosystem, and hands on building experience with LLMs Excitement about Anthropic's mission to develop AI that is safe and beneficial Preferred qualifications Personal cl…
> `machine learning` → …such as Apollo and HubSpot Experience in API-first, consumption-based, or platform business models Background in AI or machine learning, cloud infrastructure, or developer platforms Familiarity with enterprise procurement, security review,…

False-friend check:
> `pipeline`: …build and manage a team of 6-10 Business Development Representatives (BDRs) who generate high-value pipeline inside complex enterprise organizations through account-based prospecting, multi-threaded o…
> `pipeline`: …ties 

 
 Build, lead, and scale a team of BDRs focused on the Enterprise segment

 Drive strategic pipeline generation through account-based prospecting and targeted outbound campaigns to Global 2000…
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

<details><summary>Posting text (excerpt)</summary>

About the role 

 As a Sales Development Manager for Enterprise at Anthropic, you will lead the team that opens our most strategic customer relationships. You'll build and manage a team of 6-10 Business Development Representatives (BDRs) who generate high-value pipeline inside complex enterprise organizations through account-based prospecting, multi-threaded outreach, and rigorous qualification.

 Enterprise buying is long and involves many stakeholders. The work here is less about volume and more about depth: knowing an account well enough to reach the right people with the right message, and staying with it long enough to turn early conversations into real opportunities. You'll bring a strong understanding of enterprise sales cycles and organizational dynamics, and you'll coach your team to develop strategic accounts over time.

 You'll partner closely with Enterprise Account Executive…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R05 · greenhouse/anthropic · 5412334008

**Research Engineer, Cybersecurity RL (Reinforcement Learning)** · Zürich, CH · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5412334008)

Filter v0.1: **reject**. location is not one Priya accepts. Score 4. Role word: -. Exclude word: -. Location: fail.
Topic words: `llm`, `evaluation`, `agents`, `machine learning`

> `llm` → …security or other experimental & research background. Familiarity with RL techniques and environments. Familiarity with LLM training methodologies. Logistics Minimum education: Bachelor’s degree or an equivalent combination of education, tr…
> `evaluation` → …and realize them in code. Your work will include designing and implementing RL environments, conducting experiments and evaluations, delivering your work into production training runs, and collaborating with other researchers, engineers, an…
> `agents` → …ner with researchers and safety teams across Anthropic to understand their analytical needs and build solutions Develop agentic integrations that allow AI systems to autonomously investigate and act on analytical findings Contribute to the…

False-friend check:
> `training`: …nting RL environments, conducting experiments and evaluations, delivering your work into production training runs, and collaborating with other researchers, engineers, and cybersecurity specialists ac…
> `training`: …al & research background.

 Familiarity with RL techniques and environments.

 Familiarity with LLM training methodologies.

 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combina…

<details><summary>Posting text (excerpt)</summary>

Responsibilities 

 
 Partner with researchers and safety teams across Anthropic to understand their analytical needs and build solutions

 
 
 Develop agentic integrations that allow AI systems to autonomously investigate and act on analytical findings

 Contribute to the strategic direction of the team, including decisions about what to build, what to partner on, and where to invest

 This role may require participation in an on-call rotation.

 
 You may be a good fit if you 

 
 Have experience with machine learning.

 Have experience in cybersecurity research.

 Have strong software engineering skills.

 Can balance research exploration with engineering implementation.

 Are passionate about AI's potential and committed to developing safe and beneficial systems.

 
 Strong candidates may also have 

 
 Professional experience in security engineering, fuzzing, detection and response,…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R06 · greenhouse/anthropic · 5426651008

**Enterprise Account Executive, Industries - BFSI** · Mumbai, India · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5426651008)

Filter v0.1: **reject**. location is not one Priya accepts. Score 0. Role word: -. Exclude word: -. Location: fail.
Topic words: none


False-friend check:
> `training`: …plus

 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “15+ years of enterprise sales experience in the Indian market, with a proven track record of closing large, complex deals, ideall”

<details><summary>Posting text (excerpt)</summary>

About the role 

 We are seeking an Enterprise Account Executive, Industries - BFSI to pioneer Anthropic's enterprise AI adoption across India's banking, financial services, and insurance sector. You will build our presence from the ground up, securing transformative deals with leading banks, NBFCs, insurers, and fintechs, and establishing Anthropic as their trusted AI partner for digital transformation. You will navigate the complex, regulated environment of Indian financial institutions and position Claude as the AI solution that drives both efficiency and innovation while maintaining the highest standards of safety and reliability. As one of our first industry specialists in India, you will shape our BFSI go-to-market strategy and build the playbook for how Anthropic serves financial institutions, working closely with global teams while adapting our approach to local market dynamics.…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R07 · greenhouse/anthropic · 5435471008

**Policy Advocacy - Political Research** · San Francisco, CA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5435471008)

Filter v0.1: **reject**. no role word in title and 0 topic words < T=3. Score 0. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: none


False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “8+ years of professional experience in political or public opinion research, ideally spanning multiple campaign cycles and polic”

<details><summary>Posting text (excerpt)</summary>

About the role 

 We are seeking an experienced public opinion researcher to build and expand Anthropic's in-house polling and research function. This role will be fundamental to understanding how key audiences — from policymakers and third-party groups to the general public — perceive and respond to Anthropic's policy positions, messages, and campaigns. This is a foundational role: you'll establish the research function from the ground up, with high autonomy and limited precedent.

 The Central Policy team sits at the operational heart of Anthropic's policy function — distinct from government relations and communications, but essential to enabling both. You'll work cross-functionally to ensure our policy and communications strategy is grounded in a rigorous understanding of stakeholder sentiment. The polling insights you generate will directly feed into high-visibility campaigns and wil…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R08 · greenhouse/anthropic · 5391184008

**AWS GTM Partnership Lead, Global System Integrators** · San Francisco, CA | New York City, NY | Seattle, WA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5391184008)

Filter v0.1: **reject**. exclude word in title: 'Lead'. Score 0. Role word: -. Exclude word: Lead. Location: pass (San Francisco, CA).
Topic words: none


False-friend check:
> `pipeline`: …tems.

 In this role, you will build the go-to-market motion that turns partner interest into joint pipeline and closed revenue, working across AWS's partner organization and the AWS practices inside…
> `pipeline`: …ding co-selling motions, joint business plans, events and segment-specific plays

 Own forecasting, pipeline development, and revenue targets for partner-sourced and partner-influenced business

 Desi…
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “12+ years of enterprise partnerships, alliances, or business development experience, with meaningful time spent on partner ecosys”

<details><summary>Posting text (excerpt)</summary>

About the role 

 Anthropic is seeking a partnerships leader to own the tri-party motion for systems integrator partnerships selling through AWS. Global systems integrators and specialist SIs are how Claude reaches enterprise customers at scale, and AWS is the surface most of that work runs on. You will own the intersection of those two ecosystems.

 In this role, you will build the go-to-market motion that turns partner interest into joint pipeline and closed revenue, working across AWS's partner organization and the AWS practices inside the world's largest integrators. You will define how Claude is positioned inside AWS partner programs, design the commercial mechanics that let partners transact and get rewarded, and build the joint plays that partners take to their customers.

 This is a build role. The partner ecosystem is early, the programs are still being designed, and you will be…

</details>

**My verdict:** keep
**Why (one line):** Mayank: the filter was wrong here (rejected only on the exclude word 'Lead') (filter wrong? yes)
**False friend? (word, or -):** -

### R09 · greenhouse/anthropic · 5391999008

**Community Engagement Manager, Data Centres (Australia)** · Sydney, Australia | Remote-Friendly, Australia · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5391999008)

Filter v0.1: **reject**. exclude word in title: 'Manager'. Score 0. Role word: -. Exclude word: Manager. Location: fail.
Topic words: none


False-friend check:
> `training`: …ng



 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “7+ years of experience in community engagement specifically on data centre, utility, energy, or large-scale industrial infrastru”

<details><summary>Posting text (excerpt)</summary>

About the role

 Anthropic is building AI systems that will shape the trajectory of one of the most consequential technologies in human history. That work requires physical infrastructure at significant scale, and building that infrastructure the right way means being a real, long-term partner to the communities where we operate.

 We are looking for a Community Engagement Manager in Australia to join our Public Policy team and serve as Anthropic's on-the-ground presence in the communities where our data centres are sited, built, and operated. This is not a communications role or a government affairs role, though you will do elements of both. It is a relationship role: your job is to make Anthropic a trusted, visible, and valued neighbour, from the earliest stages of site selection through construction and long-term operations.

 You will be the connective tissue between Anthropic's Poli…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R10 · greenhouse/anthropic · 5458689008

**Enterprise Account Executive, Public Sector** · Milan, Italy · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5458689008)

Filter v0.1: **reject**. location is not one Priya accepts. Score 0. Role word: -. Exclude word: -. Location: fail.
Topic words: none


False-friend check:
> `pipeline`: …nd IT departments

 Proven experience exceeding revenue targets by effectively managing an evolving pipeline and sales process

 Excellent communication skills and the ability to present confidently t…
> `pipeline`: …esperienza comprovata nel superare gli obiettivi di fatturato grazie a una gestione efficace di una pipeline e di un processo di vendita in continua evoluzione

 Eccellenti capacità di comunicazione e…
> `training`: …iano.
 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “7+ years of B2B sales experience in SaaS, API solutions, or emerging technologies, including selling to public sector organisati”

<details><summary>Posting text (excerpt)</summary>

About the role 

 As an Enterprise Account Executive at Anthropic, you'll join the foundational team at the forefront of introducing our cutting-edge AI productivity API and SaaS solutions to public sector organisations across Italy. You'll drive the adoption of safe, frontier AI by securing strategic agreements with central government ministries, regional and local administrations, and public agencies. You'll leverage your consultative sales expertise in the public sector to propel revenue growth while becoming a trusted partner to public sector stakeholders, helping them embed and deploy AI while uncovering its full range of capabilities in citizen services, administration, and research. In collaboration with GTM, Product, and Marketing teams, you'll continuously refine our value proposition, sales methodology, and market positioning to resonate with public sector decision-makers.

 Th…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R11 · greenhouse/anthropic · 5391983008

**Community Engagement Manager, Data Centers (West Texas)** · Austin, TX | Remote-Friendly, United States · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5391983008)

Filter v0.1: **reject**. exclude word in title: 'Manager'. Score 0. Role word: -. Exclude word: Manager. Location: pass (Remote-Friendly, United States).
Topic words: none


False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “7+ years of experience in community engagement specifically on data center, utility, energy, or large-scale industrial infrastru”

<details><summary>Posting text (excerpt)</summary>

About the role

 Anthropic is building AI systems that will shape the trajectory of one of the most consequential technologies in human history. That work requires physical infrastructure at significant scale, and building that infrastructure the right way means being a real, long-term partner to the communities where we operate.

 We are looking for a Community Engagement Manager in West Texas to join our Public Policy team and serve as Anthropic's on-the-ground presence in the communities where our data centers are sited, built, and operated. This is not a communications role or a government affairs role, though you will do elements of both. It is a relationship role: your job is to make Anthropic a trusted, visible, and valued neighbor, from the earliest stages of site selection through construction and long-term operations.

 You will be the connective tissue between Anthropic's Poli…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R12 · ashby/notion · 7a044182-7787-47cd-b8eb-18ebf5642ed4

**Forward Deployed Architect** · London, United Kingdom · [original posting](https://jobs.ashbyhq.com/notion/7a044182-7787-47cd-b8eb-18ebf5642ed4)

Filter v0.1: **reject**. location is not one Priya accepts. Score 1. Role word: -. Exclude word: -. Location: fail.
Topic words: `agents` (×5)

> `agents` → WHO WE ARE Notion is the collaborative AI workspace where teams and agents think together https://www.youtube.com/watch?v=vkpYpWfEK5s. We're building one place where your knowledge, projects, meetings, and AI tools live side by side, so wor…

Experience lines in the text: “- 5+ years of experience in tech services/consulting, solutions architecture, implementation, customer engineering, or a similar c”

<details><summary>Posting text (excerpt)</summary>

WHO WE ARE

Notion is the collaborative AI workspace where teams and agents think together https://www.youtube.com/watch?v=vkpYpWfEK5s. We're building one place where your knowledge, projects, meetings, and AI tools live side by side, so work is faster, clearer, and less fragmented. Millions of individuals, small teams, and large companies run their work on Notion.



Notinos (our employees) are customer zero in bringing this future of work to life. We care about craft, building things that last, and the belief that great work is still fundamentally human. Our goal isn’t to ship the next feature. Each and every team of Notinos is working to set the standard for how humans work together in the AI era. From building a business’s system of record to making and managing AI agents to automating away the busy work, we care deeply about giving our customers more time for their life’s work.…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R13 · greenhouse/anthropic · 5442048008

**Manager, Forward Deployed Engineering** · Munich, Germany · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5442048008)

Filter v0.1: **reject**. exclude word in title: 'Manager'. Score 0. Role word: -. Exclude word: Manager. Location: fail.
Topic words: none


False-friend check:
> `training`: …tems.
 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “10+ years of experience in software engineering, solutions architecture, or a technical customer-facing role such as forward depl” · “2+ years of people management experience within a services/post-sales/FDE organization with a track record of hiring, developing”

<details><summary>Posting text (excerpt)</summary>

About the role 

 Anthropic is building the team to help the world's most ambitious organizations adopt Claude in ways that are transformative, safe, and lasting. Our Forward Deployed Engineers embed directly with strategic customers to ship production AI applications that solve real business problems. As this practice grows, we need a founding leader to build and scale it.

 As the first FDE Manager in DACH, you'll own the team that sits at the frontier of enterprise AI deployment. You'll hire and develop a high-performing team of FDEs, set the technical and operational bar for customer engagements, and build the playbooks that turn one-off successes into repeatable patterns. You'll work hand-in-hand with Engagement Managers who own delivery logistics and stakeholder management, while you ensure your team is shipping quality code, growing technically, and representing Anthropic at the h…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R14 · greenhouse/anthropic · 5470528008

**Product Marketing Manager, Knowledge Work - Enterprise** · San Francisco, CA | New York City, NY · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5470528008)

Filter v0.1: **reject**. exclude word in title: 'Manager'. Score 0. Role word: -. Exclude word: Manager. Location: pass (San Francisco, CA).
Topic words: none


False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “7+ years of product marketing experience with experience as a Senior PMM or PMM Lead at an enterprise productivity, collaboratio”

<details><summary>Posting text (excerpt)</summary>

About the role 

 There are close to a billion knowledge workers in the world, and only a small fraction of them have worked with AI that makes them better at what they do. In the enterprise, reaching the rest depends on the IT, security, and business leaders who decide whether to adopt AI, and the admins who decide how it's deployed, governed, and scaled across their organizations. They ask hard questions before they say yes, and this role owns how we answer them.

 We're looking for a Product Marketing Manager to own positioning for Claude's core knowledge-work products (Chat, Cowork, and the broader non-coding suite) for enterprise decision makers and admins. You'll work across the areas that matter most to enterprise customers today: security and observability, workspace management and deployment controls, and pricing and packaging. You'll own the materials that help a decision maker…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R15 · greenhouse/hubspotjobs · 8355054

**Sales Manager, Small Business - DACH** · Remote - Ireland · [original posting](https://www.hubspot.com/careers/jobs/8355054?gh_jid=8355054)

Filter v0.1: **reject**. exclude word in title: 'Manager'. Score 0. Role word: -. Exclude word: Manager. Location: fail.
Topic words: none


False-friend check:
> `training`: …ther sales managers, directors & executives to aid the growth of the business

 Supervise & conduct training on skills improvement, inbound sales, product & marketing topics

 Strong sales skills & ab…
> `training`: …ourcing and sales strategies to new team members

 Maintain headcount via recruiting, selecting and training new members

 Maintain professional and technical knowledge of inbound marketing and the Hu…

Experience lines in the text: “Experience managing a sales team, 2 years required minimum”

<details><summary>Posting text (excerpt)</summary>

Sales (People) Manager, Small Business - DACH 

 As a HubSpot Small Business Sales Manager of our Account Executive team, you will execute our world-class sales methodology, hire exceptional talent, deliver sales quota each month, uncover strategies to coach and develop your team and build a sales environment and culture we can be proud of.

 We are looking for a Sales Manager to join us in our Berlin or Dublin office. Please check out this article for more context: The Future of Work at HubSpot: How We're Building a Hybrid Company. 

 What are the responsibilities of a Sales (People) Manager? 

 In this role, you will need to:

 
 Lead and manage a sales team to meet monthly goals: activity metrics, forecasted opportunities and revenue targets

 Build confidence & trust with direct reports as well as provide developmental feedback for continuous improvement

 Coach team members to devel…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R16 · ashby/notion · a31170a3-a951-4794-a61f-56640dce1aee

**Outcomes Growth Strategy and Programs Lead** · San Francisco, California; Remote · [original posting](https://jobs.ashbyhq.com/notion/a31170a3-a951-4794-a61f-56640dce1aee)

Filter v0.1: **reject**. exclude word in title: 'Lead'. Score 1. Role word: -. Exclude word: Lead. Location: fail.
Topic words: `agents` (×2)

> `agents` → WHO WE ARE Notion is the collaborative AI workspace where teams and agents think together https://www.youtube.com/watch?v=vkpYpWfEK5s. We're building one place where your knowledge, projects, meetings, and AI tools live side by side, so wor…

<details><summary>Posting text (excerpt)</summary>

WHO WE ARE

Notion is the collaborative AI workspace where teams and agents think together https://www.youtube.com/watch?v=vkpYpWfEK5s. We're building one place where your knowledge, projects, meetings, and AI tools live side by side, so work is faster, clearer, and less fragmented. Millions of individuals, small teams, and large companies run their work on Notion.



Notinos (our employees) are customer zero in bringing this future of work to life. We care about craft, building things that last, and the belief that great work is still fundamentally human. Our goal isn’t to ship the next feature. Each and every team of Notinos is working to set the standard for how humans work together in the AI era. From building a business’s system of record to making and managing AI agents to automating away the busy work, we care deeply about giving our customers more time for their life’s work.…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R17 · greenhouse/anthropic · 5428030008

**Enterprise Account Executive, Pharmaceuticals & Life Sciences** · Munich, Germany · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5428030008)

Filter v0.1: **reject**. location is not one Priya accepts. Score 0. Role word: -. Exclude word: -. Location: fail.
Topic words: none


False-friend check:
> `pipeline`: …n experience exceeding revenue targets in the enterprise sector by effectively managing an evolving pipeline and sales process



 
 Excellent communication skills and the ability to present confident…
> `training`: …UR 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “7+ years of B2B sales experience in enterprise technology, preferably pharmaceuticals or life sciences”

<details><summary>Posting text (excerpt)</summary>

About the role 

 As an Enterprise Account Executive at Anthropic, you'll join the foundational team at the forefront of introducing our cutting-edge AI productivity SaaS solution to large enterprise organizations across DACH. You'll drive the adoption of safe, frontier AI by securing strategic deals with major corporations, technology companies, and research institutions. You'll leverage your consultative sales expertise in the enterprise sector to propel revenue growth while becoming a trusted partner to enterprise stakeholders, helping them embed and deploy AI while uncovering its full range of capabilities across business operations, research, and administration. In collaboration with GTM, Product, and Marketing teams, you'll continuously refine our value proposition, sales methodology, and market positioning to resonate with enterprise decision-makers in the German market.

 Respons…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R18 · greenhouse/anthropic · 5245851008

**Staff + Senior Software Engineer, Inference Infrastructure** · San Francisco, CA | New York City, NY | Seattle, WA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5245851008)

Filter v0.1: **reject**. exclude word in title: 'Senior'. Score 3. Role word: -. Exclude word: Senior. Location: pass (San Francisco, CA).
Topic words: `python`, `llm`, `machine learning` (×2)

> `python` → …, batching, and caching strategies Experience with Kubernetes and cloud infrastructure (AWS, GCP, Azure) Proficiency in Python or Rust Representative projects Designing intelligent routing algorithms that optimize request distribution acros…
> `llm` → …arning systems at scale Experience with load balancing, request routing, or traffic management systems Familiarity with LLM inference optimization, batching, and caching strategies Experience with Kubernetes and cloud infrastructure (AWS, G…
> `machine learning` → …bility and impact Willingness to pick up slack, even if it goes outside your job description Desire to learn more about machine learning systems and infrastructure Thrive in environments where technical excellence directly drives both busin…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

<details><summary>Posting text (excerpt)</summary>

About the role

 Our Inference team is responsible for building and maintaining the critical systems that serve Claude to millions of users worldwide. We bring Claude to life by serving our models via the industry’s largest compute-agnostic inference deployments. We are responsible for the entire stack from intelligent request routing to fleet-wide orchestration across diverse AI accelerators.

 The team has a dual mandate: maximizing compute efficiency to reliably serve our explosive customer growth, while enabling breakthrough research by giving our scientists the high-performance inference infrastructure they need to develop next-generation models. We tackle complex, distributed systems challenges across multiple accelerator families and emerging AI hardware running in multiple cloud platforms.

 Inference systems are highly performance sensitive distributed systems. Inference serves…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R19 · greenhouse/anthropic · 5022845008

**Staff Software Security Engineer** · London, UK · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5022845008)

Filter v0.1: **reject**. exclude word in title: 'Staff'. Score 1. Role word: -. Exclude word: Staff. Location: fail.
Topic words: `python`

> `python` → …are engineering experience implementing and maintaining critical systems at scale Strong software engineering skills in Python or at least one systems language (Go, Rust, C/C++) Experience implementing and operating critical systems at scal…

False-friend check:
> `training`: …mplement network security controls: default-deny ingress and egress, segmentation between research, training and production environments, private connectivity across clouds and data centers, cloud fir…
> `training`: …network traffic visibility or exfiltration detection systems

 Exposure to large-scale distributed training and what it demands of a network

 Led cross-functional security initiatives and navigated…

Experience lines in the text: “Have 8-15+ years of software engineering experience implementing and maintaining critical systems at scale”

<details><summary>Posting text (excerpt)</summary>

About the role 

 The Security Engineering team's mission is to safeguard our AI systems and maintain the trust of our users and society at large. Whether we're developing critical security infrastructure, building secure development practices, or partnering with our research and product teams, we are committed to operating as a world-class security organization and keeping the safety and trust of our users at the forefront of everything we do.

 Responsibilities: 

 
 Build security for large-scale AI clusters across multiple clouds and bare-metal data centers, including IAM, network segmentation and encryption controls

 Design and implement network security controls: default-deny ingress and egress, segmentation between research, training and production environments, private connectivity across clouds and data centers, cloud firewall policy and mTLS with service identity

 Ship these…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R20 · greenhouse/anthropic · 5205541008

**Director, Technical Revenue Accounting** · San Francisco, CA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5205541008)

Filter v0.1: **reject**. exclude word in title: 'Director'. Score 3. Role word: -. Exclude word: Director. Location: pass (San Francisco, CA).
Topic words: `sql`, `evaluation`, `agents` (×2)

> `sql` → …llenges Have hands-on experience with revenue recognition tools (e.g., Workday Financial Management, Zuora RevPro) Have SQL proficiency for querying and analyzing large revenue and contract datasets Have proven ability to lead cross-functio…
> `evaluation` → …ct offerings (NPI) and programs, serving as the accounting decision-maker on performance obligation identification, SSP evaluation, and contract modification frameworks, and providing authoritative guidance to Product, Pricing, and GTM cros…
> `agents` → …accounting guidance on partnership and marketplace arrangements for cloud third-party channels, including principal-vs-agent determinations, and revenue-share / co-sell economics Own key accounting processes such as SSP analysis and relate…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “Have 14+ years of progressive accounting experience, with extensive expertise in ASC 606 implementation and complex revenue recognitio” · “n scenarios, including 4+ years in a technical revenue leadership or managerial role”

<details><summary>Posting text (excerpt)</summary>

About the role 

 We are looking for a Director, Technical Revenue Accounting to join our Accounting Team. In this role, you will own the company’s most complex ASC 606 technical positions, lead the revenue accounting memo portfolio, and serve as the senior accounting decision-maker for new product revenue recognition treatments, non-standard deal structures, and partnership / marketplace go-to-market initiatives. You will partner directly with Deal Desk, Product, Legal, and Partnership leadership and set the technical revenue policy direction for the company! If you are looking for an opportunity to make a significant impact on the financial infrastructure of an innovative company, come join us in our mission to build cutting-edge, safe AI.

 Key responsibilities 

 
 Own the company’s ASC 606 technical accounting memo portfolio — authoring and reviewing position papers on the most comp…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** agents ("principal-vs-agent", an accounting term)

### R21 · greenhouse/anthropic · 5363469008

**Staff Software Engineer, Growth** · San Francisco, CA | New York City, NY | Seattle, WA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5363469008)

Filter v0.1: **reject**. exclude word in title: 'Staff'. Score 0. Role word: -. Exclude word: Staff. Location: pass (San Francisco, CA).
Topic words: none


False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “5+ years of experience as a software engineer”

<details><summary>Posting text (excerpt)</summary>

About the role 

 We are looking for growth engineers to join our growth team. This key role will help drive user acquisition, engagement, retention, and monetization through data-driven strategies and technical implementations. At Anthropic, we're not just building AI tools; we're reimagining how AI can enhance and expand its user base! As a member of the growth team, you will have a unique opportunity to shape our growth strategy. You will work with a cross-functional team of engineers, data scientists, marketers, and product managers to design, implement, and optimize growth initiatives that scale our AI-powered tools and maximize their impact.

 Key responsibilities 

 
 Develop and implement technical solutions to support user acquisition, activation, retention, and revenue growth

 Design and execute A/B tests and experiments to optimize user onboarding, feature adoption, subscript…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R22 · greenhouse/anthropic · 5439499008

**Applied AI Architects, Partner** · Tokyo, Japan · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5439499008)

Filter v0.1: **reject**. location is not one Priya accepts. Score 2. Role word: Applied AI. Exclude word: -. Location: fail.
Topic words: `llm`, `machine learning`

> `llm` → …lders Experience designing scalable cloud architectures and integrating with enterprise systems Familiarity with common LLM frameworks and tools or a background in machine learning or data science Excitement for engaging in cross-organizati…
> `machine learning` → …chitectures and integrating with enterprise systems Familiarity with common LLM frameworks and tools or a background in machine learning or data science Excitement for engaging in cross-organizational collaboration, working through trade-of…

False-friend check:
> `training`: …h 



 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “5+ years of experience in technical customer-facing/partner-facing roles such as Solutions Architect, Sales Engineer, Partner Sa”

<details><summary>Posting text (excerpt)</summary>

About the role 

 As a Partners Solutions Architect on the Applied AI team at Anthropic, you will be a Pre-Sales architect focused on cultivating technical relationships with our Global and Regional System Integrators (GSIs/RSIs), and our cloud partners (AWS and GCP). You will strengthen our relationships with key partners to accelerate indirect revenue, enable their AI practices, and execute on long-term GTM strategy.

 Key Responsibilities 

 
 
 Strategic Technical Partnership : Be a technical thought partner to the Anthropic GTM partnerships team, providing technical expertise to better understand the partner landscape, driving key strategic programs, and identifying opportunities to deepen partner technical capabilities. Embed with GSI and cloud partner technical teams to enable their AI practices, support troubleshooting, evangelize Anthropic in their developer communities, and ser…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R23 · greenhouse/anthropic · 5398829008

**Transaction Principal, EU** · London, UK · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5398829008)

Filter v0.1: **reject**. exclude word in title: 'Principal'. Score 1. Role word: -. Exclude word: Principal. Location: fail.
Topic words: `evaluation`

> `evaluation` → …ties Lead the RFP and commercial sourcing process for European data center deals, managing developer outreach, proposal evaluation, and competitive selection across multiple markets Negotiate term sheets and manage the LOI process, structur…

False-friend check:
> `training`: …BP 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “Have 10+ years of experience in transaction management, commercial real estate, data center leasing, or infrastructure procurement”

<details><summary>Posting text (excerpt)</summary>

About the role 
 As a Transaction Principal for Europe at Anthropic, you'll drive the commercial sourcing and transaction execution process for our European data center capacity deals. You'll lead RFP processes, negotiate term sheets, and serve as the central leader ensuring seamless stakeholder alignment from initial sourcing through lease execution.
 This role is critical to securing the infrastructure that powers Anthropic's frontier AI systems across Europe — you'll bridge commercial negotiations with complex internal coordination across legal, finance, engineering, and network teams, and partner closely with our Compute Markets team who own the Europe market strategy and government relationships. This is not an established leasing org; you'll be building process alongside execution, and doing so across multiple countries with distinct regulatory, power, and development dynamics.
 Re…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R24 · greenhouse/anthropic · 5457043008

**Product Manager, Claude Marketplace** · San Francisco, CA | New York City, NY · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5457043008)

Filter v0.1: **reject**. exclude word in title: 'Manager'. Score 1. Role word: -. Exclude word: Manager. Location: pass (San Francisco, CA).
Topic words: `llm`

> `llm` → …operational workflows behind it, and were the person accountable for its outcomes Have built with or shipped on top of large language models, and have used them to make a product experience better Have led cross-functional work where most…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “8+ years of product management experience”

<details><summary>Posting text (excerpt)</summary>

About the role 

 
 
 
 
 
 The vision for Claude Marketplace is to create an ecosystem flywheel, connecting builders and buyers. We're hiring a Product Manager to own the Marketplace as a product, for the partners who sell on it and the customers who buy through it. You'll work closely with the Marketplace team, which owns the partner and customer relationships as well as the commercial motion, and build on systems owned by other product and engineering teams. You'll have a lot of room to define and build the experience fitting for an AI native world.











 Key responsibilities 

 
 Own the Marketplace product end to end for partners and customers, from onboarding and listing through purchase and billing

 Design the commercial workflows behind the Marketplace from first principles, so they scale and meet partners' and customers' finance, audit and compliance requirements

 Shape…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R25 · greenhouse/anthropic · 5456491008

**Customer Success Manager** · Tokyo, Japan · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5456491008)

Filter v0.1: **reject**. exclude word in title: 'Manager'. Score 0. Role word: -. Exclude word: Manager. Location: fail.
Topic words: none


False-friend check:
> `training`: …ayer

 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “6+ years of experience in relevant field”

<details><summary>Posting text (excerpt)</summary>

About Anthropic 

 Anthropic’s mission is to create reliable, interpretable, and steerable AI systems. We want AI to be safe and beneficial for our users and for society as a whole. Our team is a quickly growing group of committed researchers, engineers, policy experts, and business leaders working together to build beneficial AI systems.

 About the Role 
 Join Anthropic's Customer Success team as one of the founding members of our Japan Customer Success team as we pioneer the future of enterprise AI adoption. As a Customer Success Manager at Anthropic, you'll be the strategic partner and trusted advisor to our most complex customers across Japan, helping them harness the full potential of all our Claude capabilities: API, Claude for Enterprise, and Claude Code.
 You'll develop genuine partnerships with customers, gaining a deep understanding of their business objectives, strategic dire…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R26 · ashby/notion · a8143379-6693-4046-b8cf-1528178d0f0f

**CX Systems & Automation Lead** · San Francisco, California; Remote · [original posting](https://jobs.ashbyhq.com/notion/a8143379-6693-4046-b8cf-1528178d0f0f)

Filter v0.1: **reject**. exclude word in title: 'Lead'. Score 3. Role word: -. Exclude word: Lead. Location: fail.
Topic words: `python`, `sql`, `agents` (×4)

> `python` → …rations, and have partnered with technical teams to deploy AI agents in a support environment; scripting (JavaScript or Python) or integration tools (e.g., Workato, Zapier) are a plus - You're as comfortable in a strategy discussion as in t…
> `sql` → …Cloud, Fin); experience running or migrating between platforms is a plus - You're comfortable with APIs, webhooks, and SQL, have built custom integrations, and have partnered with technical teams to deploy AI agents in a support environmen…
> `agents` → WHO WE ARE Notion is the collaborative AI workspace where teams and agents think together https://www.youtube.com/watch?v=vkpYpWfEK5s. We're building one place where your knowledge, projects, meetings, and AI tools live side by side, so wor…

Experience lines in the text: “- You have 7+ years of relevant experience, ideally in SaaS or AI, with deep hands-on administration of an enterprise helpdesk or CRM (e”

<details><summary>Posting text (excerpt)</summary>

WHO WE ARE

Notion is the collaborative AI workspace where teams and agents think together https://www.youtube.com/watch?v=vkpYpWfEK5s. We're building one place where your knowledge, projects, meetings, and AI tools live side by side, so work is faster, clearer, and less fragmented. Millions of individuals, small teams, and large companies run their work on Notion.



Notinos (our employees) are customer zero in bringing this future of work to life. We care about craft, building things that last, and the belief that great work is still fundamentally human. Our goal isn’t to ship the next feature. Each and every team of Notinos is working to set the standard for how humans work together in the AI era. From building a business’s system of record to making and managing AI agents to automating away the busy work, we care deeply about giving our customers more time for their life’s work.…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R27 · greenhouse/anthropic · 5425680008

**Procurement Operations Business Partner - Workplace, Security and People** · San Francisco, CA | Seattle, WA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5425680008)

Filter v0.1: **reject**. no role word in title and 0 topic words < T=3. Score 0. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: none


False-friend check:
> `training`: …recruiting agencies and recruiting operations, HR systems, benefits and Total Rewards vendors, and training and development.

 You will be the person who makes all of it feel simple to the teams who…
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…

Experience lines in the text: “5 to 7+ years of procurement operations, purchasing, or vendor operations, including time supporting Workplace or Facilities, Securit”

<details><summary>Posting text (excerpt)</summary>

About the role 

 Procurement Operations is the front door for buying at Anthropic. We sit inside Finance Operations and own the path from "I need to buy something" to a signed agreement, an accurate purchase order, and clean spend data at month end.

 We are hiring a Procurement Operations Business Partner to own that path for the teams that keep Anthropic's offices, people, and physical spaces running. Workplace covers real estate, office build outs and leases, furniture and equipment, facilities services, maintenance, and food and beverage. Security covers physical security: guard services, access control and badging, cameras, and security consulting that protect our offices and people. People covers recruiting agencies and recruiting operations, HR systems, benefits and Total Rewards vendors, and training and development.

 You will be the person who makes all of it feel simple to th…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R28 · greenhouse/anthropic · 5427309008

**APAC Recruiting Coordinator** · Singapore · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5427309008)

Filter v0.1: **reject**. location is not one Priya accepts. Score 0. Role word: -. Exclude word: -. Location: fail.
Topic words: none


False-friend check:
> `training`: …ety.

 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “4+ years of experience in recruiting coordination or high volume scheduling, ideally supporting multiple APAC markets”

<details><summary>Posting text (excerpt)</summary>

About the role  

 Anthropic is growing quickly across Asia Pacific, and our International Recruiting Coordination team is building for it. As our first Recruiting Coordinator based in Singapore, you'll deliver a warm, high touch interview experience for candidates across APAC, including Japan, Korea, India, Australia, New Zealand and South East Asia. You'll partner closely with our APAC recruiters and recruiting managers, be the local point of contact for candidates and interviewers in the region and help keep hiring moving around the clock as part of a follow the sun coordination model with your teammates.

 As you'll be first in seat, you'll also help shape how coordination works in a region where we're still building: spotting what's missing, documenting what works and making it easier for the people who join after you.

 You'll own coordination for your region end to end and act as…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R29 · greenhouse/anthropic · 5451912008

**Director, Order-to-Cash Assurance** · San Francisco, CA | Seattle, WA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5451912008)

Filter v0.1: **reject**. exclude word in title: 'Director'. Score 1. Role word: -. Exclude word: Director. Location: pass (San Francisco, CA).
Topic words: `sql`

> `sql` → …ing systems, billing platforms, or ERP systems (for example Salesforce, Stripe, or Workday Financials) Proficiency with SQL or similar tools for analyzing and testing transactional data Experience using automation or AI for monitoring, test…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “10+ years of progressive experience in revenue operations, billing operations, revenue assurance, finance operations, or internal”

<details><summary>Posting text (excerpt)</summary>

About the role

 Anthropic's global order-to-cash (O2C) function is scaling faster than the processes and systems behind it, across direct enterprise contracts, consumption-based commercial models, and third-party cloud marketplaces. We're looking for a Director, Order-to-Cash Assurance to make sure every order is priced, billed, collected, and recorded correctly, and that we can prove it.

 You'll be embedded in the O2C Transformation team, working closely with Order Management, AR & Collections, Revenue Accounting, Billing Engineering, and Go-to-Market. You'll design and run the pricing audits and accuracy measures that show us where we leak revenue or create rework, then fix the root cause at the source. You'll be the compliance advocate for global O2C, helping the business find the compliant way to yes, and often improving a process by removing steps rather than adding them.

 You'll…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### R30 · ashby/notion · 8109628c-ff17-4e90-b388-d159dc1c53ca

**Solutions Consultant, Enterprise, MEDIT** · Dublin, Ireland · [original posting](https://jobs.ashbyhq.com/notion/8109628c-ff17-4e90-b388-d159dc1c53ca)

Filter v0.1: **reject**. location is not one Priya accepts. Score 2. Role word: -. Exclude word: -. Location: fail.
Topic words: `evaluation`, `agents` (×2)

> `evaluation` → …discovery, qualify business needs and urgency, align stakeholders, shape the solution and business case, and drive the evaluation and commercial decision. Navigate commercial sizing, proposal construction, procurement, legal, and security…
> `agents` → WHO WE ARE Notion is the collaborative AI workspace where teams and agents think together https://www.youtube.com/watch?v=vkpYpWfEK5s. We're building one place where your knowledge, projects, meetings, and AI tools live side by side, so wor…

False-friend check:
> `pipeline`: …ing together technical fluency and commercial ownership to grow your book of business. You’ll build pipeline with BDRs, engage key stakeholders, lead discovery, co-build workflow solutions live with c…
> `pipeline`: …rsection of AI, productivity, and enterprise—this is the role.

 


WHAT YOU'LL ACHIEVE:

 - Create pipeline across your book of business. Build target-account plans with BDRs and initiate outreach to…

<details><summary>Posting text (excerpt)</summary>

WHO WE ARE

Notion is the collaborative AI workspace where teams and agents think together https://www.youtube.com/watch?v=vkpYpWfEK5s. We're building one place where your knowledge, projects, meetings, and AI tools live side by side, so work is faster, clearer, and less fragmented. Millions of individuals, small teams, and large companies run their work on Notion.



Notinos (our employees) are customer zero in bringing this future of work to life. We care about craft, building things that last, and the belief that great work is still fundamentally human. Our goal isn’t to ship the next feature. Each and every team of Notinos is working to set the standard for how humans work together in the AI era. From building a business’s system of record to making and managing AI agents to automating away the busy work, we care deeply about giving our customers more time for their life’s work.…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

## Part: close-calls (15)

### C01 · greenhouse/anthropic · 5406367008

**Cyber Evaluations Engineer** · Remote-Friendly, United States; San Francisco, CA | Washington, DC · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5406367008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (Remote-Friendly, United States).
Topic words: `python`, `evaluation` (×10)

> `python` → …experience (e.g., CTF participation, vulnerability research, exploit development, or security research) Proficiency in Python Strong ability to communicate evaluation results with multiple cross-functional stakeholders or potential policy…
> `evaluation` → …policy experts, and business leaders working together to build beneficial AI systems. About the role We're hiring Cyber Evaluations Engineers to build and run the evaluations that measure cyber-relevant capabilities and safeguard robustness…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

<details><summary>Posting text (excerpt)</summary>

About the role 

 We're hiring Cyber Evaluations Engineers to build and run the evaluations that measure cyber-relevant capabilities and safeguard robustness in our models. You'll design new evals, run per-release robustness testing, and dig into data on jailbreaks and prompt bypasses to understand where our safeguards hold up and where they don't. You'll also design many of the probes that detect cyber abuse in production and help shape the overall detection architecture alongside the policy team. 

 Key responsibilities 

 
 
 Design and run capability, uplift, and safety evaluations to assess cyber-relevant risk in new models



 
 Execute per-release safeguard-robustness testing ahead of major model launches



 
 Analyze evaluation results and communicate findings clearly to the team and to stakeholders



 
 Design, prototype, and tune detection probes for cyber misuse



 
 Work w…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C02 · greenhouse/anthropic · 5462893008

**Enforcement Analyst, Agentic Alignment** · Boston, MA; San Francisco, CA | Seattle, WA | New York City, NY | Washington, DC · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5462893008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (Boston, MA).
Topic words: `python`, `agents` (×8)

> `python` → …eports on agentic harm trends and enforcement outcomes Minimum qualifications Can read and understand code (for example Python, JavaScript or shell scripts) well enough to follow what happened and why it matters Have a background in securit…
> `agents` → …ms. We want AI to be safe and beneficial for our customers and society as a whole. As an Enforcement Analyst focused on Agentic Alignment, you will play a crucial role in identifying and investigating harmful and unexpected behavior by mode…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

<details><summary>Posting text (excerpt)</summary>

About the role 

 Anthropic is an AI safety and research company working to build reliable, interpretable, and steerable AI systems. We want AI to be safe and beneficial for our customers and society as a whole. As an Enforcement Analyst focused on Agentic Alignment, you will play a crucial role in identifying and investigating harmful and unexpected behavior by models, and make enforcement decisions accordingly. You'll work closely with a suite of cross-functional teams, within and outside of Safeguards, including: Policy, Threat Intel, Engineering, Research, and Transparency. Your work will be essential in maintaining Anthropic's commitment to safe and beneficial AI as Claude takes on more autonomous work.

 Important context for this role: In this position you may be exposed to and engage with explicit content spanning a range of topics, including those of a sexual, violent, or psycho…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C03 · greenhouse/anthropic · 5396384008

**IT Systems Engineer, Mobile Client Platform Engineer** · Boston, MA; Remote-Friendly (Travel-Required) | San Francisco, CA | Seattle, WA | New York City, NY; Washington, DC · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5396384008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (Boston, MA).
Topic words: `python`, `llm`

> `python` → …g device tooling Have used LLMs to automate operational work, or are excited to make Claude a teammate Technical Skills Python and shell scripting iOS and Android platform internals (depth on iOS, working knowledge of Android) Modern MDM or…
> `llm` → …sive rollout systems with promotion gated on telemetry Bring proficiency in Swift for building device tooling Have used LLMs to automate operational work, or are excited to make Claude a teammate Technical Skills Python and shell scripting…

False-friend check:
> `pipeline`: …al coverage, spares, and refresh cycles

 Bring mobile configuration into the team’s config-as-code pipeline so mobile policies are reviewed, tested, and progressively rolled out like the rest of the…
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “Have owned a global or multi-region mobile device program end to end, with 8+ years managing corporate fleets at thousands-of-devices scale”

<details><summary>Posting text (excerpt)</summary>

About the role

 The Endpoint team (Client Platform Engineering) manages the laptops and handsets every Anthropic employee works on, plus the infrastructure underneath them. We treat the fleet as a distributed platform, not a collection of devices, and every piece of configuration ships as code through pull requests, CI, staging, and a canary group. Today the mobile side of the fleet is BYOD. This role exists to change that. You will design and implement a corporate-issued mobile device program (managed company phones and managed Apple accounts) in every region Anthropic operates in, and take it from early design to production.

 The team is deliberately lean and runs with high autonomy. You’ll define what a corporate mobile program looks like at Anthropic and own the platform decisions that get it there.

 Responsibilities

 
 Design the corporate-issued mobile device program: device st…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C04 · greenhouse/anthropic · 4020350008

**Performance Engineer** · San Francisco, CA | New York City, NY | Seattle, WA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/4020350008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `llm`, `machine learning` (×3)

> `llm` → …ternals Language modeling with transformers Representative projects: Implement low-latency high-throughput sampling for large language models Implement GPU kernels to adapt our models to low-precision inference Write a custom load-balancing…
> `machine learning` → …ngineers, policy experts, and business leaders working together to build beneficial AI systems. About the role: Running machine learning (ML) algorithms at our scale often requires solving novel systems problems. As a Performance Engineer,…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

<details><summary>Posting text (excerpt)</summary>

About the role:



 Running machine learning (ML) algorithms at our scale often requires solving novel systems problems. As a Performance Engineer, you'll be responsible for identifying these problems, and then developing systems that optimize the throughput and robustness of our largest distributed systems. Strong candidates here will have a track record of solving large-scale systems problems and will be excited to grow to become an expert in ML also.



 You may be a good fit if you:

 
 Have significant software engineering or machine learning experience, particularly at supercomputing scale

 Are results-oriented, with a bias towards flexibility and impact

 Pick up slack, even if it goes outside your job description

 Enjoy pair programming (we love to pair!)

 Want to learn more about machine learning research

 Care about the societal impacts of your work

 
 Strong candidates ma…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C05 · greenhouse/anthropic · 5477464008

**Security Risk & Compliance, SOX IT** · San Francisco, CA | Seattle, WA | New York City, NY | Washington, DC · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5477464008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `llm`, `agents` (×2)

> `llm` → …ors, and can work independently on complex workstreams while keeping senior stakeholders informed. Use Claude and other LLMs as daily working tools, and have grounded, specific views on which SOX assurance workflows AI can run today and whi…
> `agents` → …etrofitted after the fact. Pressure-test changes for SOX impact during design. Review major infrastructure, system, and agent framework changes for control impact while decisions are still cheap, and keep a clear view of which changes alter…

False-friend check:
> `pipeline`: …uency, possibly from an earlier engineering career: you can read code and Terraform, follow a CI/CD pipeline end to end, and challenge a design on its technical merits.

 Have deep familiarity with de…
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “12+ years of hands-on IT audit and SOX compliance experience”

<details><summary>Posting text (excerpt)</summary>

About the role 

 Anthropic's Security Governance, Risk, and Compliance (GRC) team is the connective tissue that holds the company accountable to its security and control commitments. We translate regulatory, customer, and voluntary obligations into controls that teams act on, and give leadership a bird's-eye view of how well we're meeting them. We're building continuous assurance, to challenge and evidence the performance of controls continuously rather than through periodic audits.

 As Anthropic scales to meet public-company standards, the Sarbanes-Oxley (SOX) control environment over our technology stack is one of the most consequential things this team will drive. Within Security GRC's technical controls assurance function, you will be a hands-on senior contributor on what the IT general controls must achieve to support SOX 404 compliance. You will work as a peer to Internal Audit's…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C06 · greenhouse/anthropic · 5107890008

**Data Center Controls Engineer** · Remote-Friendly (Travel Required) | San Francisco, CA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5107890008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `sql`

> `python` → …nd in database integration (SQL Server, InfluxDB, PostgreSQL, TimescaleDB) and data logging architecture Proficiency in Python or scripting for automation/configuration within SCADA/BMS frameworks Experience deploying multi-site redundant c…
> `sql` → …BMS/SCADA systems such as Ignition, Niagara/Tridium, Wonderware, or similar Strong background in database integration (SQL Server, InfluxDB, PostgreSQL, TimescaleDB) and data logging architecture Proficiency in Python or scripting for auto…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “7+ years of experience in control systems design and implementation for industrial automation, building automation, or datacente” · “10+ years in datacenter, critical facilities, or mission-critical infrastructure environments”

<details><summary>Posting text (excerpt)</summary>

Responsibilities 

 System Architecture & Integration 

 
 
 Design and implement multi-site controls architecture across Anthropic's global datacenter facilities



 
 Define network topology, redundancy, and high-availability requirements for control nodes and servers



 
 Develop and maintain standardized frameworks for BACnet, Modbus TCP/IP, OPC-UA, MQTT, and SNMP communication layers



 
 Ensure integration between control systems and enterprise networks while maintaining security boundaries and compliance with cybersecurity frameworks for industrial control systems



 
 Control System Design & Implementation 

 
 
 Define, design, develop, and implement control systems for datacenter mechanical, electrical, and building management systems with focus on AI compute environments



 
 Develop SCADA/BMS applications using platforms including Ignition, Niagara/Tridium, or similar HMI…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C07 · greenhouse/anthropic · 5413418008

**Research Counsel** · San Francisco, CA | New York City, NY · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5413418008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `evaluation` (×2), `machine learning`

> `evaluation` → …oss the full lifecycle of building and studying frontier AI models: data acquisition and use, training pipelines, model evaluation and launch, and alignment, interpretability, model welfare, societal impacts, and beneficial deployments rese…
> `machine learning` → …at often have no settled answer. The ideal candidate will have navigated complex legal questions at the intersection of machine learning, data, and academic research in a fast-moving technical environment, with the judgment to work at the c…

False-friend check:
> `training`: …cs across the full lifecycle of building and studying frontier AI models: data acquisition and use, training pipelines, model evaluation and launch, and alignment, interpretability, model welfare, soc…
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…

Experience lines in the text: “At least 8 years of legal experience advising technology companies on copyright, privacy, data, AI regulation, and related product and p”

<details><summary>Posting text (excerpt)</summary>

About the role 

 As a member of the Research Legal team, you'll advise on legal topics across the full lifecycle of building and studying frontier AI models: data acquisition and use, training pipelines, model evaluation and launch, and alignment, interpretability, model welfare, societal impacts, and beneficial deployments research, as well as Responsible Scaling Policy work on biological risk. You'll be a subject matter expert on copyright, privacy, data use, and AI regulation (including the EU AI Act, U.S. state laws, and emerging global rules), and will work directly with researchers on questions that often have no settled answer.

 The ideal candidate will have navigated complex legal questions at the intersection of machine learning, data, and academic research in a fast-moving technical environment, with the judgment to work at the cutting edge of AI development while effectively…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C08 · greenhouse/anthropic · 5456619008

**3P Revenue Accounting & Reporting** · San Francisco, CA | Seattle, WA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5456619008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `sql` (×2), `agents` (×2)

> `sql` → …nical Accounting on complex judgments. Partner with the Engineering teams to automate manual close processes, including SQL-driven workbooks, automated reconciliations and system-generated journal entries. Own 3P SOX controls, including des…
> `agents` → …nd drive reporting improvements that support an on-time close. Apply ASC 606 to 3P arrangements, including principal-vs-agent, variable consideration and reseller arrangements. Estimate and document reserves, including credit loss (ASC 326)…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “Have 10+ years of progressive accounting experience, including 3+ years managing revenue accounting or close teams”

<details><summary>Posting text (excerpt)</summary>

About the role 

 We are looking for a Senior Manager, 3P Revenue Accounting & Reporting to join our Accounting team. You will own revenue recognition, month-end close and reporting for Claude sold through our cloud service provider (CSP) channels: AWS Bedrock, Google Cloud Vertex AI and Microsoft Azure Marketplace. These channels are among the fastest-growing revenue streams at the company. They run on consumption-based, partner-reported data that changes every month.

 You will be the accounting point of contact for the finance and partner teams at AWS, Google and Microsoft. Internally, you will partner with Finance, FAB, Engineering and business teams to turn partner billing feeds into accurate, auditable revenue. You will also lead the automation of a close that is still heavily manual. If you want to build the financial infrastructure behind a fast-growing AI company, come join us i…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** agents ("principal-vs-agent", an accounting term)

### C09 · greenhouse/anthropic · 5423737008

**IT Operations Engineer, Asset Management** · San Francisco, CA | New York City, NY · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5423737008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `evaluation`

> `python` → …ndidates may also Have supported a corporate mobile program or carrier account Have basic scripting experience (Bash or Python) for inventory or reporting automation Have experience using AI tools to improve personal or team productivity Ha…
> `evaluation` → …develop the processes on-site engineers in each office execute against, including the storage room process Support the evaluation and onboarding of a hardware lifecycle services vendor and, once in place, run the day-to-day relationship In…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

<details><summary>Posting text (excerpt)</summary>

About the role

 The IT Operations team keeps Anthropic running. We make sure every employee can do their best work without friction. We're hiring an IT Operations Engineer to develop our global asset management and hardware lifecycle program across our offices in San Francisco, New York, Seattle, London, Dublin and Sydney. You will bring program expertise to how we track hardware as inventory through its whole life: procurement and receiving, the inventory of record, assignment, refresh, collection and recovery, e-waste and secure disposal, and reseller relationships, iterating and scaling practices as we mature. The same person runs day-to-day operations for our corporate mobile program in addition to expertise in management of laptop and workstation lifecycle operations.

 You'll partner with several teams within the IT, Security and business operations organizations: IT Hardware Ops…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C10 · greenhouse/anthropic · 5490572008

**Strategic Account Executive, Hedge Funds** · New York City, NY · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5490572008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (New York City, NY).
Topic words: `llm`, `evaluation`

> `llm` → …vance Anthropic's mission of building safe, beneficial AI Preferred qualifications Experience bringing generative AI or LLM-based products, or other emerging platform technologies, to hedge funds Deep familiarity with regulated-industry sel…
> `evaluation` → …thin your accounts, building and executing account plans that turn strategic relationships into committed revenue Drive evaluation, deployment, and adoption of Claude within your accounts across research, engineering, and operations, turnin…

False-friend check:
> `pipeline`: …rch, engineering, and operations, turning early wins into durable, scaled usage

 Run a disciplined pipeline and forecasting cadence: consistent pipeline generation, accurate deal inspection, clear ne…
> `pipeline`: …ly wins into durable, scaled usage

 Run a disciplined pipeline and forecasting cadence: consistent pipeline generation, accurate deal inspection, clear next steps, and predictable, coachable executio…
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “5+ years of enterprise sales experience, with demonstrated success selling into hedge funds”

<details><summary>Posting text (excerpt)</summary>

About the role 

 As a Strategic Account Executive (Hedge Funds) at Anthropic, you'll join our new Hedge Funds sales team within Enterprise FSI, bringing frontier AI to the world's leading hedge funds: multi-strategy platforms, quantitative and systematic firms, discretionary long/short equity, global macro, and credit funds. These are some of the most technically sophisticated and competitive organizations in financial services, rethinking how they generate ideas, conduct research, build and test strategies, manage risk, and run their operations. They're looking for a partner they trust to take frontier AI from promising experiments into production across research, engineering, and operations.

 The ideal candidate is energized by building a new category in a highly competitive industry, identifying high-potential opportunities within each fund and running the strategies to win them. Th…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C11 · greenhouse/anthropic · 5485188008

**Research Engineer, Beneficial Deployments** · San Francisco, CA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5485188008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `llm` (×3), `evaluation`

> `llm` → …L research teams and product teams to align on capability goals Minimum qualifications Have experience with fine-tuning large language models for specific domains or real-world use cases Have experience with reinforcement learning, reward d…
> `evaluation` → …trategy and influence Preferred qualifications Have experience training production ML systems Have experience designing evals or benchmarks for LLMs Have domain expertise in healthcare, global health, or philanthropy Have experience with mu…

False-friend check:
> `training`: …als used to train them, run experiments, and measure whether new capabilities generalize beyond the training data. You'll also work closely with the Beneficial Deployments team, using your knowledge o…
> `training`: …wn the end-to-end process of creating RL environments, from task sourcing and reward design through training, using both real-world and synthetic data

 Collaborate with domain experts to design data…

<details><summary>Posting text (excerpt)</summary>

About the role

 Beneficial Deployments ensures AI reaches and benefits the communities that need it most. We partner with nonprofits, foundations, and mission-driven organizations to deploy Claude in education, global health, economic mobility, and life sciences — focusing on raising the floor for those who need it most.

 We're looking for a Research Engineer to make Claude better at the real-world work that matters most to Beneficial Deployments. You'll identify where our models fall short, build the environments and reward signals used to train them, run experiments, and measure whether new capabilities generalize beyond the training data. You'll also work closely with the Beneficial Deployments team, using your knowledge of the capability frontier to advise on how they can achieve their goals over the coming years.

 Key responsibilities

 
 Identify capability gaps in our models an…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C12 · greenhouse/anthropic · 5457137008

**Audit, Security GRC** · San Francisco, CA | Seattle, WA | New York City, NY | Washington, DC · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5457137008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `llm`, `evaluation`

> `llm` → …l schemes (for example IRAP, ISMAP or C5) Have automated evidence collection or audit reporting, or use Claude or other LLMs day to day to plan, track and report program work Experience with a GRC platform or building lightweight internal t…
> `evaluation` → …ection with GRC Engineering Plan new audits and audit expansions as we commit to them Run framework and scope expansion evaluations and gap assessments, with a recommendation and an effort estimate leadership can act on Work closely with co…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

<details><summary>Posting text (excerpt)</summary>

About the role 

 You'll help run Anthropic's unified audit program: quarterly audits across SOC 2, HIPAA and the ISO 27000 family including ISO 42001, plus the rest of our certifications, working with our audit firms, our GRC Partners, and control owners across the company. You'll plan new audits as we expand to new frameworks, platforms and regions, and run the gap assessments that tell us what each expansion takes before we commit to it.

 You'll help build the audit operating model and runbook, and drive automation in the program so evidence is collected once and reused across frameworks, requests reach control owners once, and each audit cycle takes less effort than the last. Building with Claude is a normal part of the job, with you deciding where human judgment stays in the loop.

 This is an individual contributor role for someone with program management experience who writes cle…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C13 · greenhouse/anthropic · 5432000008

**Commercial Legal Specialist, Technical AI Implementation** · San Francisco, CA | New York City, NY · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5432000008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `llm` (×2), `machine learning`

> `llm` → …ment systems, or document management tools Show genuine curiosity about AI/ML applications and hands-on experience with LLM tools (especially Claude!) Possess excellent problem-solving skills and can translate legal business needs into scal…
> `machine learning` → …echnical aptitude with system integration knowledge Familiarity with common LLM frameworks and tools or a background in machine learning or data science Excellent verbal and written communication, analytical, collaboration, and interpersona…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “At least 5 years of relevant experience in legal operations, legal technology, or technical roles supporting legal teams”

<details><summary>Posting text (excerpt)</summary>

About the role 

 Join Anthropic's Commercial Legal team as a Technical AI implementation specialist, where you'll be responsible for leveraging Claude and other technologies to scale and increase efficiency of legal operations. You'll drive AI adoption across team workflows, optimize internal tooling, and lead cross-functional initiatives to enhance productivity. This role offers the unique opportunity to shape the future of legal operations through technology while working with Claude and other business critical systems.

 Key responsibilities 

 
 Implement AI-powered solutions to streamline contract review and redlining processes

 Manage integrations between existing legal systems and AI tools

 Develop automated self-service solutions for high-volume, low-touch contracting processes, including FAQ chatbots and guided workflows

 Create AI-based tools for handling commercial contrac…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C14 · greenhouse/anthropic · 5421263008

**Software Engineer, Tokens and Prompt Structures** · San Francisco, CA | New York City, NY · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5421263008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `llm`

> `python` → …other text/data encoding systems Maintaining a widely-used library over a long period of time Performance optimization Python and/or Rust Reinforcement learning or model training infrastructure Representative projects: Working with a resea…
> `llm` → …th meaningful time spent maintaining libraries, SDKs, or developer-facing APIs Have familiarity with ML terminology and LLM architecture — you don't need to be an ML expert, but enough understanding to work effectively alongside researchers…

False-friend check:
> `training`: …time



 
 Performance optimization



 
 Python and/or Rust



 
 Reinforcement learning or model training infrastructure



 
 Representative projects: 

 
 
 Working with a research team to ship a…
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…

Experience lines in the text: “Have 5+ years of software engineering experience, with meaningful time spent maintaining libraries, SDKs, or developer-facing APIs”

<details><summary>Posting text (excerpt)</summary>

Responsibilities: 

 
 
 Maintain and improve the encoding libraries used by engineers and researchers across Anthropic



 
 Run experiments to determine the optimal way to feed structured data into Claude without confusing it



 
 Design data structures and abstractions that shield most of the organization from the details of how encoded data works while enabling “power users”



 
 Adapt the encoding libraries to support new research directions as they emerge, and make sure that we can ship these research ideas to production



 
 Optimize encoding performance across the systems that depend on these libraries



 
 You may be a good fit if you: 

 
 
 Have 5+ years of software engineering experience, with meaningful time spent maintaining libraries, SDKs, or developer-facing APIs



 
 Have familiarity with ML terminology and LLM architecture — you don't need to be an ML expert, but…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### C15 · greenhouse/anthropic · 5387564008

**Research Scientist, Life Sciences (Chemistry)** · San Francisco, CA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5387564008)

Filter v0.1: **reject**. no role word in title and 2 topic words < T=3. Score 2. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `evaluation`

> `python` → …ations Computational chemistry, cheminformatics, or coding skills, for example quantum mechanical calculations (DFT) or Python with RDKit or pandas for data analysis and automation Experience using AI or ML tools in chemistry or the life sc…
> `evaluation` → …s, and formulations, and relate their composition and structure to their properties Coordinate synthesis and biological evaluation with external contract research organizations and academic partners Evaluate AI-designed molecules, AI-propos…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “5+ years of experience in your area of chemistry beyond the PhD”

<details><summary>Posting text (excerpt)</summary>

About the role

 Anthropic's Life Sciences team is building a research group focused on biological discoveries by combining AI with hands-on biological research. We're seeking research scientists with deep expertise in experimental chemistry to join the team. We welcome chemists from across the field, including medicinal, synthetic organic, physical organic, organometallic, inorganic, analytical, physical, and materials chemistry, as well as formulation science. Our goal is to speed up progress in the life sciences by an order of magnitude, and this role puts that mission into practice. You'll be an expert in your area of chemistry with hands-on experience designing, and running experiments, from synthesizing, purifying, and characterizing compounds to studying reaction mechanisms and kinetics. Above all, you'll close the loop between AI-generated hypotheses and experimental data to shar…

</details>

**My verdict:** reject
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

## Part: kept (10)

### K01 · greenhouse/anthropic · 5074217008

**Research Engineer, Visual Knowledge Work** · New York City, NY; San Francisco, CA; Seattle, WA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5074217008)

Filter v0.1: **keep**. 3 distinct topic words in text (T=3). Score 3. Role word: -. Exclude word: -. Location: pass (New York City, NY).
Topic words: `llm` (×3), `evaluation` (×4), `agents` (×2)

> `llm` → …for a research engineer who believes that visual and spatial reasoning are core to fully unlocking the capabilities of LLMs. On the Vision team, you'll own the end-to-end process of creating training data and RL environments targeting visu…
> `evaluation` → …ing data and RL environments targeting visual knowledge work: identifying long-horizon and vision-heavy tasks, building evals, designing rewards, and scaling data. This is a unique role that combines applied research with hands-on data work…
> `agents` → …training, SL, and RL on language models Deep learning research on images, video, or other modalities Developing complex agentic systems using LLMs Large-scale ETL and data pipeline development Representative projects: Writing a vendor-facin…

False-friend check:
> `pipeline`: …deo, or other modalities

 Developing complex agentic systems using LLMs

 Large-scale ETL and data pipeline development

 
 Representative projects: 

 
 Writing a vendor-facing specification for a n…
> `training`: …locking the capabilities of LLMs. On the Vision team, you'll own the end-to-end process of creating training data and RL environments targeting visual knowledge work: identifying long-horizon and visi…
> `training`: …ustry, academia, or other projects

 Have experience with reinforcement learning, reward design, or training data curation for large language or vision-language models

 Are familiar with the architec…

Experience lines in the text: “Have 7+ years of ML, computer vision, and software engineering experience through industry, academia, or other projects”

<details><summary>Posting text (excerpt)</summary>

About the role 

 We're looking for a research engineer who believes that visual and spatial reasoning are core to fully unlocking the capabilities of LLMs. On the Vision team, you'll own the end-to-end process of creating training data and RL environments targeting visual knowledge work: identifying long-horizon and vision-heavy tasks, building evals, designing rewards, and scaling data. This is a unique role that combines applied research with hands-on data work. It's also highly collaborative — you'll partner with external vendors, pretraining, RL, and product teams to make sure the environments you build translate into real-world knowledge work capabilities.

 What you'll do: 

 
 Own the data strategy for vision capabilities end-to-end, from building evals and scaling RL environments

 Manage technical relationships with external data vendors, including writing task specifications,…

</details>

**My verdict:** keep
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### K02 · greenhouse/anthropic · 5461863008

**Research Scientist, Life Sciences (Computational Chemistry)** · San Francisco, CA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5461863008)

Filter v0.1: **keep**. 4 distinct topic words in text (T=3). Score 4. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `llm`, `evaluation` (×4), `machine learning` (×3)

> `python` → …ic and medicinal chemistry, including reactions, synthesis, and SAR, with experimental data as your ground truth Strong Python skills and solid machine learning fundamentals, with hands-on experience training and evaluating models Comfort n…
> `llm` → …s, with strong written and verbal communication skills Preferred qualifications Experience with reinforcement learning, large language models, or building evaluations and benchmarks Track record of supporting drug discovery programs alongsi…
> `evaluation` → …and evaluating machine learning models. Above all, you'll build the reinforcement learning environments, datasets, and evaluations that teach Claude chemistry. Working alongside our bench chemists and AI researchers, you'll turn real chemi…

False-friend check:
> `training`: …hemist who knows reactions, synthesis, and medicinal chemistry in depth and has hands-on experience training and evaluating machine learning models. Above all, you'll build the reinforcement learning…
> `training`: …r bench chemists and AI researchers, you'll turn real chemistry problems and experimental data into training tasks and measure whether the models get better at them.

 This role is fully on-site in th…

<details><summary>Posting text (excerpt)</summary>

About the role

 Anthropic's Life Sciences team is building a research group focused on biological discoveries by combining AI with hands-on biological research. We're seeking a research scientist who combines deep chemistry knowledge with machine learning expertise to join the team. Our goal is to speed up progress in the life sciences by an order of magnitude, and this role puts that mission into practice. You'll be a computational chemist who knows reactions, synthesis, and medicinal chemistry in depth and has hands-on experience training and evaluating machine learning models. Above all, you'll build the reinforcement learning environments, datasets, and evaluations that teach Claude chemistry. Working alongside our bench chemists and AI researchers, you'll turn real chemistry problems and experimental data into training tasks and measure whether the models get better at them.

 This…

</details>

**My verdict:** keep
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### K03 · greenhouse/anthropic · 5017202008

**Software Engineer, Labs** · San Francisco, CA | New York City, NY | Seattle, WA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5017202008)

Filter v0.1: **keep**. 4 distinct topic words in text (T=3). Score 4. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `llm`, `evaluation`, `machine learning`

> `python` → …, without needing constant direction Have strong technical skills across modern web development stacks (React, Node.js, Python, etc.) and are comfortable with APIs, databases, and cloud technologies Communicate effectively and translate com…
> `llm` → …of your work Strong candidates may also have Experience building products that involve AI/ML components or working with large language models Experience collaborating directly with research teams in AI/ML environments Background conducting…
> `evaluation` → …product concepts Design and run structured experiments to test hypotheses, balancing creative exploration with rigorous evaluation Generate documentation and insights to guide successful prototypes toward full product teams Advocate for use…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “Have 8+ years of experience building full-stack applications, with a track record of zero-to-one work in startup or startup-like envi”

<details><summary>Posting text (excerpt)</summary>

About the role 

 At Anthropic, we're building AI systems that are safe, beneficial, and transformative. Our mission is to develop AI that benefits humanity, and we believe the most powerful capabilities emerge when we thoughtfully bridge the gap between research breakthroughs and real-world applications.

 Anthropic Labs serves as our internal accelerator. We're looking for the next breakout hits that bring substantial revenue or transform an industry. We operate in close partnership with research and build through fast iteration cycles. Past successes include Claude Code and MCP.

 We're seeking versatile, entrepreneurial engineers to join Labs. In this role, you'll work at the intersection of cutting-edge research and real-world application, rapidly building and testing new experiences, working directly with researchers and users, and generating the insights that shape Anthropic's pro…

</details>

**My verdict:** keep
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### K04 · greenhouse/anthropic · 5468939008

**Applied Scientist, Engineering** · San Francisco, CA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5468939008)

Filter v0.1: **keep**. 3 distinct topic words in text (T=3). Score 3. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `evaluation` (×2), `machine learning` (×2)

> `python` → …he computational design, analysis, or simulation tools used in your field Basic programming proficiency, for example in Python Ability to navigate ambiguity and develop solutions in a rapidly evolving research environment Ability to work in…
> `evaluation` → …ch and development, and to test Claude's designs against real-world feedback. Key responsibilities Design and implement evaluation methodologies for assessing AI model capabilities relevant to engineering and applied science research and ap…
> `machine learning` → …rs to establish benchmarks and gather high-quality data for training Translate between engineering domain knowledge and machine learning objectives Minimum qualifications Deep expertise and hands-on R&D or industry experience in an engineer…

False-friend check:
> `training`: …r.

 We're expanding our work on engineering and the applied sciences. Our goal is to contribute to training Claude to invent, design, and engineer across every discipline and scale, reliably and safe…
> `training`: …relevant to engineering and applied science research and applications

 Design realistic tasks and training environments, and curate data from your field

 Develop and validate simulations and comput…

Experience lines in the text: “5+ years of hands-on R&D or industry experience in an engineering or applied science discipline”

<details><summary>Posting text (excerpt)</summary>

About the role

 The Discovery team at Anthropic is organized around the north star goal of building an AI scientist – a system capable of solving the long-term reasoning challenges and basic capabilities necessary to push the scientific and technological frontier.

 We're expanding our work on engineering and the applied sciences. Our goal is to contribute to training Claude to invent, design, and engineer across every discipline and scale, reliably and safely: new manufacturing and experimental techniques, processes, materials, devices, instruments, machines, energy systems, and factories. We want this work to accelerate science and technology and benefit people widely.

 We're seeking exceptional researchers with deep expertise in one or more of these areas. In this role, you'll work at the intersection of frontier AI and your field, developing rigorous methods to measure and improve…

</details>

**My verdict:** keep
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### K05 · greenhouse/anthropic · 5487188008

**Software Engineer, Model-to-Product Behavior Engineering** · San Francisco, CA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5487188008)

Filter v0.1: **keep**. 4 distinct topic words in text (T=3). Score 4. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `llm` (×2), `evaluation` (×11), `machine learning`

> `python` → …new features and models meet quality and safety standards Minimum qualifications Strong software engineering skills in Python or a similar language, including version control, testing, and CI/CD Experience owning production systems end to…
> `llm` → …design and architecture through launch and ongoing operation Hands-on experience designing and building evaluations for LLMs, such as datasets, graders, metrics, or eval harnesses Understanding of evaluation methodology for AI systems, incl…
> `evaluation` → …e behaves in ways that are consistent, safe, and genuinely helpful, whether in a new feature, a new model, or a launch. Evals are one of the sharpest tools we have for getting Claude's behavior right, but not the only one. You'll build eval…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “5+ years of software engineering experience”

<details><summary>Posting text (excerpt)</summary>

About the role 

 We're looking for engineers to join Model-to-Product Behavior Engineering, the team responsible for getting Claude's behavior right across Anthropic's products. You'll work with product, research, and safeguards teams to make sure Claude behaves in ways that are consistent, safe, and genuinely helpful, whether in a new feature, a new model, or a launch.

 Evals are one of the sharpest tools we have for getting Claude's behavior right, but not the only one. You'll build evals to see clearly where Claude shines and where it slips, use what you learn to inform how to close the gap, and build the harness improvements that get us there. That takes your own intuition and judgment about model behavior, both to decide what is worth building and to know what to do with what you find. Your work will shape launch decisions and give research and product teams a signal they can trus…

</details>

**My verdict:** keep
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### K06 · greenhouse/anthropic · 5066995008

**Technical Cyber Threat Investigator** · San Francisco, CA; San Francisco, CA | New York City, NY | Washington, DC · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5066995008)

Filter v0.1: **keep**. 4 distinct topic words in text (T=3). Score 4. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `sql`, `llm` (×2), `machine learning`

> `python` → …establishing processes, tools, and best practices You may be a good fit if you Have demonstrated proficiency in SQL and Python for data analysis and threat detection Have experience with large language models and understanding of how AI tec…
> `sql` → …rogram, establishing processes, tools, and best practices You may be a good fit if you Have demonstrated proficiency in SQL and Python for data analysis and threat detection Have experience with large language models and understanding of ho…
> `llm` → …platform Create actionable intelligence reports on new attack vectors, vulnerabilities, and threat actor TTPs targeting LLM systems Conduct cross-platform threat analysis grounded in real threat actor behavior, using open-source research, d…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

<details><summary>Posting text (excerpt)</summary>

Responsibilities 

 
 Detect and investigate attempts to misuse Anthropic's AI systems for cyber operations, including influence operations, malware development, social engineering, and other adversarial activities

 Develop abuse signals and tracking strategies to proactively detect sophisticated threat actors across our platform

 Create actionable intelligence reports on new attack vectors, vulnerabilities, and threat actor TTPs targeting LLM systems

 Conduct cross-platform threat analysis grounded in real threat actor behavior, using open-source research, dark web monitoring, and internal data

 Utilize investigation findings to implement systematic improvements to our safety approach and mitigate harm at scale

 Study trends internally and in the broader ecosystem to anticipate how AI systems could be misused, generating and publishing reports

 Build and maintain relationships wit…

</details>

**My verdict:** keep
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### K07 · greenhouse/anthropic · 5409008008

**Applied AI Architect, Strategic Enterprise Tech** · San Francisco, CA | New York City, NY | Seattle, WA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5409008008)

Filter v0.1: **keep**. role word in title: 'Applied AI'. Score 4. Role word: Applied AI. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `llm` (×3), `evaluation` (×3), `machine learning`

> `python` → …stakeholders Experience designing scalable cloud architectures and integrating with enterprise systems Comfortable with python Familiarity with common LLM frameworks and tools or a background in machine learning or data science Excitement f…
> `llm` → …heir technology stack. You'll combine your deep technical expertise with customer-facing skills to architect innovative LLM solutions that address complex business challenges while maintaining our high standards for safety and reliability.…
> `evaluation` → …rough successful deployment. You'll leverage your expertise to help customers understand Claude's capabilities, develop evals, and design scalable architectures that maximize the value of our AI systems. Responsibilities: Partner with accou…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “8+ years of experience in roles such as Field CTO, Solutions Architect, Sales Engineer, or Product Manager, with hands-on buildi”

<details><summary>Posting text (excerpt)</summary>

About the role: 

 As an Applied AI team member at Anthropic, you will be a Pre-Sales architect focused on becoming a trusted technical advisor helping large enterprises understand the value of Claude and paint the vision on how they can successfully integrate and deploy Claude into their technology stack. You'll combine your deep technical expertise with customer-facing skills to architect innovative LLM solutions that address complex business challenges while maintaining our high standards for safety and reliability.

  

 You will focus on a short list of strategic accounts within our Enterprise Technology business. For each one you will co-own the account plan with the account executive, build executive technical champions, and drive a multi-quarter adoption roadmap. You will have breadth and depth, reproducing customer environments and problems, building working solutions with them,…

</details>

**My verdict:** keep
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### K08 · greenhouse/anthropic · 5491480008

**Applied AI Architect, Technology Partnerships** · San Francisco, CA | New York City, NY · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5491480008)

Filter v0.1: **keep**. role word in title: 'Applied AI'. Score 4. Role word: Applied AI. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `llm`, `evaluation` (×6), `agents` (×2)

> `python` → …tion frameworks Strong coding ability; you can build prototypes, write evals, and work in a real codebase (comfort with Python or TypeScript expected) Exceptional ability to build relationships with and communicate technical concepts to div…
> `llm` → …tecture, including authentication and authorization models, permissions, and admin experience Hands-on familiarity with LLM applications and agentic tooling, such as the Model Context Protocol (MCP), tool use, agents, and evaluation framewo…
> `evaluation` → …sign how their platform shows up in Claude (MCP servers, connectors, plugins, and skills), hold the quality bar through evaluations, and act as the bridge between the partner's product and engineering teams and Anthropic's Product, Engineer…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “8+ years of experience in technical customer-facing or partner-facing roles such as Solutions Architect, Sales Engineer, Partner”

<details><summary>Posting text (excerpt)</summary>

About the role

 As an Applied AI Architect on the Technology Partnerships team at Anthropic, you will be the technical lead for strategic ISV and technology partners building unique product integrations with Claude. These are software companies whose platforms are systems of record for their customers, and who want those customers to be able to work with their data and workflows directly inside Claude.

 This role goes deep with each partner. You will own the technical side of product partnerships from first scoping through launch and beyond. You will help partners design how their platform shows up in Claude (MCP servers, connectors, plugins, and skills), hold the quality bar through evaluations, and act as the bridge between the partner's product and engineering teams and Anthropic's Product, Engineering, and Research teams. You will be a trusted technical advisor to partner engineeri…

</details>

**My verdict:** keep
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### K09 · greenhouse/anthropic · 5228463008

**Support Engineer** · San Francisco, CA | New York City, NY | Seattle, WA · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/5228463008)

Filter v0.1: **keep**. 3 distinct topic words in text (T=3). Score 3. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `sql`, `llm`

> `python` → …for querying logs and usage data to investigate issues Comfort with command line interfaces and basic scripting (Bash, Python, JavaScript) Understanding of LLM capabilities, prompt engineering patterns, and current limitations Familiarity…
> `sql` → …cts and the opportunity to shape how the world's largest companies get support for them Strong candidates may also have SQL proficiency for querying logs and usage data to investigate issues Comfort with command line interfaces and basic sc…
> `llm` → …investigate issues Comfort with command line interfaces and basic scripting (Bash, Python, JavaScript) Understanding of LLM capabilities, prompt engineering patterns, and current limitations Familiarity with enterprise networking concepts,…

False-friend check:
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…
> `training`: …rience

 Required field of study:  A field relevant to the role as demonstrated through coursework, training, or professional experience

 Minimum years of experience: Years of experience required wil…

Experience lines in the text: “Have 5+ years in technical product support, with meaningful time in an escalated, priority, or named-account support team for enterpr”

<details><summary>Posting text (excerpt)</summary>

About the role 

 We are hiring Support Engineers to serve as the named, dedicated Product Support point of contact for Anthropic's most strategic enterprise customers. As a Support Engineer, you'll be providing high-touch, deeply contextual support to a defined book of accounts — embedded in your customers' shared channels, known by name to their stakeholders, and partnering closely with Sales, Customer Success, and Applied AI as the technical support voice on the account team.

 You'll bring deep knowledge of how each of your customers is built on Claude to every interaction, so you can investigate, diagnose, and resolve their most complex technical needs with nuance and speed — and ensure the right internal teams are engaged when needed.

 Responsibilities 

 
 Serve as the named technical support contact for a defined book of strategic enterprise accounts, embedded in customer channe…

</details>

**My verdict:** keep
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -

### K10 · greenhouse/anthropic · 4949336008

**ML/Research Engineer, Safeguards** · San Francisco, CA | New York City, NY · [original posting](https://job-boards.greenhouse.io/anthropic/jobs/4949336008)

Filter v0.1: **keep**. 4 distinct topic words in text (T=3). Score 4. Role word: -. Exclude word: -. Location: pass (San Francisco, CA).
Topic words: `python`, `evaluation`, `agents` (×2), `machine learning`

> `python` → …of experience in ML engineering, research engineering, or applied research, in academia or industry Have proficiency in Python and experience building ML systems Are comfortable working across the research-to-deployment pipeline, from explo…
> `evaluation` → …ncludes developing synthetic data pipelines for training classifiers and methods to automatically source representative evaluations to iterate on Build systems to monitor for harms that span multiple exchanges, such as coordinated cyber att…
> `agents` → …tions, and develop new methods for aggregating and analyzing signals across contexts Evaluate and improve the safety of agentic products—developing both threat models and environments to test for agentic risks, and developing and deploying…

False-friend check:
> `pipeline`: …thon and experience building ML systems

 Are comfortable working across the research-to-deployment pipeline, from exploratory experiments to production systems

 Are worried about misuse risks of AI…
> `training`: …etect misuse and anomalous behavior at scale. This includes developing synthetic data pipelines for training classifiers and methods to automatically source representative evaluations to iterate on…
> `training`: …SD 


 Logistics 

 Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience

 Required field of study:  A field relevant to the role as demonstrated…

Experience lines in the text: “Have 4+ years of experience in ML engineering, research engineering, or applied research, in academia or industry”

<details><summary>Posting text (excerpt)</summary>

About the role 

 We are looking for ML Engineers and Research Engineers to help detect and mitigate misuse of our AI systems. As a member of the Safeguards ML team, you will build systems that identify harmful use—from individual policy violations to sophisticated, coordinated attacks—and develop defenses that keep our products safe as capabilities advance. You will also work on systems that protect user wellbeing and ensure our models behave appropriately across a wide range of contexts. This work feeds directly into Anthropic's Responsible Scaling Policy commitments.

 Responsibilities 

 
 Develop classifiers to detect misuse and anomalous behavior at scale. This includes developing synthetic data pipelines for training classifiers and methods to automatically source representative evaluations to iterate on

 Build systems to monitor for harms that span multiple exchanges, such as co…

</details>

**My verdict:** keep
**Why (one line):** Mayank: the filter got it right (filter wrong? no)
**False friend? (word, or -):** -
