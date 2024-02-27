import pickle

path = "profiling_result.pkl"
with open(path, "rb") as handle:
    tracelines = pickle.load(handle)

for key, val in tracelines.items():
    print(key, val)
    # exit()
