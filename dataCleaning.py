import pandas as pd
from pandas_streaming.df import StreamingDataFrame
from pathlib import Path


adni_merge = "data/ADNIMERGE.csv"
medhist = "data/RECMHIST.csv"



# used headers 
adni_use_header = ["RID", "VISCODE", "EXAMDATE", "DX_bl", "AGE", "PTGENDER", "PTEDUCAT", "PTETHCAT", "PTRACCAT", "PTMARRY",
               "APOE4", "DX"]
medh_use_header = ["RID", "EXAMDATE", "RECNO", "MHDESC"]



def get_headers(file_name):
    headers = list(pd.read_csv(file_name,sep="|",nrows=1).columns)[0].replace('"',"").split(",")
    return headers



# remove irrevant headers from the file and return a .csv file
def clean_data(file_name ,use_header):
    headers = get_headers(file_name)
    df = pd.read_csv(file_name)
    fname = Path(file_name).stem
    print(headers)
    for i in range(len(headers)):
        if headers[i] not in use_header:
            print("OK: popping header")
            df.pop(headers[i])
        else:
            print("Error: Headers do not exist")
    df.to_csv("processed_" + fname + ".csv")

# clean data by removing unused headers
#print(use_header)

# clean ADNIMERGE file by removing all unuse headers
#clean_data(adni_merge, adni_use_header)

# clean RECMHIST file by removing all unuse headers
#clean_data(medhist, medh_use_header)

# convert VISCODE data into column making RID primary key of the data
def row_to_col(file_name):
    df = pd.read_csv(file_name)
    viscode = df["VISCODE"].unique().tolist()
    rid_dict = {}
    vis_dict = dict.fromkeys(viscode, "")
    for row in df.itertuples():
        rid = row.RID
        vis = row.VISCODE
        dx = row.DX
        if (rid_dict.get(rid, -1) != -1):
            vis_dict = rid_dict[rid]
            vis_dict[vis] = dx
            rid_dict[rid] = vis_dict
        else:
            vis_dict = dict.fromkeys(viscode, "")
            vis_dict[vis] = dx
            rid_dict[rid] = vis_dict

    df2 = df.drop_duplicates(subset=["RID"], keep="first")
    df3 = pd.DataFrame.from_dict(rid_dict)
    df4 = df3.T
    df4 = df4.rename_axis("RID")
    result = pd.merge(df2,df4,on = "RID", how="left")
    result.to_csv("converted_ADNIMERGE.csv")

#adni_processed = "processed_ADNIMERGE.csv"
#row_to_col(adni_processed)

# add medical history info to patients data
def add_med_info(file_name, file_name2):
    df = pd.read_csv(file_name)
    recno = df["RECNO"].unique().tolist()
    rid_dict = {}
    rec_dict = dict.fromkeys(recno, "")
    for row in df.itertuples():
        rid = row.RID
        rec = row.RECNO
        med = row.MHDESC
        if (rid_dict.get(rid, -1) != -1):
            rec_dict = rid_dict[rid]
            rec_dict[rec] = med
            rid_dict[rid] = rec_dict
        else:
            rec_dict = dict.fromkeys(recno, "")
            rec_dict[rec] = med
            rid_dict[rid] = rec_dict
    df2 = pd.read_csv(file_name2)
    df3 = pd.DataFrame.from_dict(rid_dict)
    df4 = df3.T
    df4 = df4.rename_axis("RID")
    result = pd.merge(df2, df4, on = "RID", how = "left")
    result.pop("Unnamed: 0")
    result.pop("VISCODE")
    result.to_csv("all_ADNIMERGE.csv")

#adni_processed_med = "processed_RECMHIST.csv"
#adni_converted = "converted_ADNIMERGE.csv"
#add_med_info(adni_processed_med, adni_converted)
