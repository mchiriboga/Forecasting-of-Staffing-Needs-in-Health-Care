#!/usr/bin/env python
#
# This script takes exception hours data from the past year
# Use the same strategy as the user interface script
# Generates the test result of 2018, with yhat and y
# That can be shown in Tableau to reproduce the graph in the report

# example usage
# python exception_prediction_result.py ../data/exception_hours.csv

import pandas as pd
import numpy as np
import datetime
import os
from fbprophet import Prophet
from stldecompose import decompose, forecast
from stldecompose.forecast_funcs import (naive, drift, mean, seasonal_naive)
import argparse

import warnings
warnings.filterwarnings("ignore")

# read in command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('excep_train')  # exception data
args = parser.parse_args()

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

# main function
def main():
    '''
    Main function that generates the result.
    '''
    # load data
    data = pd.read_csv(args.excep_train, parse_dates=["SHIFT_DATE"])
    # create train, val, and test
    train = data[(data["SHIFT_DATE"]>"2012-12-31") & (data["SHIFT_DATE"]<"2018-01-01")]
    val = data[(data["SHIFT_DATE"]>"2017-12-31") & (data["SHIFT_DATE"]<"2019-01-01")]

    # using only a portion of the sites
    train_clean = train[(train["SITE"]=="St Paul's Hospital") |
                        (train["SITE"]=="Mt St Joseph") |
                        (train["SITE"]=="Holy Family") |
                        (train["SITE"]=="SVH Langara") |
                        (train["SITE"]=="Brock Fahrni") |
                        (train["SITE"]=="Youville Residence")]
    train_clean = train_clean[(train_clean["JOB_FAMILY"]=="DC1000") |
                        (train_clean["JOB_FAMILY"]=="DC2A00") |
                        (train_clean["JOB_FAMILY"]=="DC2B00") ]

    val_clean = val[(val["SITE"]=="St Paul's Hospital") |
                    (val["SITE"]=="Mt St Joseph") |
                    (val["SITE"]=="Holy Family") |
                    (val["SITE"]=="SVH Langara") |
                    (val["SITE"]=="Brock Fahrni") |
                    (val["SITE"]=="Youville Residence")]
    val_clean = val_clean[(val_clean["JOB_FAMILY"]=="DC1000") |
                        (val_clean["JOB_FAMILY"]=="DC2A00") |
                        (val_clean["JOB_FAMILY"]=="DC2B00") ]


    # create training dataframes
    splitting_train = train_clean.groupby(["JOB_FAMILY", "SITE", "SUB_PROGRAM", "SHIFT_DATE"]).size().reset_index()
    splitting_train = splitting_train.rename({"SHIFT_DATE":"ds", 0:"y"}, axis=1)

    # create validation dataframes
    splitting_val = val_clean.groupby(["JOB_FAMILY", "SITE", "SUB_PROGRAM", "SHIFT_DATE"]).size().reset_index()
    splitting_val = splitting_val.rename({"SHIFT_DATE":"ds", 0:"y"}, axis=1)

    # create timeframe data for prediction
    total_timeframe = pd.DataFrame(pd.date_range(start='2013-01-01', end='2017-12-31', freq="D")).rename({0:"ds"}, axis=1)
    timeframe = pd.DataFrame(pd.date_range(start='2018-01-01', end='2018-12-31', freq="D")).rename({0:"ds"}, axis=1)

    # unique combinations
    sites = train_clean["SITE"].unique()
    job_families = train_clean["JOB_FAMILY"].unique()
    sub_programs = train_clean["SUB_PROGRAM"].unique()

    # create and store predictions and true results
    models = {}
    split_data = {}
    pred_results_past = {}
    pred_results_future = {}
    true_results = {}
    for i in sites:
        for j in job_families:
            for k in sub_programs:
                temp_data_train = splitting_train[(splitting_train["SITE"]==i) & (splitting_train["JOB_FAMILY"]==j) & (splitting_train["SUB_PROGRAM"]==k)].reset_index()
                temp_data_train = pd.merge(total_timeframe, temp_data_train, on="ds", how="outer")
                temp_data_train["y"] = temp_data_train["y"].fillna(0)

                temp_data_val = splitting_val[(splitting_val["SITE"]==i) & (splitting_val["JOB_FAMILY"]==j) & (splitting_val["SUB_PROGRAM"]==k)].reset_index(drop=True)
                temp_data_val = pd.merge(timeframe, temp_data_val, on="ds", how="outer")
                temp_data_val["y"] = temp_data_val["y"].fillna(0)

                split_data[(i, j, k)] = temp_data_train
                true_results[(i, j, k)] = temp_data_val
                if temp_data_val["y"].sum() >= 300.0:
                    pred_results_past[(i, j, k)], models[(i, j, k)] = run_prophet(temp_data_train, total_timeframe)
                    pred_results_future[(i, j, k)] = models[(i, j, k)].predict(timeframe)
                    print("Fitting -", i, j, k, ": Done")

    # combine predictions and true results
    combined = {}
    for i in pred_results_future:
        combined[i] = pd.merge(true_results[i],
                               pred_results_future[i],
                               on="ds",
                               how="outer")[["ds", "y", "yhat", "yhat_lower", "yhat_upper"]]

    # convert to week and calculating errors weekly
    weekly = {}
    for i in combined:
        # create week column
        combined[i]["ds"] = combined[i]["ds"]-pd.DateOffset(weekday=0, weeks=1)
        combined[i]["week"] = combined[i]["ds"].dt.week

        # store y, yhat, yhat_lower, yhat_upper
        weekly_y = combined[i].groupby("ds").y.sum().reset_index()
        weekly_yhat = combined[i].groupby("ds").yhat.sum().astype(int).reset_index()
        weekly_yhat_lower = combined[i].groupby("ds").yhat_lower.sum().astype(int).reset_index()
        weekly_yhat_upper = combined[i].groupby("ds").yhat_upper.sum().astype(int).reset_index()

        # replace negative prediction values with 0
        weekly_yhat = weekly_yhat.where(weekly_yhat["yhat"] >= 0, 0)
        weekly_yhat_lower = weekly_yhat_lower.where(weekly_yhat_lower["yhat_lower"] >= 0, 0)
        weekly_yhat_upper = weekly_yhat_upper.where(weekly_yhat_upper["yhat_upper"] >= 0, 0)


        # merge weekly results
        weekly[i] = pd.concat([weekly_y, weekly_yhat["yhat"],
                               weekly_yhat_lower["yhat_lower"],
                               weekly_yhat_upper["yhat_upper"]], axis=1)

        # create columns "year", "site", "job_family", "sub_program"
        length = weekly[i].shape[0]
        weekly[i]["week"] = weekly[i]["ds"].dt.weekofyear
        weekly[i]["site"] = np.repeat(i[0], length)
        weekly[i]["job_family"] = np.repeat(i[1], length)
        weekly[i]["sub_program"] = np.repeat(i[2], length)

    # model residuals
    for i in weekly:
        forecasted = pred_results_past[i]
        actual = split_data[i]

        error = actual["y"] - forecasted["yhat"]
        obs = total_timeframe.copy()
        obs["error"] = error
        obs = obs.set_index("ds")

        decomp = decompose(obs, period=365)
        weekly_fcast = forecast(decomp, steps=365, fc_func=drift, seasonal=True)
        weekly_fcast["week"] = weekly_fcast.index-pd.DateOffset(weekday=0, weeks=1)
        weekly_fcast = weekly_fcast.groupby("week").sum()

        resid_fcast = weekly_fcast.reset_index()["drift+seasonal"]
        weekly_yhat = (weekly[i]["yhat"] + resid_fcast).round(0)
        weekly_yhat_lower = (weekly[i]["yhat_lower"] + resid_fcast).round(0)
        weekly_yhat_upper = (weekly[i]["yhat_upper"] + resid_fcast).round(0)

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
    total_data.to_csv(predictions_path + "exception_predictions.csv")

# call main function
if __name__ == "__main__":
    main()
