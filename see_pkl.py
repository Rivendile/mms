import pickle

path = "dataset/azure_v1.pkl"
with open(path, "rb") as handle:
    tracelines = pickle.load(handle)

cnt = 0
for key, val in tracelines.items():
    print(key, val)
    cnt += 1
    if cnt>=10:
        exit()
    # exit()
