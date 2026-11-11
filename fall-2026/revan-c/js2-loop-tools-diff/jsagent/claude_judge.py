"""Claude as the second judge, under a prompt contract. Its output is a JUDGMENT, not a record."""
import json
import os
import pathlib
from datetime import datetime, timezone

import anthropic

from .text import strip_html
from .validator import ALLOWED_RESUME_PATHS, validate_claude_output

DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_EFFORT = "medium"
DEFAULT_PROMPT = pathlib.Path(__file__).resolve().parent.parent / "prompts" / "baseline.txt"
MAX_TOKENS = 8000
FALLBACK_BETA = "server-side-fallback-2026-07-01"
# Current Claude models reject temperature/top_p/top_k, so none is sent; recorded as such.
SAMPLING_NOTE = "temperature not sent (current models reject sampling parameters)"
CREDENTIAL_VARS = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_PROFILE")
MISSING_CREDENTIALS = ("CLAUDE CREDENTIALS MISSING: set ANTHROPIC_API_KEY in this shell. "
                       "Nothing was fetched or called.")


def credentials_present():
    return any(os.environ.get(v) for v in CREDENTIAL_VARS)


def resume_for_prompt(resume):
    """Only the allowed citation paths. Name, email, and phone are never sent to the API."""
    out = {}
    for path in ALLOWED_RESUME_PATHS:
        value, node = resume, out
        parts = path.split(".")
        for part in parts:
            value = value[part]
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    return out


def posting_for_prompt(posting):
    return {
        "title": posting["title"],
        "location.name": posting["location"]["name"],
        "content": " ".join(strip_html(posting["content"]).split()),
    }


def user_message(resume, posting):
    return json.dumps({"resume": resume_for_prompt(resume), "posting": posting_for_prompt(posting)},
                      ensure_ascii=False, indent=2)


def make_claude_judge(model=DEFAULT_MODEL, effort=DEFAULT_EFFORT, prompt_path=DEFAULT_PROMPT, client=None):
    prompt_path = pathlib.Path(prompt_path)
    system = prompt_path.read_text()
    holder = {"client": client}

    def judge(resume, posting):
        meta = {
            "claude_model_requested": model,
            "claude_effort": effort,
            "claude_sampling": SAMPLING_NOTE,
            "claude_prompt": prompt_path.name,
            "claude_called_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }

        def unavailable(reason):
            return {"claude_verdict": "unavailable", "claude_justification": [],
                    "claude_reason": reason, **meta}

        try:
            if holder["client"] is None:
                holder["client"] = anthropic.Anthropic()
            response = holder["client"].beta.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                betas=[FALLBACK_BETA],
                fallbacks="default",
                output_config={"effort": effort},
                system=system,
                messages=[{"role": "user", "content": user_message(resume, posting)}],
            )
        except anthropic.AuthenticationError:
            return unavailable("authentication failed: check ANTHROPIC_API_KEY")
        except anthropic.RateLimitError:
            return unavailable("rate limited (429)")
        except anthropic.APIStatusError as exc:
            return unavailable(f"API error {exc.status_code}: {exc.message}")
        except anthropic.APIConnectionError:
            return unavailable("network error reaching the Claude API")
        except anthropic.AnthropicError as exc:
            return unavailable(f"Claude client error: {exc}")

        meta["claude_model_served"] = response.model
        meta["claude_request_id"] = getattr(response, "_request_id", None)
        usage = getattr(response, "usage", None)
        if usage is not None:
            meta["claude_usage"] = {"input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens}
        if response.stop_reason == "refusal":
            return unavailable("model declined (stop_reason=refusal)")

        text = "".join(block.text for block in response.content if block.type == "text")
        meta["claude_raw_text"] = text
        if response.stop_reason == "max_tokens":
            return {"claude_verdict": "invalid", "claude_justification": [],
                    "claude_reason": "output truncated at max_tokens", **meta}

        ok, parsed, errors = validate_claude_output(text, resume, posting)
        if not ok:
            # Recorded as invalid with the reasons; never retried or repaired.
            return {"claude_verdict": "invalid", "claude_justification": [],
                    "claude_reason": "; ".join(errors), **meta}
        return {"claude_verdict": parsed["verdict"], "claude_justification": parsed["justification"],
                "claude_reason": "passed validator (format and citations only, not correctness)", **meta}

    return judge
