#!/opt/sys/apps/python/3.6.0/bin/python

from nn_common import *
import random
import itertools
import multiprocessing
import sys


print("NOT DONE YET - I HAVE TO GO CATCH A TRAIN D:")
sys.exit()


print("Loading big dataframe")
df = pd.read_pickle("dataframe.pickled")
print("Doing some indexing")
df.dropna(subset=("Fødeår",), inplace=True)
df.set_index(["FT", "Kipnr", "Løbenr"], inplace=True)
df.sort_index(inplace=True)

years = [1845, 1850, 1860, 1880, 1885]

ssize = 100
def generate_nonmatch_scores(_):
    lots = []
    s = df.loc[random.choice(years)].sample(ssize)
    for i in range(ssize-1):
        a = s.iloc[i]
        b = s.iloc[i+1]
        lots.append(score(a,b) + (False,))
    return lots

print("Compute scores for random non-matches")
with multiprocessing.Pool() as p:
    res = p.map(generate_nonmatch_scores, [None for i in range(multiprocessing.cpu_count())])

negative = pd.DataFrame(list(itertools.chain(*res)), columns=score_columns + ["label"])
del(res)
