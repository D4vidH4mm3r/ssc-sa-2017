import pathlib
import pickle
import collections
import re
import numpy as np
import multiprocessing
import pandas as pd
import platform


def extractYear(s):
    match = re.search(r"\d{4}", s)
    if match is None:
        return None
    return int(match.group(0))

# location of data - change on local machine maybe
if platform.node() in ("daviddesktop", "davidlaptop"):
    workdir = pathlib.Path("/home/david/ssc")
else:
    workdir = pathlib.Path("/work/sdusscsa2")
datadir = workdir / "data"

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

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

trans = {
    "ä": "a", "â": "a",
    "á": "a", "ë": "e",
    "è": "e", "é": "e",
    "ï": "i", "ö": "o",
    "ü": "u", "í": "i",
    "ó": "o", "ô": "o",
    "ú": "u", "ÿ": "y"
}
for trash in "!/\\'\".,-:;_0123456789<>=?[]¤÷%()*+…":
    trans[trash] = ""
trans = str.maketrans(trans)


def parallelize(data, func):
    cores = multiprocessing.cpu_count()
    partitions = cores
    data_split = np.array_split(data, partitions)
    pool = multiprocessing.Pool(cores)
    data = pd.concat(pool.map(func, data_split))
    pool.close()
    pool.join()
    return data
