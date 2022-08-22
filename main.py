import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


adni_merge  = "processed_ADNIMERGE.csv"
medhist = "processed_RECMHIST.csv"
df_adni = pd.read_csv(adni_merge)
df_mhist = pd.read_csv(medhist)

# get data in column a given that b is equal to the desired data c 
def get_patient_data(a, b, c):
    res = df.loc[df[b] == c, a]
    return res 

# get distinct data in column a 
def distinct_val(df, a):
    res = df[a].dropna().unique()
    return res




