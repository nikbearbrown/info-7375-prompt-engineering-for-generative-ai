import json, sys, html, re
jobs = json.load(open(sys.argv[1]))['jobs']
seen = set(json.load(open(sys.argv[2]))['seen_ids'])
print('total', len(jobs))
for j in jobs:
    if j['id'] in seen:
        continue
    txt = re.sub(r'<[^>]+>', ' ', html.unescape(j.get('content', '')))
    txt = re.sub(r'\s+', ' ', txt)
    print('=' * 80)
    print(j['id'], '|', j['title'], '|', j['location']['name'], '|',
          [d['name'] for d in j.get('departments', [])], '|',
          [o['name'] for o in j.get('offices', [])])
    if len(sys.argv) > 3:
        print(txt)
