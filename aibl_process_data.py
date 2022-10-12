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
rid_info_json = "data/processed_data/aibl_rid_info.json"
aibl_disease_cond = "data/processed_data/aibl_disease_cond.json"

"""
    AIBL Data Extraction Package
    ---------------------
    This package provides functions necessary to extract data from AIBL dataset
"""


def get_disease_count(file1):
    """Get the count of each disease presented in AIBL dataset, excluding some specific condition

    Parameters
    ----------
    file1 : str
        A string path point to AIBL dataset in csv format
    ----------
    Store all the count of each disease into a dictionary and export to JSON format
    """

    # read CSV file path
    df = pd.read_csv(file1, low_memory=False)
    # select column that contain the string "Medical History"
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
    """Get the top values count of each diseases in ascending/descending order

    Parameters
    ----------
    file_json : str
        A string path point to file_json dataset in csv format
    n : int
        An integer to tell how many values to return
    order : bool
        Descending order = False, Ascending order = True

    Returns
    ----------
    dictionary
        a dictionary containing disease name as the key and count as value in the specified order
    """
    df = pd.read_json(file_json, typ="series")
    top = sorted(df.items(), key=lambda x: x[1], reverse=True)[:n]
    if order:
        return OrderedDict(top)
    return dict(top)


# store aibl_disease.json in a variable
disease_json = "data/processed_data/aibl_disease.json"
# get top dicts
sorted_dict = get_top_val(disease_json, 50, False)


def match_disease(file1, file2):
    """Match the diseases between file1 and file2

    Parameters
    ----------
    file1 : str
        A string path point to file1 disease dataset in json format
    file2 : str
        A string path point to file2 disease dataset in json format

    Returns
    ----------
    list
        a list of match diseases between file1 and file2
    """
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


# run the function match_disease to find matched diseases in file1 and file2
disease_list = match_disease(aibl_disease, adni_disease)


def get_disease_id(file1):
    """Get the list of patients id with diseases and export to json file

    Parameters
    ----------
    file1 : str
        A string path point to file1 disease dataset in json format

    ----------
        Export dictionary with store patient id for each disease to json file
    """
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
    """Convert APOE4 value from format E3/E4, E4/E4, E3/E4 to integer

    Parameters
    ----------
    s : str
        A string with value E3/E4, E4/E4, E3/E4

    E3/E3 = 0, E3/E4 = 1, E4/E4 = 2
    Returns
    ----------
    int
        the count of E4 in the string
    """

    s = str(s)
    a_list = s.split("/")
    count = a_list.count("E4")
    return count


def dob_to_age(dob):
    """Calculate age from date of birth to today's month and year

    Parameters
    ----------
    dob : int
        An integer of date of birth in Year then Month format (eg. 200010 = October 2000)

    Returns
    ----------
    float
        the age converted from date of birth using Year and Month
    """
    dob = datetime.strptime(str(dob), "%Y%m").date()
    today = date.today()
    return today.year - dob.year - ((today.month) < (dob.month))


# JSON Encoder to solve int and array problem with numpy
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
    """Calculate age from date of birth to today's month and year

    Parameters
    ----------
    file1 : str
        A string path point to file1 AIBL dataset in csv format

    Returns
    ----------
    dictionary
        A dictionary with patient id as the key and patient info as the value including DX, AGE, GENDER, APOE4 and EDUCATION
    """
    cn_index = []
    mci_index = []
    ad_index = []
    rid_summary = {}
    file = pd.read_csv(file1, low_memory=False)
    cond_list = file["Neuropsych.Confirmed Classification"].tolist()
    # Store the index of each condition found
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
    # Remove repetitive patient id
    cn_rid_list = list(np.unique(cn_list["AIBL Id"].tolist()))
    mci_rid_list = list(np.unique(mci_list["AIBL Id"].tolist()))
    ad_rid_list = list(np.unique(ad_list["AIBL Id"].tolist()))

    # add info for AD patient
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
    # add info for MCI patient
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
    # add info gor CN patient
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

# convert patient data (RID, Condition) to CSV file
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


# patient_rid_cond_to_csv(aibl_disease_rid, aibl_csv, rid_info_json)


# Retrieve patient's disease condition from csv file
def get_patient_disease_cond(top_diseases, rid_with_cond):
    df1 = pd.read_json(top_diseases)
    df2 = pd.read_json(rid_with_cond, typ="series")
    summary_dict = dict(df1["disease"][0])
    diseases = list(summary_dict.keys())
    for i in range(len(diseases)):
        cn_count = 0
        mci_count = 0
        ad_count = 0
        nan_count = 0
        d = diseases[i]
        rid_list = summary_dict[d]
        for j in range(len(rid_list)):
            try:
                rid = rid_list[j]
                cond = df2[rid]["DX"]
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
        summary_dict[d] = {
            "RID_LIST": rid_list,
            "COND_COUNT": {
                "CN": cn_count,
                "MCI": mci_count,
                "AD": ad_count,
                "NaN": nan_count,
            },
        }
    return summary_dict


# disease_and_cond = get_patient_disease_cond(aibl_disease_rid, rid_info_json)
# jsonStr = json.dumps(disease_and_cond, cls=NpEncoder)
# jsonFile = open("aibl_disease_cond.json", "w")
# jsonFile.write(jsonStr)
# jsonFile.close()


# display a summary table of each condition CN, MCI and AD
def display_summary_table(disease_cond, white_list):
    df = pd.read_json(disease_cond, typ="series")
    headers = list(df.keys())
    data_list = []
    for i in range(len(headers)):
        d = headers[i]
        if d in white_list:
            d_dict = dict(df[d])
            cn_count = d_dict["COND_COUNT"]["CN"]
            mci_count = d_dict["COND_COUNT"]["MCI"]
            ad_count = d_dict["COND_COUNT"]["AD"]
            nan_count = d_dict["COND_COUNT"]["NaN"]
            total = cn_count + mci_count + ad_count + nan_count
            data = [d, cn_count, mci_count, ad_count, nan_count, total]
            data_list.append(data)

    x = PrettyTable()
    x.field_names = ["DISEASE", "CN", "MCI", "AD", "NaN", "TOTAL"]
    x.add_rows(data_list)

    return x


selected_list = [
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

# write data to csv file
# csv_str = display_summary_table(aibl_disease_cond, selected_list).get_string(
#     sortby="TOTAL", reversesort=True
# )
# with open("aibl_patients_disease_cond.csv", "w", newline="") as f_output:
#     f_output.write(csv_str)
