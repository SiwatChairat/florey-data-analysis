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
from collections import OrderedDict, ChainMap


# import data
init_health = "data/ADNI/INITHEALTH.csv"
rec_hist = "data/ADNI/RECMHIST.csv"
adni_merge = "data/ADNI/ADNIMERGE.csv"
disease_list = "data/diseases_data.json"
disease_json = "data/processed_data/disease_dict.json"
processed_disease = "data/processed_data/processed_disease_dict.json"
di_rid_json = "data/processed_data/di_rid_dict.json"
top_diseases = "data/processed_data/top_diseases.json"
rid_with_cond = "data/processed_data/rid_with_cond.json"
disease_cond = "data/processed_data/disease_cond.json"
rid_with_info = "data/processed_data/rid_with_info.json"

# match function to compare disease types with medical history
def match_disease(disease_name, prev_dx):
    print(disease_name)
    regex = r"{d}".format(d=disease_name)
    index_list = []
    for i in range(len(prev_dx)):
        try:
            matches = re.findall(regex, prev_dx[i], re.MULTILINE | re.IGNORECASE)
            if len(matches) != 0:
                index_list.append(i)
        except Exception:
            print(prev_dx[i])
    return index_list


# check whether the rid found is presented in adni
def check_is_in_adni(adni_file, rid_list):
    result = []
    adni_file = pd.read_csv(adni_file, low_memory=False)
    adni_rid = np.unique(adni_file["RID"].tolist())
    for i in range(len(rid_list)):
        rid = rid_list[i]
        if rid in adni_rid:
            result.append(rid)
    return result


# get the count of patients with diseases
def get_disease_dict(file_name1, col1, file_name2, col2, disease_list):
    df1 = pd.read_csv(file_name1, low_memory=False)
    df2 = pd.read_csv(file_name2, low_memory=False)
    disease_dict = {}
    disease_and_rid = []
    prev_dx1 = df1[col1].tolist()
    prev_dx2 = df2[col2].tolist()
    disease_list = pd.read_json(disease_list)
    for d in disease_list.itertuples():
        temp = {}
        disease_name = d.disease
        file1_index = match_disease(disease_name, prev_dx1)
        file1_list = df1[df1.index.isin(file1_index)]
        file2_index = match_disease(disease_name, prev_dx2)
        file2_list = df2[df2.index.isin(file2_index)]
        file1_rid_list = file1_list.RID.tolist()
        file2_rid_list = file2_list.RID.tolist()
        rid_list = np.unique(file1_rid_list + file2_rid_list).tolist()
        final_rid = check_is_in_adni(adni_merge, rid_list)
        count = len(final_rid)
        if count != 0:
            disease_dict[disease_name] = count
        if len(final_rid) != 0:
            temp[disease_name] = final_rid
            disease_and_rid.append(temp)

    di_rid_dict = {"disease": disease_and_rid}
    return disease_dict, di_rid_dict


# JSON Encoder to fix int and array problem with numpy


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


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
    df = pd.read_json(file_json)
    # remove unrelated disease name
    black_list = ["Pain", "Glasses", "Smoking", "Flu", "Sleep", "Breast", "Disc", "Gas"]
    for d in disease_list.itertuples():
        disease_name = d.disease
        count = df[disease_name]
        if (
            count != 0
            and disease_name.upper() != disease_name
            and disease_name not in black_list
        ):
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
    df = pd.read_json(file_json, typ="series")
    top = sorted(df.items(), key=lambda x: x[1], reverse=True)[:n]
    if order:
        return OrderedDict(top)
    return dict(top)


# ------------------------------------------------------------
# get top diseases mentioned in the data by count
# print(get_top_val(processed_disease, 25, False))
# ------------------------------------------------------------

# extract wanted diseases from the overall dict
def get_pick_summary(file_json, pick_diseases):
    df = pd.read_json(file_json)
    data_dict = dict(df["disease"])
    summary = {}
    for i in range(len(data_dict)):
        data = dict(data_dict[i])
        disease = list(data.keys())[0]
        regex = r"{d}".format(d=disease)
        if regex in pick_diseases:
            rid_list = data[regex]
            count = len(rid_list)
            summary[regex] = {"TOTAL": count, "RID_LIST": rid_list}
    return summary


def merge_dup(data_dict, dup_a, dup_b):
    a_rid = list(data_dict[dup_a]["RID_LIST"])
    b_rid = list(data_dict[dup_b]["RID_LIST"])
    t_rid = np.unique(a_rid + b_rid)
    count = len(t_rid)
    keys = list(data_dict[dup_a].keys())
    data_dict[dup_a] = {keys[0]: count, keys[1]: t_rid}
    data_dict.pop(dup_b)
    return data_dict


# get summary of the picked diseases specified in a list
pick_diseases = [
    "Hypertension",
    "Arthritis",
    "Depression",
    "Thyroid",
    "Hypercholesterolemia",
    "High Cholesterol",
    "Hyperlipidemia",
    "Hearing",
    "Osteoarthritis",
    "Cancer",
    "Anxiety",
    "Sleep Apnea",
    "Insomnia",
]
# ------------------------------------------------------------
# picked_summary = get_pick_summary(di_rid_json, pick_diseases)

# # merge Hypercholesterolemia and High Cholesterol together because they are typically the same thing
# merge_summary = merge_dup(picked_summary, "Hypercholesterolemia", "High Cholesterol")

# print(merge_summary)
# jsonStr = json.dumps(merge_summary, cls=NpEncoder)
# jsonFile = open("top_diseases.json", "w")
# jsonFile.write(jsonStr)
# jsonFile.close()
# ------------------------------------------------------------


def get_rid_with_info(file_name):
    # col 1 = DX
    cn_index = []
    mci_index = []
    ad_index = []
    rid_summary = {}
    file = pd.read_csv(file_name, low_memory=False)
    cond_list = file["DX"].tolist()
    for i in range(len(cond_list)):
        regex = r"{c}".format(c=cond_list[i])
        try:
            if regex == "CN":
                cn_index.append(i)
            elif regex == "MCI":
                mci_index.append(i)
            elif regex == "Dementia":
                ad_index.append(i)
        except Exception:
            print("Error")

    cn_list = file[file.index.isin(cn_index)]
    mci_list = file[file.index.isin(mci_index)]
    ad_list = file[file.index.isin(ad_index)]
    cn_rid_list = list(np.unique(cn_list.RID.tolist()))
    mci_rid_list = list(np.unique(mci_list.RID.tolist()))
    ad_rid_list = list(np.unique(ad_list.RID.tolist()))

    for i in range(len(ad_rid_list)):
        rid = int(ad_rid_list[i])
        age = file.loc[file["RID"] == rid, "AGE"].iloc[0]
        gender = file.loc[file["RID"] == rid, "PTGENDER"].iloc[0]
        apoe4 = file.loc[file["RID"] == rid, "APOE4"].iloc[0]
        edu = file.loc[file["RID"] == rid, "PTEDUCAT"].iloc[0]
        data = {
            "DX": "AD",
            "AGE": age,
            "GENDER": gender,
            "APOE4": apoe4,
            "EDUCATION": edu,
        }
        rid_summary[rid] = data
    for i in range(len(mci_rid_list)):
        rid = int(mci_rid_list[i])
        if rid not in rid_summary:
            age = file.loc[file["RID"] == rid, "AGE"].iloc[0]
            gender = file.loc[file["RID"] == rid, "PTGENDER"].iloc[0]
            apoe4 = file.loc[file["RID"] == rid, "APOE4"].iloc[0]
            edu = file.loc[file["RID"] == rid, "PTEDUCAT"].iloc[0]
            data = {
                "DX": "MCI",
                "AGE": age,
                "GENDER": gender,
                "APOE4": apoe4,
                "EDUCATION": edu,
            }
            rid_summary[rid] = data
    for i in range(len(cn_rid_list)):
        rid = int(cn_rid_list[i])
        if rid not in rid_summary:
            age = file.loc[file["RID"] == rid, "AGE"].iloc[0]
            gender = file.loc[file["RID"] == rid, "PTGENDER"].iloc[0]
            apoe4 = file.loc[file["RID"] == rid, "APOE4"].iloc[0]
            edu = file.loc[file["RID"] == rid, "PTEDUCAT"].iloc[0]
            data = {
                "DX": "CN",
                "AGE": age,
                "GENDER": gender,
                "APOE4": apoe4,
                "EDUCATION": edu,
            }
            rid_summary[rid] = data
    return rid_summary


# ------------------------------------------------------------
# get rid with their condition, CN, MCI and AD
# rid_with_info = get_rid_with_info(adni_merge)
# print(rid_with_info)

# # create a json file for the rid with condition info
# jsonStr = json.dumps(rid_with_info, cls=NpEncoder)
# jsonFile = open("rid_with_info.json", "w")
# jsonFile.write(jsonStr)
# jsonFile.close()
# ------------------------------------------------------------


def get_patient_disease_cond(top_diseases, rid_with_cond):
    df1 = pd.read_json(top_diseases, typ="series")
    df2 = pd.read_json(rid_with_cond, typ="series")
    diseases = list(df1.keys())
    summary_dict = dict(df1)
    for i in range(len(diseases)):
        cn_count = 0
        mci_count = 0
        ad_count = 0
        nan_count = 0
        d = diseases[i]
        rid_list = df1[d]["RID_LIST"]
        for j in range(len(rid_list)):
            try:
                rid = rid_list[j]
                cond = df2[rid]
                if cond == "CN":
                    cn_count += 1
                elif cond == "MCI":
                    mci_count += 1
                elif cond == "AD":
                    ad_count += 1
                else:
                    print("ERROR")
            except Exception:
                print("The Key does not exist")
                nan_count += 1
        summary_dict[d]["COND_COUNT"] = {
            "CN": cn_count,
            "MCI": mci_count,
            "AD": ad_count,
            "NaN": nan_count,
        }
    return summary_dict


# ------------------------------------------------------------
# disease_and_cond = get_patient_disease_cond(top_diseases, rid_with_cond)

# create a json with picked disease, and patients conditions
# jsonStr = json.dumps(disease_and_cond, cls=NpEncoder)
# jsonFile = open("disease_cond.json", "w")
# jsonFile.write(jsonStr)
# jsonFile.close()
# ------------------------------------------------------------


def display_summary_table(disease_cond):
    df = pd.read_json(disease_cond, typ="series")
    headers = list(df.keys())
    data_list = []
    for i in range(len(headers)):
        d = headers[i]
        d_dict = dict(df[d])
        cn_count = d_dict["COND_COUNT"]["CN"]
        mci_count = d_dict["COND_COUNT"]["MCI"]
        ad_count = d_dict["COND_COUNT"]["AD"]
        nan_count = d_dict["COND_COUNT"]["NaN"]
        total = d_dict["TOTAL"]
        data = [d, cn_count, mci_count, ad_count, nan_count, total]
        data_list.append(data)

    x = PrettyTable()
    x.field_names = ["DISEASE", "CN", "MCI", "AD", "NaN", "TOTAL"]
    x.add_rows(data_list)

    return x


# ------------------------------------------------------------
# print(display_summary_table(disease_cond).get_string(sortby="TOTAL", reversesort=True))

# write data to csv file
# csv_str = display_summary_table(disease_cond).get_csv_string(
#     sortby="TOTAL", reversesort=True
# )
# with open("patients_disease_cond.csv", "w", newline="") as f_output:
#     f_output.write(csv_str)
# ------------------------------------------------------------


def patient_rid_cond_to_csv(disease_cond, adni_merge, rid_with_info, di_rid_dict):
    df1 = pd.read_json(disease_cond, typ="series")
    df2 = pd.read_csv(adni_merge, low_memory=False)
    df3 = dict(pd.read_json(rid_with_info, typ="series"))
    df4 = pd.read_json(di_rid_dict)
    d_dict = dict(df4["disease"])
    rid_list = list(np.unique(df2["RID"]))
    data_list = []
    d = sorted(
        [
            "Hypertension",
            "Arthritis",
            "Depression",
            "Thyroid",
            "Hypercholesterolemia",
            "High Cholesterol",
            "Hyperlipidemia",
            "Hearing",
            "Osteoarthritis",
            "Cancer",
            "Anxiety",
            "Sleep Apnea",
            "Insomnia",
        ]
    )
    for i in range(len(rid_list)):
        try:
            other_co_mor_count = 0
            rid = rid_list[i]
            cond = df3[rid]["DX"]
            age = df3[rid]["AGE"]
            gender = df3[rid]["GENDER"]
            apoe4 = df3[rid]["APOE4"]
            edu = df3[rid]["EDUCATION"]
            diseases_list = []
            headers = list(df1.keys())
            for j in range(len(headers)):
                if rid in df1[headers[j]]["RID_LIST"]:
                    diseases_list.append(headers[j])
            for l in range(len(d_dict)):
                data = dict(d_dict[l])
                disease = list(data.keys())[0]
                if (
                    disease.upper() != disease
                    and rid in data[disease]
                    and data[disease] not in headers
                ):
                    other_co_mor_count += 1

            ordered_list = sorted(diseases_list)
            diseases_count = len(ordered_list)
            if collections.Counter(ordered_list) != collections.Counter(d):
                for k in range(len(d)):
                    try:
                        if ordered_list[k] != d[k]:
                            ordered_list.insert(k, "-")

                    except Exception as e:
                        ordered_list.append("-")
                        continue
            data = (
                [rid, cond, age, gender, apoe4, edu]
                + ordered_list
                + [diseases_count, other_co_mor_count]
            )
            data_list.append(data)
        except Exception:
            print("No condition information on this patient")
            data = [
                rid,
                "-",
                age,
                gender,
                apoe4,
                edu,
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
            ]
            data_list.append(data)
    x = PrettyTable()
    x.field_names = [
        "RID",
        "CONDITION",
        "AGE",
        "GENDER",
        "APOE4",
        "EDUCATION",
        "Anxiety",
        "Arthritis",
        "Cancer",
        "Depression",
        "Hearing",
        "High Cholesterol",
        "Hypercholesterolemia",
        "Hyperlipidemia",
        "Hypertension",
        "Insomnia",
        "Osteoarthritis",
        "Sleep Apnea",
        "Thyroid",
        "DISEASE_COUNT",
        "OTHER_CO_MOR_COUNT",
    ]

    x.add_rows(data_list)
    csv_str = x.get_csv_string()
    with open("patients_rid_with_info_latest.csv", "w", newline="") as f_output:
        f_output.write(csv_str)


# ------------------------------------------------------------
# print patients information with the latest condition sorted by their RID

# patient_rid_cond_to_csv(disease_cond, adni_merge, rid_with_info, di_rid_json)

# ------------------------------------------------------------


def cond_count(file):
    df = pd.read_json(file, typ="series")
    dict_keys = list(df.keys())
    cn_count = 0
    mci_count = 0
    ad_count = 0
    for i in range(len(dict_keys)):
        key = dict_keys[i]
        if df[key] == "CN":
            cn_count += 1
        elif df[key] == "MCI":
            mci_count += 1
        elif df[key] == "AD":
            ad_count += 1
    return cn_count, mci_count, ad_count


# print(cond_count(rid_with_cond))

# patients = pd.read_csv(adni_merge, low_memory=False)
# count = len(np.unique(patients["RID"]))
# print(count)
