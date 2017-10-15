import pathlib
import csv
import getch
import random


cwd = pathlib.Path(".")
approved_file = cwd / "matches.csv"
discard_file = cwd / "notmatches.csv"

input_file = random.choice(list((cwd / "matches").iterdir()))

header = "pandas|FT|Amt|Herred|Sogn|Navn|Køn|Fødested|Fødeår|Civilstand|Position|Erhverv|Kipnr|Løbenr".split("|")

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


seen = set()

def nowISee(row):
    seen.add(tuple(row[-2:]))

def alreadySeen(row):
    return tuple(row[-2:]) in seen

def seeItAll(fn):
    with fn.open("r", encoding="utf-8") as fd:
        reader = csv.reader(fd)
        for row in reader:
            nowISee(row)


seeItAll(approved_file)
seeItAll(discard_file)

with input_file.open("r", encoding="utf-8") as fin, \
     approved_file.open("a", encoding="utf-8") as fapprove, \
     discard_file.open("a", encoding="utf-8") as fdiscard:
    reader = csv.reader(fin)
    writer_approve = csv.writer(fapprove)
    writer_discard = csv.writer(fdiscard)
    while True:
        try:
            score = float(next(reader)[0])
            a = next(reader)
            b = next(reader)
            next(reader) # empty line delimits pairs

            if alreadySeen(a) or alreadySeen(b):
                print("This seems familiar, don't bother")
                continue

            nowISee(a)
            nowISee(b)

            if score==1 and a[2:5] == b[2:5]: # same place, name, birth(year,place)
                print("Good match, don't look")
                writer_approve.writerow(a)
                writer_approve.writerow(b)
                continue

            if int(a[1]) > int(b[1]):
                a, b = b, a
            print(score)
            for i in range(1,12):
                s = "{:10s} {:40s} {:40s}".format(header[i], a[i], b[i])
                if a[i] != b[i]:
                    s = color.BOLD + s + color.END
                print(s)
            print("Good match (y) or bad (n)? (any other key to skip)")
            c = getch.getch()
            if c in "Yy":
                print("Okay, saving match")
                writer_approve.writerow(a)
                writer_approve.writerow(b)
            elif c in "Nn":
                print("Wheh, glad you caught that!")
                writer_discard.writerow(a)
                writer_discard.writerow(b)
            else:
                print("Okay, let's leave them for now")

        except StopIteration:
            print("File is empty now, good job!")
            break
