"""Step 5 — the same rule in Great Expectations (GX Core, the free open-source library).

One expectation: fare_amount between 0 and no upper limit. Run on the clean copy and the broken copy.
(GX Cloud's ExpectAI, which suggests expectations, is a paid hosted feature and is NOT run here.)
"""
import json, sys
from pathlib import Path
import pandas as pd
import great_expectations as gx

HERE = Path(__file__).resolve().parent


def main(out_dir):
    ctx = gx.get_context(mode="ephemeral")
    batch_def = (ctx.data_sources.add_pandas("taxi")
                 .add_dataframe_asset("trips")
                 .add_batch_definition_whole_dataframe("whole"))
    rule = gx.expectations.ExpectColumnValuesToBeBetween(column="fare_amount", min_value=0)
    out, lines = {}, [f"expectation: ExpectColumnValuesToBeBetween(fare_amount, min_value=0)   (GX Core {gx.__version__})"]
    for name in ("clean", "broken"):
        df = pd.read_parquet(HERE / "data" / f"{name}.parquet")
        res = batch_def.get_batch(batch_parameters={"dataframe": df}).validate(rule)
        n_bad = int(res.result.get("unexpected_count", 0))
        out[name] = {"success": bool(res.success), "unexpected_count": n_bad, "rows": len(df)}
        lines.append(f"{name + ' copy':<12} ({len(df):,} rows): " + ("PASS" if res.success else f"FAIL  {n_bad} unexpected values"))
    text = "\n".join(lines)
    print(text)
    (Path(out_dir) / "gx.txt").write_text(text + "\n")
    (Path(out_dir) / "gx.json").write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
