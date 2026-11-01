# Hand check of one rule verdict (Riya, 2026-10-31)

Posting 6866538002, "Data Science Intern (2027 Start)", from the 2026-10-31 live snapshot. `posting-6866538002.txt` is
the exact text the agent read. I worked through my rule by hand **before** being told the code's verdict.

| Rule step | My hand answer | Code (`rules.judge`) | Match? |
|---|---|---|---|
| Title word | yes ("Data Science") | yes ("Data Science") | yes |
| Skills (need 2) | I found none | 2: Python, SQL | **no**: both appear once, in "Proven ability to work with data in SQL and Python". I missed that line |
| Location US | yes | yes | yes |
| Seniority word in title | no | no | yes |
| **Verdict** | **not relevant**: it is an internship, and Arya is looking for full-time work | **relevant** | **no** |

What this shows:
- The code's skill count was right, and my hand count missed a line in a 700-word posting.
- My verdict disagrees with my own rule for a reason the rule doesn't contain: it has no Intern/Internship exclusion, so it lets
  internships through. I did **not** change the rule tonight, because that would change results already reported. Next version: add
  Intern and Internship to the exclusion words.
