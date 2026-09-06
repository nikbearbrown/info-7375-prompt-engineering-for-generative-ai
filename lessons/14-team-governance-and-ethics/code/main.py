# INFO 7375: Team governance and applied ethics
# Companion: lessons/14-team-governance-and-ethics/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
FIELDS = ("owner","purpose","data_classes","retention_days","approver","evaluation","incident_contact")

def assess(record):
    missing = [k for k in FIELDS if k not in record or record[k] is None or record[k] == "" or record[k] == []]
    if missing:
        return {"status":"incomplete","issues":missing}
    days = record["retention_days"]
    if type(days) is not int or days < 0:
        raise ValueError("Retention must be a nonnegative day count")
    classes = record["data_classes"]
    if not isinstance(classes, list) or not all(isinstance(x,str) for x in classes):
        raise ValueError("Data classes must be a list of strings")
    issues = []
    if set(classes) - {"public","synthetic","internal"}:
        issues.append("sensitive or unknown data review")
    if record.get("external_write"):
        issues.append("external action approval")
    return {"status":"review-required" if issues else "ready-for-human-review","issues":issues}

def demo():
    return assess({"owner":"project team","purpose":"summarize public course notes",
                   "data_classes":["public"],"retention_days":30,"approver":"instructor",
                   "evaluation":"citation audit","incident_contact":"project owner"})

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
