import pandas as pd
import numpy as np
import json
import re
from prettytable import PrettyTable
from os import walk
import scipy.stats as stats
import matplotlib.pyplot as plt

adni_merge = "data/ADNIMERGE.csv"

# prediction model for brain volumn (for each part of the brain of the patient)
# unit = mm^3
def extract_brain_data(file):
    df = pd.read_csv(file, low_memory=False)
    white_list = [
        "RID",
        "VISCODE",
        "Month",
        "EXAMDATE",
        "DX",
        "Ventricles",
        "Hippocampus",
        "WholeBrain",
        "Entorhinal",
        "Fusiform",
        "MidTemp",
        "ICV",
    ]
    df = df[white_list]
    print(df)

    return 0


extract_brain_data(adni_merge)
