import os
import pandas as pd
import numpy as np
import seaborn as sns
from plots import count_plot, hour_plot

def main(data):
    count_plot(data, "JOB_STATUS", figsize=(10,10), filename="JOB_STATUS")
    count_plot(data, "EXCEPTION_GROUP", figsize=(30,12), filename="EXCEPTION_GROUP")
    hour_plot(data, "EXCEPTION_GROUP", figsize=(30,12), filename="EXCEPTION_GROUP vs HOURS")

if __name__ == "__main__":
    raw = pd.read_csv("../data/raw_2018.csv")
    main(raw)