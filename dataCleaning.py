import pandas as pd
from pandas_streaming.df import StreamingDataFrame
from pathlib import Path

file = "testData/ADNIMERGE.csv"

# unused headers 
unuse_header = ["COLPROT","ORIGPROT","PTID","SITE","FLDSTRENG", "FSVERSION", "FSVERSION_bl", "FLDSTRENG_bl", "IMAGEUID", "IMAGEUID_bl"]

def get_headers(file_name):
    headers = list(pd.read_csv(file_name,sep="|",nrows=1).columns)[0].replace('"',"").split(",")
    print(headers)
    print(len(headers))
    return headers



# remove irrevant headers from the file and return a .csv file
def clean_data(file_name ,unuse_header):
    headers = get_headers(file_name)
    df = pd.read_csv(file_name)
    fname = Path(file_name).stem
    print(headers)
    for i in range(len(unuse_header)):
        header = unuse_header[i]
        if header in headers:
            print("Headers exist")
            print(header)
            df.pop(header)
        else:
            print("Error: Headers do not exist")
    df.to_csv("processed_" + fname + ".csv")

# clean data by removing unused headers
#print(unuse_header)
#clean_data(file, unuse_header)





