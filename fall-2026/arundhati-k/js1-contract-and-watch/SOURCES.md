# SOURCES — what I used, what I wrote, what AI contributed

## Used
- Assignment brief: `assignments/assignment-js1-the-contract-and-the-watch.md` (this repo).
- Stripe's public Greenhouse board: `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`
  (raw responses saved in `evidence/raw/`, fetched 2026-10-31).
- Persona: Rohan Desai, fictional, from The Reallocation Engine `search/examples/rohan-desai/resume.example.json`
  (copied unchanged to `persona/`).
- Claude Code CLI 2.1.283 (`claude -p`), model reported `claude-opus-5-5` (plus `claude-haiku-5-5` inside WebFetch, surface 3).

## What I wrote / decided

_Written by me, 2026-10-31._

I worked on defining the project requirements and deciding how the job-matching process should work. I changed the fictional candidate from Maya Sehgal to Rohan Desai because Maya's profile did not fit the intended new-grad software engineer persona. I also worked on selecting the relevant skills for Rohan's profile, setting the labeling rules, reviewing the job postings, and assigning the labels.

I made decisions about which requirements should be considered when classifying a posting, including the US-location requirement and the skills match. I also made the final revision to the prompt based on what I observed during testing.

## My own look at Stripe postings (date, what I saw)
_Written by me._

* Software Engineer, Early Career: I noticed that Stripe accepts experience with Java, Ruby, JavaScript, Scala and Go. It also focuses on problem-solving, teamwork and the ability to learn new systems.
* Software Engineer, Payments: This role focuses on backend services, payment integrations and working with external partners. Previous experience with payment technology is listed as preferred.

Date reviewed: October 31, 2026.

## ChatGPT contributed

_Written by me, 2026-10-31._

I used ChatGPT to help organize and improve the project instructions and contract. It helped me identify inconsistencies, correct mistakes in the labeling rules, and refine the wording.

I also used it to review the Stripe job-posting notes, discuss the labeling of individual rows, and understand the differences between the plain-chat and Code tab results. Later, it helped me organize the autonomy and sampling reflections.

I reviewed the suggestions and made decisions about which corrections to accept rather than automatically using every suggestion.

## Claude (Claude Code, this session) contributed
- All code in `jsagent/`, `run.py`, `seed.py`, `make_labeling_set.py`, `experiments.py`, and all tests, written
  against my committed contract (`122d4f1` → `bb8984b`).
- Ran the seeded baseline, both live runs, sampling, both prompts on dev and held-out, and surfaces 2 and 3.
- Pointed out: Maya is a PM persona with no Java/Spring; the "Go" verb false match; label-vs-rule inconsistencies (rows 13–16).
- Drafted the factual parts of README, SAMPLING-REPORT, PROMPT-EXPERIMENT, ACTION-SURFACES (tables, what ran, quotes).
  The conclusions in those files are mine.
- Constructed the test fixtures (`tests/fixtures.py`) — not real postings.
