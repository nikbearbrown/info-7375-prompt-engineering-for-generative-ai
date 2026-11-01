# Sampling report

Run: 2026-10-31T22:23:34-04:00  
Prompt: `prompts/baseline.txt` (sha256 07ddb9d75b98)  
Postings: first 5 dev rows of labels.csv, 4 fresh `claude -p` calls each

*agree* = runs giving the most common verdict (invalid replies are not a verdict).

| id | title | run 1 | run 2 | run 3 | run 4 | agree | my label | matched my label |
|---|---|---|---|---|---|---|---|---|
| 8006729003 | Software Engineer II - SMS International | not_relevant | not_relevant | not_relevant | not_relevant | 4/4 | not_relevant | 4/4 |
| 8004625003 | Engineering Manager, Marketing Engineering & AI Agents - Amplify | not_relevant | not_relevant | not_relevant | invalid | 3/4 | not_relevant | 3/4 |
| 7984272003 | Head of Global Compensation | not_relevant | not_relevant | not_relevant | not_relevant | 4/4 | not_relevant | 4/4 |
| 7801047003 | Sr. Lead Software Engineer | not_relevant | not_relevant | not_relevant | not_relevant | 4/4 | not_relevant | 4/4 |
| 7597868003 | Senior Software Engineer - Profiles, Lists and Segments | not_relevant | not_relevant | not_relevant | not_relevant | 4/4 | not_relevant | 4/4 |

**Invalid replies: 1/20**

## Details

### 8006729003 Software Engineer II - SMS International (my label: not_relevant)

- run 1: `not_relevant` (ok) The posting is a Fullstack Software Engineer II role asking for 3-5 years of experience, and its stack (Python, React, AWS) overlaps with the résumé's skills. It fails the location check because its only location is London, UK and the résumé targets the United States. — `sampling/raw/8006729003_20261031T222340_614341.json`
- run 2: `not_relevant` (ok) The role is a mid-level full stack Software Engineer II that matches the résumé's target roles, and its skills overlap (Python, React, AWS, CI/CD). However, the only location is London, UK, and the résumé targets only the United States. — `sampling/raw/8006729003_20261031T222346_488473.json`
- run 3: `not_relevant` (ok) The posting is a Fullstack Software Engineer II role that uses Python and React, which matches the résumé's target roles and skills. But the only location is London, UK, and the résumé's target location is the United States, so it fails the location check. — `sampling/raw/8006729003_20261031T222350_593470.json`
- run 4: `not_relevant` (ok) The posting is a Fullstack Software Engineer II role asking for 3-5 years of experience, and it uses Python and React, which match the résumé. However, its only location is London, UK, and the résumé targets only the United States, so it fails the location check. — `sampling/raw/8006729003_20261031T222355_552303.json`

### 8004625003 Engineering Manager, Marketing Engineering & AI Agents - Amplify (my label: not_relevant)

- run 1: `not_relevant` (ok) The title is Engineering Manager, and Manager-level roles are excluded. The posting also asks for 8+ years of development experience plus 4+ years as an engineering manager, far above the résumé's mid-level target of about 3 years, even though Boston is in the US, Klaviyo supports work authorization, and its TypeScript/React/Python/FastAPI stack overlaps with the résumé's skills. — `sampling/raw/8004625003_20261031T222401_157477.json`
- run 2: `not_relevant` (ok) The title is Engineering Manager, and the posting asks for 8+ years of software development and 4+ years as an engineering manager. That is Manager level, so it fails the seniority check for a candidate targeting mid-level Software, Frontend, or Full Stack Engineer roles with about 3 years of experience. — `sampling/raw/8004625003_20261031T222406_118340.json`
- run 3: `not_relevant` (ok) The posting is an Engineering Manager role that asks for 8+ years of development experience, including 4+ years managing engineers. The résumé targets mid-level Software, Frontend, or Full Stack Engineer roles with about 3 years of individual-contributor experience, so the manager-level seniority rules it out even though the location (Boston), sponsorship, and TypeScript/React/Python/FastAPI skills match. — `sampling/raw/8004625003_20261031T222411_419603.json`
- run 4: `invalid` (no Claude verdict)  — `sampling/raw/8004625003_20261031T222416_904971.json`

### 7984272003 Head of Global Compensation (my label: not_relevant)

- run 1: `not_relevant` (ok) The posting is for a Head of Global Compensation, an HR leadership role that asks for 10+ years of compensation experience. It is not a software, frontend, or full stack engineering role, and its skills do not overlap with the résumé's TypeScript, Angular, React, and Node.js skills. — `sampling/raw/7984272003_20261031T222422_325111.json`
- run 2: `not_relevant` (ok) The posting is for a Head of Global Compensation, an HR leadership role. It is not a software, frontend, or full stack engineering role, it is above Director level, and it asks for 10+ years of compensation experience. None of its skills overlap with the résumé's TypeScript, Angular, React, and Node.js skills or the target roles. — `sampling/raw/7984272003_20261031T222427_120835.json`
- run 3: `not_relevant` (ok) The posting is for a Head of Global Compensation, an HR leadership role. It asks for 10+ years of compensation experience and none of the software skills on the résumé, so it fails the role check against the résumé's target roles (Software, Frontend, and Full Stack Engineer). — `sampling/raw/7984272003_20261031T222432_661003.json`
- run 4: `not_relevant` (ok) The posting is for a Head of Global Compensation, an HR leadership role that asks for 10+ years of compensation experience. It does not match the résumé's target roles of Software, Frontend, or Full Stack Engineer, and none of the résumé's skills (TypeScript, Angular, React, Node.js) appear in it, even though the Boston, MA location is in the US. — `sampling/raw/7984272003_20261031T222437_538702.json`

### 7801047003 Sr. Lead Software Engineer (my label: not_relevant)

- run 1: `not_relevant` (ok) The title is 'Sr. Lead Software Engineer' and the posting asks for 8+ years of professional experience. That is well over the 3-year limit for Senior or Lead roles, and the résumé shows about 3 years (mid-level), so the posting is not relevant even though the Boston, MA location fits and Python/FastAPI/AWS overlap with the résumé. — `sampling/raw/7801047003_20261031T222443_918706.json`
- run 2: `not_relevant` (ok) The title "Sr. Lead Software Engineer" is a Senior/Lead role, and the content asks for 8+ years of professional software engineering experience. That is more than the 3-year limit, and the résumé shows about 3 years at a mid-level target seniority. The location (Boston, MA) and some skills (Python, FastAPI, AWS) match, but the experience requirement rules this posting out. — `sampling/raw/7801047003_20261031T222449_105522.json`
- run 3: `not_relevant` (ok) The title is Sr. Lead Software Engineer in Boston, MA, and the posting asks for 8+ years of professional software engineering experience, which is well over the 3-year limit for Senior or Lead titles. The résumé shows about 3 years of experience (target.seniority, experience), so the role fails the experience check even though the location is in the US and some skills overlap (Python, FastAPI, AWS). — `sampling/raw/7801047003_20261031T222455_862099.json`
- run 4: `not_relevant` (ok) The title is Sr. Lead Software Engineer and the content asks for 8+ years of professional experience, which is well above the 3-year limit for Senior or Lead roles and well above the résumé's roughly 3 years at mid level. Boston is a US location and some skills overlap (Python, FastAPI, AWS basics), but the experience requirement alone makes this not relevant. — `sampling/raw/7801047003_20261031T222501_722254.json`

### 7597868003 Senior Software Engineer - Profiles, Lists and Segments (my label: not_relevant)

- run 1: `not_relevant` (ok) The title is Senior Software Engineer, and the content asks for 5+ years of full-stack experience, which is more than the 3-year limit for Senior roles; the résumé shows about 3 years (2022-07 to 2025-07) and targets mid-level roles. Location (Boston, MA) and skills (React, TypeScript, JavaScript, Python, HTML, CSS) do overlap, but the experience check fails. — `sampling/raw/7597868003_20261031T222506_874580.json`
- run 2: `not_relevant` (ok) The posting is for a Senior Software Engineer and asks for 5+ years of full-stack experience. That is more than the 3-year limit for Senior titles, and the résumé shows about 3 years (2022-07 to 2025-07). The posting does match on location (Boston, MA), says nothing against sponsorship, and its React/TypeScript/Python skills overlap with the résumé's, but the experience requirement rules it out. — `sampling/raw/7597868003_20261031T222512_005849.json`
- run 3: `not_relevant` (ok) The posting is a Senior Software Engineer role in Boston, MA, and its skills (React, TypeScript, JavaScript, HTML, CSS, Python) match the résumé well. However, the content asks for 5+ years of full-stack experience, which fails the Senior-title check of more than 3 years, and the résumé shows about 3 years of experience at a mid-level target. — `sampling/raw/7597868003_20261031T222517_846133.json`
- run 4: `not_relevant` (ok) The title is Senior Software Engineer, and the content asks for '5+ years of experience in full-stack development', which is more than the 3-year limit for Senior titles. The résumé shows about 3 years (2022-07 to 2025-07), even though the Boston, MA location and the React/TypeScript/JavaScript/HTML/CSS skills match. — `sampling/raw/7597868003_20261031T222524_165424.json`

## My conclusion

