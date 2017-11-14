import networkx as nx
import pandas as pd
import sys
import pathlib
import concurrent.futures
import utils
import csv
import multiprocessing


print("Initializing")
# cutoff for probability suggested by NN; any links below this are not considered
THRESHOLD = 0.8

# just for reading stuff
dtypes = {
    "a_FT": int,
    "a_Kipnr": str,
    "a_Løbenr": int,
    "b_FT": int,
    "b_Kipnr": str,
    "b_Løbenr": int,
    "p": float
}
fout = utils.workdir / "nn-plus-matching.csv"
fdir = pathlib.Path(sys.argv[1])
m = multiprocessing.Manager()
Q = m.Queue(maxsize=100)

def process_file(fn):
    print("Loading data for", fn)
    df = pd.read_csv(fn, delimiter="|", dtype=dtypes)

    by_year = df.groupby("a_FT")
    for a_FT, data in by_year:
        print("Start", fn, "on", a_FT, "with", len(data), "links")
        G = nx.Graph()
        for t in data.itertuples():
            a = t[1:4]
            b = t[4:7]
            p = t.p
            if p > THRESHOLD:
                G.add_edge(a, b, weight=p)
        #print("Added", G.number_of_edges(), "edges from this")
        #print("Calculating max-weight-matching...")
# TODO: recover and save p for match (for further study)
        match = nx.max_weight_matching(G, maxcardinality=False)
        #print("Match had", len(match), "elems")
        Q.put(list(match.items()))
    Q.put("done")

print("Starting process pool executor")
with concurrent.futures.ProcessPoolExecutor(max_workers=47) as tpe, \
        fout.open("w", encoding="utf-8") as fd:
    todo = list(fdir.iterdir())
    print("Submit all the", len(todo), "things to map")
    _ = tpe.map(process_file, todo)

    writer = csv.writer(fd, lineterminator="\n", delimiter="|")
    writer.writerow("a_FT a_Kipnr a_Løbenr b_FT b_Kipnr b_Løbenr p".split())
    done = 0
    while True:
        print("Get something from queue...")
        res = Q.get()
        print("Got", res[:5], flush=True)
        if res == "done":
            done += 1
            if done == len(todo):
                break
        else:
            for (a, b) in res:
                writer.writerow(a + b)
