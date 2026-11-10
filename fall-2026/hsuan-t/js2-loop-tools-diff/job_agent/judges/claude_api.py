"""Optional phone line to Claude through the Anthropic API (`--claude-via api`): needs ANTHROPIC_API_KEY and API credits.

The default is claude_cli.py (D18: Claude Code subscription, no API credits). This one is kept
because it is the only line where this program itself checks the allow-list on every request,
and it is the only file that imports the SDK, so nothing else needs it installed.
"""

import os

from ..common.policy import Policy
from ..common.errors import ClaudeCallError
from .claude import MODEL, Reply

# Fixed here instead of trusting ANTHROPIC_BASE_URL, so an environment variable can't send the
# résumé to a host the allow-list never saw (CONTRACT Refuses #1).
API_BASE = "https://api.anthropic.com"
MAX_TOKENS = 16000            # room for adaptive thinking + the JSON; a cut-off reply is an error, not a verdict


def make_ask(policy: Policy, base_url: str = API_BASE, timeout_s: float = 300.0):
    """Return ask(system, user) -> Reply for the real API, or raise ClaudeCallError if there is no key.

    The key is read from the environment only and passed explicitly, so a saved CLI profile or a key
    file can never be picked up by accident (CONTRACT In: "only from ANTHROPIC_API_KEY").
    """
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ClaudeCallError("ANTHROPIC_API_KEY is not set; Claude judge did not run")
    policy.check_url(base_url)   # AgentError on purpose: a refused host stops the run (CONTRACT Refuses)
    import anthropic           # imported here so the rule judge and the tests run without the SDK installed

    # GATE §2: one call gets timeout_s (300 s); GATE §4: a failed Claude evaluation is not retried,
    # so the SDK's own retries are off (they would also make one call run past its 300 s).
    client = anthropic.Anthropic(api_key=key, base_url=base_url, timeout=timeout_s, max_retries=0)

    def ask(system: str, user: str) -> Reply:
        policy.check_url(str(client.base_url))   # every request passes the allow-list, not only the first
        try:
            msg = client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS, system=system,
                messages=[{"role": "user", "content": user}],
            )
        except anthropic.AuthenticationError as e:
            raise ClaudeCallError("Claude API rejected the API key") from e
        except anthropic.APIStatusError as e:
            raise ClaudeCallError(f"Claude API error HTTP {e.status_code}: {e.message}") from e
        except anthropic.APITimeoutError as e:     # a subclass of APIConnectionError, so it goes first
            raise ClaudeCallError(f"Claude API call timed out after {timeout_s:g} s", timed_out=True) from e
        except anthropic.APIConnectionError as e:
            raise ClaudeCallError(f"could not reach the Claude API: {e}") from e
        text = "".join(b.text for b in msg.content if b.type == "text")
        meta = {"via": "api", "model": msg.model, "request_id": msg._request_id,
                "usage": {"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens}}
        if msg.stop_reason == "refusal":
            category = getattr(msg.stop_details, "category", None) if msg.stop_details else None
            meta["refusal_category"] = category
        return Reply(text, msg.stop_reason, meta)

    return ask
