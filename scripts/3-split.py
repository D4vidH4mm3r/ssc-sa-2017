import pathlib
import pandas as pd
import utils
import metaphone

# from cleaning checkpoint
print("Read pickled clean data")
df = pd.read_pickle("dataframe.pickled")

root = pathlib.Path("/work/sdusscsa2/groups")

header = "FT|Amt|Herred|Sogn|Navn|Køn|Fødested|Fødeår|Civilstand|Position|Erhverv|Kipnr|Løbenr".split("|")

def make_keys(names):
    def f(s):
        return metaphone.doublemetaphone(s.translate(utils.trans))[0][:2]
    return names.apply(f)

print("Apply grouping function")
df["G1"] = df.FonetiskFornavn.apply(lambda x: x[0][:3])
df["G2"] = df.FonetiskFornavn.apply(lambda x: x[1][:3])

print("Do the groupby and write")
for g in ("G1", "G2"):
    for (a, b), data in df.groupby(["Køn", g]):
        if b == "":
            continue
        gender = "f" if a else "m"
        fn = root / (gender + "-" + b + ".csv")
        print("Write out group", (a,b))
        if fn.exists():
            data.to_csv(str(fn), header=False, mode="a")
        else:
            data.to_csv(str(fn), header=True, mode="a")
