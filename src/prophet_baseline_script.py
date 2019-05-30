#!/usr/bin/python
# load packages
import pandas as pd
import numpy as np
import os
from fbprophet import Prophet
from stldecompose import decompose, forecast
from stldecompose.forecast_funcs import (naive, drift, mean, seasonal_naive)

def run_prophet(series, timeframe):
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
    return forecast, model

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
small_train = small_train[(small_train["JOB_FAMILY"]=="DC1000") |
                    (small_train["JOB_FAMILY"]=="DC2A00") |
                    (small_train["JOB_FAMILY"]=="DC2B00") ]

small_val = val[(val["SITE"]=="St Paul's Hospital") |
                (val["SITE"]=="Mt St Joseph") |
                (val["SITE"]=="Holy Family") |
                (val["SITE"]=="SVH Langara") |
                (val["SITE"]=="Brock Fahrni") |
                (val["SITE"]=="Youville Residence")]
small_val = small_val[(small_val["JOB_FAMILY"]=="DC1000") |
                    (small_val["JOB_FAMILY"]=="DC2A00") |
                    (small_val["JOB_FAMILY"]=="DC2B00") ]

# create training dataframes
splitting_train = small_train.groupby(["JOB_FAMILY", "SITE", "SHIFT_DATE"]).size().reset_index()
splitting_train = splitting_train.rename({"SHIFT_DATE":"ds", 0:"y"}, axis=1)

# create validation dataframes
splitting_val = small_val.groupby(["JOB_FAMILY", "SITE", "SHIFT_DATE"]).size().reset_index()
splitting_val = splitting_val.rename({"SHIFT_DATE":"ds", 0:"y"}, axis=1)

# create timeframe data for prediction
total_timeframe = pd.DataFrame(pd.date_range(start='2013-01-01', end='2016-12-31', freq="D")).rename({0:"ds"}, axis=1)
timeframe = pd.DataFrame(pd.date_range(start="2017-01-01", end="2017-12-31", freq="D")).rename({0:"ds"}, axis=1)

# create "SITE" and "JOB_FAMILY" groups
small_sites = small_train["SITE"].unique()
small_jfs = small_train["JOB_FAMILY"].unique()

# create and store predictions and true results
models = {}
split_data = {}
pred_results_past = {}
pred_results_future = {}
true_results = {}
for i in small_sites:
    for j in small_jfs:
        temp_data_train = splitting_train[(splitting_train["SITE"]==i) & (splitting_train["JOB_FAMILY"]==j)].reset_index()
        temp_data_train = pd.merge(total_timeframe, temp_data_train, on="ds", how="outer")
        temp_data_train["y"] = temp_data_train["y"].fillna(0)

        temp_data_val = splitting_val[(splitting_val["SITE"]==i) & (splitting_val["JOB_FAMILY"]==j)].reset_index(drop=True)
        temp_data_val = pd.merge(timeframe, temp_data_val, on="ds", how="outer")
        temp_data_val["y"] = temp_data_val["y"].fillna(0)

        split_data[(i, j)] = temp_data_train
        true_results[(i, j)] = temp_data_val
        pred_results_past[(i, j)], models[(i,j)] = run_prophet(temp_data_train, total_timeframe)
        pred_results_future[(i, j)] = models[(i,j)].predict(timeframe)
        print("Fitting -", i, j, ": Done")

weekly = {}
for i in split_data.keys():
    # create week column
    combined= pd.merge(true_results[i], pred_results_future[i], on="ds", how="outer")[["ds", "y", "yhat", "yhat_lower", "yhat_upper"]]
    combined["week"] = combined["ds"].dt.week
    combined["ds"] = combined["ds"]-pd.DateOffset(weekday=0, weeks=1)

    # store y, yhat, yhat_lower, yhat_upper
    weekly_y = combined.groupby("ds").y.sum().reset_index()
    weekly_yhat = combined.groupby("ds").yhat.sum().round(0).astype(int).reset_index()
    weekly_yhat_lower = combined.groupby("ds").yhat_lower.sum().round(0).astype(int).reset_index()
    weekly_yhat_upper = combined.groupby("ds").yhat_upper.sum().round(0).astype(int).reset_index()

    # merge weekly results
    weekly[i] = pd.concat([weekly_y, weekly_yhat["yhat"],
                           weekly_yhat_lower["yhat_lower"],
                           weekly_yhat_upper["yhat_upper"]], axis=1)

    # create columns "year", "site", "JOB_FAMILY"
    length = weekly[i].shape[0]
    weekly[i]["week"] = weekly[i]["ds"].dt.weekofyear
    weekly[i]["site"] = np.repeat(i[0], length)
    weekly[i]["job_family"] = np.repeat(i[1], length)

    # code for minimizing errors (model residuals)
    forecasted = models[i].predict(total_timeframe)
    actual = split_data[i]

    # get residuals
    error = actual["y"] - forecasted["yhat"]
    obs = total_timeframe.copy()
    obs["error"] = error
    obs = obs.set_index("ds")

    # model residuals
    period = int((np.max(timeframe) - np.min(timeframe)).dt.days)+1
    decomp = decompose(obs, period=period)
    weekly_fcast = forecast(decomp, steps=period, fc_func=drift, seasonal=True)
    weekly_fcast["week"] = weekly_fcast.index-pd.DateOffset(weekday=0, weeks=1)
    weekly_fcast = weekly_fcast.groupby("week").sum()

    # replace weekly data
    resid_fcast = weekly_fcast.reset_index()["drift+seasonal"]
    weekly_yhat = (weekly[i]["yhat"] + resid_fcast).round(0)
    weekly_yhat_lower = (weekly[i]["yhat_lower"] + resid_fcast).round(0)
    weekly_yhat_upper = (weekly[i]["yhat_upper"] + resid_fcast).round(0)

    # replace negatives with 0s
    weekly[i]["yhat"] = weekly_yhat.where(weekly_yhat >= 0, 0)
    weekly[i]["yhat_lower"] = weekly_yhat_lower.where(weekly_yhat_lower >= 0, 0)
    weekly[i]["yhat_upper"] = weekly_yhat_upper.where(weekly_yhat_upper >= 0, 0)

# create data/predictions folder if it doesn't exist
predictions_path = "../data/predictions/"
if not os.path.exists(predictions_path):
    os.mkdir(predictions_path)

# export to "data/predictions/" directory
total_data = pd.DataFrame()
for i in weekly:
    total_data = pd.concat([total_data, weekly[i]], axis=0)
total_data.to_csv(predictions_path + "predictions.csv")
