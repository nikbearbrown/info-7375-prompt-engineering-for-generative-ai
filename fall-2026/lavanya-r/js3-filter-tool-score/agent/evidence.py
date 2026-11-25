"""FILTER.md section 2, the evidence rules, as code.

check_label(posting, {"claim", "label", "quote"}) -> the final label.
    A "supported" or "contradicted" label stands only if its quote is found,
    character for character (whitespace and curly quotes normalised), in the
    posting's own title, locations or text. Otherwise the final label is
    "insufficient". So a label can never rest on a word merely appearing
    somewhere (W5), or on a quote from outside the posting (E4).

answer(posting, final_labels) -> what the agent may say per topic, or
    "I cannot tell" (E1 short text, E2 silent, E3 conflicting quotes).
"""

import re

LABELS = ("supported", "contradicted", "insufficient")
MIN_TEXT = 200
CURLY = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-",
                       "—": "-", "\xa0": " "})


def norm(s):
    return " ".join((s or "").translate(CURLY).split())


def posting_text(p):
    # Exactly as the labelling prompt shows the posting, "Title:" and
    # "Location:" included (fix 2026-11-24: the first check rejected 8 quotes
    # that copied those prefixes; logs/js3-06-shortlist-check-before-fix.md).
    return norm("\n".join(["Title: " + (p.get("title") or "").strip(),
                           "Location: " + "; ".join(p.get("locations") or []),
                           p.get("text") or ""]))


def check_label(p, item):
    label, quote = item.get("label"), norm(item.get("quote"))
    if label not in LABELS:
        raise ValueError(f"unknown label {label!r}")
    out = dict(item, final=label, why="quote found in the posting")
    if label == "insufficient":
        out["why"] = "labelled insufficient"
    elif not quote:
        out.update(final="insufficient", why="no quote given")
    elif quote not in posting_text(p):
        out.update(final="insufficient", why="quote not found in the posting")
    return out


def answer(p, labels):
    if len(p.get("text") or "") < MIN_TEXT:
        return {"answer": "I cannot tell", "rule": "E1"}
    out = {"answer": "per topic"}
    for topic in ("sponsorship", "experience"):
        finals = {l["final"] for l in labels if l.get("topic") == topic}
        if {"supported", "contradicted"} <= finals:
            out[topic] = "I cannot tell"          # E3: the posting disagrees with itself
        elif "contradicted" in finals:
            out[topic] = "no"
        elif "supported" in finals:
            out[topic] = "yes"
        else:
            out[topic] = "I cannot tell"          # E2: the posting is silent
    return out
