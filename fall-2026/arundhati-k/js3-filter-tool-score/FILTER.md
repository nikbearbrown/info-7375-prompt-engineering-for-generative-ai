# FILTER.md — the gate (v1, 2026-11-25)

Written **before** any test or code in this folder. Later changes go in the Revisions section at the bottom, each
with a version number, the date, and the measurement that caused it. v1 is not edited after this commit.

**Where the words come from.** Sections 1–5 are my answers, typed in chat on 2026-11-25 (verbatim in
[Appendix A](#appendix-a--my-answers-verbatim)). Claude Code formatted them into rule tables. Anything Claude had to
fill in because my answers didn't cover it is marked **[Claude, pending]**, and its reason is Claude's, not mine. The
"training" false-friend example also appears in the assignment brief and in Claude's question to me.

Persona: Rohan Desai (fictional, `persona/rohan-desai.resume.example.json`). He is a Java / Spring Boot backend
MS student looking for co-op, internship, or early-career roles.

## 1. Role words (title), F-ROLE

A posting is a candidate only if its **title** contains one of these phrases (case-insensitive, whole words).

| id | phrase | reason |
|---|---|---|
| R1 | Backend Engineer | matches Rohan's backend experience |
| R2 | Java Developer | matches his Java experience |
| R3 | Software Engineer | matches his Java, Spring Boot and backend experience |
| R4 | Full Stack Engineer | he is also open to full-stack roles |
| R5 | Software Developer | same work as Software Engineer, different title |
| R6 | Platform Engineer | backend-side infrastructure work |

Variants **[Claude, pending]**: "Back End" / "Back-end" / "Backend", and "Full-Stack" / "Fullstack" / "Full Stack",
count as the same phrase. Reason: the same job is spelled several ways across boards.

## 2. Topic words (body), F-TOPIC

These are counted in the posting **body** (description text). Each distinct word that appears adds 1 to the topic
score.

| id | word | reason |
|---|---|---|
| T1 | Java | his main language |
| T2 | Spring Boot | his main framework |
| T3 | REST APIs | backend work he has done |
| T4 | microservices | backend architecture in his background |
| T5 | SQL | database work in his background |
| T6 | AWS | cloud platform in his background |
| T7 | PostgreSQL | his database |
| T8 | distributed systems | backend systems topic |

Matching **[Claude, pending]**: whole words only, so `Java` must **not** match `JavaScript` and `SQL` must not match
`NoSQL`. `REST` is matched as `REST`, `RESTful` or `REST API(s)` and is case-sensitive, so "the rest of the team"
does not count. Reason: each of these would otherwise match for the wrong reason.

**Expected false friend (my answer):** "training". It can mean machine-learning model training, not employee
training. (It is not a topic word in v1, so the audit must look for false friends among the words actually listed.)

## 3. Exclusion and preference rules, F-LEVEL / F-US

| id | rule | reason |
|---|---|---|
| L1 | Reject if the title contains Senior, Staff, Principal or Lead (also `Sr.` **[Claude, pending]**) | Rohan is looking for co-op, internship and early-career roles, so these are likely above his level |
| U1 | **Prefer** US-based postings. This raises rank only and never rejects | my answer says "prefer", not "require" |

US-based **[Claude, pending]**: the location text names a US state, a US city on the board, "United States", "US"
or "Remote - US". Otherwise not US. If there is no location, it is "unknown", not "not US".

## 4. Keep threshold **[Claude, pending]**

Keep = R-match **and not** L1 **and** topic score ≥ **2**.
Rank among kept = topic score + 1 if U1.
Close call = R-match, not L1, topic score of 1 or 2 (one word either side of the line).
Reason (Claude's): one topic word alone ("SQL", "AWS") appears in almost any tech posting. Two is the smallest
number that asks for more than one signal. This number is **hand-set**, not fitted.

## 5. Evidence rules (shortlist claims)

For each kept posting, the shortlist gives a justification made of claims ("requires Java", "early-career level",
"US-based", ...). Each claim gets exactly one label against **the posting's own text**:

| label | when (my rule) |
|---|---|
| supported | the posting explicitly mentions the skill in its **required** skills, qualifications or responsibilities |
| contradicted | the claim says *required* but the posting lists the skill only as optional / preferred / nice-to-have, **or** the text states the opposite (e.g. "5+ years" against "early-career", a non-US location against "US-based") **[the second half is Claude, pending]** |
| insufficient | the posting does not say either way |

- **Required vs preferred (my rule):** the agent must tell a required skill from a preferred one. A skill under a
  "preferred / nice to have / bonus / a plus" heading or sentence is preferred. It is not required.
- **Abstention (my rule):** if the posting names **no programming language at all**, the agent says
  **"I cannot tell"** for any language claim. It does not assume from the job title.
- The agent never upgrades a preferred mention to "requires".

## 6. Expected sources

| board | API (public, GET only) | fields the agent should see | if missing |
|---|---|---|---|
| Stripe | `boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | `title`, `location.name`, `content` (HTML body), `absolute_url` | no body → topic score 0, every body claim "insufficient", posting reported as "body missing" (not silently rejected as irrelevant) |
| Figma | `boards-api.greenhouse.io/v1/boards/figma/jobs?content=true` | same | same |
| Notion | `api.ashbyhq.com/posting-api/job-board/notion` | `title`, `location`, `descriptionPlain`, `jobUrl` | same |

These are the JS2 boards. If a board fails, the run says which board and why and does not report "0 relevant" for
it. Allow-list: only these two hosts. The agent never logs in, applies or messages.

## 7. Wrong versions the tests must catch

| id | wrong filter (my answer) | why it is wrong (my answer) | the test that catches it |
|---|---|---|---|
| W1 | Keep every job with "Engineer" in the title | it includes hardware, electrical and mechanical engineering roles that aren't relevant to Rohan | a "Hardware Engineer" / "Electrical Engineer" posting with topic words must be **rejected** |
| W2 | Keep every job that mentions "Java" | Java might appear in an unrelated section or as an optional skill, so it doesn't mean the role involves Java development | a non-role title that mentions Java must be rejected, **and** a Java-only-in-preferred posting must give "requires Java" = **contradicted** |
| W3 **[Claude, pending]** | Substring matching (`"java" in text`) | `JavaScript` counts as Java | a body with only "JavaScript" must have topic score 0 for T1 |

## Revisions

### v1 pending items: decided 2026-11-25 (my words, [audit/my-decisions-2026-11-25.txt](audit/my-decisions-2026-11-25.txt))

| item | decision |
|---|---|
| 2-word threshold | Accept, when both words appear in relevant job-description context (that condition became rule D below) |
| "Sr." = Senior | Accept |
| 3+ years required contradicts early-career | Accept, with preferred experience treated differently from required experience |

### v1.1: 2026-11-25, after the v1 audit ([AUDIT.md](AUDIT.md))

Measured on my 54 audit verdicts first (the dev set), then on my 20 held-out labels ([SCORE-CHANGES.md](SCORE-CHANGES.md)).

| change | status | my reason |
|---|---|---|
| **A** require US (unknown location → reject) | **rejected** | "The US should be a preference, not a hard requirement. Unknown location should stay unknown rather than automatically disqualifying a role." |
| **B** reject if 3+ years explicitly required (`max_required_years: 2`) | **added** | "Reject roles where 3+ years of experience are explicitly required. If that experience is only preferred, don't automatically reject." |
| **C** threshold 2 → 1 | **rejected** | "Lowering the threshold to one topic word would let too many loosely related jobs through." |
| **D** count topic words only in requirements / responsibilities sections (`topic_in_required_only: true`) | **added** | "Count topic words in the actual requirements section, not a general company or team description. That should reduce false matches." |

The machine copy is `filter/v1.1.json`. v1 stays in `filter/v1.json`, unchanged.

## Appendix A — my answers, verbatim

> 1. Job titles: Backend Engineer, Java Developer, Software Engineer, Full Stack Engineer, Software Developer, Platform Engineer. These match Rohan's Java, Spring Boot and backend experience. He is also open to full-stack roles.
> 2. Job description words: Java, Spring Boot, REST APIs, microservices, SQL, AWS, PostgreSQL, distributed systems. These match his technical background. A false friend would be "training" because it could refer to machine-learning model training rather than employee training.
> 3. One extra rule: Skip Senior, Staff, Principal and Lead positions. Rohan is looking for co-op, internship and early-career opportunities, so these roles are likely above his current level. Prefer US-based opportunities.
> 4. Java evidence: The posting must explicitly mention Java in its required skills, qualifications or responsibilities before the agent can say the job uses Java. If Java is mentioned only as an optional skill, label it accordingly. If no programming language is mentioned, say "I cannot tell" rather than assuming based on the job title. The agent should also distinguish between a required skill and a preferred skill.
> 5. Two wrong filters:
>    * Keep every job with "Engineer" in the title. This would include hardware, electrical and mechanical engineering roles that aren't relevant to Rohan.
>    * Keep every job that mentions "Java". Java might appear in an unrelated section or as an optional skill, and that doesn't necessarily mean the actual role involves Java development.
