"""FILTER.md v1.1 supplement-board probe (not an agent run). One GET per candidate board, public ATS APIs only.

    python3 probe/probe_v1_1.py probe/2026-11-25_board_probe_v1_1.json

The rule is FILTER.md v1.1, "v1.1 supplement boards", fixed and committed before this script ran. A posting is
a CANDIDATE when: its title has "analyst"; its title has no seniority word; at least one location is in the US;
its text has an early-career signal or a lowest stated required years of 2 or less; and its text has no refusal
to sponsor. Boards with >= 1 candidate are ranked by candidate count and the top 15 are picked.

It reads full posting text through the collector's own adapters, but saves only counts and matched titles.
No candidate here was among the 116 boards of the 2026-11-18 probe.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adapters  # noqa: E402

GREENHOUSE = """doordashusa etsy grubhub vimeo bumble hinge twitch niantic epicgames scopely applovin tripadvisor kayak
glossier allbirds sweetgreen ro hims nomihealth includedhealth capsule carbonhealth addepar blend dave varo acorns
stash civisanalytics morningconsult numerator fanduel prizepicks khanacademy joinhandshake nextdoor quora medium
substack patreon kickstarter gofundme intercom braze iterable pendo fullstory sproutsocial buzzfeed axios politico
nytimes compass opendoor redfin creditkarma block nubank payoneer ripple circle anchorage chainalysis fireblocks
alchemy consensys galaxydigital hudsonrivertrading twosigma akunacapital imc peak6 cloverhealth brightline talkspace
hingehealth omadahealth virtahealth garnerhealth transcarent swordhealth datavant thredup therealreal stockx goat
shipt via turo vroom thetradedesk taboola outbrain magnite pubmatic liveramp doubleverify integralads innovid
madhive mntn thoughtworks zynga playtika jamcity fanatics betmgm outschool newsela nerdy bluecore yotpo postscript
zoominfo gong clari seismic salesloft 6sense demandbase g2 sprinklr qualtrics medallia typeform calendly miro
clickup smartsheet wrike box freshworks servicetitan procore olo bigcommerce webflow scaleai gleanwork anduril
cockroachlabs flatiron pathward lendingclub oportun mission-lane""".split()
ASHBY = """airwallex runway harvey perplexity anysphere elevenlabs modal sierra decagon writer jasper hebbia abridge
ambiencehealthcare kalshi polymarket public wealthsimple mercor clay attio ashby cohere mistral pinecone""".split()
LEVER = """canva atlassian tala greenlight nuro appliedintuition matterport neo4j dremio imply bloomreach jumpcloud
pagerduty lucidmotors aurora metabase cars weride rover hive brillio tigeranalytics fractal quantiphi sigmoid""".split()

ANALYST = re.compile(r"\banalyst\b", re.I)
DATA_WORD = re.compile(r"\b(data|analytics|insights|reporting|bi|metrics)\b", re.I)
ROLE = re.compile(r"\b(data analyst|bi analyst|business intelligence analyst|business analyst|reporting analyst|"
                  r"analytics analyst)\b", re.I)
SENIOR = re.compile(r"\b(senior|sr|lead|principal|staff|manager|director|head|vp|vice president|chief)\b", re.I)
STATE_NAMES = ("Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware Florida Georgia Hawaii Idaho "
               "Illinois Indiana Iowa Kansas Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota "
               "Mississippi Missouri Montana Nebraska Nevada Ohio Oklahoma Oregon Pennsylvania Tennessee Texas Utah "
               "Vermont Virginia Washington Wisconsin Wyoming").split() + [
    "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Rhode Island",
    "South Carolina", "South Dakota", "West Virginia", "District of Columbia"]
CODES = ("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH "
         "OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split()
US = re.compile(r"\bUnited States\b|\bUSA\b|\bU\.S\.|\bUS\b|\b(" + "|".join(STATE_NAMES) + r")\b|, (" +
                "|".join(CODES) + r")\b|\b(US|U\.S\.|USA)[- ]?remote\b|\bremote[^,;]{0,12}\b(US|USA|U\.S\.)\b")
US_COUNTRY = {"us", "usa", "united states", "united states of america"}
EARLY = re.compile(r"\bentry[- ]level\b|\bnew grad(uate)?s?\b|\brecent (college |university )?grad(uate)?s?\b|"
                   r"\bearly[- ]career\b|\buniversity grad(uate)?s?\b|\b[01]\s*[-–to]+\s*2\+? years\b|"
                   r"\bup to 2 years\b", re.I)
YEARS = re.compile(r"\b(\d{1,2})\s*(?:\+|[-–]\s*\d{1,2}|to \d{1,2})?\+?\s*years?\b(?: of)?[^.\n]{0,40}"
                   r"\b(experience|exp)\b", re.I)
NO_SPONSOR = re.compile(r"unable to sponsor|will not sponsor|does not sponsor|no visa sponsorship|"
                        r"without sponsorship now or in the future|does not provide sponsorship|"
                        r"not able to sponsor|cannot sponsor|unable to provide sponsorship", re.I)


def is_us(p):
    if (p.get("country") or "").strip().lower() in US_COUNTRY:
        return True
    return any(US.search(loc or "") for loc in (p.get("locations") or [p.get("location")]))


def lowest_years(text):
    nums = [int(m.group(1)) for m in YEARS.finditer(text)]
    return min(nums) if nums else None


def candidate(p):
    title, text = p["title"] or "", p["text"] or ""
    if not (ROLE.search(title) or (ANALYST.search(title) and DATA_WORD.search(title))) or SENIOR.search(title) or not is_us(p) or NO_SPONSOR.search(text):
        return False
    low = lowest_years(text)
    return bool(EARLY.search(text)) or (low is not None and low <= 2)


def probe(system, token):
    row = {"system": system, "token": token}
    board = {"system": system, "token": token}
    try:
        req = urllib.request.Request(adapters.board_url(board), headers={"User-Agent": "coursework-probe"})
        with urllib.request.urlopen(req, timeout=40) as r:
            jobs = adapters.parse(board, r.read())
    except urllib.error.HTTPError as e:
        row["error"] = f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001 - a probe records the failure and moves on
        row["error"] = type(e).__name__
    else:
        cands = [p for p in jobs if candidate(p)]
        row.update(postings=len(jobs), candidates=len(cands),
                   role_phrase=sum(bool(ROLE.search(p["title"] or "")) for p in jobs),
                   candidate_titles=[f"{p['title']} | {p['location']}" for p in cands])
    return row


def main(out):
    tasks = [(s, t) for s, names in (("greenhouse", GREENHOUSE), ("ashby", ASHBY), ("lever", LEVER)) for t in names]
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda a: probe(*a), tasks))
    for r in results:
        print(f"{r['system']}/{r['token']}: " + (r.get("error") or f"{r['postings']} postings, "
                                                 f"{r['candidates']} candidates"))
    live = [r for r in results if "error" not in r]
    pick = sorted([r for r in live if r["candidates"] > 0], key=lambda r: (-r["candidates"], r["token"]))[:15]
    with open(out, "w") as f:
        json.dump({"probed": time.strftime("%Y-%m-%d"), "rule": "FILTER.md v1.1, 'v1.1 supplement boards'",
                   "candidates": len(results), "live": len(live),
                   "picked": [f"{r['system']}/{r['token']}" for r in pick], "results": results}, f, indent=1)
    print(f"\nboards {len(results)}, live {len(live)}, with >=1 candidate {sum(r['candidates'] > 0 for r in live)}")
    for r in pick:
        print(f"  {r['system']}/{r['token']}: {r['postings']} postings, {r['candidates']} candidates")
        for t in r["candidate_titles"][:6]:
            print(f"     - {t}")


if __name__ == "__main__":
    main(sys.argv[1])
