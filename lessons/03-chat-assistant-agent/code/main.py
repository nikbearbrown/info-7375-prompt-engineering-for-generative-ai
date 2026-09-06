# INFO 7375: Chat, assistant, and agent
# Companion: lessons/03-chat-assistant-agent/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
SURFACES = {"chat": {"reason"},
            "assistant": {"reason", "read"},
            "agent": {"reason", "read", "write"}}

def missing(surface, required):
    if surface not in SURFACES:
        raise ValueError("Unknown teaching surface")
    return sorted(set(required) - SURFACES[surface])

def classify(events):
    allowed = {"reason", "read", "write"}
    if set(events) - allowed:
        raise ValueError("Unknown event")
    if "write" in events:
        return "agent"
    return "assistant" if "read" in events else "chat"

def demo():
    return {"chat_missing": missing("chat", ["read", "write"]),
            "observed": classify(["reason", "read"])}

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
