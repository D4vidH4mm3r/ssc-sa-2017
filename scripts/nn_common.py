import random
import tensorflow as tf
import numpy as np
import re
import pandas as pd
import utils
import editdistance
import csv


def ss(a: str, b: str):
    """Dissimilarity score for two strings a and b"""
    if pd.isnull(a) or pd.isnull(b):
        return 1
    a = a.lower().translate(utils.trans)
    b = b.lower().translate(utils.trans)
    if a==b:
        return 0
    return editdistance.eval(a, b) / ((len(a) + len(b))/2)

score_columns="r_name r_fname r_fonname r_birthp r_fonbirth r_civil r_pos r_job m_gender d_birthy".split(" ")
def score(a, b):
    return (ss(a.Navn, b.Navn),
            ss(a.Fornavn, b.Fornavn),
            ss(a.FonetiskNavn, b.FonetiskNavn),
            ss(a.Fødested, b.Fødested),
            ss(a.FonetiskFødested, b.FonetiskFødested),
            ss(a.Civilstand, b.Civilstand), # denne er dum; lav om
            ss(a.Position, b.Position),
            ss(a.Erhverv, b.Erhverv),
            1.0 if a.Køn == b.Køn else 0.0,
            abs(a.Fødeår - b.Fødeår))

# # Build features

navn = tf.feature_column.numeric_column("r_name")
fornavn  = tf.feature_column.numeric_column("r_fname")
fonetisknavn = tf.feature_column.numeric_column("r_fonname")
fødested = tf.feature_column.numeric_column("r_birthp")
fonetiskfødested = tf.feature_column.numeric_column("r_fonbirth")
civilstand = tf.feature_column.numeric_column("r_civil")
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
    navn, fornavn, fonetisknavn, fødested, fonetiskfødested, civilstand, position, erhverv, køn, fødeår
], model_dir="model2", hidden_units=[7,5,3])

