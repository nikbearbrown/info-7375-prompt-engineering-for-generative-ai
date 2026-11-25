# Run 2026-10-30-1

- Mode: **seeded** (no network; labeled seeded)
- Source: `runs\2026-10-30-1\raw.json`
- Time (UTC): 2026-10-30T15:38:45+00:00
- Raw response: `raw.json`, 891347 bytes, sha256 `4494c56bdf5f033e213461d1bcff798e6cc46f4cd0130a9ca2551551f2af5a0f`
- Postings in response: 67
- Baseline: no
- New since last run: 3
- Citations not supported: 0

## Rule verdicts [record]

- **8747498002** Staff Applied AI/ML Scientist: `not_relevant` [record]. R4 failed: content names fewer than 1 skill(s) from the shipped skill lists.
  - R1 `title`: 'Scientist' (supported)
  - R2 `title`: absent: manager, director, head, lead, intern (supported)
  - R3 `location.name`: 'San Francisco, CA' (supported)
  - R4 `content` / résumé `skills.languages`: absent: Python, SQL (supported)
  - R4 `content` / résumé `skills.data_bi`: absent: Databricks, Unity Catalog, Power BI (supported)
  - R4 `content` / résumé `skills.backend_automation`: absent: LangGraph, MLflow, Mem0 (supported)
  - R4 `content` / résumé `skills.database_cloud`: absent: Delta Lake, AWS (supported)
- **8828560002** Senior Finance Analytics Engineer: `relevant` [record]. All four checks passed: title term 'Analytics', no excluded term, US location 'New York City, NY', skills in content: Python, SQL.
  - R1 `title`: 'Analytics' (supported)
  - R2 `title`: absent: manager, director, head, lead, intern (supported)
  - R3 `location.name`: 'New York City, NY' (supported)
  - R4 `content` / résumé `skills.languages`: 'Python' (supported)
  - R4 `content` / résumé `skills.languages`: 'SQL' (supported)
- **8911749002** Staff Product Manager, Incentives: `not_relevant` [record]. R1 failed: title 'Staff Product Manager, Incentives' contains none of the title terms.
  - R1 `title`: absent: data, analytics, analyst, scientist, machine learning, ML (supported)

## Claude verdicts [judgment]

- **8747498002**: `not_relevant` [judgment], claude-opus-5-5, session b149f979-d657-40d6-ab33-a61cc3a2388b, 2026-10-30T15:38:45+00:00
  - `title` / résumé `skills.languages`: 'Staff Applied AI/ML Scientist' (supported)
  - `location.name` / résumé `personal.location`: 'San Francisco, CA' (supported)
  - `content` / résumé `skills.languages`: 'Strong programming skills.' (supported)
- **8828560002**: `relevant` [judgment], claude-opus-5-5, session f363a98a-67f0-40bd-94a2-7744839bf9bc, 2026-10-30T15:38:53+00:00
  - `content` / résumé `skills.languages`: 'Expert in SQL' (supported)
  - `content` / résumé `skills.languages`: 'Working proficiency in Python' (supported)
  - `location.name` / résumé `personal.location`: 'New York City, NY' (supported)
  - `title` / résumé `education`: 'Senior Finance Analytics Engineer' (supported)
- **8911749002**: `not_relevant` [judgment], claude-opus-5-5, session d68a8677-2475-4ccf-8a83-a9ccef0981ba, 2026-10-30T15:38:58+00:00
  - `title` / résumé `experience.0.title`: 'Staff Product Manager, Incentives' (supported)
