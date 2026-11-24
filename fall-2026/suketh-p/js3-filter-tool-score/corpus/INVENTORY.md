# Corpus inventory

Run `2026-11-24-js3-corpus`, read by `python3 -m jobwatch.js3 inventory runs/2026-11-24-js3-corpus`.
Expected counts are the student's prediction in FILTER.md, made before the run.

| Board | Expected | Collected | Collected − expected | Captured (UTC) | Failure |
| --- | ---: | ---: | ---: | --- | --- |
| greenhouse/anthropic | 635 | 631 | -4 | 2026-11-24T22:36:19Z |  |
| greenhouse/databricks | 895 | 890 | -5 | 2026-11-24T22:36:20Z |  |
| ashby/linear | 32 | 30 | -2 | 2026-11-24T22:36:24Z |  |

## The listed fields

| Board | Postings | Blank title | Blank location | Blank description after decoding |
| --- | ---: | ---: | ---: | ---: |
| greenhouse/anthropic | 631 | 0 | 0 | 0 |
| greenhouse/databricks | 890 | 0 | 0 | 0 |
| ashby/linear | 30 | 0 | 0 | 0 |

## Fields the boards sent that FILTER.md does not list

Counts are postings where the field is present and not empty.

- **greenhouse/anthropic** (631 postings): `absolute_url` 631, `company_name` 631, `data_compliance` 631, `departments` 631, `first_published` 631, `internal_job_id` 631, `language` 631, `metadata` 631, `offices` 631, `requisition_id` 631, `updated_at` 631
- **greenhouse/databricks** (890 postings): `absolute_url` 890, `company_name` 890, `data_compliance` 890, `departments` 889, `education` 39, `first_published` 890, `internal_job_id` 890, `language` 890, `metadata` 890, `offices` 888, `requisition_id` 890, `updated_at` 890
- **ashby/linear** (30 postings): `address` 30, `applyUrl` 30, `department` 30, `descriptionPlain` 30, `employmentType` 30, `id` 30, `isListed` 30, `isRemote` 30, `publishedAt` 30, `secondaryLocations` 7, `team` 30, `workplaceType` 30

## Location fields that the location rule does not read

"Would change" counts postings whose location outcome (us / outside / unresolved) would differ if the unread fields were added to the text the U.S. test reads. This only measures the gap; the filter does not read these fields.

- **greenhouse/anthropic**: more than one entry in `offices` in 77. Adding the office names and locations would change 10 outcomes: {'unresolved → outside': 5, 'outside → us': 3, 'unresolved → us': 2}
- **greenhouse/databricks**: more than one entry in `offices` in 0. Adding the office names and locations would change 5 outcomes: {'outside → us': 2, 'unresolved → outside': 1, 'unresolved → us': 2}
- **ashby/linear**: `secondaryLocations` not empty in 7; `isRemote` true in 30; `workplaceType` {'Remote': 27, 'Hybrid': 3}; `address.postalAddress.addressCountry` {'European Union': 7, 'United States': 15, 'United Kingdom': 2, 'Australia': 1, 'Singapore': 5}. Adding `secondaryLocations` and `addressCountry` would change 17 outcomes: {'unresolved → us': 15, 'unresolved → outside': 2}
