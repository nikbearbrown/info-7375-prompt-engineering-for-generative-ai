# INFO 7375: The agent loop
# Companion: lessons/04-the-agent-loop/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
def run(policy, records, max_turns=4):
    if type(max_turns) is not int or max_turns < 1:
        raise ValueError("Positive turn budget required")
    trace = []
    iterator = iter(policy)
    for turn in range(max_turns):
        try:
            action = next(iterator)
        except StopIteration:
            return {"status": "incomplete", "trace": trace}
        name = action.get("name")
        if name == "finish":
            return {"status": "finished", "answer": action.get("answer", ""), "trace": trace}
        observation = (records.get(action.get("key"), "not found")
                       if name == "lookup" else "error: tool not allowed")
        trace.append({"turn": turn + 1, "action": name, "observation": observation})
    return {"status": "budget-exhausted", "trace": trace}

def demo():
    return run([{"name": "lookup", "key": "office"},
                {"name": "finish", "answer": "505A Dana Hall"}],
               {"office": "505A Dana Hall"})

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
