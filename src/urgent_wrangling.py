#!/bin/env python
#
# This script wrangles the productive hours data prepared for using in urgent_gui.py

# import packages
import pandas as pd
import numpy as np
from datetime import datetime

def main():
    # read in csv
    raw = pd.read_csv("../data/productive_hours.csv")

    # split training and predicting data
    train = raw[raw["SHIFT_DATE"] < "2018-01-01"]
    pred = raw[(raw["SHIFT_DATE"] < "2019-01-01") & (raw["SHIFT_DATE"] > "2017-12-31")]

    # save data
    train.to_csv("../data/productive_hours_train.csv")
    pred.to_csv("../data/productive_hours_pred.csv")


# call main function
if __name__ == "__main__":
    main()
