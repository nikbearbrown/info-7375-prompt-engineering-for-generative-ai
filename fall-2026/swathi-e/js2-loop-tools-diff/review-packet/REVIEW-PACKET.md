# Review packet: the Plaid office-name defect

Swathi Baba Eswarappa, INFO 7375, JS2. Persona: Priya Nair (fictional).
Drafted by Claude Code on 2026-11-07 from my files and commits; the Decision
section is in my own words. Every claim names its commit or file.

## 1. The defect, reproduced first

- **What goes wrong:** Plaid's Ashby board names offices, not states: "San
  Francisco HQ", "Seattle Office". My JS1 rule's location check (check 3) looks
  for the United States, a US state, or Remote. It finds none of them, so it
  rates US jobs not relevant. The response does say "United States", but in the
  `address` field, which my parser ignored (parsers.py at `e6a70a4`).
- **Scale:** in my Nov 4 and Nov 5 live runs, 41 Plaid postings failed check 3
  because of office-only names, and for 2 of them it was the only failing check.
  Claude Code counted these; I recorded the numbers in GATE.md (`d131b5f`).
- **Reproduced by me, before any fix:** posting `1bcfe93d`, *Fraud Intelligence
  Analyst*, from the REAL Nov 5 Plaid response
  (`runs/2026-11-05T23-11-48-228373-0500/005-plaid-request.json`, commit
  `bd602a2`). Raw address "San Francisco California United States"; parsed
  location "San Francisco HQ"; verdict NOT RELEVANT, *check 3 fails*
  (file 01, run on `ae284ca`).

## 2. The test, written before the patch

- **The rule change came first:** GATE.md revision (`d131b5f`).
- **Then the tests:** `tests/test_ashby_address.py`, A1–A5 (`16da614`):
  - A1 and A3: SIMULATED postings gain their country.
  - A2: the two REAL Nov 5 postings become relevant.
  - A4 (control): a posting with no address is unchanged.
  - A5 (control): a Canadian office still fails check 3.
- **They failed on the unfixed code:** run on `16da614`, `FAILED (failures=5)`:
  A1, A2 for both postings, A3 and A5. A4 passed (file 02).

## 3. The diff, read as a change in behavior (`4a3db26`)

- **Before:** an Ashby location was its place names joined with "; ", for
  example "San Francisco HQ".
- **After:** each place name is followed by its own address's `addressCountry`
  in parentheses, but only when the response gives one, for example
  "San Francisco HQ (United States)". The same applies to secondary locations.
- **What stays the same:** places without an address; duplicate names (still
  listed once); Greenhouse parsing; and the state file, which stores ids, not
  locations.
- **Effect:** new Plaid postings at US offices can now pass check 3. Postings
  judged in earlier runs are not re-judged.

## 4. Did it stay in scope?

Yes.
- **Code changed:** `4a3db26` touches only `parsers.py` (22 lines added, 10
  removed): a new helper, `_address_country`, and the body of `parse_ashby`.
- **Unchanged:** `loop.py`, `rule.py` and the Greenhouse parser.
- **No test changed** after the tests were committed (`16da614` to `4a3db26`).
- **GATE.md** was revised before the fix (`d131b5f`), not after it.

## 5. Commands I ran myself, in my own Terminal

| File | What | Commit | Result |
|---|---|---|---|
| 01 | Reproduction, before the fix | `ae284ca` | NOT RELEVANT, check 3 fails |
| 02 | `python3 -B -m unittest -v tests.test_ashby_address` | `16da614` | FAILED (failures=5) |
| 03 | `python3 -B -m unittest discover -s tests -v` | `4a3db26` | Ran 81 tests, OK |
| 04 | The same reproduction, after the fix | `4a3db26` | RELEVANT, check 3 passes: names 'United States' |

I also read the diff myself: `git show 4a3db26 -- parsers.py`.

## 6. Decision

Decision: I accept the fix, because it correctly turns "San Francisco HQ" into a US location, and it only changed the Ashby parser.
Evidence: I reproduced the bug myself, saw 4 tests fail (5 failures) before the fix, read the diff, and then saw all 81 tests pass and the same posting become relevant after the fix.
What it doesn't solve: the job became relevant only because its title has "Analyst"; a Fraud Intelligence Analyst isn't really a data or AI role for Priya.
A case my test would still miss: a posting with no address at all (like "Seattle Office" alone), or a country the rule doesn't recognize, like "U.S." with periods.
