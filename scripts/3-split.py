import pathlib
import pandas as pd
import utils
import metaphone

# from cleaning checkpoint
print("Read pickled clean data")
df = pd.read_pickle("dataframe.pickled")

root = pathlib.Path("/work/sdusscsa2/groups")

header = "FT|Amt|Herred|Sogn|Navn|Køn|Fødested|Fødeår|Civilstand|Position|Erhverv|Kipnr|Løbenr".split("|")

print("Apply grouping function")
df["G1"] = df.FonetiskFornavn.apply(lambda x: x[0][:2].replace(" ", "_"))
df["G2"] = df.FonetiskFornavn.apply(lambda x: x[0][:4].replace(" ", "_"))
df["G3"] = df.FonetiskFødested.apply(lambda x: x[0][:2].replace(" ", "_"))

def savegroup(block, data):
    fn = root / ("-".join(block) + ".csv")
    print("Write out group", fn.stem)
    if fn.exists():
        data.to_csv(str(fn), header=False, mode="a")
    else:
        data.to_csv(str(fn), header=True, mode="a")

LIMIT = 50000
print("Do the groupby and write")
for (gender, prefix1), data1 in df.groupby(["Køn", "G1"]):
    gender = "f" if gender else "m"

    print((gender, prefix1), "has size", len(data1))
    if len(data1) <= LIMIT:
        savegroup((gender, prefix1), data1)
    else: # split further
        for prefix2, data2 in data1.groupby(["G2"]):
            print(" ", prefix2, "has size", len(data2))
            if len(data2) <= LIMIT:
                savegroup((gender, prefix1, prefix2), data2)
            else: # split even further
                for prefix3, data3 in data2.groupby(["G3"]):
                    print("   ", prefix3, "has size", len(data3))
                    savegroup((gender, prefix1, prefix2, prefix3), data3)
