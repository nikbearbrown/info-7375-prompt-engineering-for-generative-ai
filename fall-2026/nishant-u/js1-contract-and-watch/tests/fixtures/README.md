# Test fixtures: all constructed

Every file here is **constructed** test data, written by hand from CONTRACT.md. None of it was fetched
from a job board, and none of it is a Claude output.

- `postings.json`: eight Greenhouse-shaped postings, each with `"provenance": "constructed"` and ids
  starting at 9000000001, so they can't collide with real Greenhouse ids. Each one carries the
  verdict I predicted by hand from the rule (`expected_verdict`, `expected_failed_check`):

  | id | Hits | Expected |
  |---|---|---|
  | 9000000001 | R1 fail (title has no data term) | not_relevant, R1 |
  | 9000000002 | R2 fail ("Manager") | not_relevant, R2 |
  | 9000000003 | R3 fail ("Toronto, ON") | not_relevant, R3 |
  | 9000000004 | R3 fail ("London, UK") | not_relevant, R3 |
  | 9000000005 | R3 pass on a multi-city string ("Kitchener-Waterloo, ON; San Francisco, CA") | relevant |
  | 9000000006 | R4 fail (only Ray/Kubeflow, which are `familiar_with_not_shipped` and don't count) | not_relevant, R4 |
  | 9000000007 | R4 pass (MLflow inside HTML tags; Senior title allowed) | relevant |
  | 9000000008 | all checks pass | relevant |

- `resume_not_fictional.json`: a constructed résumé with no FICTIONAL marker in `_comment` and a gmail
  address. The agent must refuse it.

The board files the watch tests use are built from `postings.json` in a temporary directory during the
test run; they are never written here.
