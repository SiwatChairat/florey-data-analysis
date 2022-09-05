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
brain_parts = [
    "Ventricles",
    "Hippocampus",
    "WholeBrain",
    "Entorhinal",
    "Fusiform",
    "MidTemp",
    "ICV",
]
