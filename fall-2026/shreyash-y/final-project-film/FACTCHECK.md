# FACTCHECK — Quote It or Refuse. (final project pitch)

## Executive summary

This lists every factual claim in the narration and on screen, and how each was checked.
Only one claim is about something that already ran: Dovetail's 47 tests passing. Everything
about ClaimCheck describes a plan and is said in the future tense ("will"). Constructed
material is marked EXEMPT because it is labelled CONSTRUCTED / PLANNED on screen, not
because it went unchecked. No user, employer, metric, or result is invented.

Status: checked 2026-10-14 against the files named below; drafted by Claude in Claude Code
for Shreyash Yadav. The student confirmed B05 and B10's inputs on 2026-10-07.

## Claims

| # | Beat | Claim (as spoken / shown) | Verdict | Source / derivation | Fix |
|---|---|---|---|---|---|
| 1 | B00 | "nothing in this pitch is built yet" | PASS | No ClaimCheck code, data, or test set exists on 2026-10-14 (PROJECT-BRIEF.md "Exists today") | — |
| 2 | B00 | No Claude answer is shown | PASS | Composer output lines read "No answer shown"; no model call was made for the film | — |
| 3 | B01 | ClaimCheck answers only when code can verify the quoted clause | EXEMPT | Design intent, stated as what the tool is; B03 shows it as PLANNED DESIGN | — |
| 4 | B02 | Policy, endorsement E-2, "Section 4(b)" answer | EXEMPT | Synthetic text written for the film; stamped CONSTRUCTED EXAMPLE on screen | — |
| 5 | B02 | An endorsement can override the base policy form | PASS | General structure of insurance policies (endorsements modify the base form); no specific policy cited | — |
| 6 | B03 | Will be a public GitHub repository holding a Python CLI on Claude, with test set and eval report; Claude returns answer + quote + doc id; code checks both | EXEMPT | Proposal; spoken "I will build", caption + PLANNED DESIGN - not built on screen | — |
| 7 | B04 | Four-field answer contract enforced by a parser | EXEMPT | Proposal; spoken "still a proposal", title PROPOSED_answer_contract.json | — |
| 8 | B05 | Student tried a chat assistant with a PDF upload and a LlamaIndex/LangChain RAG template | PASS | Confirmed by the student 2026-10-07 (beat_sheet.json B05 `confirmed`) | — |
| 9 | B05 | Out of the box neither checks citations by code, ships a test set, or has a refusal rule | CORRECTED | Narrowed to what the student observed; footer reads "what I saw in my own tries - not a market survey" | softened from a general claim about the tools |
| 9b | B05 | "ClaimCheck will save a claims examiner from acting on a cited clause that nobody checked, which neither of those does" | PASS | Future tense ("will save"); "neither does" rests on row 9 — what the student saw out of the box | — |
| 10 | B06 | Target reader: hiring manager, applied-AI / LLM engineer role | PASS | Student's own stated goal (PROJECT-BRIEF.md Q3) | — |
| 11 | B06 | Eval report table | EXEMPT | Placeholder rows, no scores; stamped CONSTRUCTED MOCK-UP - no results exist | — |
| 12 | B07 | Skills map to files that will prove them; "not claimed: works on real claims" | EXEMPT | Proposal; files drawn dashed = will exist | — |
| 13 | B08 | Scope: 1 synthetic claim file, 30-50 questions, at least a third traps; first run 1 policy / 10 questions | EXEMPT | Plan; labelled PLAN - nothing here runs yet | — |
| 14 | B09 | Risk: author writes documents, questions, and tool; three mitigations | EXEMPT | Plan; labelled PLAN - mitigations not yet in place | — |
| 15 | B10 | In Dovetail a solver checks the model's plan | PASS | Dovetail repo: README.md and `dovetail/feasibility.py` | — |
| 16 | B10 | "all forty-seven of its offline tests passed when I re-ran them on October seventh" | PASS | `pytest -q` 2026-10-07 21:42 EDT → `47 passed in 0.62s`; `evidence/dovetail-pytest-2026-10-07.txt`, read by scenes.py, not typed | — |
| 17 | BVDT | Exists: brief (2026-10-07), beat sheet, film (2026-10-14); the rest will exist | CORRECTED | Matches PROJECT-BRIEF.md lists | first render said "EXISTS (2026-10-07): … this film"; the film dates from 2026-10-14 |
| 18 | BHTF | Viewer prompt | EXEMPT | A suggestion for the viewer, not a claim | — |
| 19 | BOUT | Name, course, "nothing built yet" | PASS | Same as row 1 | — |

## Removed or softened while writing

- Dovetail's benchmark figures (300 scenarios, 76% of naive plans rejected) were left out:
  they were not re-run for this pitch.
- The Cybersenz internship is not mentioned (student's choice).
- A classmate writing blind test questions is not promised (not arranged).
