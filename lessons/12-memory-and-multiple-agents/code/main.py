# INFO 7375: Memory and multiple agents
# Companion: lessons/12-memory-and-multiple-agents/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
from copy import deepcopy
from threading import Lock

class Memory:
    def __init__(self):
        self.records = {}
        self.lock = Lock()

    def read(self, key):
        with self.lock:
            return deepcopy(self.records.get(key, {"version":0,"value":None,"source":None}))

    def write(self, key, value, source, expected):
        if not isinstance(source, str) or not source.strip():
            raise ValueError("Source required")
        with self.lock:
            current = self.records.get(key, {"version":0})
            if type(expected) is not int or current["version"] != expected:
                raise ValueError("Stale memory version")
            self.records[key] = {"version":expected+1,"value":deepcopy(value),"source":source}
            return expected+1

def demo():
    memory = Memory()
    memory.write("office", "505A", "syllabus", 0)
    try:
        memory.write("office", "old room", "stale-worker", 0)
    except ValueError as exc:
        return {"record":memory.read("office"),"conflict":str(exc)}

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
