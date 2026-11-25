"""JS3 subcommands of `python -m jobwatch` (one entry point; cli.main dispatches here).

Each command builds its own Policy naming exactly the folders it may read and write, and does
every disk access through jobwatch/tools.py.

    dataset --run runs/<run-id>        reads runs/; writes data/
    heldout --dataset <jsonl> --seed-a N --seed-b M
                                       reads data/, labels/; writes labels/heldout.csv, data/texts/
    label [--clear|--checklist|--family] <csv>
                                       reads labels/, audit/, shortlist/, data/; writes the csv's folder
    filter --dataset <jsonl> --version v1
                                       reads data/; writes data/filter-<version>.jsonl
    audit-sheet --dataset <jsonl> --filter <jsonl> --seed N --heldout-seed-a A --heldout-seed-b B
                                       reads data/; writes audit/audit-<version>.csv, data/texts/
    audit-append-near --dataset <jsonl> --filter <jsonl> --sheet <csv> --heldout-seed-a A --heldout-seed-b B
                                       reads data/, audit/; rewrites the sheet with the near-decision rows appended
    audit-stats --sheet <csv> --filter <jsonl> --dataset <jsonl>
                                       reads data/, audit/; writes audit/<sheet>-stats.json and -facts.md
    measure-change --change C1 --sheet <csv> --dataset <jsonl>
                                       reads data/, audit/; writes audit/changes/<change>.json and .md
    shortlist --dataset <jsonl> --filter <jsonl> [--model M]
                                       reads data/, prompts/; writes shortlist/, data/texts/; calls the Claude judge
    mcp-probe                          stdio stub; logs what a client sends to evidence/mcp/probe/; never replies
    mcp-server --dataset <jsonl> [--version v1]
                                       MCP 2026-07-28 stdio server; reads data/, runs/; writes evidence/mcp/transcripts/
    experiment-filter | experiment-judge --arm A --run N | experiment-report
        (each: --dataset <jsonl> --heldout-seed-a A --heldout-seed-b B)
                                       Phase 6; only experiment-report reads labels/heldout.csv
"""
import argparse
import os
import sys

from jobwatch.policy import Policy
from jobwatch.tools import Tools

JS3_COMMANDS = ("dataset", "heldout", "label", "filter", "audit-sheet", "audit-append-near", "audit-stats", "measure-change", "shortlist", "mcp-probe", "mcp-server", "experiment-filter", "experiment-judge", "experiment-report")
LABEL_FOLDERS = ("labels", "audit", "shortlist")


def tools_for(read_dirs, write_dirs=(), root=None, **kw):
    return Tools(Policy(root or os.getcwd(), read_dirs=read_dirs, write_dirs=write_dirs), **kw)


def build_parser():
    parser = argparse.ArgumentParser(prog="python -m jobwatch", description="JS3 commands")
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("dataset", help="build data/postings-<run-id>.jsonl from a committed run")
    d.add_argument("--run", required=True, help="runs/<run-id>")
    h = sub.add_parser("heldout", help="draw the sealed held-out set (FILTER.md section 7), once")
    h.add_argument("--dataset", required=True)
    h.add_argument("--seed-a", type=int, required=True)
    h.add_argument("--seed-b", type=int, required=True)
    lb = sub.add_parser("label", help="label a sheet by hand, one row at a time (Deepak runs this)")
    lb.add_argument("csv")
    lb.add_argument("--clear", action="store_true", help="empty the answer and reason columns (asks to confirm)")
    lb.add_argument("--checklist", action="store_true", help="answer the three FILTER.md section 0 checks per row")
    lb.add_argument("--family", action="store_true", help="seniority and location applied mechanically; asks job family (and experience)")
    f = sub.add_parser("filter", help="run a filter version on every posting of a dataset (FILTER.md sections 1-4)")
    f.add_argument("--dataset", required=True)
    f.add_argument("--version", default="v1")
    a = sub.add_parser("audit-sheet", help="draw the reject-audit sample of one filter output, once")
    a.add_argument("--dataset", required=True)
    a.add_argument("--filter", required=True)
    a.add_argument("--seed", type=int, required=True)
    a.add_argument("--heldout-seed-a", type=int, required=True)
    a.add_argument("--heldout-seed-b", type=int, required=True)
    an = sub.add_parser("audit-append-near", help="append the near-decision group to an audit sheet, once")
    an.add_argument("--dataset", required=True)
    an.add_argument("--filter", required=True)
    an.add_argument("--sheet", required=True)
    an.add_argument("--heldout-seed-a", type=int, required=True)
    an.add_argument("--heldout-seed-b", type=int, required=True)
    st = sub.add_parser("audit-stats", help="facts from the audit verdicts (errors, interval, overrides, false-friend candidates)")
    st.add_argument("--sheet", required=True)
    st.add_argument("--filter", required=True)
    st.add_argument("--dataset", required=True)
    mc = sub.add_parser("measure-change", help="measure one candidate rule change on the audit rows only")
    mc.add_argument("--change", required=True)
    mc.add_argument("--sheet", required=True)
    mc.add_argument("--dataset", required=True)
    sl = sub.add_parser("shortlist", help="the source-grounded shortlist and shortlist/claims.csv (calls the Claude judge)")
    sl.add_argument("--dataset", required=True)
    sl.add_argument("--filter", required=True)
    sl.add_argument("--model", default=None)
    sub.add_parser("mcp-probe", help="stdio stub that records what a client sends on connect (never replies)")
    ms = sub.add_parser("mcp-server", help="the score_posting tool server (MCP 2026-07-28, stdio)")
    ms.add_argument("--dataset", required=True)
    ms.add_argument("--version", default="v1")
    for name in ("experiment-filter", "experiment-judge", "experiment-report"):
        ex = sub.add_parser(name, help="Phase 6 (see jobwatch/experiments.py)")
        ex.add_argument("--dataset", required=True)
        ex.add_argument("--heldout-seed-a", type=int, required=True)
        ex.add_argument("--heldout-seed-b", type=int, required=True)
        if name == "experiment-judge":
            ex.add_argument("--arm", required=True, choices=("title_text", "title_only"))
            ex.add_argument("--run", type=int, required=True)
            ex.add_argument("--model", default=None)
    return parser


def cmd_dataset(args):
    from jobwatch import dataset

    tools = tools_for(read_dirs=("runs",), write_dirs=("data",))
    lines, meta = dataset.build(tools, args.run)
    path = dataset.write(tools, lines, meta)
    flagged = sum(s["boilerplate"] for ln in lines for s in ln["sentences"])
    total = sum(len(ln["sentences"]) for ln in lines)
    print(f"dataset: {path}: {meta['postings']} postings from run {meta['run_id']} "
          f"(failed boards: {', '.join(meta['failed_boards']) or 'none'}); "
          f"{flagged} of {total} body sentences flagged boilerplate")
    return 0


def _run_id_of(dataset_path):
    name = os.path.basename(dataset_path)
    if not (name.startswith("postings-") and name.endswith(".jsonl")):
        raise ValueError("dataset must be data/postings-<run-id>.jsonl")
    return name[len("postings-"):-len(".jsonl")]


def cmd_heldout(args):
    from jobwatch import heldout

    tools = tools_for(read_dirs=("data", "labels"), write_dirs=("labels/heldout.csv", "data/texts"))
    sizes, rows = heldout.run(tools, args.dataset, {"A": args.seed_a, "B": args.seed_b}, _run_id_of(args.dataset))
    print(f"heldout: {heldout.SHEET}: {len(rows)} rows; stratum A pool {sizes['A']} (seed {args.seed_a}), "
          f"stratum B pool {sizes['B']} (seed {args.seed_b})")
    return 0


def cmd_label(args):
    from jobwatch import label

    folder = os.path.dirname(os.path.normpath(args.csv))
    if folder not in LABEL_FOLDERS:
        raise ValueError(f"label: the sheet must be directly in one of {', '.join(LABEL_FOLDERS)}")
    tools = tools_for(read_dirs=("labels", "audit", "shortlist", "data"), write_dirs=(folder,), allow_rewrite=True)
    return label.clear(tools, args.csv) if args.clear else label.run(tools, args.csv, checklist=args.checklist, family=args.family)


def _load_dataset(tools, dataset_path):
    import json

    from jobwatch import dataset

    meta = json.loads(tools.read_file(dataset_path[:-len(".jsonl")] + ".meta.json").decode("utf-8"))
    return dataset.load(tools, dataset_path), meta


def cmd_filter(args):
    import json

    from jobwatch import filter as flt

    _run_id_of(args.dataset)
    tools = tools_for(read_dirs=("data",), write_dirs=(f"data/filter-{args.version}.jsonl",))
    lines, meta = _load_dataset(tools, args.dataset)
    outs = flt.run(lines, meta, flt.VERSIONS[args.version])
    body = "".join(json.dumps(o, ensure_ascii=False, sort_keys=True) + "\n" for o in outs)
    tools.write_file(f"data/filter-{args.version}.jsonl", body.encode("utf-8"))
    counts = {}
    for o in outs:
        counts[o["decision"]] = counts.get(o["decision"], 0) + 1
    posts = [o for o in outs if o.get("scope") != "board"]
    print(f"filter {args.version}: data/filter-{args.version}.jsonl: {len(posts)} postings: "
          f"keep {sum(o['decision'] == 'keep' for o in posts)}, reject {sum(o['decision'] == 'reject' for o in posts)}, "
          f"abstain {sum(o['decision'] == 'abstain' for o in posts)}; failed boards (abstain, once each): "
          f"{len(outs) - len(posts)}")
    return 0


def _load_jsonl(tools, path):
    import json

    return [json.loads(x) for x in tools.read_file(path).decode("utf-8").splitlines() if x.strip()]


def cmd_audit_sheet(args):
    from jobwatch import audit

    run_id = _run_id_of(args.dataset)
    tools = tools_for(read_dirs=("data", "audit"), write_dirs=("audit", "data/texts"))
    lines, _ = _load_dataset(tools, args.dataset)
    outputs = _load_jsonl(tools, args.filter)
    version = outputs[0]["version"]
    hk = audit.heldout_keys(lines, args.heldout_seed_a, args.heldout_seed_b)
    groups, pools, path = audit.write_sheet(tools, lines, outputs, run_id, version, args.seed, hk)
    print(f"audit-sheet: {path}: " + "; ".join(f"{g} {len(groups[g])} (pool {pools[g]})" for g in audit.SIZES))
    return 0


def cmd_audit_append_near(args):
    from jobwatch import audit

    run_id = _run_id_of(args.dataset)
    tools = tools_for(read_dirs=("data", "audit"), write_dirs=(args.sheet, "data/texts"))
    lines, _ = _load_dataset(tools, args.dataset)
    outputs = _load_jsonl(tools, args.filter)
    hk = audit.heldout_keys(lines, args.heldout_seed_a, args.heldout_seed_b)
    new = audit.append_near_decision(tools, lines, outputs, run_id, hk, args.sheet)
    print(f"audit-append-near: {args.sheet}: {len(new)} near_decision rows appended")
    return 0


def cmd_audit_stats(args):
    from jobwatch import auditstats

    base = args.sheet[:-len(".csv")]
    tools = tools_for(read_dirs=("data", "audit"), write_dirs=(f"{base}-stats.json", f"{base}-facts.md"))
    lines, _ = _load_dataset(tools, args.dataset)
    stats, js, md = auditstats.run(tools, args.sheet, _load_jsonl(tools, args.filter), lines)
    m = stats["random_reject_miss"]
    print(f"audit-stats: {js}, {md}; random rejects: {m['k']}/{m['n']} misses, 95% CI [{m['ci95'][0]:.4f}, {m['ci95'][1]:.4f}]")
    return 0


def cmd_measure_change(args):
    from jobwatch import measure

    tools = tools_for(read_dirs=("data", "audit"), write_dirs=(f"audit/changes/{args.change}.json", f"audit/changes/{args.change}.md"))
    lines, _ = _load_dataset(tools, args.dataset)
    m = measure.run(tools, args.change, args.sheet, lines)
    print(f"measure-change {args.change}: errors {m['errors_before']} -> {m['errors_after']} of {m['audit_rows']}; "
          f"fixed {len(m['fixed'])}, created {len(m['created'])}; {m['criterion_result']}")
    return 0


def cmd_shortlist(args, clock=None):
    import json
    import time

    from jobwatch import claude_judge, sheets, shortlist
    from jobwatch import filter as flt

    run_id = _run_id_of(args.dataset)
    model = args.model or claude_judge.DEFAULT_MODEL
    tools = tools_for(read_dirs=("data", "prompts", "shortlist"), write_dirs=("shortlist", "data/texts"))
    lines, _ = _load_dataset(tools, args.dataset)
    outputs = _load_jsonl(tools, args.filter)
    version = outputs[0]["version"]
    rules = flt.VERSIONS[version]
    template = tools.read_file("prompts/js3_claims_v1.md").decode("utf-8")
    by_key = {ln["key"]: ln for ln in lines}
    picked = shortlist.shortlisted(outputs)
    paths = sheets.write_texts(tools, [by_key[o["key"]] for o in picked], run_id)
    rows, notes, ranked = [], [], []
    for rank, o in enumerate(picked, 1):
        ln = by_key[o["key"]]
        system, user = claude_judge.fill(template, TITLE=ln["title"] or "", LOCATION=ln["location"] or "(missing)", TEXT=ln["text"])
        stem = o["key"].replace(":", "_")
        res = claude_judge.call(tools, system, user, model, stem, "shortlist/judge", clock or time.time)
        jc, why = ([], f"judge call failed: {res['error']}") if res["error"] else shortlist.parse_judge(res["result"])
        notes.append(f"judge {o['key']}: model {res['model']}, called {res['called_at']}, {len(jc)} claim(s)"
                     + (f"; {why}" if why else "") + f"; files shortlist/judge/{stem}.*")
        rows += shortlist.claims_for(ln, o, rules, rank, paths[o["key"]], jc)
        ranked.append({"rank": rank, "posting_key": o["key"], "title": ln["title"], "location": ln["location"],
                       "url": ln["url"], "score": o["score"], "matched": [m["rule"] for m in o["matched"]]})
    shortlist.write_claims(tools, "shortlist/claims.csv", run_id, version, rows, notes)
    tools.write_file("shortlist/shortlist.json", (json.dumps({"version": version, "run_id": run_id, "top_n": None,
                     "note": "FILTER.md sets no top N; every kept posting is shortlisted", "postings": ranked},
                     indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"shortlist: {len(ranked)} postings, {len(rows)} claims -> shortlist/claims.csv, shortlist/shortlist.json")
    for n in notes:
        print("  " + n)
    return 0


def cmd_mcp_probe(args):
    from jobwatch import mcp_probe

    return mcp_probe.main(os.getcwd())


def cmd_mcp_server(args):
    from jobwatch import mcp_server

    return mcp_server.Server(os.getcwd(), args.dataset, args.version).serve(sys.stdin)


def _picked(tools, args):
    from jobwatch import experiments

    lines, _ = _load_dataset(tools, args.dataset)
    return experiments.heldout_lines(lines, args.heldout_seed_a, args.heldout_seed_b)


def _write_json(tools, path, obj):
    import json

    tools.write_file(path, (json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))


def cmd_experiment_filter(args):
    from jobwatch import experiments

    tools = tools_for(read_dirs=("data",), write_dirs=("experiments/E1-decisions.json", "experiments/E2-decisions.json"))
    picked = _picked(tools, args)
    _write_json(tools, "experiments/E1-decisions.json", experiments.filter_decisions(picked, experiments.e1_arms()))
    _write_json(tools, "experiments/E2-decisions.json", experiments.filter_decisions(picked, experiments.e2_arms()))
    print(f"experiment-filter: {len(picked)} held-out postings; experiments/E1-decisions.json, experiments/E2-decisions.json")
    return 0


def cmd_experiment_judge(args):
    import time

    from jobwatch import claude_judge, experiments

    tools = tools_for(read_dirs=("data", "prompts"), write_dirs=("experiments/E3",))
    picked = _picked(tools, args)
    template = tools.read_file("prompts/js3_relevance_v1.md").decode("utf-8")
    labels = experiments.run_judge(tools, picked, args.arm, args.run, template, args.model or claude_judge.DEFAULT_MODEL, time.time)
    _write_json(tools, f"experiments/E3/{args.arm}-run{args.run}.json", labels)
    errors = sum(1 for v in labels.values() if v["error"] or v["label"] is None)
    print(f"experiment-judge {args.arm} run {args.run}: {len(labels)} calls, {errors} without a usable label")
    return 0


def cmd_experiment_report(args):
    import json

    from jobwatch import experiments

    tools = tools_for(read_dirs=("data", "labels", "experiments"), write_dirs=("experiments/results.json", "experiments/results.md"))
    picked = _picked(tools, args)
    rows = experiments.read_heldout(tools)
    load = lambda p: json.loads(tools.read_file(p).decode("utf-8"))  # noqa: E731
    e3 = {}
    for name in ("title_text-run1", "title_text-run2", "title_only-run1"):
        try:
            e3[name] = load(f"experiments/E3/{name}.json")
        except FileNotFoundError:
            pass
    res = experiments.report(rows, picked, load("experiments/E1-decisions.json"), load("experiments/E2-decisions.json"), e3)
    _write_json(tools, "experiments/results.json", res)
    tools.write_file("experiments/results.md", experiments.render(res).encode("utf-8"))
    print("experiment-report: experiments/results.json, experiments/results.md")
    return 0


def main(argv):
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2
    try:
        return {"dataset": cmd_dataset, "heldout": cmd_heldout, "label": cmd_label, "filter": cmd_filter, "audit-sheet": cmd_audit_sheet, "audit-append-near": cmd_audit_append_near, "audit-stats": cmd_audit_stats, "measure-change": cmd_measure_change, "shortlist": cmd_shortlist, "mcp-probe": cmd_mcp_probe, "mcp-server": cmd_mcp_server, "experiment-filter": cmd_experiment_filter,
                "experiment-judge": cmd_experiment_judge, "experiment-report": cmd_experiment_report}[args.command](args)
    except Exception as e:
        print(f"jobwatch: {args.command}: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
