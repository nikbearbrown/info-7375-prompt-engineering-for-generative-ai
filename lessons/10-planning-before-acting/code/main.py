# INFO 7375: Planning before acting
# Companion: lessons/10-planning-before-acting/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
FIELDS = ("objective", "inputs", "scope", "steps", "tools", "risks", "verification", "stop")

def missing_fields(plan):
    return [field for field in FIELDS if not plan.get(field)]

def order(steps):
    graph = {}
    for step in steps:
        if step["id"] in graph:
            raise ValueError("Duplicate step")
        graph[step["id"]] = set(step.get("after", []))
    if any(deps - graph.keys() for deps in graph.values()):
        raise ValueError("Unknown prerequisite")
    result = []
    while graph:
        ready = sorted(key for key, deps in graph.items() if not deps)
        if not ready:
            raise ValueError("Dependency cycle")
        for key in ready:
            result.append(key)
            del graph[key]
        for deps in graph.values():
            deps.difference_update(ready)
    return result

def demo():
    return {"order":order([{"id":"verify","after":["build"]},{"id":"build"}]),
            "missing":missing_fields({"objective":"Fix a reproducible Python bug"})}

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
