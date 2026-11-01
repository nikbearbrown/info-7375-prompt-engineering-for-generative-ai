# Labeling rule — written before I labeled anything

Date: 2026-10-31

RELEVANT: Same as CONTRACT §5. The posting must match Rohan's target role, experience level, location, and at least two skills from the approved skills list.

Early Career: Yes. Count it as new-grad/early-career if the role is intended for recent graduates or candidates with limited professional experience.

High School Internship: NOT RELEVANT. Rohan is a master's student, so high-school-specific internships don't qualify.

Machine Learning Engineer Intern: NOT RELEVANT by default. Count it only if the responsibilities clearly involve general software engineering and meet the contract's skill requirements.

US / Canada: RELEVANT for location only if the posting explicitly allows candidates to work in the United States. Don't assume Canada-only eligibility includes the US.

Nice-to-have skills: Yes, count them if they are explicitly listed as desired or preferred skills. They still need to match the approved skills list.

---

How to label: open each file in `postings/`, decide RELEVANT or NOT RELEVANT, and write it in the `my_label`
column of `labels.csv` (plus a few words in `my_note`). Label the 10 `dev` rows first. Do not open the
`heldout` files until the prompt revision is frozen.
