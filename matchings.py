
# coding: utf-8

# In[1]:

import pathlib
import re
import collections
import functools
import difflib
import operator
import networkx as nx
import warnings
import pickle
import pandas
warnings.simplefilter('ignore') # for networkx drawing
import matplotlib.pylab
get_ipython().magic('matplotlib inline')
matplotlib.pylab.rcParams["figure.figsize"] = (14, 18)


# In[2]:

get_ipython().magic('run utils.py')


# In[3]:

df = pandas.read_pickle("tmp.pickled") # from cleaning checkpoint


# Bruger namedtuples for at gøre koden senere nemmere. Og de kan hashes, så vi kan have sets og dicts.

# # Test blocking

# Ide: blocking på initialer. Problemer:
# - varierende brug af s/z, c/k m.m.?
#     - forslag: "normaliser" fonetisk hvis muligt (s/z let så længe c er strengt til k)
#     - forslag: overlappende grupper; det kan jeg slet ikke gennemskue
# - udeladte navne (det kan vi droppe alligevel)

# In[4]:

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


# In[5]:

men = collections.Counter()
women = collections.Counter()

for entry in df.itertuples():
    parts = entry.Navn.split()
    if len(parts[0]) < 2:
        continue
    if entry.Køn:
        women.update((parts[0].lower().translate(trans),))
    else:
        men.update((parts[0].lower().translate(trans),))
#    last_names.update((parts[0],))


# In[6]:

len(men)


# In[7]:

order = list(sorted(men))


# In[10]:

with open("men.txt", "w", encoding="utf-8") as fd:
    for name in order:
        fd.write(name + "\n")


# In[11]:

with open("women.txt", "w", encoding="utf-8") as fd:
    for name in sorted(women):
        fd.write(name + "\n")


# In[12]:

part = order[:100]


# In[13]:

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


# In[19]:

import numpy as np


# In[29]:

res = np.zeros([len(part),len(part)])


# In[32]:

res


# In[31]:

chunk_size = 25
for chunk_num, chunk in enumerate(chunks(part, 25)):
    m = difflib.SequenceMatcher()
    for i_a, person_a in enumerate(chunk):
        m.set_seq1(person_a)
        for i_b, person_b in enumerate(part):
            m.set_seq2(person_b)
            ratio = m.ratio()
            index_a = chunk_num*chunk_size+i_a
            res[index_a, i_b] = ratio
            #res[i_b, index_a] = ratio


# In[ ]:

m.set_seq1


# In[ ]:

difflib.SequenceMatcher


# In[8]:

order


# In[41]:

len(women)


# **TODO**: Bedre initial-ekstraktion

# In[36]:

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
_common_hard_c = set(("cristen", "cristian", "cristine", "carlotte", "catrine",
                    "carl", "caroline", "cathrine", "cirstine", "carel", "catarine"))
def initial_block(name):
    name = name.lower().translate(trans)
    # group k-like sounds with c into k
    if name.startswith("c"):
        if name in _common_hard_c:
            return "k" + name[1]
        if name.startswith("ch"):
            return "k" + name[2]
    # group czs into c
    #if name[0] in "sz":
        #return "c" + name[1]
    return name[:2]


# In[38]:

for name, freq in women.most_common(200):
    print(initial_block(name), name)


# In[ ]:

Male, Female = False, True


# In[ ]:

root = pathlib.Path(".")
(root / "m").mkdir()
(root / "f").mkdir()


# In[ ]:

import csv


# In[ ]:

fds = {}
writers = {}
header = "FT|Amt|Herred|Sogn|Navn|Køn|Fødested|Fødeår|Civilstand|Position|Erhverv|Kipnr|Løbenr".split("|")
for t in df.itertuples():
    initials = initial_block(t.Navn)
    if not initials.isalpha():
        continue
    if t.Køn:
        pair = ("f", initials)
    else:
        pair = ("m", initials)
    if pair in fds:
        fd = fds[pair]
        writer = writers[pair]
    else:
        fd = (root / pair[0] / (pair[1] + ".csv")).open("w", encoding="UTF-8")
        writer = csv.writer(fd, delimiter="|", lineterminator="\n")
        writer.writerow(header)
        fds[pair] = fd
        writers[pair] = writer
    writer.writerow(t)


# In[ ]:

for fd in fds.values():
    fd.close()


# ## Indlæs data for et subset
# 
# **Skal opdateres!**
# 
# Bemærk: alt det med rettelse af fødested herunder burde gøres i de cleanede `lc_`-datafiler, ikke her.
# 
# For resten så begrænser jeg også lige navne for at få endnu færre rækker; arbejder på min bærbare lige nu.

# In[71]:

df.drop(df[df.Fødested.apply(lambda x: isinstance(x, float))].index, inplace=True)


# In[72]:

subset = df[df.Køn == False & df.Navn.str.startswith("Ch")]


# In[73]:

by_year = subset.groupby("FT")


# Der er nogle fødesteder med flere ord, som endnu ikke håndteres.  Det kan vist nemt ordnes, men hører ikke til her (der er rigeligt med spaghetti allerede).

# # Prøv at finde nogle fornuftige matches
# ## Matches som max-weight matching
# Det ligger jo i navnet at det er en god ide.  For de uindviede: <a href="https://en.wikipedia.org/wiki/Matching_(graph_theory)">wiki</a>.

# Vil bruge edit distances til vægte - tager fødested $d_p$ og $d_n$ (ratio ens i stedet for direkte edit distance; længere navne kan have flere fejl; ratio går fra 0 til 1 hvor 1 betyder "ens").  Desuden tillader jeg op til 3 års fejl i angivelse af fødselsår (forskel $d_y$; her er det bare absolut forskel (mindre er bedre)).

# In[75]:

diff_name = difflib.SequenceMatcher()
diff_place = difflib.SequenceMatcher()


# Det hele er bare et eksperiment.  Nedenfor tilføjes kun kanter hvis $d_y \leq 3 \wedge d_n \geq 0.85$.  Vægte på kanter straffes for alle variabler, men måske med $d_n$ (problem: giver 0 hvis fødested er angivet helt forskelligt, men det kan være okay - se kommentarer til sidst).  Formel for vægt er lige nu:
# $$w = d_n^2 \cdot d_p \cdot \frac{1}{1 + \frac{d_n}{3}}$$

# In[76]:

a_year = 1845
a_data = by_year.get_group(a_year)


# In[77]:

b_year = 1850
b_data = by_year.get_group(b_year)


# In[78]:

next(a_data.itertuples())


# In[90]:

G = nx.Graph()
for a in a_data.itertuples():
    diff_name.set_seq1(a.Navn)
    diff_place.set_seq1(a.Fødested)

    for b in b_data.itertuples():
        # first filter really bad matches
        age_diff = abs(a.Fødeår - b.Fødeår)
        if age_diff > 3:
            continue

        diff_name.set_seq2(b.Navn)
        ratio_name = diff_name.ratio()
        if ratio_name < 0.85:
            continue
        
        diff_place.set_seq2(b.Fødested)
        ratio_place = diff_place.ratio()
        
        # if maybe decent match, add edge
        w = ratio_name**2 * ratio_place * 1/(1+age_diff/3)
        G.add_edge(a.Index, b.Index, weight=w)


# In[121]:

match = nx.max_weight_matching(G, maxcardinality=True)
match = list(match.items())


# In[122]:

match


# In[123]:

sorted(match, key=lambda x: G[x[0]][x[1]]["weight"], reverse=True)


# In[112]:

pair = subset.loc[[29,2291021]]


# In[124]:

print(pair.to_csv(header=False))


# In[105]:

import csv


# In[106]:

with open("testing.csv", "w") as fd:
    writer = csv.writer(fd)
    writer.writerow(subset.loc[60])


# In[ ]:

subset


# In[107]:

hmm = pandas.read_csv("testing.csv")


# In[108]:

hmm


# In[ ]:



