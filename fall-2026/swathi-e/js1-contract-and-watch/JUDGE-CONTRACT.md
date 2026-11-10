# JUDGE-CONTRACT.md — the Claude judge (prompt contract, baseline)

Written by Swathi Baba Eswarappa, 2026-10-25, before any judge runs.
The decisions below are mine. Claude (chat) helped me phrase them.
This is the BASELINE prompt contract. The prompt experiment will change one
thing at a time from this version.

## What the judge is
Claude, called through Claude Code `claude -p` (not the bare model), from an
empty folder, with tools turned off, one fresh conversation per posting.
Model pinned and recorded in the README. Its verdict is a JUDGMENT, never a
record, and every output is labelled that way.

## In (per posting)
- Posting fields: title, location, and the full description text.
- Priya's fields: target roles (AI Engineer / ML Engineer primary, Data
  Engineer secondary), current location (Boston, MA), open to remote,
  student visa (F-1, OPT year 1), from her fictional profile.

## How the judge decides
A posting is RELEVANT only if all of these hold:
1. Role: the work fits Priya's target roles (AI/ML engineering, data
   engineering, or an early-career software engineering role).
2. Experience: the description asks for 0-1 years of experience, or says
   entry level, new grad, or early career. If it asks for more than 1 year,
   it is NOT RELEVANT.
3. Work authorization: if the description requires US citizenship, a
   security clearance, or says it will not sponsor visas, it is NOT
   RELEVANT, because Priya is on F-1/OPT.
4. Location: the job is in the United States, or Remote without naming a non-US country.

If the description does not state any experience requirement, the judge
decides on the title and the skills asked for, and must say
"experience not stated".

## Out (exactly this JSON, nothing else)
{
  "verdict": "relevant" | "not_relevant",
  "label": "judgment",
  "experience_found": "<exact quote from the description, or 'experience not stated'>",
  "authorization_found": "<exact quote about citizenship/clearance/sponsorship, or 'none stated'>",
  "posting_fields_cited": ["title", "location", "description"],
  "resume_fields_cited": ["target roles", "location", "visa status"],
  "reason": "<one or two sentences>"
}

## What the validator rejects
- Anything that is not valid JSON, or has missing or extra keys.
- A verdict other than "relevant" or "not_relevant".
- A label other than "judgment".
- Empty posting_fields_cited or resume_fields_cited.
- A quote in experience_found or authorization_found that does not appear
  word for word in the posting's description (unless it is exactly
  "experience not stated" or "none stated").
A rejected output is recorded as rejected, never repaired or guessed.

## Revision (2026-10-26, before any live judge call)
Rule 4 now limits Remote to the US, to match my title rule; 'Remote - Germany'
would otherwise have passed.
