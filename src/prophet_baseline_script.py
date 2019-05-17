#!/usr/bin/python
# load packages
import pandas as pd
import numpy as np
import os
from fbprophet import Prophet

# read data
raw_data = pd.read_csv("../data/train.csv", parse_dates=["SHIFT_DATE"])

# split data to train and val
train = raw_data[(raw_data["SHIFT_DATE"]>"2012-12-31") & (raw_data["SHIFT_DATE"]<"2017-01-01")]
val = raw_data[(raw_data["SHIFT_DATE"]>"2016-12-31") & (raw_data["SHIFT_DATE"]<"2018-01-01")]

# using only a portion of the sites
small_train = train[(train["SITE"]=="St Paul's Hospital") |
                    (train["SITE"]=="Mt St Joseph") |
                    (train["SITE"]=="Holy Family") |
                    (train["SITE"]=="SVH Langara") |
                    (train["SITE"]=="Brock Fahrni") |
                    (train["SITE"]=="Youville Residence")]

small_val = val[(val["SITE"]=="St Paul's Hospital") |
                (val["SITE"]=="Mt St Joseph") |
                (val["SITE"]=="Holy Family") |
                (val["SITE"]=="SVH Langara") |
                (val["SITE"]=="Brock Fahrni") |
                (val["SITE"]=="Youville Residence")]

# create training dataframes
splitting_train = small_train.groupby(["JOB_FAMILY_DESCRIPTION", "SITE", "SHIFT_DATE"]).size().reset_index()
splitting_train = splitting_train.rename({"SHIFT_DATE":"ds", 0:"y"}, axis=1)

# create validation dataframes
splitting_val = small_val.groupby(["JOB_FAMILY_DESCRIPTION", "SITE", "SHIFT_DATE"]).size().reset_index()
splitting_val = splitting_val.rename({"SHIFT_DATE":"ds", 0:"y"}, axis=1)

# create timeframe data for prediction
timeframe = pd.DataFrame(pd.date_range(start='2017-01-01', end='2017-12-31', freq="D")).rename({0:"ds"}, axis=1)

# method for running prophet models
def run_prophet(series, timeframe=timeframe):
    """
    Runs the Prophet

    Key arguments:
    --------------
    series -- (DataFrame) time series data
    timeframe -- (DataFrame) a DataFrame with one column
                 consisting of predicted dates

    Returns:
    --------------
    Returns the forecast of the predictions

    """
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False, interval_width=0.95)
    model.fit(series)
    forecast = model.predict(timeframe)
    return forecast

# create "SITE" and "JOB_FAMILY" groups
small_sites = small_train["SITE"].unique()
small_jfs = ["Registered Nurse-DC1", "Registered Nurse-DC2A Sup", "Registered Nurse-DC2B"]

# create and store predictions and true results
split_data = {}
pred_results = {}
true_results = {}
for i in small_sites:
    for j in small_jfs:
        temp_data_train = splitting_train[(splitting_train["SITE"]==i) & (splitting_train["JOB_FAMILY_DESCRIPTION"]==j)].reset_index()
        temp_data_val = splitting_val[(splitting_val["SITE"]==i) & (splitting_val["JOB_FAMILY_DESCRIPTION"]==j)].reset_index(drop=True)
        split_data[(i, j)] = temp_data_train
        true_results[(i, j)] = temp_data_val
        try:
            pred_results[(i, j)] = run_prophet(temp_data_train)
            print("Fitting -", i, j, ": Done")
        except ValueError:
            pred_results[(i, j)] = None
            print("Fitting -", i, j, ": Failed")

# combine predictions and true results
combined = {}
for i in true_results:
    if pred_results[i] is not None:
        combined[i] = pd.merge(true_results[i], pred_results[i], on="ds", how="outer")[["ds", "y", "yhat",
                                                                                        "yhat_lower", "yhat_upper"]]

# convert to week and calculating errors weekly
weekly = {}
for i in combined:
    # create week column
    combined[i]["week"] = combined[i]["ds"].dt.week
    combined[i]["ds"] = combined[i]["ds"]-pd.DateOffset(weekday=0, weeks=1)

    # store y, yhat, yhat_lower, yhat_upper
    weekly_y = combined[i].groupby("ds").y.sum().reset_index()
    weekly_yhat = combined[i].groupby("ds").yhat.sum().round(0).astype(int).reset_index()
    weekly_yhat_lower = combined[i].groupby("ds").yhat_lower.sum().round(0).astype(int).reset_index()
    weekly_yhat_upper = combined[i].groupby("ds").yhat_upper.sum().round(0).astype(int).reset_index()

    # replace negative prediction values with 0
    weekly_yhat = weekly_yhat.where(weekly_yhat["yhat"] >= 0, 0)
    weekly_yhat_lower = weekly_yhat_lower.where(weekly_yhat_lower["yhat_lower"] >= 0, 0)
    weekly_yhat_upper = weekly_yhat_upper.where(weekly_yhat_upper["yhat_upper"] >= 0, 0)


    # merge weekly results
    weekly[i] = pd.concat([weekly_y, weekly_yhat["yhat"],
                           weekly_yhat_lower["yhat_lower"],
                           weekly_yhat_upper["yhat_upper"]],
                          axis=1)

    # create columns "year", "site", "JOB_FAMILY"
    length = weekly[i].shape[0]
    weekly[i]["week"] = weekly[i]["ds"].dt.weekofyear
    weekly[i]["site"] = np.repeat(i[0], length)
    weekly[i]["job_family"] = np.repeat(i[1], length)

# create data/predictions folder if it doesn't exist
predictions_path = "../data/predictions/"
if not os.path.exists(predictions_path):
    os.mkdir(predictions_path)


# export to "data/predictions/" directory
total_data = pd.DataFrame()
for i in weekly:
    total_data = pd.concat([total_data, weekly[i]], axis=0)
total_data.to_csv(predictions_path + "predictions.csv")
