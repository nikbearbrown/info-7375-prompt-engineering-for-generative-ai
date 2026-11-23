# How to judge the held-out cards

1. Open CARDS.md and VERDICTS.md side by side. Judge each card from the card alone, by your own sense of whether the posting is worth Jane's time, not by FILTER.md's rules (this set measures changes to those rules, so it cannot use them as its answer key).
2. Jane (fictional) is an F-1 student, not a U.S. person, who can start full time in May 2027 and will need H-1B sponsorship later; she has 3 years of full-time experience; she wants full-time backend or software engineering work in California, Austin, Boston, Cambridge, New York, Seattle, Bellevue, Redmond, or US remote ("US - Remote", "Remote - US", "United States - Remote").
3. Write Keep, Reject or ? and one short line on why. Use ? when the card does not settle it; a ? is counted on its own, never as a mistake.
4. Do not open `sealed/answers.json` until your verdicts are committed, and commit them before any change to the filter is measured on this set (chapter 9: a held-out set is touched once). After that, each one-change experiment runs the changed filter on these 30 postings and compares its keeps and rejects with your verdicts.
