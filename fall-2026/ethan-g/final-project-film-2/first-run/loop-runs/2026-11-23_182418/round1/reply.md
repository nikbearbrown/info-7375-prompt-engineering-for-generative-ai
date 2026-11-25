```python
import pandas as pd
import pandera.pandas as pa

# Earliest date for which NYC TLC yellow taxi trip records exist (publicly documented start of the dataset)
TLC_DATA_START = pd.Timestamp("2009-01-01")

# Generous physical/operational ceilings for a single yellow taxi trip
MAX_PASSENGERS = 6
MAX_TRIP_MILES = 200.0
MAX_FARE_USD = 1000.0
MAX_TRIP_HOURS = 24
MAX_AVG_SPEED_MPH = 100.0
MIN_FARE_PER_MILE = 0.5


def _duration_hours(df: pd.DataFrame) -> pd.Series:
    return (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 3600.0


schema = pa.DataFrameSchema(
    columns={
        "tpep_pickup_datetime": pa.Column(
            "datetime64[ns]",
            nullable=False,
            checks=[
                # Protects against corrupted or default timestamps (e.g. 1970/1900) predating TLC records
                pa.Check.ge(TLC_DATA_START),
                # Protects against pick-up times in the future caused by clock or parsing errors
                pa.Check(lambda s: s <= pd.Timestamp.now(), error="pickup_not_in_future"),
            ],
        ),
        "tpep_dropoff_datetime": pa.Column(
            "datetime64[ns]",
            nullable=False,
            checks=[
                # Protects against corrupted or default timestamps (e.g. 1970/1900) predating TLC records
                pa.Check.ge(TLC_DATA_START),
                # Protects against drop-off times in the future caused by clock or parsing errors
                pa.Check(lambda s: s <= pd.Timestamp.now(), error="dropoff_not_in_future"),
            ],
        ),
        "passenger_count": pa.Column(
            "int64",
            nullable=False,
            checks=[
                # Protects against empty/negative passenger counts and counts beyond a taxi's legal capacity
                pa.Check.in_range(1, MAX_PASSENGERS),
            ],
        ),
        "trip_distance": pa.Column(
            "float64",
            nullable=False,
            checks=[
                # Protects against negative odometer readings and absurd distances from meter/GPS faults
                pa.Check.in_range(0.0, MAX_TRIP_MILES),
            ],
        ),
        "fare_amount": pa.Column(
            "float64",
            nullable=False,
            checks=[
                # Protects against zero/negative fares (voids, refunds, sign errors) and absurd fare outliers
                pa.Check(lambda s: (s > 0) & (s <= MAX_FARE_USD), error="fare_positive_and_bounded"),
            ],
        ),
    },
    checks=[
        # Protects against trips that end before (or at the same instant as) they start
        pa.Check(
            lambda df: df["tpep_dropoff_datetime"] > df["tpep_pickup_datetime"],
            error="dropoff_after_pickup",
        ),
        # Protects against implausibly long trips from meters left running or swapped timestamps
        pa.Check(
            lambda df: _duration_hours(df) <= MAX_TRIP_HOURS,
            error="trip_duration_bounded",
        ),
        # Protects against physically impossible average speeds from bad distance or time values
        pa.Check(
            lambda df: (_duration_hours(df) <= 0)
            | ((df["trip_distance"] / _duration_hours(df).where(_duration_hours(df) > 0)) <= MAX_AVG_SPEED_MPH),
            error="average_speed_plausible",
        ),
        # Protects against long trips with implausibly tiny fares (e.g. distance in wrong units or truncated fare)
        pa.Check(
            lambda df: df["fare_amount"] >= MIN_FARE_PER_MILE * df["trip_distance"],
            error="fare_consistent_with_distance",
        ),
        # Protects against duplicated trip records from repeated ingestion
        pa.Check(
            lambda df: ~df.duplicated(keep=False),
            error="no_duplicate_trips",
        ),
    ],
    strict=False,
)
```