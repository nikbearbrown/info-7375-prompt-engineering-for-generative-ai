# REVIEW_PACKET.md

## 1. Defect Description & Reproduction

* **The Defect:** In JS1, the skill extraction engine used whole-word, case-insensitive matching. Even with word boundaries, ordinary English words triggered false matches. Specifically, the technology "React" matched the English verb "react" in a Wealthfront Director of Product Management posting (*"move quickly to react to new insights"*), and the programming language "Go" matched the hyphenated compound adjective "go-to" in a Wealthfront Product Designer posting (*"Become the go-to designer"*), as well as lowercase "go" in common phrases.
* **Reproduction Steps:**
  1. Ran reproduction script against saved Wealthfront postings from the JS2 live run:
     `python3 -m agent.reproduce_skills evidence/run-20261109-041358Z/raw/03-wealthfront-a1.json`
  2. Observed output: 5 matches found, 2 of which were false positives (the Product Management and Product Designer roles).
* **Reproduction Evidence:** Saved in `evidence/skills-defect-repro-20261109.txt`, committed in `f982c6a` ("port JS1 skill matcher unchanged + reproduce React/Go defect on real postings").

---

## 2. Test-First Verification (RED)

* **Test Suite Commit:** `e5a4ebc` ("JS2: React/Go skill tests written before the patch (RED, 7 failures)").
* **Test Strategy:** Added explicit positive and negative boundary test cases in `tests/test_skills.py` before modifying any code:
  * **Negative test cases (must not match):** `"move quickly to react to new insights"`, `"Become the go-to designer"`, and `"ready to hit the ground running and go"`, plus the 2 real negative Wealthfront postings.
  * **Positive test cases (must match):** `"React"`, `"React.js"`, `"ReactJS"`, `"React Native"`, `"Go"`, `"Golang"`, and the 3 real positive Wealthfront postings (Network, DevOps, Frontend).
* **Execution & Evidence:** Ran `python3 -m unittest tests.test_skills -v`. Failed with 7 failures across 6 tests as expected (`FAILED (failures=7)`), confirming the tests catch the defect in the unpatched matcher.

---

## 3. The Prompt (Task Delegation)

* **Target File:** `agent/skills.py` exclusively.
* **Exact Prompt Sent:**
  > "Please fix the false positive skill extraction bug in `agent/skills.py`. Currently, naive case-insensitive word matching incorrectly matches the JavaScript framework 'React' against ordinary English verbs (like 'react to new insights') and matches the programming language 'Go' against hyphenated adjectives (like 'go-to designer') and lowercase verbs.
  >
  > I need the extractor updated so that:
  > 1. 'React' only matches when specifically referring to the technology (including explicit variants like 'ReactJS' and 'React Native') and does not trigger on ordinary lowercase or sentence verbs like 'react'.
  > 2. 'Go' requires case-sensitive matching or explicit canonical forms (like 'Golang'), and never matches lowercase 'go' or hyphenated compounds like 'go-to'.
  > 3. Valid skill mentions that currently pass—such as explicit mentions of 'React', 'React Native', 'Go', and 'Golang'—must continue to match cleanly.
  >
  > You may only modify `agent/skills.py`. Do not modify `tests/test_skills.py` or any existing test cases. All tests in commit `e5a4ebc` must pass without altering the test suite."
* **Prompt Error:** My prompt stated that Golang "currently passes", but it was actually one of the 7 failing tests in `e5a4ebc` because the old matcher had no Golang handling. Claude flagged this in `review/03-claude-response-20261109.md`.

---

## 4. The Diff & Evaluation

* **Diff Inspection:** Ran `cat review/02-patch-20261109.diff` to review the exact changes.
* **What the Diff Actually Does:**
  * Introduces a dedicated helper `_found(skill, text)` in `agent/skills.py`. If the skill is not "React" or "Go", it routes directly to the original regex search unchanged.
  * For "React": checks for capital `React` with lookarounds ensuring no ASCII letter or digit immediately precedes or follows it (`(?<![A-Za-z0-9])React(?![A-Za-z0-9])`). It matches "React Native" naturally because "React" is followed by a space. It matches "ReactJS" and "React.js" through a separate case-insensitive regex: `(?<![A-Za-z0-9])react(?:\.js|js)(?![A-Za-z0-9])`.
  * For "Go": checks for capital `Go` with no preceding letter/digit, and ensures no letter, digit, or hyphen follows it (`(?<![A-Za-z0-9])Go(?![A-Za-z0-9\-])`). Disallowing a trailing hyphen eliminates "Go-to". It also checks `golang` in any case via `(?<![A-Za-z0-9])golang(?![A-Za-z0-9])`.
* **Scope Integrity:** Confirmed via inspecting `review/02-patch-20261109.diff` that changes were strictly isolated to `agent/skills.py`. Tests and configurations were untouched.

---

## 5. Commands Run & Results

1. **RED Test Run:**
   * Command: `python3 -m unittest tests.test_skills -v`
   * Result: `Ran 6 tests in 0.004s - FAILED (failures=7)`
2. **Diff Inspection:**
   * Command: `cat review/02-patch-20261109.diff`
   * Result: Confirmed changes were isolated strictly to `agent/skills.py` and implemented the targeted pattern checks.
3. **GREEN Test Run:**
   * Command: `python3 -m unittest discover -s tests -t . -v`
   * Result: `Ran 35 tests in 0.020s - OK`
4. **Summary Grep Check:**
   * Command: `grep -E "^(Ran|OK|FAILED)" evidence/skills-tests-GREEN-20261109.txt`
   * Result: `Ran 35 tests in 0.020s` and `OK`
5. **Real Data After-Patch Check:**
   * Command: `python3 -m agent.reproduce_skills evidence/run-20261109-041358Z/raw/03-wealthfront-a1.json > evidence/skills-after-patch-20261109.txt 2>&1 && cat evidence/skills-after-patch-20261109.txt`
   * Result: 3 matches total (Network, DevOps, Frontend); the 2 false matches in Product Management and Product Design were eliminated.

---

## 6. What Claude Flagged vs. What I Found

* **What Claude Flagged:**
  * Claude flagged that my prompt was wrong about Golang "currently passing" (it failed in RED because the old matcher had no Golang handling).
  * Claude noted that the patch leaves "Go-based" unmatched because trailing hyphens are blocked.
  * Claude flagged that all-caps "REACT" in headings will be missed by the pattern.
  * Claude flagged that capitalizing "Go" at the start of a sentence (e.g., *"Go build something people love"*) will still match.
  * Claude pointed out that the module docstring in `agent/skills.py` still mentions the old naive matching behavior.
* **What I Decided Myself:**
  * I decided that missing "Go-based" and all-caps "REACT" are acceptable trade-offs to keep the regex simple and avoid broad false-positive regressions.
  * I decided that matching "Go" at the start of a sentence is a known limitation that is rare enough in job requirements to accept for now.
  * I decided to accept the patch without forcing another round of edits just to update the stale docstring.

---

## 7. Verdict & Rationale

* **Verdict:** Accept.
* **Rationale:**
  * **Scope:** Only `agent/skills.py` was modified.
  * **Test Verification:** All 35 tests pass cleanly across the entire suite (`unittest discover -s tests -t . -v`), resolving the 7 failures from `e5a4ebc`.
  * **Real Postings:** Verified on the saved Wealthfront data in `evidence/skills-after-patch-20261109.txt`; only the 3 genuine engineering postings matched.
  * **Known Limitations (to be listed in the sign-off):**
    * Misses "Go-based" because of the trailing hyphen exclusion.
    * Misses "REACT" in all-caps headings because it requires "React" or "react.js/reactjs".
    * Falsely matches "Go" when used as a capitalized sentence-starting verb (e.g., *"Go build something people love"*).
    * The docstring in `agent/skills.py` still references the old behavior.
  * These trade-offs are acceptable because they resolve the primary defect on real postings without overcomplicating the pattern logic.
  * **Cases My Tests Would Still Miss:** No test covers "Go build something people love" (a sentence-starting verb that currently triggers a false positive) or "Go-based services" (a hyphenated variant that is missed). A change breaking or altering behavior on either phrase would pass our test suite unnoticed.
