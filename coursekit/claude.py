"""Minimal Claude Messages transport; no network requests on import.

Protocol: https://platform.claude.com/docs/en/api/messages/create
Use --live explicitly; scripted offline responses are not Claude outputs.
No retries: inspect failures before risking another billable request.
"""

import argparse
import json
import os
from urllib import error, request


def payload(prompt, model, max_tokens=256):
    if not isinstance(model, str) or not model.startswith("claude-"):
        raise ValueError("Set CLAUDE_MODEL to an available Claude model ID")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must be nonempty")
    if type(max_tokens) is not int or not 1 <= max_tokens <= 4096:
        raise ValueError("Course output budget must be 1..4096 tokens")
    return {"model": model, "max_tokens": max_tokens,
            "system": "Answer the task using supplied evidence. State uncertainty.",
            "messages": [{"role": "user", "content": prompt}]}


def send(body, *, live=False, opener=None):
    if not live:
        raise ValueError("Network access requires live=True")
    if not str(body.get("model", "")).startswith("claude-"):
        raise ValueError("Only Claude models are supported")
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY is missing; offline labs need no key")
    req = request.Request("https://api.anthropic.com/v1/messages",
                          data=json.dumps(body).encode(), method="POST",
                          headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                                   "content-type": "application/json"})
    try:
        with (opener or request.urlopen)(req, timeout=30) as response:
            result = json.load(response)
    except error.HTTPError as exc:
        raise RuntimeError(f"Claude HTTP {exc.code}; no automatic retry") from None
    except (error.URLError, TimeoutError):
        raise RuntimeError("Claude request failed or timed out; no automatic retry") from None
    if not isinstance(result, dict) or not isinstance(result.get("content"), list):
        raise ValueError("Malformed Messages response")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--prompt", default="Explain why a passing format check is not proof of truth.")
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({"mode": "offline", "note": "No Claude request made",
                          "prompt": args.prompt}, indent=2))
        return
    try:
        result = send(payload(args.prompt, os.environ.get("CLAUDE_MODEL", "")), live=True)
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps({"mode": "live", "response": result}, indent=2))


if __name__ == "__main__":
    main()
