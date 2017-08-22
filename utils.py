import pathlib
import pickle
import collections
import re


commonHeader = "amt|herred|sogn|fornavn|middelnavn|efternavn|initialer|køn|fødested|fødeaar|civilstand|position|erhverv|husstnr|kipnr|løbenr"
# location of data - change on local machine maybe
datadir = pathlib.Path("../main/data")

# namedtuple to represent rows
class Entry(collections.namedtuple("Entry", "amt,herred,sogn,fornavn,mellemnavn,efternavn,initialer,køn,fødested,fødeår,civilstand,position,erhverv,husstnr,kipnr,løbenr")):
    __slots__ = ()
    def toRow(entry):
        return "|".join(str(field) for field in iter(entry))

# so far, only birthyear is int
def parseEntry(line):
    split = line.strip().split("|")
    split[9] = int(split[9])
    return Entry(*split)

# for saving already seen matches - not currently used
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

# context manager pattern (to handle opening and closing - plus streaming)
class AllEntries():
    def __enter__(self, files=None):
        self.files = files if files is not None else sorted(datadir.glob("lc_*.csv"))
        self.fds = set()
        return self

    def __exit__(self, *stuff):
        for fd in self.fds:
            fd.close()

    def getEntries(self):
        for fn in self.files:
            year = int(re.search(r"\d{4}", fn.name).group(0))
            fd = fn.open("r", encoding="UTF-8")
            next(fd) # skip header
            self.fds.add(fd)
            yield (fn, year, (parseEntry(line) for line in fd))
