import networkx as nx
import pandas as pd
import sys
import pathlib
import concurrent.futures
import utils
import itertools


# cutoff for probability suggested by NN; any links below this are not considered
THRESHOLD = 0.7

print("Loading data for", sys.argv[1])
df = pd.read_csv(sys.argv[1], delimiter="|", dtype={
    "a_FT": int,
    "a_Kipnr": str,
    "a_Løbenr": int,
    "b_FT": int,
    "b_Kipnr": str,
    "b_Løbenr": int,
    "p": float
})
fn = pathlib.Path(sys.argv[1])
fout = (utils.workdir / "nn-graph-matching") / fn.name
print("Will write matches to", fout)

by_year = df.groupby("a_FT")
def make_matching(arg):
    a_FT, data = arg
    print(a_FT)
    print("There are", len(data), "proposed links")
    G = nx.Graph()
    for t in data.itertuples():
        a = t[1:4]
        b = t[4:7]
        p = t.p
        if p > THRESHOLD:
            G.add_edge(a, b, weight=p)
    print("Added", G.number_of_edges(), "edges from this")
    print("Calculating max-weight-matching...")
    match = nx.max_weight_matching(G, maxcardinality=False)
    match = sorted(set(tuple(sorted(item)) for item in match.items()),
                   key=lambda x: G[x[0]][x[1]]["weight"],
                   reverse=True)
    for pair in match:
        print(pair)

with concurrent.futures.ProcessPoolExecutor() as tpe:
    res = tpe.map(make_matching, by_year)

print(list(res))
