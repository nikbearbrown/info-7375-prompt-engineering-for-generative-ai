"""CONSTRUCTED test postings. These are not real Datadog postings: they are
shaped like Greenhouse records so each check in CONTRACT.md can be exercised
on purpose."""

import copy
import html
import json
import os

HERE = os.path.dirname(__file__)
PERSONA = os.path.join(HERE, "..", "persona", "priya-nair.resume.json")


def resume():
    with open(PERSONA, encoding="utf-8") as f:
        return json.load(f)


def escaped(markup):
    # Greenhouse sends its HTML escaped, e.g. &lt;p&gt;
    return html.escape(markup)


def posting(id=1, title="AI Engineer", location="Boston, Massachusetts, USA",
            body="<p>You will build pipelines in Python on AWS.</p>"):
    return {"id": id, "title": title, "location": {"name": location},
            "content": escaped(body)}


RELEVANT = posting()


def variant(**changes):
    p = copy.deepcopy(RELEVANT)
    for k, v in changes.items():
        if k == "location":
            p["location"] = {"name": v}
        elif k == "body":
            p["content"] = escaped(v)
        else:
            p[k] = v
    return p
