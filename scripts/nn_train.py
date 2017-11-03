#!/opt/sys/apps/python/3.6.0/bin/python

from nn_common import *
import random
import itertools


print("Loading golden standard")
matches = pd.read_csv(str(utils.datadir / "links" / "matches.csv"), sep="|")
print("Loading big dataframe")
df = pd.read_pickle("dataframe.pickled")
print("Doing some indexing")
df.dropna(subset=("Fødeår",), inplace=True)
df.set_index(["FT", "Kipnr", "Løbenr"], inplace=True)
df.sort_index(inplace=True)

def to_scored_frame(d):
    lots = []
    for t in d.itertuples():
        try:
            # TODO: optimize access
            s = df.loc[[t[1:4], t[4:]]]
            a = s.iloc[0]
            b = s.iloc[1]
        except KeyError:
            continue
        lots.append(score(a,b) + (True,))
    return pd.DataFrame(lots, columns=score_columns + ["label"])

years = [1845, 1850, 1860, 1880, 1885]

ssize = 100
def generate_nonmatch_scores(_):
    lots = []
    s = df.loc[random.choice(years)].sample(ssize)
    for i in range(ssize-1):
        a = s.iloc[i]
        b = s.iloc[i+1]
        lots.append(score(a,b) + (False,))
    return lots

print("Compute scores for random non-matches")
with multiprocessing.Pool() as p:
    res = p.map(generate_nonmatch_scores, [None for i in range(multiprocessing.cpu_count())])

negative = pd.DataFrame(list(itertools.chain(*res)), columns=score_columns + ["label"])
del(res)
print("Compute scores for some good matches")
positive = utils.parallelize(matches[:3000], to_scored_frame)

df_train = pd.concat([positive, negative])
df_train.dropna(inplace=True)

print("Train some models")
# # Train and evaluate models

# ## Linear model
input_fn_train = tf.estimator.inputs.pandas_input_fn(
    x=df_train,
    y=df_train.label,
    shuffle=True)
model1.train(input_fn=input_fn_train)
print(model1.evaluate(input_fn=input_fn_train))

# ## DNN model
model2.train(input_fn_train)
print(model2.evaluate(input_fn_train))
