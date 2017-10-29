import difflib
import networkx as nx
import pandas
import sys
import pathlib
import concurrent.futures
import utils


print("Loading data for", sys.argv[1])
subset = pandas.read_pickle(sys.argv[1])
fn = pathlib.Path(sys.argv[1])
fout = (utils.workdir / "matches") / fn.name
print("Will write matches to", fout)
by_year = subset.groupby("FT")

# Der er nogle fødesteder med flere ord, som endnu ikke håndteres.  Det kan vist nemt ordnes, men hører ikke til her (der er rigeligt med spaghetti allerede).

# # Prøv at finde nogle fornuftige matches
# ## Matches som max-weight matching
# Det ligger jo i navnet at det er en god ide.  For de uindviede: <a href="https://en.wikipedia.org/wiki/Matching_(graph_theory)">wiki</a>.

# Vil bruge edit distances til vægte - tager fødested $d_p$ og $d_n$ (ratio ens i stedet for direkte edit distance; længere navne kan have flere fejl; ratio går fra 0 til 1 hvor 1 betyder "ens").  Desuden tillader jeg op til 3 års fejl i angivelse af fødselsår (forskel $d_y$; her er det bare absolut forskel (mindre er bedre)).

# Det hele er bare et eksperiment.  Nedenfor tilføjes kun kanter hvis $d_y \leq 3 \wedge d_n \geq 0.85$.  Vægte på kanter straffes for alle variabler, men måske med $d_n$ (problem: giver 0 hvis fødested er angivet helt forskelligt, men det kan være okay - se kommentarer til sidst).  Formel for vægt er lige nu:
# $$w = d_n^2 \cdot d_p \cdot \frac{1}{1 + \frac{d_n}{3}}$$

a_year = 1845
a_data = by_year.get_group(a_year)

b_year = 1850
b_data = by_year.get_group(b_year)

print("Building graph")

G = nx.Graph()

def doWork(G, chunk, b_data):
    print("Staritng new chunk")
    diff_name = difflib.SequenceMatcher()
    diff_place = difflib.SequenceMatcher()

    for a in chunk.itertuples():
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

with concurrent.futures.ThreadPoolExecutor() as tpe:
    for chunk in utils.chunks(a_data, 100):
        tpe.submit(doWork, G, chunk, b_data)

print("Finding matching")
match = nx.max_weight_matching(G, maxcardinality=False)
match = sorted(set(tuple(sorted(item)) for item in match.items()), key=lambda x: G[x[0]][x[1]]["weight"], reverse=True)

print("Writing it out")
with fout.open("w") as fd:
    for (a, b) in match:
        fd.write(str(G[a][b]["weight"]) + "\n")
        fd.write(subset.loc[[a]].to_csv(header=False))
        fd.write(subset.loc[[b]].to_csv(header=False))
        fd.write("\n")
