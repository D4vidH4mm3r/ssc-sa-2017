import pathlib
import re
import collections
import difflib
import pandas
import utils

df = pandas.read_csv(str(utils.datadir / "clean"/ "complete.csv"),
                     delimiter="|",
                     dtype={
                         "FT": int,
                         "Navn": str,
                         "Erhverv": str,
                         "Kipnr": str,
                         "Fødested": str,
                         "Løbenr": str
                     },
                    converters={
                        "Fødeår": (lambda x: -1000 if x=="" else int(x)) # missing fødeår for some
                    })

print("Before dropping stupid NaN fields", len(df))
df.dropna(subset=["Fødested", "Navn", "Fødeår", "Køn"], inplace=True)
len(df)

def maybeInSogn(s):
    s = s.lower().strip()
    return "i sognet" in s or \
            s == "sognet" or \
            re.search(r"h(er|\.)? i s", s) is not None

sogn = df.Fødested.apply(maybeInSogn)
df.loc[sogn, "Fødested"] = df.Sogn
sogn = df[df.Fødested.str.contains("sogn", case=False)]
del(sogn)

# ## Part two: change "ditto" or "do" into previous
# Note that this is very sensitive to data reordering; consider sorting first.
replacements = []
for r in df.itertuples():
    s = r.Fødested.lower()
    if re.search(r"\b(do|ditto|dito)\b", s):
        replacements.append((r.Index, prev))
    else:
        prev = r.Fødested

print("Updating birthplace for", len(replacements), "entries")
indices, values = zip(*replacements)
df.loc[list(indices), "Fødested"] = list(values)

# ## Discard bad rows

# ### Fødeår
# People weren't that old back then, so discard anyone who seems to be >100.  Or negative numbers obviously - *intentionally used to represent missing fødeår*.

ages = df.FT - df.Fødeår
print("Before dropping age > 100:", len(df))
df.drop(df[ages>100].index, inplace=True)
print("After:", len(df))
print("Before dropping age < 0:", len(df))
df.drop(df[ages<0].index, inplace=True)
print("After:", len(df))
del(ages)

# ### Navn
print("Before dropping empty names with no letters:", len(df))
df.drop(df[df.Navn.str.match(r"^[^a-zæøå]*$", case=False)].index, inplace=True)
print("After:", len(df))

# Get rid of children without names.
def isProbablyChild(s):
    s = s.lower()
    return "barn" in s and ("navn" in s or
                           "døbt" in s or
                           "dreng" in s or
                           "pige" in s or
                           "nyfødt" in s)
maybe_children = df[df.Navn.map(isProbablyChild).astype(bool, copy=False)]
print("Before dropping unchristened children:", len(df))
df.drop(maybe_children.index, inplace=True)
print("After:", len(df))
del(maybe_children)

def guessGender(s):
    s = s.lower()
    if "k" in s or "f" in s:
        return "K"
    if "m" in s:
        return "M"
    return "?"
df.Køn = df.Køn.astype(str).apply(guessGender)
df.Køn.value_counts()

print("Before dropping rows lacking gender:", len(df))
df.drop(df[df.Køn=="?"].index, inplace=True)
print("After:", len(df))
Male, Female = False, True
df.Køn = df.Køn.apply(lambda s: Male if s=="M" else Female)

# # Check løbenr
print("Before dropping annoying løbenr:", len(df))
df.drop(df[df.Løbenr.str.match(r"\d*,\d*[1-9]\d*")].index, inplace=True)
print("After:", len(df))
df.Løbenr = df.Løbenr.apply(lambda s: s.split(",")[0] if "," in s else s).astype(int)

def extract_fornavn(s):
    s = s.replace(".", " ")
    return s.split()[0]

df["Fornavn"] = df.Navn.apply(extract_fornavn)

import metaphone

def make_keys(names):
    def f(s):
        return metaphone.doublemetaphone(s.translate(utils.trans))
    return names.apply(f)

df["FonetiskNavn"] = utils.parallelize(df.Navn, make_keys)
df["FonetiskFødested"] = utils.parallelize(df.Fødested, make_keys)
print("Saving")
pandas.to_pickle(df, "dataframe.pickled")
df.set_index(["FT", "Kipnr", "Løbenr"], inplace=True)
df.sort_index(inplace=True)
pandas.to_pickle(df, "indexed.pickled")
