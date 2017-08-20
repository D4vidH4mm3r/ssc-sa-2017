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

def geo(loc1, loc2, max_dist=6e5):
    if loc1 == loc2:
        return 1
    if not (loc1 in _gps and loc2 in _gps):
        return 0
    dist = geo_dist(*_gps[loc1], *_gps[loc2])
    return max(0, 1 - dist/max_dist)

# en string similarity (relativ til længste streng)
def string_linear(a, b):
    d = editdistance.eval(a, b)
    return 1 - d / (max(len(a), len(b), 1))

# en anden (omvendt proportional)
def string_inverse(a,b):
    d = editdistance.eval(a,b)
    return 1 / (1 + (d/(1 + len(a) + len(b))))

def birthyear(y1, y2, max_dist=4):
    # lineært skalering med max
    return max(0, 1 - (abs(y1 - y2)/max_dist))

ugift, gift, enke, fraskilt, forlovet = range(0, 5)
ukendt = -1

_follow_status = {
    enke: {
        gift: 0.5,
        fraskilt: 0.1,
        forlovet: 0.5
    },
    ugift: {
        gift: 0.8,
        forlovet: 1,
        fraskilt: 0.5,
        enke: 0.1
    },
    gift: {
        fraskilt: 0.6,
        enke: 0.8
    },
    fraskilt: {
        forlovet: 0.3,
        gift: 0.2
    },
    forlovet: {
        gift: 0.9,
        fraskilt: 0.2,
        enke: 0.3
    }
}

def parse_string(status):
    if status[0:4].lower() == "enke":
        return enke
    elif status[0:4].lower() == "gift":
        return gift
    elif status[0:5].lower() == "ugift":
        return ugift
    elif status[0:6].lower() == "fraskil" or status[0:8].lower() == "separeret":
        return fraskilt
    elif status[0:7].lower() == "forlovet":
        return forlovet
    else:
        return ukendt

def status(status1, status2):
    status1 = parse_string(status1)
    status2 = parse_string(status2)
    if status1 == -1 or status2 == -1:
        return 0
    elif status1 == status2:
        return 1
    elif status1 != status2:
        return _follow_status[status1].get(status2, 0)
