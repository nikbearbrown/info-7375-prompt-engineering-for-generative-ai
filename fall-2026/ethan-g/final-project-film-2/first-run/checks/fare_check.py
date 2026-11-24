"""The one check for the first piece, written in pandera: fare_amount must not be negative.

Hand-written for this first run (the Claude Code check writer comes later). It knows only the column
names and types, never the answer key. It deliberately covers one property, so the run can show
both a defect it catches and one it misses.
"""
try:
    import pandera.pandas as pa      # pandera >= 0.24
except ImportError:
    import pandera as pa             # older pandera

RULE = "fare_amount >= 0"

schema = pa.DataFrameSchema({"fare_amount": pa.Column(float, pa.Check.ge(0), nullable=False)})
