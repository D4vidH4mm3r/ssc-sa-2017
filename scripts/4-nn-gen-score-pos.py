#!/opt/sys/apps/python/3.6.0/bin/python

from nn_common import *
import itertools
import utils
import concurrent.futures


print("Loading golden standard")
matches = pd.read_csv(str(utils.datadir / "links" / "matches.csv"), sep="|",
    dtype={"a_FT": int, "a_Kipnr": str, "a_Løbenr": int, "b_FT": int, "b_Kipnr": str, "b_Løbenr": int},
    comment="#")
print("Loaded", len(matches), "matches in total")
print("Loading big dataframe")
df = pd.read_pickle("indexed.pickled")
print("Loaded!")
print("Converting to dict")
d = {}
for t in df.itertuples():
    d[t.Index] = t 
del(df)
print("Done")

def to_scored_frame(subset):
    print("Starting on index", subset.index[0], flush=True)
    res = []
    for t in subset.itertuples():
        a = t[1:4]
        b = t[4:]
        try:
            a = d[a]
            b = d[b]
        except KeyError:
            #print(a, "or", b, "not found")
            continue
        res.append(score(a,b) + (True,))
    return res

print("Starting the processing")
with concurrent.futures.ProcessPoolExecutor(max_workers=48) as tpe:
    data = tpe.map(to_scored_frame, utils.chunks(matches, 500))

df = pd.DataFrame(list(itertools.chain(*data)), columns=score_columns+["labels"])
df.to_csv(str(utils.workdir / "scores-positive.csv"))
