# Permission boundary table

**Predictions** were drafted by Claude Code on 2026-11-10 from `GATE.md` §5 and `GATE_ADDENDUM_1.md` §1–2. They were committed **before** `agent/policy.py` and `tests/test_boundary.py` existed, which the commit order shows. Aditya has not separately reviewed them.

The **Observed** column is filled in only after the suite has run, in a later commit.

"No side effect" means: no request reaches the network or a local test server, no file is created or changed, and no HTTP attempt is counted.

| # | Case | Kind | Predicted outcome (written before running) | Test | Observed |
|---|---|---|---|---|---|
| B1 | GET `https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true` | network, allowed | allowed | `test_b01_allowed_greenhouse_url` | |
| B2 | GET `https://api.ashbyhq.com/posting-api/job-board/notion` | network, allowed | allowed | `test_b02_allowed_ashby_url` | |
| B3 | GET `https://api.lever.co/v0/postings/x` (host off the allow-list) | network, denied | refused before dispatch; 0 attempts counted; the transport is never called | `test_b03_off_list_host_refused_before_dispatch` | |
| B4 | GET `https://boards-api.greenhouse.io.evil.com/...` (deceptive suffix) | network, denied | refused; exact hostname match only | `test_b04_deceptive_suffix_refused` | |
| B5 | `http://`, `user:pw@`, `:8443`, and a path outside the board endpoints | network, denied | each refused | `test_b05_scheme_userinfo_port_path_refused` | |
| B6 | POST to an allowed board URL | network, denied | refused; only GET is permitted | `test_b06_write_method_refused` | |
| B7 | Allowed host answers 302 → another host (real HTTP client against two local test servers) | network, redirect | run-level `error`, exit 2; the **destination server receives 0 requests**; staged state not published | `test_b07_redirect_refused_destination_never_contacted` | |
| B8 | URL taken from posting text (an Ashby `jobUrl` on `jobs.ashbyhq.com`) | network, denied | refused; the agent never fetches posting-supplied URLs | `test_b08_posting_supplied_url_refused` | |
| B9 | Write `out/runs/<id>/report.json` | write, allowed | allowed; file created inside `out/` | `test_b09_write_inside_out_allowed` | |
| B10 | Write `out/../GATE.md` (parent traversal) | write, denied | refused; `GATE.md` unchanged | `test_b10_parent_traversal_refused` | |
| B11 | Write `out-evil/x.json` (a sibling with the same prefix as `out`) | write, denied | refused; nothing created | `test_b11_sibling_prefix_refused` | |
| B12 | Write `out/link/x.json`, where `out/link` is a symlink to a folder outside the project | write, denied | refused; nothing created outside | `test_b12_symlink_escape_refused` | |
| B13 | Read `config/boards.json` vs write `config/boards.json` | read vs write | read allowed; write refused; file unchanged | `test_b13_read_allowed_write_refused` | |
| B14 | Runtime writes `approvals/<run-id>.json` | write, denied | refused (the runtime may read approvals, never create or edit them) | `test_b14_runtime_cannot_write_approval` | |
| B15 | Runtime writes `out/approved-shortlists/<run-id>.json` directly | write, protected | refused without the export path and a matching approval | `test_b15_protected_export_needs_export_path` | |
| B16 | `--export <run-id>` with a proposal and **no** approval record | protected write | refused; exit 3 (pending); no export file; result recorded | `test_b16_export_without_approval_refused` | |
| B17 | `--export` with an approval whose sha256 (or destination) differs from the proposal | protected write | refused; exit 2; no export file | `test_b17_export_with_mismatched_approval_refused` | |
| B18 | `--export` with a matching approval, then the same export a second time | protected write | first run creates the file (exit 0); second is refused (create-only, exit 2) and the file is unchanged | `test_b18_matching_approval_creates_once` | |
| B19 | The same GET dispatched twice in one run, outside the single retry rule | repeat rule | second dispatch refused; run-level `error`, exit 2 | `test_b19_repeated_action_refused` | |
| B20 | Read of a file outside the project root (e.g. `../../secret.txt`) | read, denied | refused | `test_b20_read_outside_root_refused` | |
