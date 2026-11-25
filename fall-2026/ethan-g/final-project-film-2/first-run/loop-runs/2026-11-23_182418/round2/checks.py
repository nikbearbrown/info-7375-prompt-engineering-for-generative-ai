import pandas as pd
import pandera.pandas as pa

# Earliest date for which NYC TLC yellow taxi trip records exist (publicly documented start of the dataset)
TLC_DATA_START = pd.Timestamp("2009-01-01")

# Generous physical/operational ceilings for a single yellow taxi trip
MAX_PASSENGERS = 9
MAX_TRIP_MILES = 200.0
MAX_FARE_USD = 1000.0
MAX_TRIP_HOURS = 24
MAX_AVG_SPEED_MPH = 100.0
MIN_HOURS_FOR_SPEED_CHECK = 10 / 60
MIN_MILES_FOR_FARE_CHECK = 5.0
MIN_FARE_PER_MILE = 0.25


def _duration_hours(df: pd.DataFrame) -> pd.Series:
    return (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 3600.0


def _speed_ok(df: pd.DataFrame) -> pd.Series:
    hours = _duration_hours(df)
    long_enough = hours >= MIN_HOURS_FOR_SPEED_CHECK
    speed = df["trip_distance"] / hours.where(long_enough)
    return ~long_enough | (speed <= MAX_AVG_SPEED_MPH)


def _fare_vs_distance_ok(df: pd.DataFrame) -> pd.Series:
    applies = (df["fare_amount"] > 0) & (df["trip_distance"] >= MIN_MILES_FOR_FARE_CHECK)
    return ~applies | (df["fare_amount"] >= MIN_FARE_PER_MILE * df["trip_distance"])


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
                # Protects against negative passenger counts and counts far beyond any taxi's seating (0 = not entered by driver)
                pa.Check.in_range(0, MAX_PASSENGERS),
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
                # Protects against negative fares (sign errors) and absurd fare outliers
                pa.Check.in_range(0.0, MAX_FARE_USD),
            ],
        ),
    },
    checks=[
        # Protects against trips that end before they start (swapped or corrupted timestamps)
        pa.Check(
            lambda df: df["tpep_dropoff_datetime"] >= df["tpep_pickup_datetime"],
            error="dropoff_not_before_pickup",
        ),
        # Protects against implausibly long trips from meters left running or mis-parsed timestamps
        pa.Check(
            lambda df: _duration_hours(df) <= MAX_TRIP_HOURS,
            error="trip_duration_bounded",
        ),
        # Protects against physically impossible average speeds on trips long enough for timing noise to be negligible
        pa.Check(_speed_ok, error="average_speed_plausible"),
        # Protects against long paid trips with fares far too small for the distance (wrong units or truncated fare)
        pa.Check(_fare_vs_distance_ok, error="fare_consistent_with_distance"),
        # Protects against duplicated trip records from repeated ingestion
        pa.Check(
            lambda df: ~df.duplicated(keep=False),
            error="no_duplicate_trips",
        ),
    ],
    strict=False,
)
