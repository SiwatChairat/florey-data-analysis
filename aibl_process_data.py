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
from datetime import date, datetime


# import excel data
aibl_csv = "data/AIBL/aibl-ids-preliminary-7.0.0-202006160457.csv"
adni_disease = "data/processed_data/processed_disease_dict.json"
aibl_disease = "data/processed_data/aibl_disease.json"
aibl_disease_rid = "data/processed_data/aibl_disease_rid.json"
rid_info_json = "data/processed_data/rid_info.json"


def get_disease_count(file1):
    df = pd.read_csv(file1, low_memory=False)
    diseases_cols = [col for col in df.columns if "Medical History" in col]
    diseases_dict = {}
    for d in diseases_cols:
        yes = "Yes"
        yes_list = np.unique(df.loc[df[d] == yes, "AIBL Id"])
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
            diseases_dict[new_d] = count

    # write the new entries to json file
    jsonStr = json.dumps(diseases_dict)
    jsonFile = open("aibl_disease.json", "w")
    jsonFile.write(jsonStr)
    jsonFile.close()


def get_top_val(file_json, n, order):
    df = pd.read_json(file_json, typ="series")
    top = sorted(df.items(), key=lambda x: x[1], reverse=True)[:n]
    if order:
        return OrderedDict(top)
    return dict(top)


disease_json = "data/processed_data/aibl_disease.json"
sorted_dict = get_top_val(disease_json, 50, False)


def match_disease(file1, file2):
    df1 = pd.read_json(file1, typ="series")
    df2 = pd.read_json(file2, typ="series")
    keys_1 = df1.keys()
    keys_2 = df2.keys()
    matched = []

    for k in keys_2:
        disease = r"{d}".format(d=k)
        if disease in keys_1:
            matched.append(disease)
    return matched


disease_list = match_disease(aibl_disease, adni_disease)


def get_disease_id(file1):
    df = pd.read_csv(file1, low_memory=False)
    diseases_cols = [col for col in df.columns if "Medical History" in col]
    diseases_dict = {}
    for d in diseases_cols:
        yes = "Yes"
        yes_list = np.unique(df.loc[df[d] == yes, "AIBL Id"])
        yes_list = list(map(int, yes_list))
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
            if new_d == "HighCholesterol":
                new_d = "High Cholesterol"
            diseases_dict[new_d] = list(yes_list)

    # export to json
    result = {"disease": [diseases_dict]}
    jsonStr = json.dumps(result)
    jsonFile = open("aibl_disease_rid.json", "w")
    jsonFile.write(jsonStr)
    jsonFile.close()


# get_disease_id(aibl_csv)
# print top disease list
# print("{:<30} {:<15}".format("Disease", "Count"))
# for d in sorted_dict.items():
#     print("{:<30} {:<15}".format(d[0], d[1]))


def convert_apoe4(s):
    s = str(s)
    a_list = s.split("/")
    count = a_list.count("E4")
    return count


# calculate age from date of birth to today's month and year
def dob_to_age(dob):
    dob = datetime.strptime(str(dob), "%Y%m").date()
    today = date.today()
    return today.year - dob.year - ((today.month) < (dob.month))


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


def get_rid_with_info(file1):
    cn_index = []
    mci_index = []
    ad_index = []
    rid_summary = {}
    file = pd.read_csv(file1, low_memory=False)
    cond_list = file["Neuropsych.Confirmed Classification"].tolist()
    for i in range(len(cond_list)):
        regex = r"{c}".format(c=cond_list[i])
        try:
            if (
                regex == "Non-Memory Complainer (Healthy control)"
                or regex == "Memory Complainer (Healthy control)"
            ):
                cn_index.append(i)
            elif regex == "MCI patient":
                mci_index.append(i)
            elif regex == "AD patient":
                ad_index.append(i)
        except Exception:
            print("Error")

    cn_list = file[file.index.isin(cn_index)]
    mci_list = file[file.index.isin(mci_index)]
    ad_list = file[file.index.isin(ad_index)]
    cn_rid_list = list(np.unique(cn_list["AIBL Id"].tolist()))
    mci_rid_list = list(np.unique(mci_list["AIBL Id"].tolist()))
    ad_rid_list = list(np.unique(ad_list["AIBL Id"].tolist()))

    for i in range(len(ad_rid_list)):
        rid = int(ad_rid_list[i])
        age = dob_to_age(
            file.loc[file["AIBL Id"] == rid, "Demographic.YearMonthOfBirth"].iloc[0]
        )
        gender = file.loc[file["AIBL Id"] == rid, "Demographic.Sex"].iloc[0]
        apoe4 = convert_apoe4(
            file.loc[file["AIBL Id"] == rid, "Demographic.ApoE genotype"].iloc[0]
        )
        edu = file.loc[
            file["AIBL Id"] == rid, "Demographic.Years of Education Exact"
        ].iloc[0]

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
            age = dob_to_age(
                file.loc[file["AIBL Id"] == rid, "Demographic.YearMonthOfBirth"].iloc[0]
            )
            gender = file.loc[file["AIBL Id"] == rid, "Demographic.Sex"].iloc[0]
            apoe4 = convert_apoe4(
                file.loc[file["AIBL Id"] == rid, "Demographic.ApoE genotype"].iloc[0]
            )
            edu = file.loc[
                file["AIBL Id"] == rid, "Demographic.Years of Education Exact"
            ].iloc[0]
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
            age = dob_to_age(
                file.loc[file["AIBL Id"] == rid, "Demographic.YearMonthOfBirth"].iloc[0]
            )
            gender = file.loc[file["AIBL Id"] == rid, "Demographic.Sex"].iloc[0]
            apoe4 = convert_apoe4(
                file.loc[file["AIBL Id"] == rid, "Demographic.ApoE genotype"].iloc[0]
            )
            edu = file.loc[
                file["AIBL Id"] == rid, "Demographic.Years of Education Exact"
            ].iloc[0]
            data = {
                "DX": "CN",
                "AGE": age,
                "GENDER": gender,
                "APOE4": apoe4,
                "EDUCATION": edu,
            }
            rid_summary[rid] = data
    return rid_summary


rid_info = get_rid_with_info(aibl_csv)
# jsonStr = json.dumps(rid_info, cls=NpEncoder)
# jsonFile = open("rid_info.json", "w")
# jsonFile.write(jsonStr)
# jsonFile.close()


def patient_rid_cond_to_csv(disease_cond, aibl, rid_with_info):
    df1 = pd.read_json(disease_cond)
    df2 = pd.read_csv(aibl, low_memory=False)
    df3 = dict(pd.read_json(rid_with_info, typ="series"))
    rid_list = list(np.unique(df2["AIBL Id"]))
    d_dict = dict(df1["disease"][0])
    diseases = list(d_dict.keys())
    data_list = []
    d_list = sorted(
        [
            "Hypertension",
            "Arthritis",
            "Depression",
            "Thyroid/Parathyroid Disease",
            "High Cholesterol",
            "Diabetes",
            "Transient Ischemic Attack",
            "Epilepsy",
            "Cancer",
            "Anxiety",
            "Kidney Disease",
            "Liver Disease",
            "Heart Attack",
        ]
    )
    for i in range(len(rid_list)):
        try:
            all_count = 0
            rid = rid_list[i]
            cond = df3[rid]["DX"]
            age = df3[rid]["AGE"]
            gender = df3[rid]["GENDER"]
            apoe4 = df3[rid]["APOE4"]
            edu = df3[rid]["EDUCATION"]
            diseases_list = []
            headers = diseases
            for j in range(len(headers)):
                d = headers[j]
                if rid in d_dict[d] and d in d_list:
                    diseases_list.append(headers[j])
                    all_count += 1
                elif rid in d_dict[d] and d not in d_list:
                    all_count += 1

            ordered_list = sorted(diseases_list)
            diseases_count = len(ordered_list)
            if collections.Counter(ordered_list) != collections.Counter(d_list):
                for k in range(len(d_list)):
                    try:
                        if ordered_list[k] != d_list[k]:
                            ordered_list.insert(k, "-")

                    except Exception as e:
                        ordered_list.append("-")
                        continue
            data = (
                [rid, cond, age, gender, apoe4, edu]
                + ordered_list
                + [diseases_count, all_count]
            )
            data_list.append(data)
        except Exception:
            print(rid, ": No condition information on this patient")
            data = [
                rid,
                "",
                age,
                gender,
                apoe4,
                edu,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
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
        "Diabetes",
        "Epilepsy",
        "Heart Attack",
        "High Cholesterol",
        "Hypertension",
        "Kidney Disease",
        "Liver Disease",
        "Thyroid/Parathyroid Disease",
        "Transient Ischemic Attack",
        "SELECTED_DISEASE_COUNT",
        "ALL_DISEASE_COUNT",
    ]

    x.add_rows(data_list)
    csv_str = x.get_csv_string()
    with open("aibl_rid_with_info.csv", "w", newline="") as f_output:
        f_output.write(csv_str)


patient_rid_cond_to_csv(aibl_disease_rid, aibl_csv, rid_info_json)
