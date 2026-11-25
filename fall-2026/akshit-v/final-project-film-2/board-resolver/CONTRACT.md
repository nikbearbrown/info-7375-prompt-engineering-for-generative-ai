# CONTRACT — SponsorScout board resolver v0.1

Drafted by Claude Code on 2026-11-23, **before** `resolver.py` was written. The tests in
`test_resolver.py` were written from this contract, also before the code.
**Status: DRAFT. Akshit Verma has not reviewed or signed it yet.** Until he does, it is
Claude's contract, not his. (The final project's "gate" device asks for the contract and
tests *you* wrote before Claude implemented, so this needs his review and edits.)

## Purpose

The pitch (2026-10-14) said: *"First piece: a board resolver for the 107 companies that
currently have no mapped job board. You'll know it ran because board coverage is reported
as a number (today 16/123), with each new mapping saved with its raw API response and a test."*

The resolver finds **candidate** public job boards for those 107 companies. It never
decides that a board belongs to a company. A person does, at gate G1.

## Inputs (copied, read-only; see `inputs/PROVENANCE.md`)

| File | What | Label |
|---|---|---|
| `inputs/run-2-candidates.json` | the 123 sponsors from Assignment 1 run-2; 107 have `g1 = no-board-in-map` | record (80 Days CSV) |
| `inputs/boards.json` | the 16 boards confirmed at G1 on 2026-10-03 | your-input |
| `--aliases FILE` (optional) | extra slugs a person supplies, e.g. `SOCIAL FINANCE INC → sofi` | your-input |

## The loop

For each unmapped company: **observe** (the company and what's been tried) → **decide** (the
next slug × ATS to try, or stop for this company) → **act** (one GET through the tool) →
**record** (the raw response, its SHA-256, a log line) → **stop** when a stop condition holds.

- **Slugs** come from the name only: the full name (`outsetmedical`), hyphenated
  (`outset-medical`), with descriptor words removed (`zoominfo`), and the first word
  (`upstart`, marked *weak*). Alias slugs go first. At most 4 name slugs per company.
- **ATS order** per slug: Greenhouse, Lever, Ashby.
- A company's search ends early on a `name-match` (Greenhouse) or `exists-no-name`
  (Lever/Ashby with postings). On anything else it keeps going.

## Tools and permission policy (enforced in code, `check_policy`)

- **Only `GET`**, only `https`, and only these hosts: `boards-api.greenhouse.io`, `api.lever.co`,
  `api.ashbyhq.com`. Anything else raises `PolicyError` before a request is made.
- Slugs must match `^[a-z0-9][a-z0-9-]{0,62}$` (no path or query injection).
- **No network unless `--live` is given.** The default is to refuse (exit 3). Tests block `urlopen`.
- Files are written only inside `runs/`. Any other `--out-dir` is refused (exit 3).
- It never applies, emails, posts, or contacts anyone. It has no code path that sends anything.

## Outcomes per probe

| Outcome | Meaning | Counts as |
|---|---|---|
| `name-match` | Greenhouse board name equals the company name, legal suffixes removed | strong hit |
| `name-partial` | shares a non-descriptor word (e.g. "Upstart" vs "UPSTART NETWORK INC") | weak hit |
| `name-mismatch` | Greenhouse board exists but shares no word with the company name | hit, likely a collision |
| `exists-no-name` | Lever/Ashby board with ≥1 posting. These APIs give no company name | weak hit, human must check |
| `exists-empty` | Lever/Ashby returned 200 with 0 postings | weakest hit |
| `not-found` | HTTP 404 | miss |
| `error` | 429, 5xx, other status, network error, malformed JSON | **not** a miss |

## Stop conditions (none is "the model said it was done")

1. **done**: every planned probe ran.
2. **budget**: `--budget` requests used (default 1000). Remaining companies are `incomplete`.
3. **upstream-errors**: `--max-errors` consecutive `error` outcomes (default 5).
4. **canary-failed**: before the loop, one made-up slug is probed per ATS. If any returns
   something other than `not-found`, that ATS's "exists" answers can't be trusted, and the run stops.

## Company status

`proposed` (best hit is anything but `name-mismatch`) · `mismatch-only` · `not-found` (every
planned probe was a 404) · `incomplete` (errors, or the run stopped first).

## Human gate G1 (`decide`)

A person runs `decide` with `--decision approve|refuse|defer`, `--by`, and `--seen-sha256`, the
hash printed in `review.md` for the raw response they looked at. The gate refuses (exit 7) if:
- that probe isn't on record, or isn't a hit;
- the saved raw file's hash no longer matches what was recorded, meaning the file changed;
- `--seen-sha256` (at least 12 characters) doesn't match the recorded hash.

Every decision is appended to `decisions.json`. For each company the **last** decision counts.

## Coverage (`coverage`)

`covered = (boards confirmed in inputs/boards.json) ∪ (companies whose last decision is approve)`.
**Proposals never count.** Denominator = all candidates (123). Writes `coverage.json`,
`coverage.md`, and `boards.resolved.json` (same schema as `boards.json`; existing entries copied
unchanged, plus each approval with `confirmed_by`, `seen_sha256` and its raw file).

## Exit codes

`0` done · `2` usage/input error · `3` refused by policy (network without `--live`, out-dir outside `runs/`) ·
`4` stopped on budget · `5` stopped on upstream errors · `6` canary failed · `7` gate refused.

## Not in scope

Liveness and verdicts (that's `network_targets.py`); scraping career pages; guessing aliases
(SoFi, Lime) by model judgment; any write to the Assignment 1 repository.
