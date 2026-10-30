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
- "citations": a non-empty list of objects, each with exactly the keys "resume_field", "posting_field" and "quote":
  - "resume_field": a dotted path that exists in the résumé JSON, such as "skills.languages"
  - "posting_field": one of "title", "location.name", "content"
  - "quote": text copied exactly from that posting field
- "label": "judgment"

## Résumé (fictional persona)
{{RESUME_JSON}}

## Posting
{{POSTING_JSON}}
