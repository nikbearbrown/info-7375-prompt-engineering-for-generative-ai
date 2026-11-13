# Tasks

Synthetic tasks (docs/02-data-boundary.md): small Python repos written for this project. Each task directory has:
- `repo/`: copied into the pod as `/workspace`. It is the only part the agent sees.
- `contract.json`: the goal, the allowed tools, and the budget.
- `check.sh`: the hidden check. It pins the SHA-256 of the test file, then runs pytest with `python -I -B`.
- `reference.patch`: a known fix, outside `repo/`, so it never reaches the pod. It does not touch the test file. A test (`cmd/apg/tasks_test.go`) runs each check in `apg-sandbox:dev`: it must FAIL on the untouched repo and PASS with `reference.patch` applied.

| Task | Purpose | Reference patch |
|---|---|---|
| 001-fix-function | Fix one wrong operator (`//` instead of `/`) in a small arithmetic package. | `001-fix-function/reference.patch` (calc/ops.py) |
| 002-chunk-list | Fix an off-by-one in a loop: `chunks` drops the last chunk. | `002-chunk-list/reference.patch` (listutil/chunks.py) |
| 003-slugify | Fix string handling: `slugify` must collapse every run of non-alphanumerics into one hyphen and trim the ends. | `003-slugify/reference.patch` (textkit/slug.py) |
| 004-parse-duration | Implement a function from its docstring alone (`parse_duration("1h30m") == 5400`, with its error cases). | `004-parse-duration/reference.patch` (timeparse/duration.py) |
| 005-cart-total | A fix across two files: a discount that is not rounded to whole cents, and a cart total that ignores quantity. Fixing either file alone still fails. | `005-cart-total/reference.patch` (shop/pricing.py, shop/cart.py) |

These are normal tasks. The deliberate failure cases come in T3.1.
