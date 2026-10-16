# PROJECT-BRIEF — Fine Print (working title)

Suketh Reddy Produtoor · INFO 7375 Final Project pitch · target role **new-grad ML/AI engineer** · Python, Claude

*Drafted by Claude Code from my Assignment 3 (A3) record; §2's alternatives, §5's background rule and §7 are from my own
answers (FRICTIONAL.md, entry 1). Each past-tense claim is checked in FACTCHECK.md.*

## 1. What is it?

**An agent that reads new-grad ML job postings for an F-1 student, quotes the exact sentence behind every requirement
that could rule them out, compares it with the applicant's documented background, and stops for my approval before
anything reaches my shortlist.** When done: a public Python repository with the agent, tests, a hand-labelled
evaluation set of real public postings, an evaluation log, and a README with a one-command offline demo. It grows out
of my A3 recipe in the course's Reallocation Engine ([PR #12](https://github.com/nikbearbrown/the-reallocation-engine/pull/12)),
whose next-steps list names this check (A3 `PROPOSED-ADDITIONS.md`, proposal 5).

## 2. Why would anyone care?

It tells a new-grad ML engineer who needs sponsorship whether a role deserves their time before they tailor an
application. Titles and sponsorship history are useful signals, but the posting can change the decision: my A3 recipe
screened eight real postings by title and company record, and read in full, **six asked for 2 to 12+ years of
experience or excluded new graduates** (A3 `POSTING-REVIEW.md`).

**Alternatives I actually used:** *my A3 recipe* (its sample report, rules audit and posting review, read 2026-10-02):
matching the title and finding sponsorship history did not establish that the posting fit the applicant. *LinkedIn*,
where I search: on 2026-10-14 I checked two graduate ML descriptions there (Qualcomm, *Machine Learning Engineer, College
Graduate*; TikTok, *Machine Learning Engineer Graduate, Supply Chain & Logistics, 2027 Start*). Both separate minimum and
preferred qualifications; neither accessible description states sponsorship. Two examples support a narrow comparison,
not a claim about all of LinkedIn. **What Fine Print will add:** keep those distinctions, show each requirement beside
its exact source sentence (code checks it is really there), compare it with the applicant's documented background, and
mark missing sponsorship evidence *unknown* instead of guessing.

## 3. Who opens it, and what do they do?

A hiring manager or ML engineer reviewing a new-grad ML/AI engineer's portfolio. In the first minute they will run one
command that needs no API key (recorded model outputs) and read the report: each posting, each requirement beside its
sentence and quote-check result, the sponsorship line, and my decision; then the evaluation table of where it was wrong.

## 4. What does it prove about me?

Prompt contracts (each requirement returns a verbatim quote, required/preferred, its section, any either/or pathway);
source grounding (a deterministic quote check; values labelled `record`, `model-judgment` or `your-input`; a model's value
keeps its `model-judgment` source label and my approval is recorded in a separate review field, fixing my A3 defect D9,
where AI-proposed numbers were labelled as mine); agent loops (a budget, designed exits, permissions enforced
in code); evaluation (a held-out set labelled before tuning, at least five deliberate failure cases, and two error counts
kept apart: unsupported clearances and false exclusions). A reviewer could fairly conclude I can build a small agent
whose claims can be checked and measure where it fails, **not** that it is accurate in general or that I train models.

## 5. What is in, what is out, what comes first?

- **Out:** it will never apply, email, message or log in; no legal advice, no visa predictions.
- **In:** public postings from Greenhouse, Lever and Ashby, read only from an allowlist of hosts (as A3's live checks
  already are); the sponsorship record; quoted requirements; a comparison with the applicant's **documented** background
  that keeps education-and-experience pathways separate (PathAI's: a master's plus 2–4 years, or a PhD plus 0–2); the
  human gate. The repository uses a fictional profile; mine stays on my machine.
- **First:** one loop over one public posting: fetch, extract, check every quote, record, stop. **You will know it ran**
  when one command prints each requirement with its quote found or not found, and a test fails if one word of a quote
  changes.

## 6. What could sink it?

**A true quote read the wrong way.** The quote check catches an invented sentence, not a real one misread ("5+ years
preferred" recorded as required; an either/or rule read as one requirement), and a green "quote found" would make that
wrong answer look trustworthy. **What I will do:** keep required, preferred and either/or apart in the contract, send
ambiguity to the human gate, seed such postings into the held-out set, and report misreads separately from invented
quotes. (Smaller risk: boards can refuse automated reads; in A3 OpenAI's Ashby API returned 403. Such postings go to a
person.)

## 7. Why this project?

I want to know whether a role deserves my time before I tailor an application, and I am on F-1, so I must check both
role eligibility and sponsorship evidence. It is **a mix of showing and learning.**
**Already have:** production ML and Python (about two and a half years at Amazon); data contracts and human sign-off on
low-confidence matches (six months at Vertex); controls around model behaviour in **AgentOS**, my public project
([github.com/sukethrp/agentos](https://github.com/sukethrp/agentos): budget controls, permissions, a kill switch, audit
logging; CI passed 439 tests on 2026-09-19); and in A3 I re-ran the tests, sample, broken-authorization case and CSV check
myself (Claude Code wrote that code). Work history is described, not shown: employer data stays private.
**New to me:** interpreting requirements without changing their meaning, a labelled posting dataset, evaluating
extraction and interpretation separately, and showing those distinctions clearly in a short film.

---

## Exists today

- A3 recipe and prototype (role-level sponsor match), `sukethrp/the-reallocation-engine` at `95d4982`; PR #12 open since
  2026-10-02, no GitHub review yet (checked 2026-10-13).
- Its 36 offline tests, passing on a fresh clone, 2026-10-13 (run by Claude Code; `evidence/`).
- The eight-posting finding, made for a fictional applicant (Arjun Rao) with no work history: Codex, an AI reviewer, read
  the postings 2026-09-29; Claude Code re-checked; I held all eight on 2026-10-02.
- My LinkedIn check of two graduate ML postings, 2026-10-14 (`evidence/linkedin-check-2026-10-14.md`).

## Will exist

- Fine Print: the loop, tools and permission policy, saved state, stop condition and human gate. **None of it exists yet.**
- The quote check, the background comparison and their tests.
- The labelled evaluation set (development and held-out), failure cases and evaluation log.
- A README a stranger can follow, with the offline demo and a fictional profile.
