import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

adni = "all_ADNIMERGE.csv"
# List of diseases curated from medicinenet.com
# Source : https://github.com/Shivanshu-Gupta/web-scrapers/blob/master/medical_ner/medicinenet-diseases.json
disease_file = "diseases_data.json"

df = pd.read_csv(adni)
df.drop(df.filter(regex="Unname"),axis=1, inplace=True)
di = pd.read_json(disease_file)


# create a dict from list of diseases 
def create_diseases_dict():
    temp_dict = {}
    for row in di.itertuples():
        d = row.disease
        temp_dict[d] = ""

    return temp_dict

# create a list of diseases
def dict_key_to_list(a_dict):
    return list(a_dict.keys())


# get column index
def column_index(df, query_cols):
    cols = df.columns.values
    sidx = np.argsort(cols)
    return sidx[np.searchsorted(cols,query_cols,sorter=sidx)]


# get count of each diseases according to medical history
def count_diseases(d_data, d_list, di_dict):
    d_data = d_data.applymap(lambda s: s.lower() if type(s) == str else s)
    print("PROCESSING...")
    total = 0
    for d in d_list:
        data = (d_data == d.lower()).any(axis=1).value_counts().sort_index(ascending = True)
        headers = data.index.tolist()
        if (True in headers):
            i = headers.index(True)
            count = data[i]
            di_dict[d] = count
            print(d + ": ", count)
            if ("diabetes" in d.lower()):
                total = total + count
    
    print("Diabetes: ", total)
    print("COMPLETED !!!")
    print(di_dict)
        
        
    

#------------------------------------------------------------
#
# PROGRAMME RUNNING
#
#------------------------------------------------------------
# create dictionary for all the diseases
di_dict = create_diseases_dict()

# create list of diseases from the dictionary 
diseases_list = dict_key_to_list(di_dict)

# count the number of diseases present in the patient medical history
count_diseases(df, diseases_list, di_dict)

#------------------------------------------------------------
