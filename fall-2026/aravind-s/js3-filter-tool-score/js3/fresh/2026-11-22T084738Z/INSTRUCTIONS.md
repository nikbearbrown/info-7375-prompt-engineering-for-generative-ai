# How to judge the fresh cards

1. Open CARDS.md and VERDICTS.md side by side. Judge each card from the card alone, by your own sense of whether the posting is worth Jane's time, not by FILTER.md's rules (this set tests v1.1's calls, so it cannot use them as its answer key).
2. Jane (fictional) is an F-1 student, not a U.S. person, who can start full time in May 2027 and will need H-1B sponsorship later; she has 3 years of full-time experience; she wants full-time backend or software engineering work in California, Austin, Boston, Cambridge, New York, Seattle, Bellevue, Redmond, or US remote ("US - Remote", "Remote - US", "United States - Remote").
3. Write Keep, Reject or ? and one short line on why. Use ? when the card does not settle it; a ? is counted on its own, never as a mistake.
4. Do not open `sealed/answers.json` until your verdicts for all 20 cards are committed. Then `python3 tools/score_fresh.py js3/fresh/<run id>` scores them once.
