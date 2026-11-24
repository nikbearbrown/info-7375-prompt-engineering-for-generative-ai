# G1 decide commands for runs/live-2026-11-23 - generated from proposals.json on 2026-11-23
# Open each link BEFORE deciding. Replace CHOOSE with approve, refuse or defer.
# A line left as CHOOSE is rejected (invalid choice) and records nothing.
# Optional: add  --note "why"  at the end of a line.

cd "C:/Users/Akshit Verma/PromptEngr/Assignment_Final Project Film v2/board-resolver"
$r = "runs/live-2026-11-23"; $me = "Akshit Verma"

# ===== GROUP 1 - exact name match on Greenhouse (you reviewed these and chose approve) (13) =====

# ANAPLAN INC | https://boards.greenhouse.io/anaplan | name-match: 'Anaplan'
python resolver.py decide --run $r --company "ANAPLAN INC" --ats greenhouse --slug anaplan --decision approve --by $me --seen-sha256 c50b5646d54e

# CHARGEPOINT INC | https://boards.greenhouse.io/chargepoint | name-match: 'ChargePoint'
python resolver.py decide --run $r --company "CHARGEPOINT INC" --ats greenhouse --slug chargepoint --decision approve --by $me --seen-sha256 016b13e1befa

# DV01 INC | https://boards.greenhouse.io/dv01 | name-match: 'dv01'
python resolver.py decide --run $r --company "DV01 INC" --ats greenhouse --slug dv01 --decision approve --by $me --seen-sha256 55af151a04e1

# ECLINICAL SOLUTIONS LLC | https://boards.greenhouse.io/eclinicalsolutions | name-match: 'eClinical Solutions'
python resolver.py decide --run $r --company "ECLINICAL SOLUTIONS LLC" --ats greenhouse --slug eclinicalsolutions --decision approve --by $me --seen-sha256 41ec032ca893

# ENTRUPY INC | https://boards.greenhouse.io/entrupy | name-match: 'Entrupy'
python resolver.py decide --run $r --company "ENTRUPY INC" --ats greenhouse --slug entrupy --decision approve --by $me --seen-sha256 52918b6964b6

# EXABEAM INC | https://boards.greenhouse.io/exabeam | name-match: 'Exabeam'
python resolver.py decide --run $r --company "EXABEAM INC" --ats greenhouse --slug exabeam --decision approve --by $me --seen-sha256 eb823d86924e

# HAPPY MONEY INC | https://boards.greenhouse.io/happymoney | name-match: 'Happy Money'
python resolver.py decide --run $r --company "HAPPY MONEY INC" --ats greenhouse --slug happymoney --decision approve --by $me --seen-sha256 6a837502c12d

# SENDBIRD INC | https://boards.greenhouse.io/sendbird | name-match: 'Sendbird'
python resolver.py decide --run $r --company "SENDBIRD INC" --ats greenhouse --slug sendbird --decision approve --by $me --seen-sha256 e40389168eef

# SOCIAL FINANCE INC | https://boards.greenhouse.io/socialfinance | name-match: 'Social Finance'
python resolver.py decide --run $r --company "SOCIAL FINANCE INC" --ats greenhouse --slug socialfinance --decision approve --by $me --seen-sha256 d1565c53eda5

# VERACYTE INC | https://boards.greenhouse.io/veracyte | name-match: 'Veracyte'
python resolver.py decide --run $r --company "VERACYTE INC" --ats greenhouse --slug veracyte --decision approve --by $me --seen-sha256 5a657346ae51

# WELBE HEALTH LLC | https://boards.greenhouse.io/welbehealth | name-match: 'WelbeHealth'
python resolver.py decide --run $r --company "WELBE HEALTH LLC" --ats greenhouse --slug welbehealth --decision approve --by $me --seen-sha256 a9743c48ad85

# YEXT INC | https://boards.greenhouse.io/yext | name-match: 'Yext'
python resolver.py decide --run $r --company "YEXT INC" --ats greenhouse --slug yext --decision approve --by $me --seen-sha256 8b62492e7be9

# YIELDMO INC | https://boards.greenhouse.io/yieldmo | name-match: 'Yieldmo'
python resolver.py decide --run $r --company "YIELDMO INC" --ats greenhouse --slug yieldmo --decision approve --by $me --seen-sha256 e8c15b1b9893

# ===== GROUP 2 - Greenhouse board, name only partly matches (7) =====

# CREDIBLE LABS INC | https://boards.greenhouse.io/credible | name-partial: 'Credible'
python resolver.py decide --run $r --company "CREDIBLE LABS INC" --ats greenhouse --slug credible --decision CHOOSE --by $me --seen-sha256 12eca6be3ae9

# GEMINI SPACE STATION LLC | https://boards.greenhouse.io/gemini | name-partial: 'Gemini' | NOTE: check it is Gemini the crypto exchange
python resolver.py decide --run $r --company "GEMINI SPACE STATION LLC" --ats greenhouse --slug gemini --decision CHOOSE --by $me --seen-sha256 20b2ff0a6a4b

# INMARKET MEDIA LLC | https://boards.greenhouse.io/inmarket | name-partial: 'InMarket'
python resolver.py decide --run $r --company "INMARKET MEDIA LLC" --ats greenhouse --slug inmarket --decision CHOOSE --by $me --seen-sha256 191903e761de

# KIZEN TECHNOLOGIES INC | https://boards.greenhouse.io/kizen | name-partial: 'Kizen'
python resolver.py decide --run $r --company "KIZEN TECHNOLOGIES INC" --ats greenhouse --slug kizen --decision CHOOSE --by $me --seen-sha256 e20a3137a467

# PROVE IDENTITY INC | https://boards.greenhouse.io/prove | name-partial: 'Prove'
python resolver.py decide --run $r --company "PROVE IDENTITY INC" --ats greenhouse --slug prove --decision CHOOSE --by $me --seen-sha256 691d4ecbdab6

# TALENT INC | https://boards.greenhouse.io/talent | name-partial: 'Slice Talent Community' | NOTE: board is 'Slice Talent Community' - probably a different company
python resolver.py decide --run $r --company "TALENT INC" --ats greenhouse --slug talent --decision CHOOSE --by $me --seen-sha256 86d2a8655763

# VILLAGE PRACTICE MANAGEMENT COMPANY LLC | https://boards.greenhouse.io/village | name-partial: 'The Village Learning Center' | NOTE: board is 'The Village Learning Center' - probably a different company
python resolver.py decide --run $r --company "VILLAGE PRACTICE MANAGEMENT COMPANY LLC" --ats greenhouse --slug village --decision CHOOSE --by $me --seen-sha256 78859ae467d7

# ===== GROUP 3 - Lever/Ashby board with postings (these APIs give no company name) (13) =====

# AUTOFI INC | https://jobs.lever.co/autofi | exists-no-name: 5 postings
python resolver.py decide --run $r --company "AUTOFI INC" --ats lever --slug autofi --decision CHOOSE --by $me --seen-sha256 7307d5af83b0

# CLARIFY HEALTH SOLUTIONS INC | https://jobs.lever.co/clarifyhealth | exists-no-name: 3 postings
python resolver.py decide --run $r --company "CLARIFY HEALTH SOLUTIONS INC" --ats lever --slug clarifyhealth --decision CHOOSE --by $me --seen-sha256 b7082d6d0ea7

# DISQO INC | https://jobs.lever.co/disqo | exists-no-name: 3 postings
python resolver.py decide --run $r --company "DISQO INC" --ats lever --slug disqo --decision CHOOSE --by $me --seen-sha256 92b70462461f

# HINGE HEALTH INC | https://jobs.ashbyhq.com/hinge-health | exists-no-name: 89 postings
python resolver.py decide --run $r --company "HINGE HEALTH INC" --ats ashby --slug hinge-health --decision CHOOSE --by $me --seen-sha256 6d778568c0ff

# HUMAN INC | https://jobs.ashbyhq.com/human | exists-no-name: 10 postings | NOTE: slug is a common word - check it is HUMAN the company
python resolver.py decide --run $r --company "HUMAN INC" --ats ashby --slug human --decision CHOOSE --by $me --seen-sha256 1dbc41208886

# LEANTAAS INC | https://jobs.lever.co/leantaas | exists-no-name: 2 postings
python resolver.py decide --run $r --company "LEANTAAS INC" --ats lever --slug leantaas --decision CHOOSE --by $me --seen-sha256 d1d7dd6607da

# MUTINY HQ CORP | https://jobs.ashbyhq.com/mutiny | exists-no-name: 7 postings
python resolver.py decide --run $r --company "MUTINY HQ CORP" --ats ashby --slug mutiny --decision CHOOSE --by $me --seen-sha256 4a351beff7b2

# PLUME DESIGN INC | https://jobs.lever.co/plume | exists-no-name: 1 postings | NOTE: slug is a common word - check carefully
python resolver.py decide --run $r --company "PLUME DESIGN INC" --ats lever --slug plume --decision CHOOSE --by $me --seen-sha256 c6b6f89b91db

# RISE INTERACTIVE MEDIA & ANALYTICS LLC | https://jobs.lever.co/rise | exists-no-name: 20 postings | NOTE: slug is a common word - check carefully
python resolver.py decide --run $r --company "RISE INTERACTIVE MEDIA & ANALYTICS LLC" --ats lever --slug rise --decision CHOOSE --by $me --seen-sha256 9a9f1ee6428b

# SAIL INTERNET INC | https://jobs.ashbyhq.com/sail | exists-no-name: 8 postings | NOTE: slug is a common word - check carefully
python resolver.py decide --run $r --company "SAIL INTERNET INC" --ats ashby --slug sail --decision CHOOSE --by $me --seen-sha256 10a1153a8f97

# SILA NANOTECHNOLOGIES INC | https://jobs.lever.co/sila | exists-no-name: 216 postings
python resolver.py decide --run $r --company "SILA NANOTECHNOLOGIES INC" --ats lever --slug sila --decision CHOOSE --by $me --seen-sha256 2cf1a2f0d04c

# SOFAR SOUNDS LTD | https://jobs.lever.co/sofarsounds | exists-no-name: 10 postings
python resolver.py decide --run $r --company "SOFAR SOUNDS LTD" --ats lever --slug sofarsounds --decision CHOOSE --by $me --seen-sha256 8b7c8546d55d

# WATERSHED TECHNOLOGY INC | https://jobs.ashbyhq.com/watershed | exists-no-name: 40 postings
python resolver.py decide --run $r --company "WATERSHED TECHNOLOGY INC" --ats ashby --slug watershed --decision CHOOSE --by $me --seen-sha256 431542cc1d69

# ===== GROUP 4 - board exists but has 0 postings (5) =====

# AFFINITY SOLUTIONS INC | https://jobs.ashbyhq.com/affinity | exists-empty: 0 postings
python resolver.py decide --run $r --company "AFFINITY SOLUTIONS INC" --ats ashby --slug affinity --decision CHOOSE --by $me --seen-sha256 03e836a65ca1

# DOCUSIGN INC | https://jobs.lever.co/docusign | exists-empty: 0 postings
python resolver.py decide --run $r --company "DOCUSIGN INC" --ats lever --slug docusign --decision CHOOSE --by $me --seen-sha256 4f53cda18c2b

# FRESHWORKS INC | https://jobs.lever.co/freshworks | exists-empty: 0 postings
python resolver.py decide --run $r --company "FRESHWORKS INC" --ats lever --slug freshworks --decision CHOOSE --by $me --seen-sha256 4f53cda18c2b

# LUA TECHNOLOGIES INC | https://jobs.ashbyhq.com/lua | exists-empty: 0 postings
python resolver.py decide --run $r --company "LUA TECHNOLOGIES INC" --ats ashby --slug lua --decision CHOOSE --by $me --seen-sha256 03e836a65ca1

# ZANBATO INC | https://jobs.ashbyhq.com/zanbato | exists-empty: 0 postings
python resolver.py decide --run $r --company "ZANBATO INC" --ats ashby --slug zanbato --decision CHOOSE --by $me --seen-sha256 03e836a65ca1

# ===== GROUP 5 - Greenhouse board with a different name (1) =====

# WW INTERNATIONAL INC | https://boards.greenhouse.io/ww | name-mismatch: 'Weight Watchers' | NOTE: board is 'Weight Watchers' - names differ, but WW International is the Weight Watchers company
python resolver.py decide --run $r --company "WW INTERNATIONAL INC" --ats greenhouse --slug ww --decision CHOOSE --by $me --seen-sha256 4622002e2920

# ===== then the real number =====
python resolver.py coverage --run $r
