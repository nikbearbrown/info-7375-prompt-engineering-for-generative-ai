import json, hashlib, sys, time, urllib.request, urllib.error, datetime as dt
URLS = [
 ("greenhouse","databricks","https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true"),
 ("greenhouse","figma","https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true"),
 ("ashby","notion","https://api.ashbyhq.com/posting-api/job-board/notion"),
 ("ashby","openai","https://api.ashbyhq.com/posting-api/job-board/openai"),
 ("greenhouse","js2-no-such-board-zzz","https://boards-api.greenhouse.io/v1/boards/js2-no-such-board-zzz/jobs?content=true"),
 ("ashby","js2-no-such-board-zzz","https://api.ashbyhq.com/posting-api/job-board/js2-no-such-board-zzz"),
]
out=[]
for prov,b,u in URLS:
    t0=time.monotonic(); r={"provider":prov,"board":b,"url":u,"at_utc":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"js2-recon (INFO 7375 coursework; read-only)","Accept":"application/json"}),timeout=30) as resp:
            body=resp.read(); r["status"]=resp.status; r["final_url"]=resp.geturl(); r["content_type"]=resp.headers.get("Content-Type")
    except urllib.error.HTTPError as e:
        body=e.read(); r["status"]=e.code; r["content_type"]=e.headers.get("Content-Type")
    r["seconds"]=round(time.monotonic()-t0,2); r["bytes"]=len(body); r["sha256"]=hashlib.sha256(body).hexdigest()
    try:
        d=json.loads(body); r["top_keys"]=sorted(d) if isinstance(d,dict) else type(d).__name__
        jobs=d.get("jobs") if isinstance(d,dict) else None
        if isinstance(jobs,list):
            r["n_jobs"]=len(jobs)
            if jobs:
                j=jobs[0]; r["job_keys"]=sorted(j); r["id_type"]=type(j.get("id")).__name__; r["id_sample"]=j.get("id")
                ids=[x.get("id") for x in jobs]; r["ids_unique"]=len(set(map(str,ids)))==len(ids); r["ids_missing"]=sum(i is None for i in ids)
                if "isListed" in j: r["unlisted"]=sum(1 for x in jobs if x.get("isListed") is False)
        if isinstance(d,dict) and "meta" in d: r["meta"]=d["meta"]
    except Exception as e:
        r["json_error"]=str(e)[:80]; r["body_head"]=body[:120].decode("utf-8","replace")
    out.append(r); print(json.dumps(r))
json.dump(out,open(sys.argv[1],"w"),indent=1)
