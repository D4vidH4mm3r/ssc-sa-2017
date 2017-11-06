#!/opt/sys/apps/python/3.6.0/bin/python

from nn_common import *
import random
import itertools
import multiprocessing


print("Loading scores")
print("First for positive matches")
dtypes = {c: np.float64 for c in score_columns}
dtypes["label"] = bool
dtypes["t_civil"] = str
positive = pd.read_csv(str(utils.workdir / "scores-positive.csv"), dtype=dtypes)
positive.dropna(inplace=True)
print("And then for negative matches")
negative = pd.read_csv(str(utils.workdir / "scores-negative.csv"), dtype=dtypes)
negative.dropna(inplace=True)
print("Done loading")

df_train = pd.concat([positive[:-1000], negative[:-2000]])
df_eval = pd.concat([positive[-1000:], negative[-2000:]])

# Train and evaluate models
print("Train some models")

# set up input functions
input_fn_train = tf.estimator.inputs.pandas_input_fn(x=df_train, y=df_train.label, shuffle=True)
input_fn_eval = tf.estimator.inputs.pandas_input_fn(x=df_eval, y=df_eval.label, shuffle=False)

# Linear model
print("First a simple linear model")
#model1.train(input_fn=input_fn_train)
print(model1.evaluate(input_fn=input_fn_train))

# DNN model
print("Then a DNN")
model2.train(input_fn_train)
print(model2.evaluate(input_fn_train))
