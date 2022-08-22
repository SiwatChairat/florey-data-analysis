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

data_summary = {"RID" : "", 
               "GENDER" : "", 
               "AGE" : "", 
               "ETHNIC" : "", 
               "RACE" : "",
               "VISCODE" : [],
               "MEDHIST": []}

viscode_data_format = {
                "VISCODE" : "",
                "DATE" : "",
                "MSTATUS" : "",
                "MONTH" : "",
                "APOE4" : "",
                "DX_bl" : "",
                "DX" : ""
               }

medhist_data_format = {"RECNO" : "",
                       "DATE" : "",
                       "DESCRIPTION" : ""}

def set_summary(temp, info):
    date = row.EXAMDATE
    m_status = row.PTMARRY
    month = row.Month
    apoe4 = row.APOE4
    dx_bl = row.DX_bl
    dx = row.DX


def create_json():
    json = []
    recorded_rid = []
    # iterate through row in adni merge, extract out wanted data and store in json format
    for row in df_adni.itertuples():
        counter = counter + 1
        rid = row.RID
        gender = row.PTGENDER
        age = row.AGE
        ethnic = row.PTETHCAT
        race = row.PTRACCAT
        viscode = row.VISCODE
        date = row.EXAMDATE
        m_status = row.PTMARRY
        month = row.Month
        apoe4 = row.APOE4
        dx_bl = row.DX_bl
        dx = row.DX
        info1 = [rid, gender, age, ethnic, race]
        if (len(json) == 0 or rid not in recorded_rid):
            temp1 = data_summary
            temp2 = viscode_data_format
            temp1["RID"] = rid
            temp1["GENDER"] = gender
            temp1["AGE"] = age
            temp1["ETHNIC"] = ethnic
            temp1["RACE"] = race
            temp2["VISCODE"] = viscode
            temp2["DATE"] = date
            temp2["MSTATUS"] = m_status
            temp2["MONTH"] = month
            temp2["APOE4"] = apoe4 
            temp2["DX_bl"] = dx_bl
            temp2["DX"] = dx
            temp1["VISCODE"] = [temp2]
            json.append(data_summary)
            recorded_rid.append(rid)
        elif (rid in recorded_rid):
            temp2 = viscode_data_format
            temp2["VISCODE"] = viscode
            temp2["DATE"] = date
            temp2["MSTATUS"] = m_status
            temp2["MONTH"] = month
            temp2["APOE4"] = apoe4
            temp2["DX_bl"] = dx_bl
            temp2["DX"] = dx
            json
        else:
            return 0 
        


create_json()





