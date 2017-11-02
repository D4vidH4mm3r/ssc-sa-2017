import pathlib
import csv
import getch
import random
import pandas as pd
import sys


# TODO: update
input_file = pathlib.Path("complete.csv")
accept_file = pathlib.Path("good.csv")
reject_file = pathlib.Path("bad.csv")

# see https://stackoverflow.com/questions/8924173/how-do-i-print-bold-text-in-python
class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# find known matches; index by left guy
print("Starting by reading accepted matches so we don't see them again")
seen = {}
for fn in ("good.csv", "data/links/matches.csv"):
    print(fn)
    tmp = pd.read_csv(str(fn), delimiter="|", comment="#")
    for t in tmp.itertuples():
        seen[(t.a_FT, t.a_Kipnr, t.a_Løbenr)] = (t.b_FT, t.b_Kipnr, t.b_Løbenr)

print("And also remember already rejected matches")
rejected = {}
tmp = pd.read_csv("bad.csv", delimiter="|", comment="#")
for t in tmp.itertuples():
    rejected[(t.a_FT, t.a_Kipnr, t.a_Løbenr)] = (t.b_FT, t.b_Kipnr, t.b_Løbenr)

# to look stuff up in
print("Reading in big data file")
lookup = pd.read_pickle("experiments/scripts/dataframe.pickled")
print("Indexing...")
lookup.set_index(["FT", "Kipnr", "Løbenr"], inplace=True)
print("Sorting...")
lookup.sort_index(inplace=True)

# the matches to review
print("Now getting list of matches")
matches = pd.read_csv(str(input_file), delimiter="|", comment="#")
matches.sort_values(by="p", ascending=False, inplace=True)

# for printing
header = "Amt|Herred|Sogn|Navn|Køn|Fødested|Fødeår|Civilstand|Position|Erhverv|Kipnr|Løbenr|Group".split("|")
with accept_file.open("a", encoding="utf-8") as fapprove, \
        reject_file.open("a", encoding="utf-8") as fdiscard:
    writer_acc = csv.writer(fapprove, lineterminator="\n", delimiter="|")
    writer_rej = csv.writer(fdiscard, lineterminator="\n", delimiter="|")

    for _, a_FT, a_Kip, a_Løb, b_FT, b_Kip, b_Løb, prob in matches.itertuples():
        a_key = (a_FT, a_Kip, a_Løb)
        b_key = (b_FT, b_Kip, b_Løb)

        # maybe no need to look at this again
        if a_key in seen:
            print("Have already accepted this match!")
            if b_key != seen[a_key]:
                print("Fun fact: was different")
            continue

        if a_key in rejected and rejected[a_key] == b_key:
            print("Have already rejected this match")
            continue

        # okay let's look them up
        a = lookup.loc[(a_FT, a_Kip, a_Løb)]
        b = lookup.loc[(b_FT, b_Kip, b_Løb)]
        # pretty-printing what we know
        print("FT", a_FT, "vs", b_FT)
        for i in range(1,10):
            s = "{:10s} {:40s} {:40s}".format(header[i], str(a[i]), str(b[i]))
            if a[i] != b[i]:
                s = color.BOLD + s + color.END
            print(s)

        # make a decision
        print("Good match (y) or bad (n)? (q to quit, any other key to skip)")
        c = getch.getch()
        if c in "Yy":
            print("Okay, saving match")
            writer_acc.writerow([a_FT, a_Kip, a_Løb, b_FT, b_Kip, b_Løb])
        elif c in "Nn":
            print("Wheh, glad you caught that!")
            writer_rej.writerow([a_FT, a_Kip, a_Løb, b_FT, b_Kip, b_Løb])
        elif c in "Qq":
            print("Okay bye!")
            break
        else:
            print("Okay, let's leave them for now")
