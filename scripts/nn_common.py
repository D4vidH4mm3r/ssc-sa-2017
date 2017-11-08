import random
import tensorflow as tf
import numpy as np
import re
import pandas as pd
import utils
import editdistance
import csv
import itertools


def ss(a: str, b: str):
    """Dissimilarity score for two strings a and b"""
    if pd.isnull(a) or pd.isnull(b):
        return 1
    a = a.lower().translate(utils.trans)
    b = b.lower().translate(utils.trans)
    if a==b:
        return 0
    return editdistance.eval(a, b) / max(len(a), len(b))

def ss_pair(A, B):
    # for metaphone string pairs
    best = 1
    for a in A:
        if a == "":
            continue
        for b in B:
            if b == "":
                continue
            best = min(best, ss(a, b))
    return best

score_columns="r_name r_fname r_fonname r_birthp r_fonbirth t_civil r_pos r_job m_gender d_birthy".split(" ")
def score(a, b):
    return (ss(a.Navn, b.Navn),
            ss(a.Fornavn, b.Fornavn),
            ss_pair(a.FonetiskNavn, b.FonetiskNavn), # metaphone pair
            ss(a.Fødested, b.Fødested),
            ss_pair(a.FonetiskFødested, b.FonetiskFødested), # metaphone pair
            a.Civilstand + b.Civilstand,
            ss(a.Position, b.Position),
            ss(a.Erhverv, b.Erhverv),
            1.0 if a.Køn == b.Køn else 0.0,
            abs(a.Fødeår - b.Fødeår))

# # Build features

navn = tf.feature_column.numeric_column("r_name")
fornavn = tf.feature_column.numeric_column("r_fname")
fonetisknavn = tf.feature_column.numeric_column("r_fonname")
fødested = tf.feature_column.numeric_column("r_birthp")
fonetiskfødested = tf.feature_column.numeric_column("r_fonbirth")
civilstand = tf.feature_column.categorical_column_with_vocabulary_list(
  "t_civil",
  list(a+b for (a,b) in itertools.product("uges?", repeat=2)))
position = tf.feature_column.numeric_column("r_pos")
erhverv = tf.feature_column.numeric_column("r_job")
køn = tf.feature_column.numeric_column("m_gender")
fødeår = tf.feature_column.numeric_column("d_birthy")

# # Build model

model1 = tf.estimator.LinearClassifier(feature_columns=[
    navn, fornavn, fonetisknavn, fødested, fonetiskfødested, civilstand, position, erhverv, køn, fødeår
], model_dir="model1")

# # Or other model

model2 = tf.estimator.DNNClassifier(feature_columns=[
    navn, fornavn, fonetisknavn, fødested, fonetiskfødested,
    tf.feature_column.indicator_column(civilstand), position, erhverv, køn, fødeår
], model_dir="model2", hidden_units=[7,5,3])

