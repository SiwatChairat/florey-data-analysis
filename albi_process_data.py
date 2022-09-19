import collections
from operator import le
import pandas as pd
import numpy as np
import json
import re
from prettytable import PrettyTable
from os import remove, walk
import scipy.stats as stats
import matplotlib.pyplot as plt
from collections import OrderedDict


# import excel data
df1 = pd.read_csv("data/AIBL/aibl-ids-preliminary-7.0.0-202006160457.csv")

diseases_cols = [col for col in df1.columns if "Medical History" in col]
diseases_dict = {}
for d in diseases_cols:
    yes = "Yes"
    yes_list = np.unique(df1.loc[df1[d] == yes, "AIBL Id"])
    new_d = d.partition(".")[2]
    count = len(yes_list)
    if (
        "Details" not in new_d
        and count != 0
        and "in Last 18 Months" not in new_d
        and "smoke" not in new_d
        and "drink" not in new_d
        and "Recent" not in new_d
        and "Last18" not in new_d
        and "History" not in new_d
    ):
        print(new_d, ": ", count)
        diseases_dict[new_d] = count

# write the new entries to json file
jsonStr = json.dumps(diseases_dict)
jsonFile = open("albi_disease.json", "w")
jsonFile.write(jsonStr)
jsonFile.close()


def get_top_val(file_json, n, order):
    df = pd.read_json(file_json, typ="series")
    top = sorted(df.items(), key=lambda x: x[1], reverse=True)[:n]
    if order:
        return OrderedDict(top)
    return dict(top)


disease_json = "albi_disease.json"
sorted_dict = get_top_val(disease_json, 50, False)

top_disease_list = [
    "Visual Defects",
    "Arthritis",
    "Hypertension",
    "HighCholesterol",
    "Gastric Complaints",
    "Cancer",
    "Depression",
    "Anxiety",
    "Joint Replacement",
    "Neurological Disorders",
    "Thyroid/Parathyroid Disease",
    "Diabetes",
]

print("{:<30} {:<15}".format("Disease", "Count"))
for d in sorted_dict.items():
    print("{:<30} {:<15}".format(d[0], d[1]))
