"""Source-selection probe for JS3 (not an agent run). One GET per candidate board, public ATS APIs only.

Selection rule, fixed before any result is seen (2026-11-18):
- A title is RELEVANT if it has a role phrase (data / BI / business intelligence / business / reporting /
  analytics analyst), no seniority word, and a location that looks like the US (or US remote).
- RELEVANT boards: every board with >= 1 relevant title, ranked by relevant-title count, then by bare-analyst
  count; keep the top 22.
- CONTRAST boards: JS2's three (abacusinsights, valon, xsolla), plus the 5 boards with zero relevant titles
  and the most bare-"analyst" titles.
- Total at most 30; every system must appear.
Writes one JSON summary (counts and matched titles only, no descriptions).
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request

GREENHOUSE = """abacusinsights cloudflare hellofresh affirm mongodb gusto toast klaviyo robinhood instacart duolingo
squarespace lyft flatironhealth sofi chime zocdoc coursera databricks hubspotjobs airbnb stripe coinbase dropbox twilio
pinterest reddit discord peloton warbyparker seatgeek betterment wealthfront marqeta carta gemini brex upstart oscar
headway springhealth lyrahealth devotedhealth cityblockhealth komodohealth tempus faire stitchfix renttherunway datadog
asana airtable gitlab okta elastic confluent amplitude mixpanel fivetran dbtlabsinc sigmacomputing thoughtspot voxmedia
guild hopper riotgames roblox flexport samsara rapid7 simplisafe formlabs figma anthropic gopuff poshmark chegg
masterclass noom calm headspace lemonade ziprecruiter yext bombas everlane casper""".split()
ASHBY = "valon ramp notion linear openai vercel replit posthog supabase hightouch retool deel zapier rippling lattice".split()
LEVER = "xsolla palantir spotify veeva eventbrite outreach quizlet highspot attentive kraken yelp zoox mindbody shieldai".split()

URL = {"greenhouse": "https://boards-api.greenhouse.io/v1/boards/{}/jobs",
       "ashby": "https://api.ashbyhq.com/posting-api/job-board/{}",
       "lever": "https://api.lever.co/v0/postings/{}?mode=json"}
ROLE = re.compile(r"\b(data|bi|business intelligence|business|reporting|analytics)\s+analyst\b", re.I)
ANALYST = re.compile(r"\banalyst\b", re.I)
SENIOR = re.compile(r"\b(senior|sr|lead|principal|staff|manager|director|head|vp|vice president|chief)\b", re.I)
STATES = ("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH "
          "OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split()
US = re.compile(r"United States|\bUSA?\b|\bU\.S\.|\bAmericas?\b|New York|San Francisco|Boston|Chicago|Seattle|Austin|"
                r"Denver|Los Angeles|Atlanta|Washington|Miami|Philadelphia|\b(" + "|".join(STATES) + r")\b")


def postings(system, data):
    if system == "greenhouse":
        return [(j.get("title", ""), (j.get("location") or {}).get("name", "")) for j in data.get("jobs", [])]
    if system == "ashby":
        out = []
        for j in data.get("jobs", []):
            country = (((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry") or "")
            out.append((j.get("title", ""), f"{j.get('location', '')} {country}".strip()))
        return out
    return [(j.get("text", ""), f"{(j.get('categories') or {}).get('location', '')} {j.get('country') or ''}".strip())
            for j in data]


results = []
for system, names in (("greenhouse", GREENHOUSE), ("ashby", ASHBY), ("lever", LEVER)):
    for token in names:
        row = {"system": system, "token": token}
        try:
            req = urllib.request.Request(URL[system].format(token), headers={"User-Agent": "coursework-probe"})
            with urllib.request.urlopen(req, timeout=25) as r:
                jobs = postings(system, json.loads(r.read()))
        except urllib.error.HTTPError as e:
            row["error"] = f"HTTP {e.code}"
        except Exception as e:  # noqa: BLE001 - a probe records the failure and moves on
            row["error"] = type(e).__name__
        else:
            relevant = [(t, l) for t, l in jobs if ROLE.search(t) and not SENIOR.search(t) and US.search(l)]
            bare = [t for t, _ in jobs if ANALYST.search(t) and not ROLE.search(t)]
            row.update(postings=len(jobs), relevant=len(relevant), bare_analyst=len(bare),
                       relevant_titles=[f"{t} | {l}" for t, l in relevant])
        results.append(row)
        print(f"{system}/{token}: " + (row.get("error") or f"{row['postings']} postings, {row['relevant']} relevant, "
                                       f"{row['bare_analyst']} bare analyst"), flush=True)
        time.sleep(0.3)

live = [r for r in results if "error" not in r]
js2 = {("greenhouse", "abacusinsights"), ("ashby", "valon"), ("lever", "xsolla")}
rel = sorted([r for r in live if r["relevant"] > 0 and (r["system"], r["token"]) not in js2],
             key=lambda r: (-r["relevant"], -r["bare_analyst"], r["token"]))[:22]
contrast = sorted([r for r in live if r["relevant"] == 0 and (r["system"], r["token"]) not in js2],
                  key=lambda r: (-r["bare_analyst"], r["token"]))[:5]
pick = [r for r in live if (r["system"], r["token"]) in js2] + contrast + rel
json.dump({"probed": time.strftime("%Y-%m-%d"), "candidates": len(results), "live": len(live),
           "picked": [f"{r['system']}/{r['token']}" for r in pick], "results": results},
          open(sys.argv[1], "w"), indent=1)
print(f"\ncandidates {len(results)}, live {len(live)}, with >=1 relevant {sum(r['relevant'] > 0 for r in live)}")
print("PICKED:", len(pick), "systems:", sorted({r['system'] for r in pick}))
for r in pick:
    tag = "JS2" if (r["system"], r["token"]) in js2 else ("contrast" if r["relevant"] == 0 else "relevant")
    print(f"  {tag:8} {r['system']}/{r['token']}: {r['postings']} postings, {r['relevant']} relevant, {r['bare_analyst']} bare")
    for t in r["relevant_titles"][:4]:
        print(f"           - {t}")
