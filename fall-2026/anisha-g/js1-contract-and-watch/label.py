import csv, glob, re, agent
ps = {p["id"]: p for p in agent.all_postings(glob.glob("runs/*-live-raw.json")[0])}
rows = list(csv.reader(open("labels/labels.csv"))); head, body = rows[0], rows[1:]
for i, r in enumerate(body, 1):
    if r[4].strip(): continue
    p = ps[r[0]]
    print("\n" + "=" * 70 + f"\n[{i}/20] {p['title']}  |  {p['location']}\n{p['url']}")
    lines = [l for l in p["text"].splitlines() if re.search(r"year|experience|SQL|Python|Tableau|Power BI|Excel|dbt|Looker|Snowflake|degree", l, re.I)]
    print("\n".join("  - " + l[:160] for l in lines[:8]) or "  (open the link to read it)")
    v = ""
    while v not in ("r", "n"):
        v = input("relevant for an entry-level BI/data analyst? [r/n]: ").strip().lower()
    r[4] = "relevant" if v == "r" else "not_relevant"
    r[5] = input("short reason: ").strip()
    csv.writer(open("labels/labels.csv", "w", newline="")).writerows([head] + body)
print("\nsaved labels/labels.csv")
