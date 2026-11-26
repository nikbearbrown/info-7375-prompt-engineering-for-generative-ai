# FILTER — JS3 The Filter, the Tool, and the Score

Persona: Priya Nair (fictional, from the course Reallocation Engine).
Decided by Rithika Sankar Rajeswari, 2026-11-25. Wording drafted with Claude from my decisions.
Written and committed before any JS3 code.

## Version

- **v1.0** (this file, 2026-11-25): first version, not yet measured.
- Every later change is recorded in the Change log at the bottom: rule added, cut, or rejected, with the measurement that justified it.

## Corpus (frozen)

The three real board responses from the JS2 live run of 2026-11-10 (`out/raw/20261110T183029Z_*`).
SHA-256 hashes are in `CORPUS.sha256`. All SEEDED files are excluded.

## 1. The filter (v1.0)

A posting gets a score. It is **kept** if it is not excluded and its score is **≥ 4**.

| Rule | What it checks | Weight | Reason |
|---|---|---|---|
| R1 role words | Title contains `ai engineer`, `ml engineer`, `machine learning`, `data engineer`, `ml infrastructure`, or `ml platform` (case-insensitive, whole words) | +3 (counted once) | Inherited from Priya's target roles (`data/target.example.json`). The title is the strongest signal of what the job is. |
| R2 topic words | Body contains `llm`, `pytorch`, `tensorflow`, `inference`, `training`, `embedding`, `retrieval`, `mlops`, `model`, `spark` (case-insensitive, whole words) | +1 per distinct word, at most 3 | Hand-set. Shows the work is actually ML or data, beyond what the title says. |
| R3 exclusion | `clearance` anywhere in title or body (case-insensitive) | reject | Inherited. Priya cannot hold a security clearance. |
| R4 exclusion | Title contains `manager`, `director`, `head of`, or `vp` (whole words) | reject | Hand-set. Priya targets individual-contributor engineering roles. |
| Threshold | Keep if score ≥ 4 | — | Hand-set. Requires a title match plus at least one topic word. **Close calls** are postings scoring 3 or 4. |

Senior and Staff titles are **not** excluded in v1. JS1 set no seniority level for Priya, so cutting them would be a guess. The audit decides.

Known risk, written before measuring: `training` and `model` may match for the wrong reason (sales training, business model). This is to be tested, not assumed.

## 2. Evidence rules

Each claim in a shortlist justification is checked against that posting's own text (title, location, body).

- **Supported:** a quoted span of the posting states the claim. The verdict must include the span.
- **Contradicted:** a span states the opposite (for example, the claim "remote" against "on-site in San Francisco").
- **Insufficient:** no span supports or contradicts the claim.
- **"I cannot tell" (abstain):** the agent gives no verdict when the claim concerns something the posting never addresses (visa sponsorship, salary when not listed, team size), or when the posting body is empty or missing.
- **Relevance is not entailment:** matching the filter's words only puts a posting on the shortlist. Only a quoted span counts as evidence for a claim.

## 3. Expected sources

| Board | ATS | Postings in corpus | Fields used |
|---|---|---|---|
| Databricks | Greenhouse | 915 | id, title, location, content (as normalized by `agent/adapters.py`) |
| Scale AI | Greenhouse | 169 | same |
| OpenAI | Ashby | 830 | same |

- **Missing or failed board** (for example the 404 board `rithika-js2-no-such-board`): reported as "not evaluated", never as "0 relevant postings".
- **Posting with an empty body:** R2 cannot be scored, so the posting goes to an "abstain: no body" list instead of being rejected.

## 4. Wrong versions the tests must catch

| ID | Plausible but wrong | Why it's wrong |
|---|---|---|
| W1 | Substring matching instead of whole words | "HTML Engineer" would match `ml engineer`. |
| W2 | Role words searched in the body instead of the title | Sales and recruiting postings that mention "machine learning" would be kept. |
| W3 | Case-sensitive exclusion | "Security Clearance required" would pass `clearance`. |
| W4 | Topic words counted without the cap of 3 | A posting repeating "model" ten times would outrank a real ML role. |
| W5 | Empty body treated as a reject | The posting disappears silently instead of being marked "cannot tell". |

## Change log

(Empty at v1.0. Every rule added, cut, or rejected after measuring goes here, with its version number, the measurement behind it, and the date.)

### v1.1 — 2026-11-25 (after the reject audit, see AUDIT.md)
- **Added** `research engineer` to R1. Two postings I labeled relevant ("Research Engineer / Research Scientist, Post Training") were rejected only by title wording.
- **Added** title exclusions `applied ai engineer`, `fde`, `forward deployed`, `solutions architect`, `developer advocate`, `fellow` to R4 (renamed "management and customer-facing titles"). False friend: `ai engineer` and `machine learning` matched customer-facing roles (Applied AI Engineer ×4, AI FDE, Solutions Architect – AI&ML Engineer, Machine Learning Fellow), 7 of 9 kept-stratum errors.
- **Rejected** adding `software engineer` to R1: three relevant misses had it, but it would admit hundreds of non-ML software roles.
- Known cost: "Applied AI Engineer, Codex Core Agent" (audit row 38, labeled relevant) is now rejected.
- Audit errors on the same 50 rows: 14 (v1.0) → 5 (v1.1). Tuned on these labels, so not evidence for unseen postings; held-out check in SCORE.md.
