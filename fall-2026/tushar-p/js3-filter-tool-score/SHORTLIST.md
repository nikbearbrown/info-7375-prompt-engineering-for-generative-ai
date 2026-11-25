# SHORTLIST.md: source-grounded shortlist (JS3 step 2.3)

Tushar Patel · INFO 7375 · Fall 2026 · 2026-11-24

- **Rules frozen at commit `f3edf99`.** FILTER.md and every rule are unchanged; this file only applies the evidence rules as written.
- **The shortlist** is the 17 postings that filter v0.2 keeps on `evidence/runs/live-text-1`. For each one, Claude (`claude-sonnet-5-5`) proposed 3–6 claims with verbatim quotes in a live, billed API run (commit `65c97a2e`; prompt `prompts/claims-v1.txt`; 96 claims, 0 quote_not_found, 0 failed replies). The raw requests and responses are in `evidence/claims/raw/`.
- **My labels are the reference.** I labeled all 96 claims blind, before reading Claude's proposed labels (commit `aaf850a0`). I typed them directly into `labels/claims-sheet.csv` as s/c/i, not through `tools/label_claims.py`, so the sheet has no per-row label times. **Claude's labels are model judgment**, not ground truth.
- **Sources of the numbers.** Every block marked "checks/shortlist_report.py" is that script's verbatim output (`python checks/shortlist_report.py --section a|b|c|d|e`), and `tests/test_shortlist_report.py` reruns the script and compares. Claude drafted the prose between the blocks. Candidates marked "you choose" are Claude's proposals. The choices are Tushar's, recorded in "Featured cases" below.

## Featured cases, chosen by Tushar on 2026-11-24

FILTER.md and every rule are unchanged. These are the cases I chose to feature from the candidates in sections c and e. `tests/test_shortlist_report.py` checks each number below against `checks/shortlist_report.py`.

### 1. Relevance is not entailment: row 48

- **Claim:** "The role requires PostgreSQL experience."
- **Quote:** "have some familiarity with relational databases like Postgres or MySQL"
- **Labels:** I labeled it **insufficient**. Claude labeled it **supported**.
- **Why:** the key word is present, but "familiarity" with "Postgres or MySQL" doesn't assert that the role requires PostgreSQL.

### 2. The abstention rule and its counterexample: `ca74504a` Product Infrastructure

**The rule abstained on all 17.** The rule says that if any verdict-critical claim (role, location, experience, sponsorship) is insufficient, the answer is "I cannot tell". It abstained on all 17 shortlisted postings, because none of them mentions sponsorship.

**Featured counterexample: Software Engineer, Product Infrastructure (`ca74504a`).**
- **Supported:** role (row 61) and location (row 62).
- **Insufficient:** experience (row 63) and sponsorship (row 64), only because the posting is silent on both.
- **The conflict:** FILTER.md's own gates treat both silences as passes. C1 says "Silence about experience is not a bar", and G5 says "Silence is not a no." So the evidence rule and the filter disagree about what silence means.

### 3. "Every critical claim supported, but still wrong": none exists in this sample

None exists, because a silent posting can never support a sponsorship claim.

**Closest: Software Engineer, Developer Platform (`8c0bf773`).**
- Role (row 79) and location (row 80) are supported.
- The experience quote (row 81) is "2+ years of experience shipping production software, with a strong track record of owning features end-to-end".
- It's probably not right for someone with 0 years of experience.

### 4. Open limits: unresolved, not fixed

- **Contradicted critical claims.** FILTER.md doesn't define what a contradicted critical claim does. Five Stripe postings have one: experience in `6042172`, `7476555`, `7292520`, `8131144` and `8243617`.
- **Silence.** The evidence rule's treatment of silence conflicts with G5 and C1.

Both are candidates for a future version. Each would be measured before any change.

### 5. Which way Claude's errors run

In all 9 disagreements where Claude said supported, I said insufficient. Claude never under-credited a claim: every claim I labeled supported (35 of them), Claude labeled supported too.

## a. Claims per shortlisted posting

<!-- BEGIN checks/shortlist_report.py --section a output -->
#### Backend Engineer, Core Technology · greenhouse/stripe · `6042172`

Location fields: US-Remote, Chicago, Seattle, San Francisco

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 1 | The role is a software engineering role. | role | "You'll work on projects that span technologies, systems, and processes where you'll design, build, test, and ship great code every day." | supported | supported | yes | Designing, building, testing, and shipping code supports an engineering role. |
| 2 | The job can be done from the US. | location | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 3 | The role accepts a candidate with 0 years of professional experience. | experience | "2–12+ years of professional hands-on software development experience, able to write well-factored algorithms and have experience with commonly used data structures and algorithms" | contradicted | contradicted | yes | Requires 2–12+ years, contradicting zero experience. |
| 4 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 5 | The work uses Python. | skill | *(empty)* | insufficient | insufficient | yes | Empty quote. |

#### Backend Engineer, Developer & End-user Experience Platform · greenhouse/stripe · `7476555`

Location fields: SEA, SF, NY, Toronto

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 6 | The role is a backend software engineering role. | role | "We're looking for Backend Engineers who want to make an impact on managing money at a global scale with a passion for building ergonomic APIs." | supported | supported | yes | Explicitly describes backend engineers building APIs. |
| 7 | The job can be done in the US. | location | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 8 | The role requires no more than 0 years of industry software engineering experience. | experience | "2–12+ years of industry software engineering experience (does not include internships or co-ops)" | contradicted | contradicted | yes | Requires 2–12+ years excluding internships and co-ops. |
| 9 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 10 | The role requires Docker or AWS experience. | skill | "Good understanding and practical knowledge in cloud-based services (e.g., gRPC, GraphQL, Docker and Kubernetes, cloud services such as AWS, etc.)" | insufficient | insufficient | yes | Docker and AWS are examples, not mandatory skills. |

#### Backend Engineer, Developer & End-user Experience Platform · greenhouse/stripe · `7292520`

Location fields: Toronto Canada, San Francisco, Remote in US, Remote in Canada

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 11 | The role is a backend software engineering role. | role | "We're looking for Backend Engineers who want to make an impact on managing money at a global scale with a passion for building ergonomic APIs." | supported | supported | yes | Explicitly describes backend engineers building APIs. |
| 12 | The job can be done in the US. | location | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 13 | The role is open to candidates with no professional experience (0 years). | experience | "2–12+ years of industry software engineering experience (does not include internships or co-ops)" | contradicted | contradicted | yes | Requires at least two years of industry experience, excluding internships and co-ops. |
| 14 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 15 | The role requires Docker. | skill | "Good understanding and practical knowledge in cloud-based services (e.g., gRPC, GraphQL, Docker and Kubernetes, cloud services such as AWS, etc.)" | insufficient | insufficient | yes | Docker is an example, not a stated requirement. |

#### Backend Engineer, Link · greenhouse/stripe · `8131144`

Location fields: NYC, Sea, SF, Tor

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 16 | The role is a backend software engineering role. | role | "Interest in working as a backend specialist across varying technologies and stacks to solve problems and delight both internal and external users" | supported | supported | yes | Describes a backend specialist working across technologies. |
| 17 | The job can be done in the US. | location | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 18 | The role is open to a candidate with no industry software engineering experience. | experience | "2–10+ years of industry software engineering experience (does not include internships or co-ops)" | contradicted | contradicted | yes | Requires 2–10+ years of industry experience, contradicting zero experience. |
| 19 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 20 | The work requires Python. | skill | "Strong coding skills in any programming language" | contradicted | insufficient | **no** | Accepts strong coding in any language, contradicting a Python-specific requirement. |

#### Machine Learning Engineer, Radar · greenhouse/stripe · `8243617`

Location fields: Seattle

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 21 | The role involves building and deploying machine learning models in production, which fits an AI Engineer role. | role | "Build, train, evaluate, and deploy models that detect fraud and abuse across Stripe’s global network." | supported | supported | yes | Building, training, evaluating, and deploying fraud models supports the claim. |
| 22 | The job can be done in the US. | location | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 23 | The role is open to candidates with 0 years of professional experience. | experience | "2+ years of experience developing, evaluating, and deploying machine learning models in a production environment." | contradicted | contradicted | yes | Requires 2+ years of production ML experience. |
| 24 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 25 | The work uses Python. | skill | *(empty)* | insufficient | insufficient | yes | Empty quote. |

#### Software Engineer, Early Career — Immediate Start · greenhouse/stripe · `8212508`

Location fields: San Francisco, Seattle, New York

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 26 | The role is a software engineering role. | role | "Experience and familiarity with programming, either through side projects or classwork." | insufficient | insufficient | yes | Programming familiarity alone does not establish the role’s responsibilities. |
| 27 | The job can be done in the US. | location | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 28 | The role requires at most 2 years of professional experience. | experience | "New grad candidates should have no more than 18 months of professional experience (excluding internship experience)" | supported | supported | yes | A maximum of 18 months is within two years. |
| 29 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 30 | The work uses Java. | skill | "We work mostly in Java, Ruby, JavaScript, Scala, and Go." | supported | supported | yes | Explicitly says the team works mostly in Java and other named languages. |

#### Software Engineer, New Grad · greenhouse/stripe · `8128744`

Location fields: San Francisco, Seattle, New York

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 31 | The role is a software engineering role. | role | "Experience and familiarity with programming, either through side projects or classwork." | insufficient | insufficient | yes | Programming familiarity alone does not establish the role. |
| 32 | The role is entry-level, aimed at new graduates. | seniority | "New grad candidates should have no more than 18 months of professional experience (excluding internship experience)." | supported | supported | yes | Explicitly targets new graduates with at most 18 months of experience. |
| 33 | The job can be done in the US. | location | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 34 | The role requires at most 2 years of professional experience. | experience | "New grad candidates should have no more than 18 months of professional experience (excluding internship experience)." | supported | supported | yes | A maximum of 18 months is within two years. |
| 35 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 36 | The work uses Java. | skill | "We work mostly in Java, Ruby, JavaScript, Scala, and Go." | supported | supported | yes | Explicitly identifies Java as a language used at work. |

#### Software Engineer, Privy · greenhouse/stripe · `7235875`

Location fields: NYC-Privy

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 37 | The role is a backend software engineering role. | role | "Design and build the backend systems that power wallets, identity, and onchain infrastructure at scale" | supported | supported | yes | Explicitly describes designing and building backend systems. |
| 38 | The job can be done in the US. | location | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 39 | The role requires at most 2 years of experience. | experience | "Deep experience building and maintaining a production system at scale" | insufficient | insufficient | yes | “Deep experience” gives no numerical experience limit. |
| 40 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 41 | The work uses React. | skill | "In practice, we use boring technology like Node, React, and AWS so we can focus our engineering energy entirely on pushing the boundaries of Privy's core product, e.g. through hardware enclaves, multi-region low latency APIs, and blockchain abstractions that are accessible to mainstream developers." | supported | supported | yes | Explicitly says the team uses React. |
| 42 | The work uses AWS. | skill | "In practice, we use boring technology like Node, React, and AWS so we can focus our engineering energy entirely on pushing the boundaries of Privy's core product, e.g. through hardware enclaves, multi-region low latency APIs, and blockchain abstractions that are accessible to mainstream developers." | supported | supported | yes | Explicitly says the team uses AWS. |

#### Software Engineer, Early Career (AI) · ashby/notion · `85947779-6b87-466a-98bc-30a640448c28`

Location fields: San Francisco, California

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 43 | The role is an AI engineering / software engineering role. | role | "We're looking for an Early Career AI Engineer to join as a strategic partner in shaping Notion's AI vision." | supported | supported | yes | Explicitly names an Early Career AI Engineer role. |
| 44 | The role is early-career level, suitable for a candidate with no professional experience. | seniority | "This role is for candidates with 0-2 YOE and can start full time right away." | supported | supported | yes | The stated 0–2 years includes zero experience. |
| 45 | The job can be done in the US. | location | "For roles based in San Francisco and New York, the estimated base salary range for this role is $130,000-$150,000." | insufficient | supported | **no** | Conditional US salary information does not establish the role’s location. |
| 46 | The role requires at most 2 years of experience. | experience | "You have less than two years of engineering experience." | supported | supported | yes | “Less than two years” supports the stated experience ceiling. |
| 47 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 48 | The role requires PostgreSQL experience. | skill | "have some familiarity with relational databases like Postgres or MySQL" | insufficient | supported | **no** | Postgres or MySQL does not make PostgreSQL mandatory: relevance is not entailment. |

#### Software Engineer, Growth (Early Career) · ashby/notion · `297b4ece-765f-4eea-b1b8-46057cb6501f`

Location fields: San Francisco, California

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 49 | The role is a software engineering role. | role | "As an Early Career Software Engineer at Notion, you’ll help shape core user experiences and accelerate how people discover value in Notion." | supported | supported | yes | Explicitly names an Early Career Software Engineer role. |
| 50 | The job can be done in the US. | location | "For roles based in San Francisco or New York City, the estimated salary range for this role is $130,000 - $150,000" | insufficient | supported | **no** | Conditional US salary information does not establish location. |
| 51 | The role requires at most 2 years of experience. | experience | "This role is for candidates with 0-2 YOE and can start full time right away." | supported | supported | yes | The stated 0–2 years includes zero experience. |
| 52 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 53 | The role is early-career or entry-level. | seniority | "This role is for candidates with 0-2 YOE and can start full time right away." | supported | supported | yes | The stated 0–2 years supports an early-career role. |
| 54 | The role requires React or TypeScript. | skill | "You have experience with any part of our technology stack: React, TypeScript, Node.js, Postgres, and Elasticsearch." | insufficient | insufficient | yes | Experience with any part of the stack does not require React or TypeScript specifically. |

#### Software Engineer, Infrastructure Security · ashby/notion · `e3d8dc06-da05-4e9d-a143-2e9c51fa3d51`

Location fields: San Francisco, California \| New York, New York

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 55 | The role involves backend/infrastructure software engineering work that writes production code. | role | "Backend/infrastructure development: you’ve written and shipped production-grade code, and can contribute to the codebase and architecture to raise the bar on secure systems design." | supported | supported | yes | Explicitly describes backend or infrastructure development and production code. |
| 56 | The job can be done in the US. | location | "This role can be based in either San Francisco or New York City." | supported | supported | yes | Explicitly identifies San Francisco or New York City. |
| 57 | The role requires at most 0 years of experience (entry level). | experience | "you’ll own meaningful infrastructure security problems end-to-end: from identifying risk, to designing pragmatic controls, to shipping secure defaults that scale across engineering." | insufficient | insufficient | yes | Ownership responsibilities do not establish that zero experience is accepted. |
| 58 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 59 | The role is entry-level or junior. | seniority | "As an IC4 on this team, you’ll own meaningful infrastructure security problems end-to-end" | insufficient | insufficient | yes | “IC4” and the responsibilities do not establish a junior role without a level definition. |
| 60 | The work involves AWS. | skill | "Proactively enhance the security posture of our AWS accounts and cloud infrastructure." | supported | supported | yes | Explicitly describes work securing AWS accounts. |

#### Software Engineer, Product Infrastructure · ashby/notion · `ca74504a-9b91-4ce3-b0df-97919b46e749`

Location fields: San Francisco, California \| New York, New York

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 61 | The role is a software engineering role building backend and front-end systems. | role | "We solve problems that span multiple product surfaces and typically stretch across both front-end and backend and unblock new product avenues that were previously challenging to create." | supported | supported | yes | Describes frontend and backend technical work. |
| 62 | The job can be done in the US. | location | "This role can be based in either San Francisco or New York City." | supported | supported | yes | Explicitly identifies San Francisco or New York City. |
| 63 | The role requires at most 0 years of experience (entry-level friendly). | experience | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 64 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 65 | The work uses TypeScript, React, Postgres and AWS. | skill | "using whatever tools are required for the job, such as AWS, Postgres, NodeJS, TypeScript, React on the frontend." | supported | supported | yes | Explicitly names AWS, Postgres, Node.js, TypeScript, and React as work tools. |
| 66 | The role is open to entry-level candidates. | seniority | "If you’re excited about this role but don’t meet every bullet, we still encourage you to apply." | insufficient | insufficient | yes | Encouraging applicants who lack some qualifications does not establish entry-level eligibility. |

#### Software Engineer, New Grad (Dec 2026) · ashby/notion · `e32799d2-8ef8-4803-8189-c72514afa816`

Location fields: San Francisco, California

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 67 | The role is a software engineering role building product features. | role | "You'll work with others to plan, shape, and build new product features from start to finish: through conception, research, implementation, and maintenance." | insufficient | supported | **no** | Building product features alone does not clearly establish software engineering work. |
| 68 | The job can be done in the US. | location | "For roles based in San Francisco or New York City, the estimated salary range for this role is $135,000 - $155,000" | insufficient | supported | **no** | Conditional salary information does not establish location. |
| 69 | The role requires at most 2 years of experience (entry-level/new grad). | experience | "Pursuing a bachelor's or master’s degree in computer science, engineering, or another related field." | insufficient | supported | **no** | Degree enrollment does not establish a two-year experience limit. |
| 70 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 71 | The role is entry-level, aimed at new graduates. | seniority | "To be eligible for this role, you need to graduate by Dec 2026 and be able to start FTE by January/February 2027." | supported | supported | yes | Graduation and start dates explicitly support new-graduate hiring. |
| 72 | The work uses Python. | skill | "Working towards a proficiency of one or more programming languages such as TypeScript, Node.js, or Python." | insufficient | insufficient | yes | Python is an example of an accepted language, not necessarily a language used in the role. |

#### Software Engineer, Mobile Core (Android) · ashby/notion · `d82a0b31-59b8-4699-ae8d-6fb3fe47518c`

Location fields: San Francisco, California

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 73 | The role is a software engineering role. | role | "As an Android engineer, you’ll help build that native foundation, from how pages render and how people write and edit, to the navigation and app chrome people use every day, like Home, Search, and Inbox, along with the shared frameworks the rest of the app is built on." | supported | supported | yes | Explicitly describes Android engineering on a native application. |
| 74 | The job can be done in the US. | location | "This role can be based in either San Francisco or New York City." | supported | supported | yes | Explicitly identifies San Francisco or New York City. |
| 75 | The role requires at most 2 years of experience. | experience | "You’ve built and shipped Android apps, through work, internships, or your own projects, and you’re comfortable with modern Android—Kotlin, Jetpack Compose, Coroutines/Flow, and Gradle." | insufficient | insufficient | yes | Shipping apps through work, internships, or projects gives no numerical experience limit. |
| 76 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 77 | The work uses TypeScript. | skill | "Web experience (TypeScript, React, Node) is welcome but not required." | insufficient | insufficient | yes | Optional TypeScript experience does not establish that the role uses TypeScript. |
| 78 | The role is open to entry-level candidates. | seniority | "You’ve built and shipped Android apps, through work, internships, or your own projects, and you’re comfortable with modern Android—Kotlin, Jetpack Compose, Coroutines/Flow, and Gradle." | insufficient | insufficient | yes | Accepting personal projects as evidence does not establish the role’s overall seniority. |

#### Software Engineer, Developer Platform · ashby/notion · `8c0bf773-e536-45c9-9a6c-8ee478148cc8`

Location fields: San Francisco, California \| New York, New York

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 79 | The role is a software engineering role. | role | "You will build tools, APIs, and platform experiences that help customers connect Notion to the world — bringing their apps, data, and workflows into one workspace." | supported | supported | yes | Building tools, APIs, and platforms supports an engineering role. |
| 80 | The job can be done in the US. | location | "This role can be based in either San Francisco or New York City." | supported | supported | yes | Explicitly identifies San Francisco or New York City. |
| 81 | The role requires at most 2 years of experience. | experience | "2+ years of experience shipping production software, with a strong track record of owning features end-to-end" | insufficient | contradicted | **no** | “2+ years” states a minimum, not a maximum of two years. This label interprets the claim as an upper limit; if it means someone with two years meets the minimum, the quote supports that interpretation. |
| 82 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 83 | The work uses TypeScript. | skill | "Fluency with TypeScript across both backend and frontend" | supported | supported | yes | TypeScript fluency for backend and frontend work supports its use in the role. |
| 84 | The role requires Python. | skill | *(empty)* | insufficient | insufficient | yes | Empty quote. |

#### Software Engineer, Web Infrastructure · ashby/notion · `06c2599d-4dd5-4f97-843f-7194b546f042`

Location fields: San Francisco, California \| New York, New York

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 85 | The role is a software engineering role building web infrastructure. | role | "Web Infrastructure builds the foundations behind Notion’s web clients so product engineers can ship fast, reliable, accessible experiences." | insufficient | supported | **no** | A team’s infrastructure mission does not establish the particular role’s duties. |
| 86 | The role is junior or entry level. | seniority | "As a junior engineer on the team, you’ll help make those experiences measurably faster and more resilient." | supported | supported | yes | Explicitly describes the role as junior. |
| 87 | The job can be done in the US. | location | "This role can be based in either San Francisco or New York City." | supported | supported | yes | Explicitly identifies San Francisco or New York City. |
| 88 | The role requires at most 2 years of experience. | experience | "You don’t need to arrive as a performance expert; we’re looking for strong fundamentals, curiosity, and a desire to learn by shipping useful work." | insufficient | insufficient | yes | Not requiring performance expertise gives no numerical experience limit. |
| 89 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 90 | The work uses TypeScript. | skill | "Solid programming fundamentals and some experience building software with JavaScript or TypeScript; familiarity with React or another component-based UI framework is helpful." | insufficient | supported | **no** | JavaScript or TypeScript experience does not establish that the work uses TypeScript specifically. |

#### Software Engineer, Collections Infra · ashby/notion · `0fb1f7e2-ffe4-433c-a27d-62fa7f1d880f`

Location fields: San Francisco, California

| row | claim | kind | quote | my label | Claude's label | agree? | my note |
|---|---|---|---|---|---|---|---|
| 91 | The role is a software engineering role with a backend focus. | role | "As a Software Engineer on Collections Infra, you’ll help scale the infrastructure behind Notion’s database block." | supported | supported | yes | A software engineering role in database infrastructure supports backend work. |
| 92 | The job can be done in the US. | location | "For roles based in San Francisco, the estimated base salary range for this role is $150,000 - $168,000 per year." | insufficient | supported | **no** | Conditional San Francisco salary information does not establish the role’s location. |
| 93 | The role requires at most 2 years of experience. | experience | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 94 | The employer will sponsor a work visa. | sponsorship | *(empty)* | insufficient | insufficient | yes | Empty quote. |
| 95 | The work uses TypeScript. | skill | "Practical comfort with JavaScript or TypeScript, or the ability to ramp quickly in a codebase where those tools matter." | supported | supported | yes | Describes a codebase where JavaScript or TypeScript matters, supporting their use at work. |
| 96 | The role is suitable for an early-career engineer. | seniority | "You’ll partner with senior engineers and product-facing teams to evolve Collections as a platform, balancing internal developer needs with the external customer experience of databases." | insufficient | insufficient | yes | Working with senior engineers does not itself establish an early-career role. |

<!-- END checks/shortlist_report.py --section a output -->

## b. Agreement: my labels vs Claude's

<!-- BEGIN checks/shortlist_report.py --section b output -->
- **Overall:** 85/96 = 88.5% (95% Wilson 80.6–93.5%).
- **Claims with a quote:** 55/66 = 83.3% (95% Wilson 72.6–90.4%).
- **Claims with an empty quote:** 30/30 = 100.0% (95% Wilson 88.6–100.0%). The prompt contract forces an empty quote to be proposed insufficient, so this agreement is mechanical, not judgment.

| kind | claims | agree | agreement |
|---|---|---|---|
| role | 17 | 15 | 88.2% |
| seniority | 9 | 9 | 100.0% |
| location | 17 | 13 | 76.5% |
| experience | 17 | 15 | 88.2% |
| sponsorship | 17 | 17 | 100.0% |
| skill | 19 | 16 | 84.2% |

Confusion matrix (rows: my label, the reference; columns: Claude's proposed label):

| me ↓ / Claude → | supported | contradicted | insufficient | total |
|---|---|---|---|---|
| **supported** | 35 | 0 | 0 | 35 |
| **contradicted** | 0 | 5 | 1 | 6 |
| **insufficient** | 9 | 1 | 45 | 55 |
| **total** | 44 | 6 | 46 | 96 |

Disagreements: 11 (rows 20, 45, 48, 50, 67, 68, 69, 81, 85, 90, 92). me contradicted, Claude insufficient: 1; me insufficient, Claude contradicted: 1; me insufficient, Claude supported: 9.
<!-- END checks/shortlist_report.py --section b output -->

**Reading.** All 11 disagreements are on claims that have a quote. In 9 of them I said insufficient and Claude said supported. Four are location (rows 45, 50, 68, 92), where a conditional salary sentence ("For roles based in San Francisco…") was taken as the role's location. Four are role or skill mentions taken as assertions (rows 48, 67, 85, 90). One is experience (row 69), where degree enrollment was taken as an experience ceiling. Claude never labeled supported where I labeled contradicted, and I never labeled supported where Claude did not. Claude's errors run one way: **it is more willing to call a claim supported than I am.**

## c. Relevance is not entailment

The test: the quote was found in the text, it holds a key word of the claim, and my label is insufficient or contradicted. A claim's key words are FILTER.md's own words for its kind:
- role: the G1 title words
- seniority: the G2 words, plus early-career words chosen for this report only
- experience: "year", "YOE" or "experience"
- location: any G3 US marker
- sponsorship: the G5 phrases, plus "sponsor" and "visa"
- skill: the persona skills that the claim names ("Postgres" counts for PostgreSQL)

The full definition is in `checks/shortlist_report.py`.

<!-- BEGIN checks/shortlist_report.py --section c output -->
20 claims have a found quote that holds a key word of the claim, yet my label is insufficient (15) or contradicted (5).

| row | posting | kind | claim | quote | key words in quote | my label | Claude's label |
|---|---|---|---|---|---|---|---|
| 3 | Backend Engineer, Core Technology | experience | The role accepts a candidate with 0 years of professional experience. | "2–12+ years of professional hands-on software development experience, able to write well-factored algorithms and have experience with commonly used data structures and algorithms" | year, experience | contradicted | contradicted |
| 8 | Backend Engineer, Developer & End-user Experience Platform | experience | The role requires no more than 0 years of industry software engineering experience. | "2–12+ years of industry software engineering experience (does not include internships or co-ops)" | year, experience | contradicted | contradicted |
| 10 | Backend Engineer, Developer & End-user Experience Platform | skill | The role requires Docker or AWS experience. | "Good understanding and practical knowledge in cloud-based services (e.g., gRPC, GraphQL, Docker and Kubernetes, cloud services such as AWS, etc.)" | Docker, AWS | insufficient | insufficient |
| 13 | Backend Engineer, Developer & End-user Experience Platform | experience | The role is open to candidates with no professional experience (0 years). | "2–12+ years of industry software engineering experience (does not include internships or co-ops)" | year, experience | contradicted | contradicted |
| 15 | Backend Engineer, Developer & End-user Experience Platform | skill | The role requires Docker. | "Good understanding and practical knowledge in cloud-based services (e.g., gRPC, GraphQL, Docker and Kubernetes, cloud services such as AWS, etc.)" | Docker | insufficient | insufficient |
| 18 | Backend Engineer, Link | experience | The role is open to a candidate with no industry software engineering experience. | "2–10+ years of industry software engineering experience (does not include internships or co-ops)" | year, experience | contradicted | contradicted |
| 23 | Machine Learning Engineer, Radar | experience | The role is open to candidates with 0 years of professional experience. | "2+ years of experience developing, evaluating, and deploying machine learning models in a production environment." | year, experience | contradicted | contradicted |
| 39 | Software Engineer, Privy | experience | The role requires at most 2 years of experience. | "Deep experience building and maintaining a production system at scale" | experience | insufficient | insufficient |
| 45 | Software Engineer, Early Career (AI) | location | The job can be done in the US. | "For roles based in San Francisco and New York, the estimated base salary range for this role is $130,000-$150,000." | San Francisco, New York | insufficient | supported |
| 48 | Software Engineer, Early Career (AI) | skill | The role requires PostgreSQL experience. | "have some familiarity with relational databases like Postgres or MySQL" | Postgres | insufficient | supported |
| 50 | Software Engineer, Growth (Early Career) | location | The job can be done in the US. | "For roles based in San Francisco or New York City, the estimated salary range for this role is $130,000 - $150,000" | San Francisco, New York, New York City | insufficient | supported |
| 54 | Software Engineer, Growth (Early Career) | skill | The role requires React or TypeScript. | "You have experience with any part of our technology stack: React, TypeScript, Node.js, Postgres, and Elasticsearch." | TypeScript, React | insufficient | insufficient |
| 68 | Software Engineer, New Grad (Dec 2026) | location | The job can be done in the US. | "For roles based in San Francisco or New York City, the estimated salary range for this role is $135,000 - $155,000" | San Francisco, New York, New York City | insufficient | supported |
| 72 | Software Engineer, New Grad (Dec 2026) | skill | The work uses Python. | "Working towards a proficiency of one or more programming languages such as TypeScript, Node.js, or Python." | Python | insufficient | insufficient |
| 77 | Software Engineer, Mobile Core (Android) | skill | The work uses TypeScript. | "Web experience (TypeScript, React, Node) is welcome but not required." | TypeScript | insufficient | insufficient |
| 81 | Software Engineer, Developer Platform | experience | The role requires at most 2 years of experience. | "2+ years of experience shipping production software, with a strong track record of owning features end-to-end" | year, experience | insufficient | contradicted |
| 85 | Software Engineer, Web Infrastructure | role | The role is a software engineering role building web infrastructure. | "Web Infrastructure builds the foundations behind Notion’s web clients so product engineers can ship fast, reliable, accessible experiences." | Engineer | insufficient | supported |
| 90 | Software Engineer, Web Infrastructure | skill | The work uses TypeScript. | "Solid programming fundamentals and some experience building software with JavaScript or TypeScript; familiarity with React or another component-based UI framework is helpful." | TypeScript | insufficient | supported |
| 92 | Software Engineer, Collections Infra | location | The job can be done in the US. | "For roles based in San Francisco, the estimated base salary range for this role is $150,000 - $168,000 per year." | San Francisco | insufficient | supported |
| 96 | Software Engineer, Collections Infra | seniority | The role is suitable for an early-career engineer. | "You’ll partner with senior engineers and product-facing teams to evolve Collections as a platform, balancing internal developer needs with the external customer experience of databases." | Senior | insufficient | insufficient |
<!-- END checks/shortlist_report.py --section c output -->

The five contradicted rows (3, 8, 13, 18, 23) are a different case. Their quotes do assert something: the opposite of the claim. The 15 insufficient rows are the relevance-is-not-entailment cases proper.

**Recommendation (you choose which to feature): row 48.**
- **Claim:** "The role requires PostgreSQL experience."
- **Quote:** "have some familiarity with relational databases like Postgres or MySQL"
- **Why this row:** the quote names the skill but makes it one example among alternatives, so it doesn't make PostgreSQL a requirement. That is FILTER.md's "Python in a nice-to-have list" example almost word for word. Claude labeled it **supported**, so this row shows the model itself making the mistake the rule exists to catch. My note on it already says "relevance is not entailment".
- **Runner-up: row 77.** "Web experience (TypeScript, React, Node) is welcome but not required." against "The work uses TypeScript." The quote says outright that it is not required, but Claude agreed it was insufficient, so the row shows the rule without showing a model failure.

## d. Abstention rule, applied with my labels

FILTER.md "When the agent must say 'I cannot tell'": "A shortlist claim that the verdict depends on is insufficient." The verdict-critical kinds are role, location, experience and sponsorship.

<!-- BEGIN checks/shortlist_report.py --section d output -->
- **Shortlisted postings:** 17 (every v0.2 keep).
- **Stay keep:** 0.
- **Become cannot_tell:** 17.

| posting | role | location | experience | sponsorship | insufficient critical kinds | verdict |
|---|---|---|---|---|---|---|
| Backend Engineer, Core Technology `6042172` | supported | insufficient | contradicted | insufficient | location, sponsorship | cannot_tell |
| Backend Engineer, Developer & End-user Experience Platform `7476555` | supported | insufficient | contradicted | insufficient | location, sponsorship | cannot_tell |
| Backend Engineer, Developer & End-user Experience Platform `7292520` | supported | insufficient | contradicted | insufficient | location, sponsorship | cannot_tell |
| Backend Engineer, Link `8131144` | supported | insufficient | contradicted | insufficient | location, sponsorship | cannot_tell |
| Machine Learning Engineer, Radar `8243617` | supported | insufficient | contradicted | insufficient | location, sponsorship | cannot_tell |
| Software Engineer, Early Career — Immediate Start `8212508` | insufficient | insufficient | supported | insufficient | role, location, sponsorship | cannot_tell |
| Software Engineer, New Grad `8128744` | insufficient | insufficient | supported | insufficient | role, location, sponsorship | cannot_tell |
| Software Engineer, Privy `7235875` | supported | insufficient | insufficient | insufficient | location, experience, sponsorship | cannot_tell |
| Software Engineer, Early Career (AI) `85947779-6b87-466a-98bc-30a640448c28` | supported | insufficient | supported | insufficient | location, sponsorship | cannot_tell |
| Software Engineer, Growth (Early Career) `297b4ece-765f-4eea-b1b8-46057cb6501f` | supported | insufficient | supported | insufficient | location, sponsorship | cannot_tell |
| Software Engineer, Infrastructure Security `e3d8dc06-da05-4e9d-a143-2e9c51fa3d51` | supported | supported | insufficient | insufficient | experience, sponsorship | cannot_tell |
| Software Engineer, Product Infrastructure `ca74504a-9b91-4ce3-b0df-97919b46e749` | supported | supported | insufficient | insufficient | experience, sponsorship | cannot_tell |
| Software Engineer, New Grad (Dec 2026) `e32799d2-8ef8-4803-8189-c72514afa816` | insufficient | insufficient | insufficient | insufficient | role, location, experience, sponsorship | cannot_tell |
| Software Engineer, Mobile Core (Android) `d82a0b31-59b8-4699-ae8d-6fb3fe47518c` | supported | supported | insufficient | insufficient | experience, sponsorship | cannot_tell |
| Software Engineer, Developer Platform `8c0bf773-e536-45c9-9a6c-8ee478148cc8` | supported | supported | insufficient | insufficient | experience, sponsorship | cannot_tell |
| Software Engineer, Web Infrastructure `06c2599d-4dd5-4f97-843f-7194b546f042` | insufficient | supported | insufficient | insufficient | role, experience, sponsorship | cannot_tell |
| Software Engineer, Collections Infra `0fb1f7e2-ffe4-433c-a27d-62fa7f1d880f` | supported | insufficient | insufficient | insufficient | location, experience, sponsorship | cannot_tell |

Postings with each critical kind insufficient: role 4, location 12, experience 8, sponsorship 17.

Postings with a contradicted critical claim: 5 (`6042172` experience, `7476555` experience, `7292520` experience, `8131144` experience, `8243617` experience). FILTER.md's evidence rules say what an insufficient critical claim does, not what a contradicted one does; all of these are already cannot_tell through an insufficient claim, so the count above does not depend on that gap.
<!-- END checks/shortlist_report.py --section d output -->

**Reading.** The rule turns the whole shortlist into cannot_tell, and sponsorship alone is enough to do it. Every sponsorship claim Claude wrote was "The employer will sponsor a work visa", and no posting says anything about sponsorship, so every one is insufficient.

The five Stripe postings with a contradicted experience claim (they ask for "2–12+", "2–10+" or "2+" years) are a separate open question. Claude phrased those claims against Cole's 0 years ("accepts a candidate with 0 years"), but G4 in v0.2 passes a minimum of 2 because the cutoff is 2 (C3, a stretch-role choice). The claim's frame and the gate's frame differ, and the evidence rules don't say what a contradicted critical claim should do. I have not resolved either point.

## e. Counterexamples: where the rule's limits show

<!-- BEGIN checks/shortlist_report.py --section e output -->
| posting | location fields (G3 reads these) | sponsorship words anywhere in the text | insufficient critical kinds | supported critical kinds |
|---|---|---|---|---|
| Backend Engineer, Core Technology `6042172` | US-Remote, Chicago, Seattle, San Francisco | none | location, sponsorship | role |
| Backend Engineer, Developer & End-user Experience Platform `7476555` | SEA, SF, NY, Toronto | none | location, sponsorship | role |
| Backend Engineer, Developer & End-user Experience Platform `7292520` | Toronto Canada, San Francisco, Remote in US, Remote in Canada | none | location, sponsorship | role |
| Backend Engineer, Link `8131144` | NYC, Sea, SF, Tor | none | location, sponsorship | role |
| Machine Learning Engineer, Radar `8243617` | Seattle | none | location, sponsorship | role |
| Software Engineer, Early Career — Immediate Start `8212508` | San Francisco, Seattle, New York | none | role, location, sponsorship | experience |
| Software Engineer, New Grad `8128744` | San Francisco, Seattle, New York | none | role, location, sponsorship | experience |
| Software Engineer, Privy `7235875` | NYC-Privy | none | location, experience, sponsorship | role |
| Software Engineer, Early Career (AI) `85947779-6b87-466a-98bc-30a640448c28` | San Francisco, California | none | location, sponsorship | role, experience |
| Software Engineer, Growth (Early Career) `297b4ece-765f-4eea-b1b8-46057cb6501f` | San Francisco, California | none | location, sponsorship | role, experience |
| Software Engineer, Infrastructure Security `e3d8dc06-da05-4e9d-a143-2e9c51fa3d51` | San Francisco, California \| New York, New York | none | experience, sponsorship | role, location |
| Software Engineer, Product Infrastructure `ca74504a-9b91-4ce3-b0df-97919b46e749` | San Francisco, California \| New York, New York | none | experience, sponsorship | role, location |
| Software Engineer, New Grad (Dec 2026) `e32799d2-8ef8-4803-8189-c72514afa816` | San Francisco, California | none | role, location, experience, sponsorship | – |
| Software Engineer, Mobile Core (Android) `d82a0b31-59b8-4699-ae8d-6fb3fe47518c` | San Francisco, California | none | experience, sponsorship | role, location |
| Software Engineer, Developer Platform `8c0bf773-e536-45c9-9a6c-8ee478148cc8` | San Francisco, California \| New York, New York | none | experience, sponsorship | role, location |
| Software Engineer, Web Infrastructure `06c2599d-4dd5-4f97-843f-7194b546f042` | San Francisco, California \| New York, New York | none | role, experience, sponsorship | location |
| Software Engineer, Collections Infra `0fb1f7e2-ffe4-433c-a27d-62fa7f1d880f` | San Francisco, California | none | location, experience, sponsorship | role |

Postings silent on sponsorship (no G5 phrase, "sponsor", "sponsorship" or "visa"): 17 of 17.
Postings with every critical claim supported: 0.
<!-- END checks/shortlist_report.py --section e output -->

### (i) The rule abstains, but the posting may still be one I'd keep (you choose)

**Candidate 1: Software Engineer, Product Infrastructure (`ca74504a`), where the abstention comes purely from silence.**
- **Role supported, row 61:** "We solve problems that span multiple product surfaces and typically stretch across both front-end and backend…"
- **Location supported, row 62:** "This role can be based in either San Francisco or New York City."
- **Experience insufficient, row 63: empty quote.** The text states no years of experience anywhere. G4 treats that silence as a pass ("Silence about experience is not a bar", C1).
- **Sponsorship insufficient, row 64: empty quote.** The text never mentions sponsorship. G5 says "Silence is not a no."
- **Why it matters:** both insufficient claims come from silences that the gates have already decided are passes. The evidence rule then abstains on the same silences, so the gates and the evidence rule disagree about what silence means.

**Candidate 2: Software Engineer, Early Career (AI) (`85947779`), the strongest fit for Cole.**
- **Role supported, row 43:** "We're looking for an Early Career AI Engineer…" AI Engineer is one of Cole's target titles.
- **Seniority supported, row 44:** "This role is for candidates with 0-2 YOE…"
- **Experience supported, row 46:** "You have less than two years of engineering experience."
- **Location insufficient, row 45.** The only quote is the conditional salary sentence. The location field G3 reads says "San Francisco, California", but the evidence rules accept only quotes from the posting text, so metadata can't support the claim.
- **Sponsorship insufficient, row 47:** silence again.
- **Similar posting:** Growth (Early Career) (`297b4ece`, rows 49–52) has the same pattern.

Whether you would keep either posting is your judgment. The evidence above shows only why the rule abstains.

### (ii) Every critical claim is supported, but I'd still not want the posting

**None exists in this data.** Section e shows 0 postings with every critical claim supported, because a silent posting can never support "The employer will sponsor a work visa." So (ii) can't be tested on this shortlist; that is not the same as the rule passing the test.

**Closest candidate (you choose): Software Engineer, Developer Platform (`8c0bf773`).**
- **Role supported, row 79:** "You will build tools, APIs, and platform experiences…"
- **Location supported, row 80:** "This role can be based in either San Francisco or New York City."
- **Experience, row 81:** "2+ years of experience shipping production software, with a strong track record of owning features end-to-end". I labeled the claim "The role requires at most 2 years of experience" insufficient. My note records the other reading: "if it means someone with two years meets the minimum, the quote supports that interpretation."
- **Why it's close:** under that other reading, every critical claim except the silent sponsorship one is supported. Yet the quote describes a role that wants 2+ years and a track record of owning features end to end, which a 0-year candidate may not want. A supported claim can be true and still miss what matters for the person.
