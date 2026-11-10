# How to label (blind)

Follow `LABELING-RULE.md`: apply R1–R4 from `CONTRACT.md` yourself, before you see any rule or Claude
verdict. Nothing in this folder contains a verdict.

1. Open `<posting_id>.txt`. It has the title, the location and the posting text with HTML removed.
2. Read the title (R1, R2) and the location (R3) yourself.
3. For R4, Ctrl+F each of Priya's **10 shipped skills** as a whole word, ignoring case:

   | List | Skills |
   |---|---|
   | `skills.languages` | Python, SQL |
   | `skills.data_bi` | Databricks, Unity Catalog, Power BI |
   | `skills.backend_automation` | LangGraph, MLflow, Mem0 |
   | `skills.database_cloud` | Delta Lake, AWS |

   Ray and Kubeflow (`familiar_with_not_shipped`) and the `agent_note` text **do not count**.
4. Fill in `labels.csv`:
   - `my_label`: `relevant` or `not_relevant`
   - `my_failed_check`: the first check that failed (`R1`–`R4`), blank if relevant
   - `my_notes`: anything uncertain, such as a skill found only inside another word

Label development and held-out postings the same way. Until labeling is done, don't run the agent or
Claude on these postings.

Note: in these files, line breaks are kept at paragraph and list boundaries so they are readable. The
agent's R4 check runs on the same text with all whitespace collapsed to single spaces, so a skill name
split across a line break would match for the agent but might not for Ctrl+F.
