#!/opt/sys/apps/python/3.6.0/bin/python

from nn_common import *
import random
import itertools
import concurrent.futures
import sys


print("Loading big dataframe")
df = pd.read_pickle("indexed.pickled")

years = [1845, 1850, 1860, 1880, 1885]

ssize = 10000
def generate_nonmatch_scores(_):
    lots = []
    s = df.loc[random.choice(years)].sample(ssize)
    for i in range(ssize-1):
        a = s.iloc[i]
        b = s.iloc[i+1]
        lots.append(score(a,b) + (False,))
    return lots

print("Compute scores for random non-matches")
with concurrent.futures.ProcessPoolExecutor(max_workers=48) as tpe:
    data = tpe.map(generate_nonmatch_scores, [None for i in range(48)])

df = pd.DataFrame(list(itertools.chain(*data)), columns=score_columns + ["label"])
df.to_csv(str(utils.workdir / "scores-negative.csv"))
