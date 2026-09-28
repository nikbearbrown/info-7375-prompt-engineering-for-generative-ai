from main import sample
for seed in range(1, 21):
    print(seed, sample([1, 2, 3], seed=seed)[2])
