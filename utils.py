import pathlib
import pickle
import collections


Entry = collections.namedtuple("Entry", "amt,herred,sogn,navn,køn,fødested,fødeår,civilstand,position,erhverv,husstnr,kipnr,løbenr")

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
