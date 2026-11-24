You are writing data-quality checks for one table: a sample of NYC yellow taxi trips. You will not see the data. You get only the column names and their types:

- tpep_pickup_datetime: datetime64 (pick-up time)
- tpep_dropoff_datetime: datetime64 (drop-off time)
- passenger_count: int64 (number of passengers)
- trip_distance: float64 (miles)
- fare_amount: float64 (fare in US dollars)

Write the checks as ONE Python file, following this contract exactly:

1. Use pandera 0.29 with `import pandera.pandas as pa`. You may also import pandas as pd.
2. Define one variable named `schema` that is a `pa.DataFrameSchema`. Put column-level rules in `columns`, and rules that involve more than one column or the whole table in the schema-level `checks` list.
3. Write one rule per property you think every valid trip should have. Every rule must pass on normal, correct trips.
4. Do not hard-code row numbers, row counts, or specific values from any dataset.
5. Above each rule, write a one-line comment saying what it protects against.
6. Return only the Python code, in a single code block, with no explanation before or after it.
