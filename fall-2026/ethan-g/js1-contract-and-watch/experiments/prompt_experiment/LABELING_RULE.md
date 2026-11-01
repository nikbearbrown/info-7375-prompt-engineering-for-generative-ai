# Labeling rule for hand labels


Labels finalized by Ethan on: 31st October 2026

Persona: Evan Gordon (fictional). About **4 years** of data engineering in Airflow, dbt, Spark, Snowflake, Kafka, AWS,
Tableau/Power BI. MS Information Systems (Northeastern, 2024–2026), BS Computer Engineering. Lives in Boston, open to remote **within the US**, willing to relocate but prefers Boston. Target: data engineering **or data analyst** roles asking for **2–5 years**.

A posting is **relevant** only if all of these hold. Otherwise it is **not_relevant**.

1. **The job is data engineering or data analysis.** Either building and running data pipelines, models, or a data
   platform (data, analytics, or data-platform engineering), or a **data analyst** role doing SQL, reporting, metrics,
   and dashboards. Not data science or ML research, sales, support, or people management.
2. **The level fits ~4 years.** The posting's **required** experience is at most 5 years. Roles asking **0–4 years are preferred**, 5 is
   acceptable, and more than 5 is not relevant. Not Staff, Principal,
   Lead, or Manager scope. Not an internship. A "Senior" title is fine if the requirement fits.
   If it says 5+ years, decide whether ~4 years is close enough and say so in the note.
3. **The job is in the US.** Boston on-site or hybrid (preferred), remote that includes the US, or on-site or hybrid
   anywhere else in the US (Evan will relocate). Non-US locations, including non-US remote, are not relevant.
   Boston being preferred does **not** make a non-Boston US job irrelevant. Mention it in the note if it mattered.
4. **The core stack overlaps.** Evan has most of the required tools, or close equivalents (e.g. Redshift vs.
   Snowflake is close; "must have 3 years of Scala streaming at scale" may not be).

Tie-break: if one point is ambiguous and nothing else rules the posting out, label it **relevant** and say what was
ambiguous in `label_note`.

How to label: `python3 experiments/prompt_experiment/label.py`. It shows only the whole posting text and its URL,
never the rule or Claude verdicts. Requirements are usually near the end, so scroll.
