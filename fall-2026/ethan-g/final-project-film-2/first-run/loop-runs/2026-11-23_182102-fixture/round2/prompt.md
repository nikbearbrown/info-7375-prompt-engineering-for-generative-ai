I ran your checks on a clean copy of the real table: 10,000 normal trips that are known to be good. Your checks rejected 220 of those normal trips. Here is how many normal trips each of your rules rejected:

- trip_distance not positive: 110 trips
- passenger_count below 1: 79 trips
- fare too high for distance and duration: 49 trips
- dropoff not after pickup: 8 trips
- fare too low for distance: 4 trips
- fare_amount not positive: 4 trips
- average speed above 100 mph: 3 trips

Revise your checks so they still protect against real data problems but no longer reject these normal trips. Keep the same contract as before: pandera 0.29 with `import pandera.pandas as pa`, one variable named `schema`, one-line comments above each rule, no hard-coded row numbers or dataset values, and return only the Python code in a single code block.
