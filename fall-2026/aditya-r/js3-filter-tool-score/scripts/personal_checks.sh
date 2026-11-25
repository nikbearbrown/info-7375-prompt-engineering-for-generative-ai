#!/bin/sh
# Aditya's personal checks. Run them yourself; the output is the record:
#   sh scripts/personal_checks.sh | tee evidence/aditya_personal_checks.txt
set -u
cd "$(dirname "$0")/.."
echo "== run by: $(whoami | sed 's/.*/<local user>/') at $(date '+%Y-%m-%d %H:%M:%S %Z') on commit $(git rev-parse HEAD)"
echo "== 1. tests";            .venv/bin/python -m pytest -q -p no:cacheprovider | tail -1
echo "== 2. wrong versions";   .venv/bin/python tests/mutation_check.py | tail -7
echo "== 3. S43 score (compare with your own hand computation from review/postings/S43.md)"
for v in v1.0 v1.1; do .venv/bin/python -m js3.explain 6233043004 --filter "$v" | tail -1; done
echo "== 4. freeze came before the H2 labels"
git log --format='%h %ad %s' --date=iso -- FREEZE.json | tail -1
git log --format='%h %ad %s' --date=iso -- labels/SEAL_H2.json | tail -1
echo "== 5. H2 sheet unchanged since its seal"
.venv/bin/python -c "import json,hashlib;s=json.load(open('labels/SEAL_H2.json'));print('match' if hashlib.sha256(open('review/LABEL_SHEET_H2.csv','rb').read()).hexdigest()==s['sheet_sha256'] else 'MISMATCH')"
echo "== 6. tool server over real stdio (js3 test client, not Claude)"
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_mcp_server.py | tail -1
