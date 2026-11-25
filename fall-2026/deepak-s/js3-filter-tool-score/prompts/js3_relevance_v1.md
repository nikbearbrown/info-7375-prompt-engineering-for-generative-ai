## System
You label one job posting for one fictional job seeker, using only the posting context you are given and the labeling rule below. You never use knowledge outside that context.

## User
Labeling rule (FILTER.md section 0, quoted): a posting is relevant when all of these hold, and not_relevant otherwise:
  - Job family: machine learning engineering, AI engineering, applied science, data science, LLM engineering, or applied ML research.
  - Seniority: entry level through mid level. Intern, Staff, Senior Staff, Principal, Director, Lead, Head and management roles are not relevant. A Senior role is relevant only when the stated minimum experience requirement is five years or less.
  - Location: Boston, New York or NYC, Seattle, or a remote position that explicitly allows working from the United States.
  - Title versus text: the actual responsibilities and minimum qualifications take priority over the title. A suitable title does not rescue a posting whose minimum required experience is more than five years (the same line as rule E01).
  - When I am unsure, the label is not_relevant.

Posting context:
{{CONTEXT}}

Answer with JSON only, no prose and no code fence:
{"label": "relevant"} or {"label": "not_relevant"}
