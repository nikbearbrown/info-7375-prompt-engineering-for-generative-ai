You are judging one job posting for one fictional job seeker. Apply the rule below exactly as written.

## The rule
A posting is relevant only if all four checks hold (case-insensitive, whole words):
- R1 Title: `title` contains at least one of: data, analytics, analyst, scientist, machine learning, ML.
- R2 Not management or intern: `title` contains none of: manager, director, head, lead, intern.
- R3 US location: at least one `;`-separated part of `location.name` ends in a US state code (`, CA`, `, NY`, `, IL`, ...) or is `Remote - US`.
- R4 Résumé skill: at least 1 skill from the résumé's shipped skill lists (`skills.languages`, `skills.data_bi`, `skills.backend_automation`, `skills.database_cloud`) appears in `content`. `skills.familiar_with_not_shipped` and the text note `skills.agent_note` do not count.

Otherwise it is not relevant. Seniority fit is not judged: Senior and Staff titles can be relevant.

## Output
Reply with exactly one JSON object and nothing else: no prose, no Markdown, no code fence. It must have exactly these keys:
- "posting_id": the integer id of the posting below
- "verdict": "relevant" or "not_relevant"
- "failed_check": apply R1, R2, R3, R4 in order and give the first check that fails: "R1", "R2", "R3" or "R4"; null when the verdict is "relevant"
- "citations": a non-empty list of objects, each with exactly the keys "resume_field", "posting_field" and "quote":
  - "resume_field": a dotted path that exists in the résumé JSON, such as "skills.languages"
  - "posting_field": one of "title", "location.name", "content"
  - "quote": text copied exactly from that posting field
- "label": "judgment"

## Résumé (fictional persona)
{
  "_comment": "FICTIONAL EXAMPLE PERSONA - safe to commit. Pairs with resumes/priya-nair-cv.md.",
  "attested": true,
  "attested_date": "2026-08-17",
  "attestation_note": "Example data: fictional, consistent with resumes/priya-nair-cv.md.",
  "personal": {
    "name": "Priya Nair",
    "location": "Boston, MA",
    "phone": "(617) 555-0163",
    "email": "priya.nair@example.com",
    "linkedin": "linkedin.com/in/priyanair-example",
    "github": "github.com/priyanair-example"
  },
  "education": [
    {
      "institution": "Northeastern University",
      "location": "Boston, MA",
      "degree": "MS, Information Systems",
      "gpa": "3.9/4.0",
      "start_date": "2023-08",
      "end_date": "2025-12",
      "status": "completed",
      "coursework": [
        "Machine Learning",
        "Data Management",
        "LLM Systems"
      ]
    }
  ],
  "experience": [
    {
      "company": "Staples",
      "location": "Framingham, MA",
      "title": "AI Engineer Co-op",
      "start_date": "2025-01",
      "end_date": "2025-08",
      "bullets": [
        "Built a Genie Router Agent (Databricks Genie API + LangGraph) used by 120+ analysts, cutting SQL query time ~30%.",
        "Designed an inference pipeline with MLflow 3.0 tracing, drift monitoring, and performance dashboards.",
        "Built an A/B framework for LLM evaluation with significance testing across 5+ production experiments."
      ],
      "attestation_correction": ""
    }
  ],
  "projects": [
    {
      "name": "eval-guardrails",
      "start_date": "2025-09",
      "end_date": "2025-11",
      "type": "coursework, published",
      "team_size": "2",
      "bullets": [
        "Custom MLflow scorers for missing-response detection and routing accuracy; used in two course sections."
      ],
      "agent_note": "Team of two - bullets describe only this persona's share."
    }
  ],
  "skills": {
    "languages": [
      "Python",
      "SQL"
    ],
    "data_bi": [
      "Databricks",
      "Unity Catalog",
      "Power BI"
    ],
    "backend_automation": [
      "LangGraph",
      "MLflow",
      "Mem0"
    ],
    "database_cloud": [
      "Delta Lake",
      "AWS"
    ],
    "familiar_with_not_shipped": [
      "Ray",
      "Kubeflow"
    ],
    "agent_note": "No certification claims - none exist for this persona."
  }
}

## Posting
{
  "id": 8660923002,
  "title": "Senior Applied ML/AI Scientist - Search",
  "location.name": "New York City, NY; San Francisco, CA",
  "content": "About Faire Faire is a technology wholesale platform built on the belief that the future is local. Independent retailers around the globe collectively represent a multi-hundred-billion-dollar wholesale market that has historically been fragmented and offline. At Faire, we're using the power of tech, data, and machine learning to connect this thriving community of entrepreneurs across the globe. Picture your favorite boutique in town — we help them discover the best products from around the world to sell in their stores. With the right tools and insights, we believe that we can level the playing field so businesses can grow and local communities can thrive. We’re looking for smart, resourceful and passionate people to join us as we power the shop local movement. If you believe in community, come join ours. About the role As a Senior Applied AI/ML Scientist on the Search team, you will help shape the technical vision, machine-learning algorithm strategy, and system design behind one of our most important growth levers: Search (the primary tool used by customers on any e-commerce site). You will advance real-time search and recommendation systems that power next-generation shopping experiences. You’ll work at the frontier of algorithms, combining query understanding, deep learning, transformer-based sequential modeling, graph neural networks, and structured behavioral data to return hyper-relevant, personalized products and brands for every user query. This is a rare chance to influence the end-to-end personalized discovery experience at Faire within a high-scale, deeply multi-modal environment, while collaborating closely with a talented team of scientists and engineers. What you'll do Build our next-generation Search ranking algorithms by integrating the latest advances in deep learning and machine learning to personalize the retailer discovery journey at Faire Leverage LLM to extract multimodal signals (text, visual) to better profile users and their intents. Partner closely with teams across Faire to experiment and improve the ML models for search ranking and beyond. Design and productionize natural-language search and discovery systems so that intelligent agents can generate relevant and personalized collections, explain search results, and assist retailers with browsing, filtering, and evaluation. Share best practices regarding deep learning model development, agent-workflow evaluation, and MLOps, and help teammates level up through code reviews and technical guidance. You're a great fit if you have 5+ years of industry experience building large-scale ML models with business impact and shipping ML solutions to production, including 3+ years in search, recommendation, or ads ranking A Master’s or PhD in Computer Science, Statistics, or a related STEM field. Strong programming skills (Python, Java, or equivalent) and hands-on experience with deep-learning libraries (e.g., PyTorch) and big data technologies (e.g., Spark). Deep understanding of machine learning best practices (e.g., training/serving, imbalanced data, A/B testing, feature engineering, and feature/model selection) and algorithms (e.g., user modeling, deep learning, and reinforcement learning) with applications in search, recommendation, and advertising domains. A product-focused mindset and a bias toward execution—moving quickly from research papers to prototypes and production. Excellent written and verbal communication skills and strong cross-functional influence that raise the technical bar beyond your immediate team. Bonus Points Contributions to open-source ML libraries or peer-reviewed publications in ML/AI. Industry experience developing and productizing LLM-based applications and systems in the search domain. Industry experience building search and recommendation systems for e-commerce or two-sided marketplaces. Experience using AI tools (e.g., Cursor, Claude Code, Codex) for code development and daily productivity. Familiarity with Kotlin Salary Range US: the pay range for this role is $211,000 to $290,500 per year. This role will also be eligible for equity and benefits. Actual base pay will be determined based on permissible factors such as transferable skills, work experience, market demands, and primary work location. The base pay range provided is subject to change and may be modified in the future. Hybrid Faire employees currently go into the office 3 days per week on Tuesdays, Thursdays, and a third flex day of their choosing (Monday, Wednesday, or Friday). Additionally, hybrid in-office roles will have the flexibility to work remotely up to 4 weeks per year. Specific Workplace and Information Technology positions may require onsite attendance 5 days per week as will be indicated in the job posting. Why you’ll love working at Faire Move fast: You'll own meaningful problems that serve customers around the globe with the agency to move fast and see your results clearly. Equipped to scale: We invest in what matters, including the latest enterprise AI tools, to help you work smarter and get more out of every day. Best in class: Our team is full of sharp, kind, and generous colleagues who care about their craft and about helping you grow in yours. Real rewards. Competitive pay, equity, and comprehensive benefits designed to support your life inside and outside of work. Belonging: We're intentional about building an environment where every Faire employee has equal access to opportunities, growth, and success. Faire was founded in 2017 by a team of early product and engineering leads from Square. We’re backed by some of the top investors in retail and tech including: Y Combinator, Lightspeed Venture Partners, Forerunner Ventures, Khosla Ventures, Sequoia Capital, Founders Fund, and DST Global. We have headquarters in San Francisco and Kitchener-Waterloo, and a global employee presence across offices in Toronto, London, and New York. To learn more about Faire and our customers, you can read more on our blog . Faire provides equal employment opportunities (EEO) to all employees and applicants for employment without regard to race, color, religion, sex, national origin, age, disability, genetics, sexual orientation, gender identity or gender expression. Faire is committed to providing access, equal opportunity and reasonable accommodation for individuals with disabilities in employment, its services, programs, and activities. Accommodations are available throughout the recruitment process and applicants with a disability may request to be accommodated throughout the recruitment process. We will work with all applicants to accommodate their individual accessibility needs. To request reasonable accommodation, please fill out our Accommodation Request Form ( https://bit.ly/faire-form) Privacy For information about the type of personal data Faire collects from applicants, as well as your choices regarding the data collected about you, please visit Faire’s Privacy Notice (https://www.faire.com/privacy)"
}
