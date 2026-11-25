# Correction to the regression test after running revision 2

*Claude Code, 2026-11-09. Recorded because the brief says not to weaken a test to get a green report; this note shows what changed and the ad text behind it.*

- **What the test asserted** (`ae13048`): none of the 16 Linear postings fails condition 5 on rule v2. The reasoning was that their only "years" match on rev 1 was the perk.
- **What rev 2 showed:** the perk is gone from every one of them. But two still fail condition 5, each on a real requirement in the ad:
  - **Solutions Engineer, APAC:** under "What we're looking for": "8+ years in a Solutions Engineering, Pre-Sales, or similar role".
  - **Account Executive, Enterprise:** under "What we're looking for": "3+ years selling to the enterprise, and 7+ years in a quota-carrying sales role".
- **Why both were missed before:** rule v1 missed them because the word "experience" does not follow the number. Rev 1 reported the perk's "4 years" instead, because it took the largest number and the perk was read first.
- **The change:** the test still requires, on all 16, that the perk is never the quoted requirement. It now requires these two to fail condition 5 **with their own requirement quoted** and the ad to contain those words; the other 14 must still pass condition 5. Nothing became looser: the two now carry more assertions than before.
- **Who checked it:** Claude Code read the two ads in the saved raw response. On 2026-11-10 Shreyash re-read both and confirmed 8+ and 7+ years as mandatory requirements (`review/19`).
