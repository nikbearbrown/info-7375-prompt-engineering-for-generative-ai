# How to judge the cards

1. Open CARDS.md and VERDICTS.md side by side. Judge each card from the card alone, by your own sense of whether the posting is worth Jane's time, not by FILTER.md's rules (the audit checks those rules, so it cannot use them as the answer key).
2. Jane (fictional) is an F-1 student, not a U.S. person, who can start full time in May 2027 and will need H-1B sponsorship later; she has 3 years of full-time experience; she wants full-time backend or software engineering work in California, Austin, Boston or Cambridge, New York, Seattle, Bellevue or Redmond, or US remote.
3. Write Keep, Reject or ? and one short line on why. Use ? when the card does not settle it; a ? is counted on its own, never as a mistake.
4. Do not open `sealed/answers.json` until your verdicts are committed. After that, Claude Code computes the agreement: a miss is a posting the filter rejected that you marked Keep; a wrong keep is one it kept that you marked Reject. The random rejects give the miss count with its exact bound; the close calls and the kept sample show where the boundary is and what got through.
