# dependencies: python3.6, editdistance
import pathlib
import re
import collections
import functools
import difflib
import operator
import json
import time
import editdistance
import random
import math

# ret til
datadir = pathlib.Path("/home/david/pro/scc/data")

with (datadir / "gps-coords.csv").open("r", encoding="utf-8") as fd:
    next(fd)
    _gps = {}
    for line in fd:
        place, lat, lon = line.split("|")
        _gps[place] = (float(lat), float(lon))

# geografisk (til fødested)
def geo_dist(lat1, lon1, lat2, lon2):
    # pasta
    R = 6371e3 # Jordens radius i meter
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δφ = math.radians(lat2-lat1)
    Δλ = math.radians(lon2-lon1)

    a = math.sin(Δφ/2) * math.sin(Δφ/2) + \
            math.cos(φ1) * math.cos(φ2) * \
            math.sin(Δλ/2) * math.sin(Δλ/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def geo_similarity(loc1, loc2, max_dist=6e5):
    if loc1 == loc2:
        return 1
    if not (loc1 in _gps and loc2 in _gps):
        return 0
    dist = geo_dist(*_gps[loc1], *_gps[loc2])
    return max(0, 1 - dist/max_dist)

# en string similarity (relativ til længste streng)
def string_similarity_linear(a, b):
    d = editdistance.eval(a, b)
    return 1 - d / (max(len(a), len(b), 1))

# en anden (omvendt proportional)
def string_similarity_inverse(a,b):
    d = editdistance.eval(a,b)
    return 1 / (1 + (d/(1 + len(a) + len(b))))