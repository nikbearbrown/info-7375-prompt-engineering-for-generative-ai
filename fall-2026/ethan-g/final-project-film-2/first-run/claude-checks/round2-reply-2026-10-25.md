<!-- Claude's reply, round 2, received 2026-10-25 in the same Claude desktop app chat as round 1
     ("NYC taxi trips data-quality checks"), after PROMPT-round2.md was pasted unchanged.
     Model: Opus 5.5, effort "High" (shown in the app's model selector; screenshot from Ethan, 2026-10-25).
     Copied with the app's code-block copy button, so the reply is the code only. Saved verbatim below; round2_checks.py is identical. -->

```python
import pandas as pd
import pandera.pandas as pa


def _is_datetime(s: pd.Series) -> bool:
    return pd.api.types.is_datetime64_any_dtype(s)


def _not_in_future(s: pd.Series) -> pd.Series:
    return s <= pd.Timestamp.now(tz=s.dt.tz)


def _duration_seconds(df: pd.DataFrame) -> pd.Series:
    return (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds()


schema = pa.DataFrameSchema(
    columns={
        "tpep_pickup_datetime": pa.Column(
            checks=[
                # Guards against the pickup column being loaded as strings/objects instead of timestamps
                pa.Check(_is_datetime, element_wise=False, error="pickup must be a datetime dtype"),
                # Guards against epoch/default timestamps, since TPEP yellow-taxi records begin in 2009
                pa.Check(lambda s: s.dt.year >= 2009, error="pickup before TPEP era"),
                # Guards against clock errors that put the pickup in the future
                pa.Check(_not_in_future, error="pickup in the future"),
            ],
            nullable=False,
        ),
        "tpep_dropoff_datetime": pa.Column(
            checks=[
                # Guards against the dropoff column being loaded as strings/objects instead of timestamps
                pa.Check(_is_datetime, element_wise=False, error="dropoff must be a datetime dtype"),
                # Guards against epoch/default timestamps, since TPEP yellow-taxi records begin in 2009
                pa.Check(lambda s: s.dt.year >= 2009, error="dropoff before TPEP era"),
                # Guards against clock errors that put the dropoff in the future
                pa.Check(_not_in_future, error="dropoff in the future"),
            ],
            nullable=False,
        ),
        "passenger_count": pa.Column(
            "int64",
            checks=[
                # Guards against negative rider counts (zero is allowed because drivers often leave it unentered)
                pa.Check.ge(0, error="passenger_count negative"),
                # Guards against counts above what a licensed yellow cab can carry (max 5 plus a lap child)
                pa.Check.le(6, error="passenger_count above vehicle capacity"),
            ],
            nullable=False,
        ),
        "trip_distance": pa.Column(
            "float64",
            checks=[
                # Guards against negative distances (zero is allowed for cancelled or flat-rate trips)
                pa.Check.ge(0, error="trip_distance negative"),
                # Guards against odometer/GPS glitches producing implausibly long trips
                pa.Check.le(300, error="trip_distance implausibly large"),
            ],
            nullable=False,
        ),
        "fare_amount": pa.Column(
            "float64",
            checks=[
                # Guards against NaN/inf fares slipping through as floats
                pa.Check(lambda s: pd.Series(pd.api.types.is_number(v) for v in s).values & s.abs().lt(float("inf")).values,
                         error="fare_amount not finite"),
                # Guards against keying errors producing absurd fares in either direction (refund adjustments may be negative)
                pa.Check(lambda s: s.abs() <= 1000, error="fare_amount magnitude implausibly large"),
            ],
            nullable=False,
        ),
    },
    checks=[
        # Guards against an empty load that would pass every row-level rule
        pa.Check(lambda df: len(df) > 0, element_wise=False, error="table is empty"),
        # Guards against dropoff times recorded before the pickup (equal times are allowed for zero-length trips)
        pa.Check(lambda df: _duration_seconds(df) >= 0, error="dropoff before pickup"),
        # Guards against meters left running, giving trips longer than a day
        pa.Check(lambda df: _duration_seconds(df) <= 24 * 3600, error="trip longer than 24 hours"),
        # Guards against impossible average speeds, measured only on trips long enough for timestamp rounding not to dominate
        pa.Check(
            lambda df: (_duration_seconds(df) < 300)
            | (df["trip_distance"] / (_duration_seconds(df) / 3600) <= 100),
            error="average speed above 100 mph",
        ),
        # Guards against metered fares far beyond what distance and time could produce, skipping trips with no recorded distance/time (flat or negotiated fares)
        pa.Check(
            lambda df: (df["trip_distance"] <= 0)
            | (_duration_seconds(df) <= 0)
            | (df["fare_amount"] <= 150 + 10 * df["trip_distance"] + 2.0 * (_duration_seconds(df) / 60)),
            error="fare too high for distance and duration",
        ),
        # Guards against the same trip being ingested more than once
        pa.Check(lambda df: ~df.duplicated(keep=False), error="duplicate trip row"),
    ],
)
```
