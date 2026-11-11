# Labeling rule for the 20 hand labels

Written 2026-11-01, before any posting was labelled and before any Claude verdict existed.
(Drafted with Claude; the labels themselves are Saloni's, entered with `scripts/label.py`.)

Read the posting as Priya Nair would: MS Information Systems (Dec 2025), one 8-month AI Engineer
co-op, Python/SQL, LangGraph, MLflow, Databricks. Label it **relevant** only if all hold:

1. The job is hands-on building: engineering in ML, AI applications, or data. Customer-facing
   pre-sales, architecture-for-clients, research science, IT and security operations are not.
2. Its stated requirements are within reach for her: no more than roughly 3 years required, no PhD
   required, and her stack covers a real part of what it asks for.
3. It is not a senior, staff, lead, principal or manager role, whatever the title says.

Otherwise label it **not_relevant**. Location and visa sponsorship are not considered (same as
the code rule), so the comparison isolates what the job is.

This rule is deliberately broader than the code rule, which reads only the title. Where they
disagree is the point of the comparison.
