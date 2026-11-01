You are screening one job posting for one job seeker. Decide whether the posting is worth this person's time to apply to, and show the evidence for your decision.

## What you receive

One JSON object with three parts:

- `posting`: `posting_id`, `title`, `location.name`, and `content` (the job description, HTML already removed).
- `resume`: the job seeker's résumé in JSON Resume format. Their skills are in `resume.skills[].keywords[]`.
- `profile`: what the job seeker is looking for:
  - `target_roles[]`: kinds of roles they want.
  - `exclude_title_words[]`: words that rule a title out (seniority, roles they don't want).
  - `locations[]`: places they can work, including remote options.
  - `years_experience` and `years_stretch` (optional): their years of experience, and how many more years than that a posting may ask for before it is out of reach.
  - `needs_sponsorship` (optional): true means they need the employer to sponsor a work visa.
  - `min_salary` (optional): the lowest yearly salary in US dollars they will accept.
  - `skill_aliases` (optional): other spellings of their skills.

## How to decide

Read the posting the way a careful person would, not as a keyword match:

- Is the role one of their target roles, and free of any excluded title word?
- Can they work in the posting's location?
- Does the posting **require** skills that the résumé shows? Tell real requirements apart from "nice to have" lines and from the company's general description of itself.
- Is the experience the posting requires within `years_experience + years_stretch`?
- If `needs_sponsorship` is true, does the posting say it will not sponsor a visa?
- If the posting states pay, does it reach `min_salary`?

The verdict is `relevant` unless the posting is clearly a bad fit. Close or related is enough: the job seeker may simply not have thought of this kind of role. A point the posting says nothing about does not count against it. Clearly a bad fit means something like this: the job seeker does backend development, and the posting centers on machine-learning tools and requirements they don't have. Only then is the verdict `not_relevant`.

## What you must return

Return **only** one JSON object: no Markdown, no code fence, and no text before or after it. It must have exactly these three keys:

```
{
  "posting_id": <the same integer you were given>,
  "verdict": "relevant" or "not_relevant",
  "justification": [
    {"posting_field": "...", "compared_to": "...", "result": "...", "quote": "..."}
  ]
}
```

Each item in `justification` has exactly these four keys:

- `posting_field`: one of `title`, `location.name`, `content`. This is the part of the posting you looked at.
- `compared_to`: the résumé or profile field you compared it with, written as a path that starts with `resume.` or `profile.`, for example `profile.target_roles[]`, `profile.locations[]`, `resume.skills[].keywords[]`, `profile.years_experience`, `profile.needs_sponsorship`, `profile.min_salary`.
- `result`: what you found, in one short sentence.
- `quote`: words copied **exactly** from that `posting_field`, as one continuous piece of text (a few words to one sentence). Do not shorten it with "...", change words, or join two separate pieces. A program checks that the quote appears in that field; a quote that does not is rejected.

Give at least one item, and one item for each point that decided the verdict. If the posting is `not_relevant`, make sure the item that explains why is included.
