I ran your checks on a clean copy of the real table: 10,000 normal trips that are known to be good. Your checks rejected 94 of those normal trips. Here is how many normal trips each of your rules rejected:

- in_range(1, 6): 79 trips
- dropoff_after_pickup: 8 trips
- fare_positive_and_bounded: 4 trips
- average_speed_plausible: 3 trips
- fare_consistent_with_distance: 3 trips

Revise your checks so they still protect against real data problems but no longer reject these normal trips. Keep the same contract as before: pandera 0.29 with `import pandera.pandas as pa`, one variable named `schema`, one-line comments above each rule, no hard-coded row numbers or dataset values, and return only the Python code in a single code block.
