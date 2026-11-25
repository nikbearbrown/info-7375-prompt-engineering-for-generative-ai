"""Rule-4 design evidence from the DEV split only. Prints, for every dev
filter-relevant posting, its dev hand label and every sentence-window that
mentions years, plus management/eligibility phrases. Never touches held-out.

    python3 tools/dev_evidence.py
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from js3 import experiment as ex
from js3 import filter as flt

items = ex.dataset()
dev, _ = ex.load_split()
lab = ex.labels("dev")                       # dev only; held-out is locked
YEARS = re.compile(r"[^.\n]{0,90}\byears?\b[^.\n]{0,90}", re.I)
MGMT = re.compile(r"[^.\n]{0,60}\b(manag\w*|lead(?:ing)? (?:a )?team|people leader|direct reports|hire|hiring|P&L|clearance|graduat\w*)\b[^.\n]{0,60}", re.I)
for k in sorted((k for k in dev if items[k]["filter_bucket"] == "relevant"), key=lambda k: items[k]["audit_labels"][0]):
    it = items[k]; t = flt.field_text(it["posting"], "content")
    print(f"=== {it['audit_labels'][0]} [{it['board']}] {it['title'].strip()}  | dev label: {lab[k]['label']}")
    print(f"    reason: {lab[k]['reason']}")
    for m in YEARS.finditer(t): print("    YEARS:", m.group(0).strip())
    for m in MGMT.finditer(t): print("    MGMT/ELIG:", m.group(0).strip())
