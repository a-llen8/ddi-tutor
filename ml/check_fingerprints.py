import numpy as np
import pandas as pd

d = np.load("data/processed/fingerprints.npz")
fps = d["fps"]
info = pd.read_csv("data/processed/fingerprint_info.csv")

bits = fps.sum(axis=1)
print("bits set: min", bits.min(), "median", int(np.median(bits)), "max", bits.max())
low = info[bits <= 5]
print("drugs with 5 or fewer bits:", len(low))
print(low["drug"].head(20).to_string(index=False))

keys = pd.Series([row.tobytes() for row in fps])
dup = keys.duplicated(keep=False)
print("\ndrugs sharing a fingerprint with another drug:", int(dup.sum()))
print("number of shared groups:", keys[dup].nunique())
for k, g in list(info[dup.values].groupby(keys[dup].values))[:15]:
    print(" | ".join(g["drug"].tolist()))