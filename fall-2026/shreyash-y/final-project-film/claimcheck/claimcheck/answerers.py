"""Answerers produce a raw reply (a string that should satisfy the contract) for one question.

baseline  no model: picks the document line that shares the most words with the question.
          It exists so the checker and the eval run offline, and as a floor to compare against.
claude    live Claude API call. Only used when asked for explicitly (--answerer claude).
recorded  replays the raw replies saved by an earlier claude run, so anyone can re-check
          that run offline. It never calls the API and is labelled as a replay in reports.
"""

import json
import os
import re
from pathlib import Path

from .contract import SCHEMA

PROMPT_VERSION = "v1"
SYSTEM_PROMPT = (
    "You answer questions about an insurance claim file using only the document provided.\n"
    "Reply with JSON matching the schema. Fields:\n"
    "- answer: one plain sentence that answers the question.\n"
    "- quote: a span copied exactly, word for word, from the document that contains the answer, "
    "including any amount, percentage or day count you state. Do not paraphrase inside quote.\n"
    "- doc_id: the id of the document the quote comes from.\n"
    "- status: \"answered\", or \"not_in_documents\" if the document does not answer the question. "
    "When it is not_in_documents, leave answer and quote empty. Do not use outside knowledge."
)
CLAUDE_MODEL = "claude-opus-5-5"

_WORD = re.compile(r"[a-z0-9$%]+")


def _words(text):
    return {w for w in _WORD.findall(text.lower()) if len(w) >= 4}


class BaselineAnswerer:
    name = "baseline"
    model = "none (keyword overlap, no model)"

    def answer(self, question: str, docs: dict[str, str]) -> dict:
        best = (0, "", "")
        q = _words(question)
        for doc_id, text in docs.items():
            for line in text.splitlines():
                line = line.strip()
                score = len(q & _words(line))
                if score > best[0]:
                    best = (score, doc_id, line)
        score, doc_id, line = best
        if score < 2:
            reply = {"answer": "", "quote": "", "doc_id": doc_id, "status": "not_in_documents"}
        else:
            reply = {"answer": line, "quote": line, "doc_id": doc_id, "status": "answered"}
        return {"raw": json.dumps(reply), "served_by": self.model}


class ClaudeAnswerer:
    name = "claude"
    model = CLAUDE_MODEL

    def __init__(self):
        if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            raise SystemExit(
                "The claude answerer needs ANTHROPIC_API_KEY set in your shell. "
                "Run offline instead with --answerer baseline, or replay a saved run with --answerer recorded."
            )
        import anthropic  # only needed for live runs

        self._anthropic = anthropic
        self.client = anthropic.Anthropic()

    def answer(self, question: str, docs: dict[str, str]) -> dict:
        documents = "\n\n".join(f'<document id="{i}">\n{t}\n</document>' for i, t in docs.items())
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": f"{documents}\n\nQuestion: {question}"}],
        )
        if response.stop_reason == "refusal":
            return {"raw": "", "served_by": response.model, "stop_reason": "refusal"}
        text = next((b.text for b in response.content if b.type == "text"), "")
        return {
            "raw": text,
            "served_by": response.model,
            "stop_reason": response.stop_reason,
            "request_id": response._request_id,
            "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
        }


class RecordedAnswerer:
    name = "recorded"

    def __init__(self, path: Path):
        self.path = Path(path)
        rows = [json.loads(l) for l in self.path.read_text().splitlines() if l.strip()]
        self.by_id = {r["id"]: r for r in rows}
        self.model = f"replay of {rows[0].get('served_by', '?')} run {rows[0].get('run_at', '?')}" if rows else "replay"

    def answer_for(self, qid: str) -> dict:
        row = self.by_id.get(qid)
        if row is None:
            return {"raw": "", "served_by": "missing from recording"}
        return {"raw": row["raw"], "served_by": row.get("served_by", "?")}
