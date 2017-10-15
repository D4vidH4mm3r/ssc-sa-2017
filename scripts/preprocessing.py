import pathlib
import re
import collections
import functools
import difflib
import operator
import warnings
import pickle
import csv
import pandas
import utils

# # Prep for pandas
# Headers seem to be one of:
#     'Amt|Herred|Sogn|aarfra|navn|køn|Fødested|Fødeaar|Civilstand|Position|Erhverv|kipnr|løbenr',
#     'Amt|Herred|Sogn|aarfra|navn|køn|Fødested|Fødeaar|Civilstand|Stilling_i_husstanden|Erhverv|kipnr|løbenr',
#     'Amt|Herred|Sogn|navn|køn|Fødested|Fødeaar|Civilstand|Position|Erhverv|husstnr|kipnr|løbenr',
#     'Amt|Herred|Sogn|navn|køn|Fødested|Fødeaar|Civilstand|Position|Erhverv|kipnr|løbenr',
#     'Amt|Herred|Sogn|navn|køn|Fødested|Fødeaar|Civilstand|stilling_i_husstanden|Erhverv|husstnr|kipnr|løbenr'

# # Initial
df = pandas.read_csv(str(utils.datadir / "clean"/ "complete.csv"),
                     delimiter="|",
                     low_memory=False,
                     converters={
                         "FT": int,
                         "Navn": str,
                         "Fødeår": str, # some are "", will be removed later
                         "Fødested": str # here, there are errors, too
                     })

# ## Discard bad rows
# ### Fødeår
# Empty fødeår is not useful...
print("Before dropping Fødeår==\"\":", len(df))
df.drop(df[df.Fødeår==""].index, inplace=True)
print("After:", len(df))
df.Fødeår = pandas.to_numeric(df.Fødeår)

# People weren't that old back then, so discard anyone who seems to be >100.  Or negative numbers obviously.
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

# **TODO**: extract names where possible; some are like `Dorthea Kirstine Hansen (Udøbt Pigebarn)` or `1 udøbt drengebarn [Iflg.KB.28/1-1845: Carl Christian Sørensen]` where there is actually a name even though they claim not to have one.
print("Before dropping unchristened children:", len(df))
df.drop(maybe_children.index, inplace=True)
print("After:", len(df))
del(maybe_children)
# Look at remaining rows containing "barn":

# ## Køn
# Look for "K" or "M" primarily.  Anything not seemingly gender related will be discarded for now...

def guessGender(s):
    s = s.lower()
    if "k" in s or "f" in s:
        return "K"
    if "m" in s:
        return "M"
    return "?"

df.Køn = df.Køn.astype(str).apply(guessGender)
print("Before dropping rows lacking gender:", len(df))
df.drop(df[df.Køn=="?"].index, inplace=True)
print("After:", len(df))

# We can just replace the field with Boolean values now.
Male, Female = False, True
df.Køn = df.Køn.apply(lambda s: Male if s=="M" else Female)

# # Check løbenr
# There is one guy with ",50000", lets remove him.  Løbenr seems to be "something,subnumber" and sometimes only the first something. But with only subnumber, what can be done?
print("Before dropping invalid løbenr:", len(df))
df.drop(df[df.Løbenr.str.startswith(",")].index, inplace=True)
print("After:", len(df))

# # Drop dårlige fødesteder

print("Now dropipng floaty Fødested")
df.drop(df[df.Fødested.apply(lambda x: isinstance(x, float))].index, inplace=True)
print(len(df))
print("Now dropipng empty Fødested")
df.drop(df[df.Fødested.apply(lambda x: x=="")].index, inplace=True)
print(len(df))


# # Checkpoint!
pandas.to_pickle(df, "cleaned.pickled")
