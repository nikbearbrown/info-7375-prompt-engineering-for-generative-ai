"""A CONSTRUCTED project folder for the MCP server/client and shortlist
tests: the js3_fixtures corpus plus the v1.1 config, the justify prompt,
the persona target and a decisions.jsonl computed by the real filter.

Nothing here came from a real board.
"""

import json
import shutil
from pathlib import Path

from js3 import corpus as js3_corpus
from js3 import filter as js3_filter
from tests.js3_fixtures import make_corpus

ROOT = Path(__file__).resolve().parent.parent
CONFIG_V11 = ROOT / "config" / "filter-v1.1.json"
DECISIONS = Path("out") / "filter" / "v1.1" / "decisions.jsonl"


def make_root(folder, jobs=None):
    root = make_corpus(folder, jobs=jobs)
    shutil.copy(CONFIG_V11, root / "config" / "filter-v1.1.json")
    (root / "prompts").mkdir()
    shutil.copy(ROOT / "prompts" / "justify-v1.md", root / "prompts")
    (root / "data").mkdir()
    shutil.copy(ROOT / "data" / "target.example.json", root / "data")
    config = js3_filter.load_config(CONFIG_V11)
    path = root / DECISIONS
    path.parent.mkdir(parents=True)
    with open(path, "w", encoding="utf-8") as fh:
        for posting in js3_corpus.load(root)["postings"]:
            fh.write(json.dumps(js3_filter.evaluate(posting, config)) + "\n")
    return root
