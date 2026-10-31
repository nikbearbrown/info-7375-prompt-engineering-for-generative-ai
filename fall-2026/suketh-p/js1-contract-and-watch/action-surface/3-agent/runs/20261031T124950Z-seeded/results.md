# Run 20261031T124950Z-seeded (SEEDED: replay of a saved earlier response, not a live fetch)

- Board: anthropic (Greenhouse), endpoint `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true`
- Source: saved earlier response runs/20261028T102612Z-live/raw_response.json.gz
- Retrieved at: 2026-10-31T12:49:50Z · raw sha256 `5f74dcc8cdb11ed84ba808a693fd63539ce8fc78bf46fbedf2dcaf91acf99ae5`
- Postings in response: 681 · previously seen ids: 680
- New since last run: 1

## 5418610008: Data Engineer, GTM (San Francisco, CA | New York City, NY)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | relevant | record: recomputable from CONTRACT.md |
| Claude | relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** relevant: all four conditions passed. posting.title "Data Engineer, GTM" contains resume.preferences.title_word "engineer" and resume.preferences.focus_terms "data". posting.title "Data Engineer, GTM" contains none of resume.preferences.excluded_title_words. posting.location.name "San Francisco, CA | New York City, NY" contains resume.preferences.location_terms "new york", "san francisco". posting.content contains python and resume.skills "sql".

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | yes | resume.preferences.title_word: engineer; resume.preferences.focus_terms: data |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | yes | resume.preferences.location_terms: new york, san francisco |
| skills | yes | resume.skills: python, sql |

**Claude, model judgment (judge_v1).** All four conditions pass: the title contains "engineer" and the focus term "data" with no excluded seniority words, the location matches "san francisco" and "new york", and the content mentions "python" plus the additional skill "sql".

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.focus_terms: "data"; resume.preferences.location_terms: "san francisco"; resume.skills: "python"; resume.skills: "sql"
- Posting evidence: posting.title: "Data Engineer, GTM"; posting.location.name: "San Francisco, CA"; posting.content: "Expertise in SQL and Python"
- Reply saved verbatim: `claude/5418610008.txt`

