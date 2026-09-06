# INFO 7375: Prompt contracts and evaluation
# Companion: lessons/02-prompt-contracts-and-evaluation/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
import json

def validate(text, source_ids):
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return False
    return (isinstance(data, dict) and set(data) == {"answer", "sources"}
            and isinstance(data["answer"], str) and bool(data["answer"].strip())
            and isinstance(data["sources"], list) and bool(data["sources"])
            and all(isinstance(s, str) and s in source_ids for s in data["sources"]))

def pass_rate(responses, source_ids):
    if not responses:
        raise ValueError("An empty experiment has no pass rate")
    return sum(validate(r, source_ids) for r in responses) / len(responses)

def demo():
    return {"format_pass_rate": pass_rate([
        '{"answer":"Class is on ground.","sources":["syllabus"]}',
        '{"answer":42,"sources":[]}'], {"syllabus"})}

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
