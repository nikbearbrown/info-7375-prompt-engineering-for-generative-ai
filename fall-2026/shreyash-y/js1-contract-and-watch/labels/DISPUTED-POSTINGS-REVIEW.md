# Review of the five postings where the judges disagreed

*Shreyash's words, pasted into the session on 2026-10-31, after the experiment and after the TA-style review. Claude Code added only this note and the headings.*

## Which reading was correct

| Posting ID | Condition | Correct reading | Evidence |
|---|---|---|---|
| 8083703 | C5 — Experience | Claude | Senior Data Scientist requires 4+ years in industry or another quantitative field. The original rule missed this because the sentence didn't contain the word "experience." |
| 6555819 | C3 — Location | Claude | The office tag says Remote, but the description requires commuting to an office in New York, Tempe, or Los Angeles. |
| 8319419 | C5 — Experience | Claude | Technical Program Manager requires 5+ years of technical program, project management, or related operations work. The original parser missed the long phrase. |
| 8250366 | C3 — Location | Claude | The office tag says Remote (New York), but the description explicitly requires three days per week in the NYC office. |
| 8172223 | C3 — Location | Claude | The Utilization Review Nurse position permits remote work only from 17 named states. Massachusetts is not included. |

## Posting review — 2026-10-31

After checking the five disputed postings against the saved job descriptions, I found that Claude's interpretation was supported in each case. The deterministic rule missed two experience requirements and three location restrictions.

I decided to keep the largest required experience minimum, but only for mandatory qualifications. I also decided that a remote job should count as eligible only when the applicant can legally and practically work from Massachusetts.

I am keeping the original experiment results unchanged because these corrections were made after the experiment. I will use the corrected rule for future runs and keep the original outputs as evidence of what failed.

---

*Check by Claude Code, 2026-10-31: the 8172223 ad, in `runs/raw/oscar-20261030T230217Z.json`, lists exactly 17 states and does not list Massachusetts.*
