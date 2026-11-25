# Run 20261031T125015Z-live (LIVE fetch)

- Board: anthropic (Greenhouse), endpoint `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true`
- Source: live GET of the board endpoint
- Retrieved at: 2026-10-31T12:50:15Z · raw sha256 `1e5b62fec42a5b1d83e1c491da70215c5b8f77776097b2ef26e1fb4e7b0a7e88`
- Postings in response: 675 · previously seen ids: 681
- New since last run: 27

## 5173120008: Staff+ Software Engineer, Enterprise Connectivity (San Francisco, CA | New York City, NY)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, skills. posting.title "Staff+ Software Engineer, Enterprise Connectivity" contains none of resume.preferences.focus_terms. posting.title "Staff+ Software Engineer, Enterprise Connectivity" contains resume.preferences.excluded_title_words "staff". posting.location.name "San Francisco, CA | New York City, NY" contains resume.preferences.location_terms "new york", "san francisco". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: engineer; resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: staff |
| location | yes | resume.preferences.location_terms: new york, san francisco |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails: the title contains "engineer" but none of the focus terms. Condition 2 fails because the title contains the excluded word "staff", and condition 4 fails because the content never mentions "python". Only condition 3 (location) passes, on "san francisco" and "new york".

- Résumé evidence: resume.preferences.excluded_title_words: "staff"; resume.preferences.focus_terms: "machine learning"; resume.skills: "python"; resume.preferences.location_terms: "san francisco"
- Posting evidence: posting.title: "Staff+ Software Engineer, Enterprise Connectivity"; posting.location.name: "San Francisco, CA"
- Reply saved verbatim: `claude/5173120008.txt`

## 5174755008: Staff+ Software Engineer, Backend (San Francisco, CA | New York City, NY)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, skills. posting.title "Staff+ Software Engineer, Backend" contains none of resume.preferences.focus_terms. posting.title "Staff+ Software Engineer, Backend" contains resume.preferences.excluded_title_words "staff". posting.location.name "San Francisco, CA | New York City, NY" contains resume.preferences.location_terms "new york", "san francisco". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: engineer; resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: staff |
| location | yes | resume.preferences.location_terms: new york, san francisco |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title contains 'engineer' but no focus term, and condition 2 fails because the title contains the excluded word 'staff'. Location passes on 'san francisco', but condition 4 fails because the content never mentions 'python'.

- Résumé evidence: resume.preferences.excluded_title_words: "staff"; resume.preferences.focus_terms: "machine learning"; resume.skills: "python"; resume.preferences.location_terms: "san francisco"
- Posting evidence: posting.title: "Staff+ Software Engineer, Backend"; posting.location.name: "San Francisco, CA"
- Reply saved verbatim: `claude/5174755008.txt`

## 5394403008: Engineering Manager, Integrity and Attestation (San Francisco, CA | Seattle, WA)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, skills. posting.title "Engineering Manager, Integrity and Attestation" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Engineering Manager, Integrity and Attestation" contains resume.preferences.excluded_title_words "manager". posting.location.name "San Francisco, CA | Seattle, WA" contains resume.preferences.location_terms "san francisco", "seattle". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: manager |
| location | yes | resume.preferences.location_terms: san francisco, seattle |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title has the token "engineering" but not "engineer", and it has no focus term. Condition 2 fails because the title contains the excluded word "manager", and condition 4 fails because the content never mentions "python"; only condition 3 (location) passes.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.excluded_title_words: "manager"; resume.skills: "python"; resume.preferences.location_terms: "san francisco"
- Posting evidence: posting.title: "Engineering Manager, Integrity and Attestation"; posting.location.name: "San Francisco, CA"
- Reply saved verbatim: `claude/5394403008.txt`

## 5419154008: Staff / Senior Data Center Security Engineer (Remote-Friendly (Travel Required) | San Francisco, CA)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed title_seniority, skills. posting.title "Staff / Senior Data Center Security Engineer" contains resume.preferences.title_word "engineer" and resume.preferences.focus_terms "data". posting.title "Staff / Senior Data Center Security Engineer" contains resume.preferences.excluded_title_words "senior", "staff". posting.location.name "Remote-Friendly (Travel Required) | San Francisco, CA" contains resume.preferences.location_terms "san francisco". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | yes | resume.preferences.title_word: engineer; resume.preferences.focus_terms: data |
| title_seniority | no | resume.preferences.excluded_title_words: senior, staff |
| location | yes | resume.preferences.location_terms: san francisco |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 passes because the title contains "engineer" and "data", and condition 3 passes because the location contains "san francisco". Condition 2 fails because the title contains the excluded words "staff" and "senior", and condition 4 fails because the content never mentions "python".

- Résumé evidence: resume.preferences.excluded_title_words: "staff"; resume.preferences.excluded_title_words: "senior"; resume.skills: "python"; resume.preferences.title_word: "engineer"; resume.preferences.location_terms: "san francisco"
- Posting evidence: posting.title: "Staff / Senior Data Center Security Engineer"; posting.location.name: "San Francisco, CA"
- Reply saved verbatim: `claude/5419154008.txt`

## 5426617008: Public Sector Sales Lead (Paris, France)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, location, skills. posting.title "Public Sector Sales Lead" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Public Sector Sales Lead" contains resume.preferences.excluded_title_words "lead". posting.location.name "Paris, France" contains none of resume.preferences.location_terms. posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: lead |
| location | no | resume.preferences.location_terms: (none) |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title lacks "engineer" and every focus term, condition 2 fails because the title contains the excluded word "lead", and condition 3 fails because "Paris, France" matches no location term. Condition 4 also fails because the content never mentions "python".

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.excluded_title_words: "lead"; resume.preferences.location_terms: "united states"; resume.skills: "python"
- Posting evidence: posting.title: "Public Sector Sales Lead"; posting.location.name: "Paris, France"
- Reply saved verbatim: `claude/5426617008.txt`

## 5438311008: Anthropic Research Resident (San Francisco, CA | New York City, NY)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, skills. posting.title "Anthropic Research Resident" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Anthropic Research Resident" contains none of resume.preferences.excluded_title_words. posting.location.name "San Francisco, CA | New York City, NY" contains resume.preferences.location_terms "new york", "san francisco". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | yes | resume.preferences.location_terms: new york, san francisco |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title has neither "engineer" nor any focus term, and condition 4 fails because the content never mentions "python". Condition 2 passes with no excluded title words, and condition 3 passes on "san francisco" and "new york".

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.skills: "python"; resume.preferences.location_terms: "san francisco"
- Posting evidence: posting.title: "Anthropic Research Resident"; posting.location.name: "San Francisco, CA"
- Reply saved verbatim: `claude/5438311008.txt`

## 5439169008: Anthropic Research Resident (London, UK)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, location, skills. posting.title "Anthropic Research Resident" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Anthropic Research Resident" contains none of resume.preferences.excluded_title_words. posting.location.name "London, UK" contains none of resume.preferences.location_terms. posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | no | resume.preferences.location_terms: (none) |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title has no "engineer" token and no focus term. Condition 3 fails because "London, UK" matches no location term, and condition 4 fails because the content never mentions "python"; only condition 2 (no excluded title words) passes.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.location_terms: "united states"; resume.skills: "python"
- Posting evidence: posting.title: "Anthropic Research Resident"; posting.location.name: "London, UK"
- Reply saved verbatim: `claude/5439169008.txt`

## 5451912008: Director, Order-to-Cash Assurance (San Francisco, CA | Seattle, WA)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, skills. posting.title "Director, Order-to-Cash Assurance" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Director, Order-to-Cash Assurance" contains resume.preferences.excluded_title_words "director". posting.location.name "San Francisco, CA | Seattle, WA" contains resume.preferences.location_terms "san francisco", "seattle". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: director |
| location | yes | resume.preferences.location_terms: san francisco, seattle |
| skills | no | resume.skills: sql |

**Claude, model judgment (judge_v1).** Conditions 1 and 2 fail: the title has no "engineer" or focus term, and it contains the excluded word "director". Location passes on San Francisco and Seattle, but condition 4 fails because the content never mentions "python" (it mentions sql only).

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.excluded_title_words: "director"; resume.preferences.location_terms: "san francisco"; resume.skills: "python"
- Posting evidence: posting.title: "Director, Order-to-Cash Assurance"; posting.location.name: "San Francisco, CA | Seattle, WA"; posting.content: "Proficiency with SQL or similar tools"
- Reply saved verbatim: `claude/5451912008.txt`

## 5458064008: Enterprise Account Executive, Public Sector (Madrid, Spain)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, location, skills. posting.title "Enterprise Account Executive, Public Sector" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Enterprise Account Executive, Public Sector" contains none of resume.preferences.excluded_title_words. posting.location.name "Madrid, Spain" contains none of resume.preferences.location_terms. posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | no | resume.preferences.location_terms: (none) |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title has no "engineer" token and no focus term. Condition 3 fails because the location "Madrid, Spain" matches no location term. Condition 4 also fails because the content does not contain "python", although condition 2 passes.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.location_terms: "united states"; resume.skills: "python"
- Posting evidence: posting.title: "Enterprise Account Executive, Public Sector"; posting.location.name: "Madrid, Spain"
- Reply saved verbatim: `claude/5458064008.txt`

## 5458689008: Enterprise Account Executive, Public Sector (Milan, Italy)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, location, skills. posting.title "Enterprise Account Executive, Public Sector" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Enterprise Account Executive, Public Sector" contains none of resume.preferences.excluded_title_words. posting.location.name "Milan, Italy" contains none of resume.preferences.location_terms. posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | no | resume.preferences.location_terms: (none) |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title has no "engineer" token and no focus term. Condition 3 fails because "Milan, Italy" matches no location term. Condition 4 also fails because the content never contains the token "python".

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.location_terms: "united states"; resume.skills: "python"
- Posting evidence: posting.title: "Enterprise Account Executive, Public Sector"; posting.location.name: "Milan, Italy"
- Reply saved verbatim: `claude/5458689008.txt`

## 5461024008: Enterprise Account Executive - Semiconductors (London, UK)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, location, skills. posting.title "Enterprise Account Executive - Semiconductors" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Enterprise Account Executive - Semiconductors" contains none of resume.preferences.excluded_title_words. posting.location.name "London, UK" contains none of resume.preferences.location_terms. posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | no | resume.preferences.location_terms: (none) |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title has no 'engineer' token and no focus term. Condition 3 fails because 'London, UK' matches no location term. Condition 4 fails because the content does not contain 'python'. Condition 2 passes because the title has no excluded word.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.location_terms: "united states"; resume.skills: "python"
- Posting evidence: posting.title: "Enterprise Account Executive - Semiconductors"; posting.location.name: "London, UK"
- Reply saved verbatim: `claude/5461024008.txt`

## 5462040008: Customer Success Manager, Beneficial Deployments EMEA (London, UK)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, location, skills. posting.title "Customer Success Manager, Beneficial Deployments EMEA" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Customer Success Manager, Beneficial Deployments EMEA" contains resume.preferences.excluded_title_words "manager". posting.location.name "London, UK" contains none of resume.preferences.location_terms. posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: manager |
| location | no | resume.preferences.location_terms: (none) |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title has no "engineer" token and no focus term. Condition 2 fails on "manager", condition 3 fails because "London, UK" matches no location term, and condition 4 fails because the content never mentions "python".

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.excluded_title_words: "manager"; resume.preferences.location_terms: "united states"; resume.skills: "python"
- Posting evidence: posting.title: "Customer Success Manager, Beneficial Deployments EMEA"; posting.location.name: "London, UK"
- Reply saved verbatim: `claude/5462040008.txt`

## 5464234008: Data Engineer (San Francisco, CA | New York City, NY; Seattle, WA)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | relevant | record: recomputable from CONTRACT.md |
| Claude | relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** relevant: all four conditions passed. posting.title "Data Engineer" contains resume.preferences.title_word "engineer" and resume.preferences.focus_terms "data". posting.title "Data Engineer" contains none of resume.preferences.excluded_title_words. posting.location.name "San Francisco, CA | New York City, NY; Seattle, WA" contains resume.preferences.location_terms "new york", "san francisco", "seattle". posting.content contains python and resume.skills "sql".

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | yes | resume.preferences.title_word: engineer; resume.preferences.focus_terms: data |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | yes | resume.preferences.location_terms: new york, san francisco, seattle |
| skills | yes | resume.skills: python, sql |

**Claude, model judgment (judge_v1).** All four conditions pass. The title contains "engineer" and the focus term "data" with no excluded words, the location includes "San Francisco", and the content mentions Python plus SQL.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.focus_terms: "data"; resume.preferences.location_terms: "san francisco"; resume.skills: "python"; resume.skills: "sql"
- Posting evidence: posting.title: "Data Engineer"; posting.location.name: "San Francisco, CA"; posting.content: "Strong SQL and Python"
- Reply saved verbatim: `claude/5464234008.txt`

## 5465561008: Senior Partner Systems Analyst  (San Francisco, CA)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, skills. posting.title "Senior Partner Systems Analyst " lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Senior Partner Systems Analyst " contains resume.preferences.excluded_title_words "senior". posting.location.name "San Francisco, CA" contains resume.preferences.location_terms "san francisco". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: senior |
| location | yes | resume.preferences.location_terms: san francisco |
| skills | no | resume.skills: sql |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title lacks the token "engineer" and every focus term, and condition 2 fails because the title contains the excluded word "senior". Condition 3 passes on "san francisco", and condition 4 fails because the content never contains the token "python", though it does mention "sql".

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.excluded_title_words: "senior"; resume.skills: "python"
- Posting evidence: posting.title: "Senior Partner Systems Analyst"; posting.location.name: "San Francisco"
- Reply saved verbatim: `claude/5465561008.txt`

## 5465578008: Performance & Talent Programs Manager  (New York City, NY; San Francisco, CA | New York City, NY; Seattle, WA)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, skills. posting.title "Performance & Talent Programs Manager " lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Performance & Talent Programs Manager " contains resume.preferences.excluded_title_words "manager". posting.location.name "New York City, NY; San Francisco, CA | New York City, NY; Seattle, WA" contains resume.preferences.location_terms "new york", "san francisco", "seattle". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: manager |
| location | yes | resume.preferences.location_terms: new york, san francisco, seattle |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title lacks "engineer" and every focus term, and condition 2 fails because the title contains the excluded word "manager". Location passes (New York, San Francisco, Seattle), but condition 4 fails because the content never mentions "python".

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.excluded_title_words: "manager"; resume.skills: "python"
- Posting evidence: posting.title: "Performance & Talent Programs Manager"; posting.location.name: "New York City, NY"
- Reply saved verbatim: `claude/5465578008.txt`

## 5466480008: Staff+ Software Engineer, Deployment (Remote-Friendly (Travel-Required) | San Francisco, CA | Seattle, WA | New York City, NY)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, skills. posting.title "Staff+ Software Engineer, Deployment" contains none of resume.preferences.focus_terms. posting.title "Staff+ Software Engineer, Deployment" contains resume.preferences.excluded_title_words "staff". posting.location.name "Remote-Friendly (Travel-Required) | San Francisco, CA | Seattle, WA | New York City, NY" contains resume.preferences.location_terms "new york", "san francisco", "seattle". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: engineer; resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: staff |
| location | yes | resume.preferences.location_terms: new york, san francisco, seattle |
| skills | no | resume.skills: aws |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title has "engineer" but no focus term, and condition 2 fails because the title contains the excluded word "staff". Location passes via "San Francisco", but condition 4 fails because the content never mentions "python".

- Résumé evidence: resume.preferences.excluded_title_words: "staff"; resume.preferences.title_word: "engineer"; resume.skills: "python"
- Posting evidence: posting.title: "Staff+ Software Engineer, Deployment"; posting.location.name: "San Francisco, CA"; posting.content: "such as Rust, Go, C++, or Java"
- Reply saved verbatim: `claude/5466480008.txt`

## 5466517008: Field Engineer, Data Center Design and Engineering (Remote-Friendly, United States)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed skills. posting.title "Field Engineer, Data Center Design and Engineering" contains resume.preferences.title_word "engineer" and resume.preferences.focus_terms "data". posting.title "Field Engineer, Data Center Design and Engineering" contains none of resume.preferences.excluded_title_words. posting.location.name "Remote-Friendly, United States" contains resume.preferences.location_terms "united states". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | yes | resume.preferences.title_word: engineer; resume.preferences.focus_terms: data |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | yes | resume.preferences.location_terms: united states |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Conditions 1-3 pass: the title contains 'engineer' and 'data', has no excluded title words, and the location contains 'united states'. Condition 4 fails because the posting content never mentions 'python'.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.focus_terms: "data"; resume.preferences.location_terms: "united states"; resume.skills: "python"
- Posting evidence: posting.title: "Field Engineer, Data Center Design and Engineering"; posting.location.name: "Remote-Friendly, United States"
- Reply saved verbatim: `claude/5466517008.txt`

## 5467083008: Senior Engineer, Bioinformatics (San Francisco, CA)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, skills. posting.title "Senior Engineer, Bioinformatics" contains none of resume.preferences.focus_terms. posting.title "Senior Engineer, Bioinformatics" contains resume.preferences.excluded_title_words "senior". posting.location.name "San Francisco, CA" contains resume.preferences.location_terms "san francisco". posting.content contains python but no other item from resume.skills.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: engineer; resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: senior |
| location | yes | resume.preferences.location_terms: san francisco |
| skills | no | resume.skills: python |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title contains "engineer" but none of the focus terms, and condition 2 fails because the title contains the excluded word "senior". Condition 3 passes on "San Francisco", but condition 4 fails because the content mentions Python and none of the other listed skills (sql, spark, pytorch, aws, docker).

- Résumé evidence: resume.preferences.excluded_title_words: "senior"; resume.preferences.focus_terms: "machine learning"; resume.preferences.location_terms: "san francisco"; resume.skills: "python"
- Posting evidence: posting.title: "Senior Engineer, Bioinformatics"; posting.location.name: "San Francisco, CA"; posting.content: "Are proficient in Python"
- Reply saved verbatim: `claude/5467083008.txt`

## 5467092008: Research Scientist, Life Sciences (Large Molecules, Antibody Design)  (San Francisco, CA)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, skills. posting.title "Research Scientist, Life Sciences (Large Molecules, Antibody Design) " lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Research Scientist, Life Sciences (Large Molecules, Antibody Design) " contains none of resume.preferences.excluded_title_words. posting.location.name "San Francisco, CA" contains resume.preferences.location_terms "san francisco". posting.content contains python but no other item from resume.skills.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | yes | resume.preferences.location_terms: san francisco |
| skills | no | resume.skills: python |

**Claude, model judgment (judge_v1).** Condition 1 fails: the title does not contain "engineer" or any focus term such as "ai", "ml", or "data". The title has no excluded words, the location matches "san francisco", and the content mentions python and ml, but the posting is still not relevant because condition 1 fails.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.location_terms: "san francisco"
- Posting evidence: posting.title: "Research Scientist, Life Sciences (Large Molecules, Antibody Design) "; posting.location.name: "San Francisco, CA"
- Reply saved verbatim: `claude/5467092008.txt`

## 5467099008: Research Scientist, Life Sciences (Large Molecules, Process Development)  (San Francisco, CA)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, skills. posting.title "Research Scientist, Life Sciences (Large Molecules, Process Development) " lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Research Scientist, Life Sciences (Large Molecules, Process Development) " contains none of resume.preferences.excluded_title_words. posting.location.name "San Francisco, CA" contains resume.preferences.location_terms "san francisco". posting.content contains python but no other item from resume.skills.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | yes | resume.preferences.location_terms: san francisco |
| skills | no | resume.skills: python |

**Claude, model judgment (judge_v1).** Condition 1 fails: the title has no "engineer" token and no focus term. Conditions 2 (no excluded title words) and 3 ("san francisco" in the location) pass, and condition 4 fails because the content mentions Python but no other résumé skill (sql, spark, pytorch, aws, docker).

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.skills: "sql"
- Posting evidence: posting.title: "Research Scientist, Life Sciences (Large Molecules, Process Development)"; posting.location.name: "San Francisco, CA"; posting.content: "Python for data analysis and automation"
- Reply saved verbatim: `claude/5467099008.txt`

## 5467233008: Contracts Manager, GTM (San Francisco, CA)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, skills. posting.title "Contracts Manager, GTM" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Contracts Manager, GTM" contains resume.preferences.excluded_title_words "manager". posting.location.name "San Francisco, CA" contains resume.preferences.location_terms "san francisco". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: manager |
| location | yes | resume.preferences.location_terms: san francisco |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title has no "engineer" token and no focus term, and condition 2 fails because the title contains the excluded word "manager". Condition 3 passes (San Francisco), and condition 4 fails because "python" does not appear in the content.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.excluded_title_words: "manager"; resume.preferences.location_terms: "san francisco"; resume.skills: "python"
- Posting evidence: posting.title: "Contracts Manager, GTM"; posting.location.name: "San Francisco, CA"
- Reply saved verbatim: `claude/5467233008.txt`

## 5467425008: Business Recruiter (Dublin, IE)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, location, skills. posting.title "Business Recruiter" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Business Recruiter" contains none of resume.preferences.excluded_title_words. posting.location.name "Dublin, IE" contains none of resume.preferences.location_terms. posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | no | resume.preferences.location_terms: (none) |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title "Business Recruiter" contains neither "engineer" nor any focus term, and condition 3 fails because "Dublin, IE" matches no location term. Condition 4 also fails because the content never mentions "python"; condition 2 passes since the title has no excluded words.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.location_terms: "united states"; resume.skills: "python"
- Posting evidence: posting.title: "Business Recruiter"; posting.location.name: "Dublin, IE"
- Reply saved verbatim: `claude/5467425008.txt`

## 5467690008: Research Operations Lead, Biology (Boston, MA)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, skills. posting.title "Research Operations Lead, Biology" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Research Operations Lead, Biology" contains resume.preferences.excluded_title_words "lead". posting.location.name "Boston, MA" contains resume.preferences.location_terms "boston". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: lead |
| location | yes | resume.preferences.location_terms: boston |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title has no 'engineer' and no focus term, and condition 2 fails because the title contains the excluded word 'lead'. Condition 3 passes on 'Boston', and condition 4 fails because the content never mentions 'python'.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.excluded_title_words: "lead"; resume.preferences.location_terms: "boston"; resume.skills: "python"
- Posting evidence: posting.title: "Research Operations Lead, Biology"; posting.location.name: "Boston, MA"
- Reply saved verbatim: `claude/5467690008.txt`

## 5468266008: Content Strategy Lead, Executive Programs (San Francisco, CA | New York City, NY)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed engineering_role, title_seniority, skills. posting.title "Content Strategy Lead, Executive Programs" lacks resume.preferences.title_word "engineer" and contains none of resume.preferences.focus_terms. posting.title "Content Strategy Lead, Executive Programs" contains resume.preferences.excluded_title_words "lead". posting.location.name "San Francisco, CA | New York City, NY" contains resume.preferences.location_terms "new york", "san francisco". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | no | resume.preferences.title_word: (none); resume.preferences.focus_terms: (none) |
| title_seniority | no | resume.preferences.excluded_title_words: lead |
| location | yes | resume.preferences.location_terms: new york, san francisco |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Condition 1 fails because the title has no 'engineer' token or focus term, and condition 2 fails because the title contains the excluded word 'lead'. Condition 3 passes on 'San Francisco', and condition 4 fails because the content has no 'python' token.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.excluded_title_words: "lead"; resume.preferences.location_terms: "san francisco"; resume.skills: "python"
- Posting evidence: posting.title: "Content Strategy Lead, Executive Programs"; posting.location.name: "San Francisco, CA"
- Reply saved verbatim: `claude/5468266008.txt`

## 5468374008: Data Center Power Generation and Microgrids Engineer (Remote-Friendly, United States)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed skills. posting.title "Data Center Power Generation and Microgrids Engineer" contains resume.preferences.title_word "engineer" and resume.preferences.focus_terms "data". posting.title "Data Center Power Generation and Microgrids Engineer" contains none of resume.preferences.excluded_title_words. posting.location.name "Remote-Friendly, United States" contains resume.preferences.location_terms "united states". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | yes | resume.preferences.title_word: engineer; resume.preferences.focus_terms: data |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | yes | resume.preferences.location_terms: united states |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Conditions 1–3 pass: the title contains "engineer" and "data", has no excluded seniority word, and the location contains "united states". Condition 4 fails because the content never mentions "python" or any other listed skill.

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.focus_terms: "data"; resume.preferences.location_terms: "united states"; resume.skills: "python"
- Posting evidence: posting.title: "Data Center Power Generation and Microgrids Engineer"; posting.location.name: "Remote-Friendly, United States"; posting.content: "in tools such as ETAP, SKM, PSS®E, PSCAD, or EasyPower"
- Reply saved verbatim: `claude/5468374008.txt`

## 5468380008: Data Center Substation, Protection & Automation Engineer (Remote-Friendly, United States)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed skills. posting.title "Data Center Substation, Protection & Automation Engineer" contains resume.preferences.title_word "engineer" and resume.preferences.focus_terms "data". posting.title "Data Center Substation, Protection & Automation Engineer" contains none of resume.preferences.excluded_title_words. posting.location.name "Remote-Friendly, United States" contains resume.preferences.location_terms "united states". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | yes | resume.preferences.title_word: engineer; resume.preferences.focus_terms: data |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | yes | resume.preferences.location_terms: united states |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Conditions 1-3 pass: the title contains "engineer" and the focus term "data" with no excluded words, and the location contains "united states". Condition 4 fails because posting.content never mentions "python" (or any other résumé skill).

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.focus_terms: "data"; resume.preferences.location_terms: "united states"; resume.skills: "python"
- Posting evidence: posting.title: "Data Center Substation, Protection & Automation Engineer"; posting.location.name: "Remote-Friendly, United States"; posting.content: "Protection engineering and substation automation are the core of this role"
- Reply saved verbatim: `claude/5468380008.txt`

## 5468392008: Data Center Electrical Engineer – Design (Remote-Friendly, United States)

| Judge | Verdict | What it is |
|---|---|---|
| Rule | not_relevant | record: recomputable from CONTRACT.md |
| Claude | not_relevant | model judgment, not a verified fact |

Verdicts agree: yes

**Rule record.** not_relevant: failed skills. posting.title "Data Center Electrical Engineer – Design" contains resume.preferences.title_word "engineer" and resume.preferences.focus_terms "data". posting.title "Data Center Electrical Engineer – Design" contains none of resume.preferences.excluded_title_words. posting.location.name "Remote-Friendly, United States" contains resume.preferences.location_terms "united states". posting.content does not contain python as a whole word.

| Condition | Passed | Matched |
|---|---|---|
| engineering_role | yes | resume.preferences.title_word: engineer; resume.preferences.focus_terms: data |
| title_seniority | yes | resume.preferences.excluded_title_words: (none) |
| location | yes | resume.preferences.location_terms: united states |
| skills | no | resume.skills: (none) |

**Claude, model judgment (judge_v1).** Conditions 1–3 pass: the title contains "engineer" and the focus term "data" with no excluded words, and the location contains "united states". Condition 4 fails because the content never mentions "python".

- Résumé evidence: resume.preferences.title_word: "engineer"; resume.preferences.focus_terms: "data"; resume.preferences.location_terms: "united states"; resume.skills: "python"
- Posting evidence: posting.title: "Data Center Electrical Engineer"; posting.location.name: "United States"
- Reply saved verbatim: `claude/5468392008.txt`

