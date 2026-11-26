"""Load what the JS2 agent collected (FILTER.md section 3): three saved responses, checked byte for byte."""

import gzip
import hashlib
import json
from pathlib import Path

from js3.boards import normalize, parse_postings

FOLDER = Path(__file__).resolve().parent.parent
RUN = "2026-11-10T215306Z"
# system -> (board, company, saved response, SHA-256 of the response as recorded in JS2's run record)
SOURCES = {
    "greenhouse": ("anthropic", "Anthropic", "data/%s--greenhouse-anthropic--r1.body.gz" % RUN,
                   "ff2a4167a32ba76ee3260d681a38c45c4d978d4cd871fca30957a686fb22a48c"),
    "lever": ("palantir", "Palantir", "data/%s--lever-palantir--r2.body.gz" % RUN,
              "68278bad3008de2fe332541f2ee624aa4ff2e2029e1362e5285d14c04d6c4552"),
    "ashby": ("linear", "Linear", "data/%s--ashby-linear--r3.body.gz" % RUN,
              "ac2e34215a8b41df85b357494c444e8df2505cc8d762cfd6951d7f9bd2e3d35a"),
}
PERSONA = FOLDER / "persona" / "aarav-patel.resume.example.json"


class SourceChanged(ValueError):
    pass


def load_persona():
    resume = json.loads(PERSONA.read_text(encoding="utf-8"))
    personal = resume.get("personal") or {}
    if not str(personal.get("email", "")).endswith("@example.com") or "555" not in str(personal.get("phone", "")):
        raise ValueError("refused: fictional personas only (@example.com, 555 phone)")
    return resume


def load(folder=FOLDER, sources=SOURCES):
    """(postings, not_checked). A missing board is "not checked", never "no postings" (FILTER.md section 3)."""
    postings, not_checked = [], []
    for system, (board, company, relative, sha) in sources.items():
        path = Path(folder) / relative
        if not path.exists():
            not_checked.append("%s/%s" % (system, board))
            continue
        body = gzip.decompress(path.read_bytes())
        if hashlib.sha256(body).hexdigest() != sha:
            raise SourceChanged("%s is not the response JS2 recorded" % relative)
        for job in parse_postings(system, body):  # a response of the wrong shape raises BadShape: the run stops
            posting = normalize(system, job, company)
            posting.update(system=system, board=board, key="%s/%s/%s" % (system, board, posting["id"]))
            postings.append(posting)
    return postings, not_checked
