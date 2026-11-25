<!-- Claude's reply, round 1, received 2026-10-25 in the Claude desktop app (new chat, no files, no Project).
     Chat title (set by the app): "NYC taxi trips data-quality checks". Prompt: PROMPT-round1.md, pasted unchanged.
     Model: Opus 5.5, effort "High" (shown in the app's model selector; screenshot from Ethan, 2026-10-25).
     Saved verbatim below; round1_checks.py is the code block extracted without edits. -->

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
                # Guards against trips logged with zero or negative riders
                pa.Check.ge(1, error="passenger_count below 1"),
                # Guards against counts above what a licensed yellow cab can carry (max 5 plus a lap child)
                pa.Check.le(6, error="passenger_count above vehicle capacity"),
            ],
            nullable=False,
        ),
        "trip_distance": pa.Column(
            "float64",
            checks=[
                # Guards against negative or zero distances, since a real trip covers some ground
                pa.Check.gt(0, error="trip_distance not positive"),
                # Guards against odometer/GPS glitches producing implausibly long trips
                pa.Check.le(300, error="trip_distance implausibly large"),
            ],
            nullable=False,
        ),
        "fare_amount": pa.Column(
            "float64",
            checks=[
                # Guards against refunds, voids, or zero fares recorded as trips
                pa.Check.gt(0, error="fare_amount not positive"),
                # Guards against keying errors producing absurdly large fares
                pa.Check.le(1000, error="fare_amount implausibly large"),
            ],
            nullable=False,
        ),
    },
    checks=[
        # Guards against an empty load that would pass every row-level rule
        pa.Check(lambda df: len(df) > 0, element_wise=False, error="table is empty"),
        # Guards against dropoff times that are equal to or earlier than the pickup
        pa.Check(lambda df: _duration_seconds(df) > 0, error="dropoff not after pickup"),
        # Guards against meters left running, giving trips longer than a day
        pa.Check(lambda df: _duration_seconds(df) <= 24 * 3600, error="trip longer than 24 hours"),
        # Guards against distance/time mismatches implying an average speed no taxi could reach
        pa.Check(
            lambda df: (_duration_seconds(df) <= 0)
            | (df["trip_distance"] / (_duration_seconds(df) / 3600) <= 100),
            error="average speed above 100 mph",
        ),
        # Guards against fares too small for the distance driven (below $1 per mile)
        pa.Check(lambda df: df["fare_amount"] >= 1.0 * df["trip_distance"], error="fare too low for distance"),
        # Guards against fares far beyond what distance and waiting time could produce
        pa.Check(
            lambda df: df["fare_amount"]
            <= 20 + 10 * df["trip_distance"] + 1.0 * (_duration_seconds(df).clip(lower=0) / 60),
            error="fare too high for distance and duration",
        ),
        # Guards against the same trip being ingested more than once
        pa.Check(lambda df: ~df.duplicated(keep=False), error="duplicate trip row"),
    ],
)
```
