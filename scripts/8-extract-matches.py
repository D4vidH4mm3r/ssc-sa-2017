import pickle
import pandas as pd
import concurrent.futures
import pathlib

def uniqueify_max(matches):
    # take max-probability b for each a
    g = matches.groupby(by=["a_FT", "a_Kipnr", "a_Løbenr"])
    idx = g["p"].transform(max) == matches["p"]
    matches = matches[idx]
    del(g)
    del(idx)
    # and then max-probability a for each b
    g = matches.groupby(by=["b_FT", "b_Kipnr", "b_Løbenr"])
    idx = g["p"].transform(max) == matches["p"]
    matches = matches[idx]
    del(g)
    del(idx)
    # drop any duplicate a or b
    matches.drop_duplicates(subset=["a_FT", "a_Løbenr", "a_Kipnr"], inplace=True)
    matches.drop_duplicates(subset=["b_FT", "b_Løbenr", "b_Kipnr"], inplace=True)
    return matches

def process(fn):
    matches = pd.read_csv(str(fn), delimiter="|")
    matches = matches[matches.p > 0.8]
    matches = uniqueify_max(matches)
    return matches

with concurrent.futures.ProcessPoolExecutor(max_workers=10) as tpe:
    res = tpe.map(process, pathlib.Path("nn-match").glob("*.csv"))

res = list(res)

len(res)

matches = pd.concat(res)

del(res)

len(matches)

# so how many left?
g1 = matches.groupby(by=["a_FT", "a_Kipnr", "a_Løbenr"], as_index=False)
g2 = matches.groupby(by=["b_FT", "b_Kipnr", "b_Løbenr"])
l1=list(g1.size().groupby(level=0).size().iteritems())
l2=list(g2.size().groupby(level=0).size().iteritems())

for (a_year, a_count), (b_year, b_count) in zip(l1, l2):
    print(a_year, b_year, min(a_count, b_count))
print(sum(min(a, b) for ((_, a), (_, b)) in zip(l1,l2)))

g = matches.groupby("a_FT")

s = 0
for a_year, size in g.size().iteritems():
    print(a_year, size)
    s += size
s

df = pd.read_pickle("../scripts/dataframe.pickled")

g2 = df.groupby("FT")

l = list(g2.size().iteritems())

for (a_year, a_size), (b_year, b_size), (our_year, our_size) in zip(l, l[1:], g.size().iteritems()):
    ul = min(a_size, b_size)
    print(a_year, "->", b_year, our_size, "/", ul, our_size/ul)

hmm = matches.p.describe()

print(hmm.to_latex())

# ## There are probably still duplicates
# Obvious if `len(matches)` above is greater than the sum in the cell directly above

indexed = matches.set_index(["a_FT", "a_Kipnr", "a_Løbenr"])

d = indexed.index.get_duplicates()

indexed.loc[d]

len(matches)

matches.drop_duplicates(subset=["a_FT", "a_Løbenr", "a_Kipnr"], inplace=True)
matches.drop_duplicates(subset=["b_FT", "b_Løbenr", "b_Kipnr"], inplace=True)

len(matches)

matches
