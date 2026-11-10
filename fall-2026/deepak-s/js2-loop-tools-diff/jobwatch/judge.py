"""The Claude judge: CONTRACT.md In (Judge), Out › judgment, Interfaces › Judge defaults.

Its verdict is a judgment, labelled as one, and never merged into the rule's record.
"""
import json
import os
from pathlib import Path

from jobwatch.evidence import utc_iso
from jobwatch.prompt import fill_user
from jobwatch.validator import Invalid, parse_output

DEFAULT_MODEL = "claude-sonnet-5-5"
TEMPERATURE = 1.0
MAX_TOKENS = 600
CLIENT_TIMEOUT_S = 60.0


def make_client():
    import anthropic

    return anthropic.Anthropic(max_retries=0, timeout=CLIENT_TIMEOUT_S)


def build_request(prompt, model, resume, posting_id, posting_doc):
    return {
        "model": model,
        "system": prompt.system,
        "messages": [{"role": "user", "content": fill_user(prompt, resume, posting_id, posting_doc)}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }


def api_error_type(exc):
    try:
        import anthropic
    except ImportError:
        return "other"
    if isinstance(exc, anthropic.APITimeoutError):
        return "timeout"
    if isinstance(exc, anthropic.RateLimitError):
        return "rate_limit"
    if isinstance(exc, (anthropic.AuthenticationError, anthropic.PermissionDeniedError)):
        return "auth"
    if isinstance(exc, anthropic.InternalServerError) or (
        isinstance(exc, anthropic.APIStatusError) and getattr(exc, "status_code", 0) >= 500
    ):
        return "5xx"
    if isinstance(exc, anthropic.APIConnectionError):
        return "connection"
    if isinstance(exc, anthropic.APIStatusError):
        return f"http_{exc.status_code}"
    return "other"


def _judgment(status, reason, model=None, called_at=None, raw_path=None, verdict=None, citations=None):
    return {"status": status, "reason": reason, "verdict": verdict, "citations": citations,
            "model": model, "called_at": called_at, "raw_path": raw_path}


def not_run():
    return _judgment("not_run", "no_api_key")


def judge_posting(client, prompt, model, resume, posting_id, posting_doc, out_dir, clock, stem=None):
    """One request, no retries. Every call leaves its request and exact response text on disk.

    Files are claude/<stem>.*; the stem is the posting id in a run, and names one call of several
    in sample and experiment (Amendment A8).
    """
    stem = stem or posting_id
    request = build_request(prompt, model, resume, posting_id, posting_doc)
    out_dir.write_json(f"claude/{stem}.request.json", request)
    called_at = utc_iso(clock())
    try:
        response = client.messages.create(**request)
    except Exception as exc:
        return _judgment("error", f"api_error:{api_error_type(exc)}", model, called_at)

    text = "".join(b.text for b in response.content if getattr(b, "type", None) == "text")
    raw_path = out_dir.write(f"claude/{stem}.response.txt", text)
    used_model = getattr(response, "model", None) or model
    stop_reason = getattr(response, "stop_reason", None)
    out_dir.write_json(f"claude/{stem}.response.meta.json", {
        "id": getattr(response, "id", None),
        "model": used_model,
        "stop_reason": stop_reason,
        "called_at": called_at,
    })
    return judge_text(text, stop_reason, used_model, called_at, raw_path, posting_id, resume, posting_doc)


def judge_text(text, stop_reason, model, called_at, raw_path, posting_id, resume, posting_doc):
    """The judgment for one saved response: truncated, rejected with the validator's reason, or accepted."""
    if stop_reason == "max_tokens":
        return _judgment("rejected", "truncated", model, called_at, raw_path)
    try:
        out = parse_output(text, posting_id, resume, posting_doc)
    except Invalid as e:
        return _judgment("rejected", e.reason, model, called_at, raw_path)
    return _judgment("accepted", out["reason"], model, called_at, raw_path,
                     verdict=out["verdict"], citations=out["citations"])


def saved_judgment(directory, stem, posting_id, resume, posting_doc, raw_path):
    """Re-validate a saved response (replay, experiment reuse); None if no response was saved."""
    claude = Path(directory) / "claude"
    text_file = claude / f"{stem}.response.txt"
    if not text_file.exists():
        return None
    text = text_file.read_bytes().decode("utf-8")
    meta = json.loads((claude / f"{stem}.response.meta.json").read_bytes())
    return judge_text(text, meta.get("stop_reason"), meta.get("model"), meta.get("called_at"), raw_path,
                      posting_id, resume, posting_doc)


class SdkJudge:
    """The anthropic SDK backend (the default). Its errors do not stop the command."""

    name = "sdk"
    unavailable_reason = "no_api_key"

    def __init__(self, client=None):
        self.client = client
        self.stopped = None

    def available(self):
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    def request(self, prompt, model, resume, posting_id, posting_doc):
        return build_request(prompt, model, resume, posting_id, posting_doc)

    def call(self, prompt, model, resume, posting_id, posting_doc, out_dir, clock, stem=None):
        if self.client is None:
            self.client = make_client()
        return judge_posting(self.client, prompt, model, resume, posting_id, posting_doc, out_dir, clock, stem)

    def saved(self, directory, stem, posting_id, resume, posting_doc, raw_path):
        return saved_judgment(directory, stem, posting_id, resume, posting_doc, raw_path)


def not_available(backend):
    return _judgment("not_run", backend.unavailable_reason)


def stopped_judgment():
    """A posting left unjudged because an earlier call stopped the judge (Amendment A14)."""
    return _judgment("not_run", "judge_stopped")
