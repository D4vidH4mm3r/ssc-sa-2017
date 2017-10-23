import pathlib
import pandas as pd
import utils
import metaphone

# from cleaning checkpoint
print("Read pickled clean data")
df = pd.read_pickle("dataframe.pickled")

root = pathlib.Path("../work")

header = "FT|Amt|Herred|Sogn|Navn|Køn|Fødested|Fødeår|Civilstand|Position|Erhverv|Kipnr|Løbenr".split("|")

def make_keys(names):
    def f(s):
        return metaphone.doublemetaphone(s.translate(utils.trans))[0][:3]
    return names.apply(f)

print("Apply grouping function")
df["Group"] = utils.parallelize(df.Navn, make_keys)

print("Do the groupby and write")
for (a, b), data in df.groupby(["Køn", "Group"]):
    gender = "f" if a else "m"
    fn = root / (gender + "-" + b + ".pickled")
    print("Write out group", (a,b))
    pd.to_pickle(data, str(fn))
