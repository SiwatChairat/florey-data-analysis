import pandas as pd
import numpy as np
import pprint
import json
import re
from os import walk
import scipy.stats as stats
import matplotlib.pyplot as plt
from collections import OrderedDict


# import data
init_health = pd.read_csv("data/INITHEALTH.csv", low_memory=False)
rec_hist = pd.read_csv("data/RECMHIST.csv", low_memory=False)
adni_merge = pd.read_csv("data/ADNIMERGE.csv", low_memory=False)
disease_list = pd.read_json("data/diseases_data.json")
disease_json = pd.read_json("disease_dict.json", typ="series")
processed_disease = pd.read_json("processed_disease_dict.json", typ="series")


# match function to compare disease types with medical history
def match(disease_name, prev_dx):
    print(disease_name)
    regex = r"{d}".format(d=disease_name)
    index_list = []
    for i in range(len(prev_dx)):
        try:
            matches = re.findall(
                regex, prev_dx[i], re.MULTILINE | re.IGNORECASE)
            if len(matches) != 0:
                index_list.append(i)
        except Exception:
            print(prev_dx[i])
    return index_list

# check whether the rid found is presented in adni


def check_is_in_adni(adni_file, rid_list):
    result = []
    adni_rid = np.unique(adni_file["RID"].tolist())
    for i in range(len(rid_list)):
        rid = rid_list[i]
        if (rid in adni_rid):
            result.append(rid)
    return result

# get the count of patients with diseases


def get_disease_dict(file_name1, col1, file_name2, col2, disease_list):
    disease_dict = {}
    disease_and_rid = []
    prev_dx1 = file_name1[col1].tolist()
    prev_dx2 = file_name2[col2].tolist()
    for d in disease_list.itertuples():
        temp = {}
        disease_name = d.disease
        file1_index = match(disease_name, prev_dx1)
        file1_list = file_name1[file_name1.index.isin(file1_index)]
        file2_index = match(disease_name, prev_dx2)
        file2_list = file_name2[file_name2.index.isin(file2_index)]
        file1_rid_list = file1_list.RID.tolist()
        file2_rid_list = file2_list.RID.tolist()
        rid_list = np.unique(file1_rid_list + file2_rid_list).tolist()
        final_rid = check_is_in_adni(adni_merge, rid_list)
        count = len(final_rid)
        if (count != 0):
            disease_dict[disease_name] = count
        if (len(final_rid) != 0):
            temp[disease_name] = final_rid
            disease_and_rid.append(temp)

    di_rid_dict = {"disease": disease_and_rid}
    return disease_dict, di_rid_dict


# ------------------------------------------------------------
# run disease dict funtion to get total number of patients with the specified medical condition
# disease_dict = get_disease_dict(
#     init_health, "IHDESC", rec_hist, "MHDESC", disease_list)
# print(disease_dict)
# print(disease_dict[1])

# put the dictionary into json format
# jsonStr = json.dumps(disease_dict[1])
# jsonFile = open("di_rid_dict.json", "w")
# jsonFile.write(jsonStr)
# jsonFile.close()
# ------------------------------------------------------------

# remove empty entries in json file
def tidy_json(file_json):
    res_dict = {}
    # remove unrelated disease name
    black_list = ["Pain", "Glasses", "Smoking",
                  "Flu", "Sleep", "Breast", "Disc", "Gas"]
    for d in disease_list.itertuples():
        disease_name = d.disease
        count = file_json[disease_name]
        if (count != 0 and disease_name.upper() != disease_name and disease_name not in black_list):
            res_dict[disease_name] = int(count)

    # write the new entries to json file
    jsonStr = json.dumps(res_dict)
    jsonFile = open("processed_disease_dict.json", "w")
    jsonFile.write(jsonStr)
    jsonFile.close()


# ------------------------------------------------------------
# remove any entry in the json file that has 0 count
# tidy_json(disease_json)
# ------------------------------------------------------------

# get top diseaes present in the patients


def get_top_val(file_json, n, order):
    top = sorted(file_json.items(), key=lambda x: x[1], reverse=True)[:n]
    if order:
        return OrderedDict(top)
    return dict(top)


# print(get_top_val(processed_disease, 25, False))

# get the numbers of patients at certain stages


def patient_cond():
    return 0


# TODO: merge high cholesterol and hypercholesterolemia merge into one
# Up to top 9 + sleep, anxiety and depression
