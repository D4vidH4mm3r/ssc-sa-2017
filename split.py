import pathlib
import re
import collections
import functools
import difflib
import operator
import warnings
import pickle
import pandas
import csv


df = pandas.read_pickle("tmp.pickled") # from cleaning checkpoint

# **TODO**: Bedre initial-ekstraktion

_common_hard_c = set(("cristen", "cristian", "cristine", "carlotte", "catrine",
                    "carl", "caroline", "cathrine", "cirstine", "carel", "catarine"))
def initial_block(name):
    name = name.lower()
    # group k-like sounds with c into k
    if name.startswith("c"):
        if name in _common_hard_c:
            return "k" + name[1]
        if name.startswith("ch"):
            return "k" + name[2]
    # group czs into c
    if name[0] in "sz":
        return "c" + name[1]
    return name[:2]

root = pathlib.Path(".")
(root / "m").mkdir()
(root / "f").mkdir()

fds = {}
writers = {}
header = "FT|Amt|Herred|Sogn|Navn|Køn|Fødested|Fødeår|Civilstand|Position|Erhverv|Kipnr|Løbenr".split("|")
for t in df.itertuples():
    initials = initial_block(t.Navn)
    if not initials.isalpha():
        continue
    if t.Køn:
        pair = ("f", initials)
    else:
        pair = ("m", initials)
    if pair in fds:
        fd = fds[pair]
        writer = writers[pair]
    else:
        fd = (root / pair[0] / (pair[1] + ".csv")).open("w", encoding="UTF-8")
        writer = csv.writer(fd, delimiter="|", lineterminator="\n")
        writer.writerow(header)
        fds[pair] = fd
        writers[pair] = writer
    writer.writerow(t)


# In[ ]:

for fd in fds.values():
    fd.close()
