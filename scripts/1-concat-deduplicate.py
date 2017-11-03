import utils
import csv

with (utils.datadir / "clean" / "complete.csv").open("w", encoding="utf-8") as fout, \
     (utils.datadir / "clean" / "problematic.csv").open("w", encoding="utf-8") as pout:
    writer = csv.writer(fout, delimiter="|", lineterminator="\n")
    bad = csv.writer(pout, delimiter="|", lineterminator="\n")
    header = "FT|Amt|Herred|Sogn|Navn|Køn|Fødested|Fødeår|Civilstand|Position|Erhverv|Kipnr|Løbenr".split("|")
    writer.writerow(header)
    bad.writerow(header)
    for fn in sorted((utils.datadir / "raw").glob("UTF8_*.csv")):
        seen = {}
        dupes = 0
        year = utils.extractYear(str(fn))
        print(fn, year)
        with fn.open("r", encoding="utf-8") as fd:
            for line in fd:
                line = line.strip()
                split = line.split("|")
                
                # detect new header inside file
                if split[0] == "Amt" or split[-1] == "løbenr":
                    #print(line)
                    prevHeader = line
                    continue
                
                # delete any useless columns
                if prevHeader ==   'Amt|Herred|Sogn|aarfra|navn|køn|Fødested|Fødeaar|Civilstand|Position|Erhverv|kipnr|løbenr':
                    del(split[3])
                elif prevHeader == 'Amt|Herred|Sogn|aarfra|navn|køn|Fødested|Fødeaar|Civilstand|Stilling_i_husstanden|Erhverv|kipnr|løbenr':
                    del(split[3])
                    # stilling ~ position
                elif prevHeader == 'Amt|Herred|Sogn|navn|køn|Fødested|Fødeaar|Civilstand|Position|Erhverv|husstnr|kipnr|løbenr':
                    del(split[10]) # husstnr only appears seldomly, cannot be that useful
                elif prevHeader == 'Amt|Herred|Sogn|navn|køn|Fødested|Fødeaar|Civilstand|Position|Erhverv|kipnr|løbenr':
                    ... # ideal
                elif prevHeader == 'Amt|Herred|Sogn|navn|køn|Fødested|Fødeaar|Civilstand|stilling_i_husstanden|Erhverv|husstnr|kipnr|løbenr':
                    del(split[10]) # husstnr only appears seldomly, cannot be that useful
                    # stilling ~ position
                else:
                    print("Unknown header!")
                    print(prevHeader)
                    break
                split.insert(0, year)
                
                key = tuple(split[-2:]) # (løb, kip)
                if key in seen:
                    if seen[key] != split:
                        bad.writerow(seen[key])
                        bad.writerow(split)
                    dupes += 1
                    continue
                seen[key] = split
                writer.writerow(split)
        print(dupes, "duplicate lines")
        del(seen)
