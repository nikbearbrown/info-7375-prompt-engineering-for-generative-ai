In this folder, jsagent/rules.py holds my job-relevance rule. It has a defect: an internship posting such as
Databricks 6866538002 "Data Science Intern (2027 Start)" is rated "relevant".

Change the rule so that a posting whose title contains the whole word "Intern" or "Internship" (any case) is
NOT RELEVANT, the same way the seniority words already exclude a posting. The justification must say which
intern word was found. Keep whole-word matching: words like "Internal", "International" and "Internals" must
not be excluded.

Only change jsagent/rules.py. Do not edit tests or any other file. When you are done, reply with a short summary
of exactly what you changed.
