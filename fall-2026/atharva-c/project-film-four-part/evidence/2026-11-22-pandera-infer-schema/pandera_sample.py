# Infer a pandera schema from the clean 2,000-row sample, then validate clean and faulted (50 nulls) copies.
import os
from pathlib import Path
SANDBOX = Path(os.environ.get("SEEDED_FAULTS_SANDBOX", Path.home() / "Projects/seeded-faults-sandbox"))
import pandas as pd, pandera, pandera.pandas as pa
sb = str(SANDBOX) + "/"
df, bad = pd.read_csv(sb + "trips_sample.csv"), pd.read_csv(sb + "trips_faulted.csv")
print("pandera", pandera.__version__, "pandas", pd.__version__)
s = pa.infer_schema(df)
for n, c in s.columns.items(): print(n, c.dtype, "nullable=", c.nullable, [str(k) for k in c.checks])
for name, d in [("clean", df), ("faulted", bad)]:
    try: s.validate(d, lazy=True); print(name, ": PASS")
    except pa.errors.SchemaErrors as e: print(name, ": FAIL"); print(e.failure_cases.groupby(["column", "check"]).size())
