"""Job-Search Agent 3 command line. Run from this folder:

  python3 -m js3 inherit --js2 <path to js2-loop-tools-diff>   one-off: keep JS2's postings
  python3 -m js3 corpus                                        build data/corpus.jsonl
  python3 -m js3 filter [--filter filter-v1.json]              run the filter, write results/
  python3 -m js3 draw                                          draw the audit and held-out samples
  python3 -m js3 label                                         blind hand-labeling (Shreyash)
  python3 -m js3 audit                                         the reject-audit report
  python3 -m js3 shortlist                                     the source-grounded shortlist
  python3 -m js3 serve                                         the MCP tool server (stdio)

Nothing here uses the network except `python3 -m jsagent run` (the JS2 loop) and the Claude runs
in js3/judge.py and js3/offer.py, which call the local `claude` CLI."""
import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
JS2_RUNS = ["20261110T002501Z", "20261110T011708Z", "20261110T204749Z"]


def live_runs():
    return sorted(p for p in (HERE / "runs").iterdir() if p.is_dir() and (p / "summary.json").exists()
                  and p.name[:8].isdigit())


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python3 -m js3")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("inherit")
    a.add_argument("--js2", required=True)
    sub.add_parser("corpus")
    f = sub.add_parser("filter")
    f.add_argument("--filter", default="filter-v1.json")
    f.add_argument("--out", default=None)
    for name in ("draw", "label", "audit", "shortlist", "serve"):
        s = sub.add_parser(name)
        s.add_argument("rest", nargs=argparse.REMAINDER)
    args, unknown = ap.parse_known_args(argv)
    if unknown and args.cmd not in ("draw", "label", "audit", "shortlist", "serve"):
        ap.error(f"unrecognized arguments: {' '.join(unknown)}")

    from js3 import corpus, filtering
    if args.cmd == "inherit":
        latest = corpus.read_run(live_runs()[-1])
        keys = {f"{p['board']}:{p['id']}" for p in latest["postings"]}
        rec = corpus.inherit_js2(args.js2, JS2_RUNS, keys)
        out = HERE / "data" / "inherited" / "js2-postings.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rec, ensure_ascii=False, indent=0) + "\n")
        print(f"wrote {out.relative_to(HERE)}: {len(rec['seen'])} JS2 postings seen, "
              f"{len(rec['jobs_not_in_latest_run'])} not in the latest run {latest['run_id']}")
        return 0
    if args.cmd == "corpus":
        inherited = json.loads((HERE / "data" / "inherited" / "js2-postings.json").read_text())
        postings, manifest = corpus.build(live_runs(), inherited)
        manifest = corpus.write(postings, manifest, HERE / "data")
        print(f"wrote data/corpus.jsonl: {manifest['postings']} postings, {manifest['open_in_latest_run']} open in "
              f"{manifest['latest_run']}; by board {manifest['by_board']}")
        for line in corpus.board_report(manifest):
            print("  " + line)
        return 0
    if args.cmd == "filter":
        cfg = filtering.load_config(HERE / args.filter)
        persona = json.loads((HERE / "persona" / "alex_morgan.json").read_text())
        postings = corpus.load()
        manifest = json.loads((HERE / "data" / "corpus-manifest.json").read_text())
        result = filtering.run(postings, manifest, persona, cfg)
        bad = [(r["key"], pr) for r, p in zip(result["records"], postings) for pr in filtering.verify_quotes(r, p)]
        out = HERE / (args.out or f"results/filter-{cfg['version']}")
        out.mkdir(parents=True, exist_ok=True)
        with open(out / "records.jsonl", "w", encoding="utf-8") as fh:
            for r in result["records"]:
                fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
        summary = {k: v for k, v in result.items() if k != "records"}
        summary["corpus_sha256"] = manifest.get("corpus_sha256")
        summary["quote_problems"] = len(bad)
        (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
        print(f"filter {cfg['version']}: {result['counts']}; quotes not found in the posting: {len(bad)}")
        for name, b in result["boards"].items():
            print(f"  {name}: {b}")
        return 1 if bad else 0
    from js3 import cli_more
    return cli_more.dispatch(args.cmd, unknown + list(args.rest))


if __name__ == "__main__":
    sys.exit(main())
