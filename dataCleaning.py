import pandas as pd
from pandas_streaming.df import StreamingDataFrame
from pathlib import Path


adni_merge = "data/ADNIMERGE.csv"
medhist = "data/RECMHIST.csv"



# used headers 
adni_use_header = ["RID", "VISCODE", "EXAMDATE", "DX_bl", "AGE", "PTGENDER", "PTEDUCAT", "PTETHCAT", "PTRACCAT", "PTMARRY",
               "APOE4", "DX", "Month"]
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


