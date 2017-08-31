import pathlib
import pickle
import collections
import re


def extractYear(s):
    return int(re.search(r"\d{4}", s).group(0))

# location of data - change on local machine maybe
datadir = pathlib.Path("../data")

_common_hard_c = set(("cristen", "cristian", "cristine", "carlotte", "catrine",
                    "carl", "caroline", "cathrine", "cirstine", "carel", "catarine"))
def initial_block(name):
    # group k-like sounds with c into k
    if name.startswith("c"):
        if name in _common_hard_c or name.startswith("ch"):
            return "k"
    # group czs into c
    if name[0] in "sz":
        return "c"
    return name[0]
