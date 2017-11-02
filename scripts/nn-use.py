#!/opt/sys/apps/python/3.6.0/bin/python

from network import *
import recordlinkage
import utils
import itertools
import sys
import pathlib
import time


start = time.time()
# # Read some subset to match
print("Loading dataset from", sys.argv[1])
df = pd.read_pickle(sys.argv[1])
fn = pathlib.Path(sys.argv[1])
fout = (utils.workdir / "nn-match") / (fn.stem + ".csv")

grouped = df.groupby("FT")

def generate_scores(d):
    lots = []
    for (a, b) in d:
        a = dfA.loc[a]
        b = dfB.loc[b]
        lots.append((a.FT, a.Kipnr, a.Løbenr, b.FT, b.Kipnr, b.Løbenr) + score(a,b))
    return lots

potential_matches = set() # no idea why duplicates occur
dfA = dfB = None
yearA = yearB = None

for year, data in grouped:
    yearB = year
    dfB = data
    if dfA is not None:
        print("Now try", yearA, "with", len(dfA), "vs", yearB, "with", len(dfB))
        indexer = recordlinkage.indexing.SortedNeighbourhoodIndex(on="Fødeår", window=3)
        index = indexer.index(dfA, dfB)
        print("Index of size", len(index))
        with multiprocessing.Pool() as p:
            res = p.map(generate_scores, utils.chunks(index, 500))
        df_eval = pd.DataFrame(list(itertools.chain(*res)),
                               columns=["a_FT", "a_Kipnr", "a_Løbenr",
                                        "b_FT", "b_Kipnr", "b_Løbenr"] + score_columns)
        del(res)
        input_fn = tf.estimator.inputs.pandas_input_fn(x=df_eval, shuffle=False)
        prediction = model1.predict(input_fn)
        for i, d in enumerate(prediction):
            if d["classes"][0] == b"1":
                r = df_eval.iloc[i]
                potential_matches.add(tuple(r[:6]) + (d["probabilities"][1],))
        print("Now have", len(potential_matches))
    dfA = dfB
    yearA = yearB

with fout.open("w", encoding="utf-8") as fd:
    writer = csv.writer(fd, lineterminator="\n", delimiter="|")
    writer.writerow("a_FT a_Kipnr a_Løbenr b_FT b_Kipnr b_Løbenr p".split())
    writer.writerows(potential_matches)

elapsed = time.time() - start
print("Spent", elapsed, "seconds on this")
