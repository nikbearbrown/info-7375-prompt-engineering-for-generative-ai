# Labeling rule — how I hand-label a posting

English translation of `LABELING_RULE.zh.md`, which was committed before any label (commit ab1e292) in my working repo (see `evidence/git-history.txt`).

Author: Isaac Tai. Written before labeling any posting (R23).

I judge from Aarav Patel's point of view (résumé: `personas/aarav-patel.resume.json`; profile: `personas/aarav-patel.profile.json`).
This is how I judge when I read a JD myself, not the program's rule: I read what the whole JD means, not whether words match.

I go in order. **If any step doesn't fit, I label it `not_relevant` and stop reading**; only if all six steps pass do I label it `relevant`.

1. **Title**: I only keep reading if it's related to engineering.
2. **Location**: is it in the US (including US remote)? Only if yes do I keep reading. **No location written (empty, `N/A`, `na`), or only `Remote` without a country → always counts as a pass; keep reading.** (This line was added after I had labeled rows 1–3; all three of those have a location, so they aren't affected.)
3. **Skills**: I jump straight to the skills section (if there is one); if not, I search the whole text for which skills it mentions. Only if **two or three of them are ones Aarav knows** (the résumé's `skills[].keywords[]`) do I keep reading.
4. **Sponsorship**: Aarav needs visa sponsorship. The JD says explicitly it won't sponsor → doesn't fit; not mentioned → keep reading.
5. **Salary**: if a salary is given, does it reach the lowest yearly salary Aarav accepts (the profile's `min_salary`)? Not given → keep reading.
6. **Other requirements**: is anything extra emphasized, for example work experience? A requirement clearly beyond Aarav's level (profile: 2 years of experience, at most 2 more) → doesn't fit.

**Nice to have counts as must have** (in steps 3 and 6): if the JD lists it, it's expected, because someone who has it will certainly apply. So skills and requirements under "Nice to have", "Preferred" or "Bonus" count the same as those under "Requirements".

Each label gets a one-line reason: which step it failed at, and which sentence in the JD made me decide.
