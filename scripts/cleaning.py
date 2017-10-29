
# coding: utf-8

# In[ ]:


import pathlib
import re
import collections
import difflib
import pandas
import utils


# # Initial
# ## Read stuff

# In[ ]:


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


# # Drop more NaN!
# Basically, we need to have name, birthplace and birthyear for sure.  Probably also more.

# In[ ]:


print("Before dropping stupid NaN fields", len(df))
df.dropna(subset=["Fødested", "Navn", "Fødeår", "Køn"], inplace=True)
len(df)


# # Fix the birthplace field

# ## Part one: replace "i sognet"

# In[ ]:


def maybeInSogn(s):
    s = s.lower().strip()
    return "i sognet" in s or         s == "sognet" or         re.search(r"h(er|\.)? i s", s) is not None


# In[ ]:


sogn = df.Fødested.apply(maybeInSogn)


# In[ ]:


df.loc[sogn, "Fødested"] = df.Sogn


# In[ ]:


sogn = df[df.Fødested.str.contains("sogn", case=False)]


# Look for more (not done)

# In[ ]:


sogn.Fødested.str.lower().value_counts()


# In[ ]:


del(sogn)


# ## Part two: change "ditto" or "do" into previous
# Note that this is very sensitive to data reordering; consider sorting first.

# In[ ]:


replacements = []
for r in df.itertuples():
    s = r.Fødested.lower()
    if re.search(r"\b(do|ditto)\b", s):
        replacements.append((r.Index, prev))
    else:
        prev = r.Fødested


# In[ ]:


print("Updating birthplace for", len(replacements), "entries")


# In[ ]:


indices, values = zip(*replacements)


# In[ ]:


df.loc[list(indices), "Fødested"] = list(values)


# ## Discard bad rows

# ### Fødeår
# People weren't that old back then, so discard anyone who seems to be >100.  Or negative numbers obviously - *intentionally used to represent missing fødeår*.

# In[ ]:


ages = df.FT - df.Fødeår


# In[ ]:


print("Before dropping age > 100:", len(df))
df.drop(df[ages>100].index, inplace=True)
print("After:", len(df))
print("Before dropping age < 0:", len(df))
df.drop(df[ages<0].index, inplace=True)
print("After:", len(df))


# In[ ]:


del(ages)


# ### Navn

# In[ ]:


print("Before dropping empty names with no letters:", len(df))
df.drop(df[df.Navn.str.match(r"^[^a-zæøå]*$", case=False)].index, inplace=True)
print("After:", len(df))


# Get rid of children without names.

# In[ ]:


def isProbablyChild(s):
    s = s.lower()
    return "barn" in s and ("navn" in s or
                           "døbt" in s or
                           "dreng" in s or
                           "pige" in s or
                           "nyfødt" in s)


# In[ ]:


maybe_children = df[df.Navn.map(isProbablyChild).astype(bool, copy=False)]


# **TODO**: extract names where possible; some are like `Dorthea Kirstine Hansen (Udøbt Pigebarn)` or `1 udøbt drengebarn [Iflg.KB.28/1-1845: Carl Christian Sørensen]` where there is actually a name even though they claim not to have one.

# In[ ]:


maybe_children.Navn.value_counts()


# In[ ]:


print("Before dropping unchristened children:", len(df))
df.drop(maybe_children.index, inplace=True)
print("After:", len(df))
del(maybe_children)


# Look at remaining rows containing "barn":

# In[ ]:


maybe_children = df[df.Navn.str.contains("barn", case=False)]


# In[ ]:


maybe_children.Navn.value_counts()


# ## Køn
# Look for "K" or "M" primarily.  Anything not seemingly gender related will be discarded for now...

# In[ ]:


def guessGender(s):
    s = s.lower()
    if "k" in s or "f" in s:
        return "K"
    if "m" in s:
        return "M"
    return "?"


# In[ ]:


df.Køn = df.Køn.astype(str).apply(guessGender)


# In[ ]:


df.Køn.value_counts()


# In[ ]:


print("Before dropping rows lacking gender:", len(df))
df.drop(df[df.Køn=="?"].index, inplace=True)
print("After:", len(df))


# We can just replace the field with Boolean values now.

# In[ ]:


Male, Female = False, True


# In[ ]:


df.Køn = df.Køn.apply(lambda s: Male if s=="M" else Female)


# # Check løbenr

# There is one guy with ",50000", lets remove him.  Løbenr seems to be "something,subnumber" and sometimes only the first something. But with only subnumber, what can be done?

# In[ ]:


re.search(r"\d*,\d*[1-9]\d*", "12341234,00000")


# In[ ]:


print("Before dropping annoying løbenr:", len(df))
df.drop(df[df.Løbenr.str.match(r"\d*,\d*[1-9]\d*")].index, inplace=True)
print("After:", len(df))


# Then we can make it int...

# In[ ]:


df.Løbenr = df.Løbenr.apply(lambda s: s.split(",")[0] if "," in s else s).astype(int)


# In[ ]:


def extract_fornavn(s):
    s = s.replace(".", " ")
    return s.split()[0]


# In[ ]:


df["Fornavn"] = df.Navn.apply(extract_fornavn)


# In[ ]:


import metaphone


# In[ ]:


def make_keys(names):
    def f(s):
        return metaphone.doublemetaphone(s.translate(utils.trans))[0]
    return names.apply(f)
df["FonetiskNavn"] = utils.parallelize(df.Navn, make_keys)
df["FonetiskFødested"] = utils.parallelize(df.Fødested, make_keys)


# # Checkpoint!

# In[ ]:


pandas.to_pickle(df, "dataframe.pickled")


# # Continue!

# df = pandas.read_pickle("tmp.pickled")
