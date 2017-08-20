import pathlib
import pickle
import collections
import re

Entry = collections.namedtuple("Entry", "amt,herred,sogn,fornavn,mellemnavn,efternavn,initialer,køn,fødested,fødeår,civilstand,position,erhverv,husstnr,kipnr,løbenr")
def parseEntry(line):
    split = line.strip().split("|")
    split[9] = int(split[9])
    return Entry(*split)

class ApprovedMatches:
    def __init__(self, fn):
        if not isinstance(fn, pathlib.Path):
            fn = pathlib.Path(fn)
        self.fn = fn
        if not fn.exists():
            self.data = {}
        else:
            self.load()
                
    def add_match(self, y1, y2, r1, r2):
        self.data.setdefault((y1, y2), set()).add((r1, r2))
    
    def flush(self):
        with self.fn.open("wb") as fd:
            pickle.dump(self.data, fd)
            
    def load(self):
        with self.fn.open("rb") as fd:
            self.data = pickle.load(fd)

re_sogn_amt = re.compile(r"(.+) \[?sogn\]?,? ?(.+) \[?amt\]?")
re_do_sogn = re.compile(r"do \[(.+)\]")
_trans = {
    "kjøbenhavn": "københavn",
    "kiøbenhavn": "københavn",
    "kbhvn": "københavn",
    "sverrig": "sverige",
    "sverige": "sverige",
    "aarhus": "århus",
    "aarhuus": "århus",
    "rønne købstad - bornholms amt": "rønne",
    "kbhv": "københavn"
}
def normalize_more(place):
    if place in ("do", "do.", "her", "født i sognet", "dito", "sognet", "h. i s."):
        return None
    elif place in _trans:
        return _trans[place]
    match = re_sogn_amt.match(place)
    if match:
        return match.group(1)
    match = re_do_sogn.match(place)
    if match:
        return match.group(1)
    return place