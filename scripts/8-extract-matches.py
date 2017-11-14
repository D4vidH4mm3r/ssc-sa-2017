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

with concurrent.futures.ProcessPoolExecutor() as tpe:
    res = tpe.map(process, (utils.workdir / "nn-match").glob("*.csv"))

matches = pd.concat(list(res))
del(res)
print(len(matches), "matches remaining")

df = pd.read_pickle("dataframe.pickled")
g2 = df.groupby("FT")
l = list(g2.size().iteritems())
for (a_year, a_size), (b_year, b_size), (our_year, our_size) in zip(l, l[1:], g.size().iteritems()):
    ul = min(a_size, b_size)
    print(a_year, "->", b_year, our_size, "/", ul, our_size/ul)

hmm = matches.p.describe()
print(hmm.to_latex())
