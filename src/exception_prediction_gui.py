#!/bin/env python
import PySimpleGUI as sg
import pandas as pd
import numpy as np
import datetime
import os
import matplotlib
matplotlib.use("TkAgg")
from fbprophet import Prophet
from stldecompose import decompose, forecast
from stldecompose.forecast_funcs import (naive, drift, mean, seasonal_naive)

import warnings
warnings.filterwarnings("ignore")

# time series model function
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

sg.ChangeLookAndFeel('BlueMono')
sg.SetOptions(element_padding=(10,3))

layout = [
    [sg.Text('Choose a file to train the models', size=(35, 1))],
    [sg.Text('Your File', size=(15, 1), auto_size_text=False, justification='right'), sg.InputText(os.path.abspath(os.path.join(os.getcwd(), "../data/exception_hours.csv"))), sg.FileBrowse()],
    [sg.Text('_'  * 80)],
    [sg.Text('Please enter the timeframe you would like to predict:')],
    [sg.Text('From (Start Date)', size=(15, 1), auto_size_text=False, justification='right'), sg.InputText(('YYYY-MM-DD'), key="startdate"), sg.CalendarButton('Choose Date', key='date1')],
    [sg.Text('To (End Date)', size=(15, 1), auto_size_text=False, justification='right'), sg.InputText(('YYYY-MM-DD'), key="enddate"), sg.CalendarButton('Choose Date', key='date2')],
    [sg.Submit(), sg.Cancel()],
    ]

# setup layout
window = sg.Window('Exception Count Prediction Tool', grab_anywhere=False).Layout(layout)

while True:
    event, values = window.Read(timeout = 200)
    # setup calendar buttons
    if values["date1"] is not None:
        window.Element("startdate").Update(str(values["date1"])[:10])

    if values["date2"] is not None:
        window.Element("enddate").Update(str(values["date2"])[:10])

    if event is None or event == 'Cancel':
        break
    elif event == "Submit":
        try:
            # create prediction timeframe
            timeframe_future = pd.DataFrame(pd.date_range(start=str(values["startdate"]), end=str(values["enddate"]), freq="D")).rename({0:"ds"}, axis=1)
            threshold_start_date = pd.to_datetime(str(values["startdate"]))-datetime.timedelta(days=4*365.25)
            threshold_dates = pd.DataFrame(pd.date_range(start=threshold_start_date, end=pd.to_datetime(str(values["startdate"])) - datetime.timedelta(days=1), freq="D")).rename({0:"ds"}, axis=1)
        except ValueError as e:
            print("Please input correct dates.")
            continue

        # read data
        try:
            data = pd.read_csv(values[0], parse_dates=["SHIFT_DATE"])
        except:
            print("Please ensure the path to the data is correct.")
            continue

        # clean data
        data_clean = data[(data["SITE"]=="St Paul's Hospital") |
                            (data["SITE"]=="Mt St Joseph") |
                            (data["SITE"]=="Holy Family") |
                            (data["SITE"]=="SVH Langara") |
                            (data["SITE"]=="Brock Fahrni") |
                            (data["SITE"]=="Youville Residence")]
        data_clean = data_clean[(data_clean["JOB_FAMILY"]=="DC1000") |
                            (data_clean["JOB_FAMILY"]=="DC2A00") |
                            (data_clean["JOB_FAMILY"]=="DC2B00") ]

        # create cleaned dataframes
        data_group = data_clean.groupby(["JOB_FAMILY", "SITE", "SUB_PROGRAM", "SHIFT_DATE"]).size().reset_index()
        data_group = data_group.rename({"SHIFT_DATE":"ds", 0:"y"}, axis=1)

        # create "SITE", "JOB_FAMILY", and "SUB_PROGRAM" groups
        sites = data_clean["SITE"].unique()
        job_families = data_clean["JOB_FAMILY"].unique()
        sub_programs = data_clean["SUB_PROGRAM"].unique()

        # create timeframe_past
        min_shift_date = np.min(data["SHIFT_DATE"])
        timeframe_past = pd.DataFrame(pd.date_range(start=min_shift_date, end=pd.to_datetime(str(values["startdate"])) - datetime.timedelta(days=1), freq="D")).rename({0:"ds"}, axis=1)

        # for progress bar
        size = len(sites)*len(job_families)*len(sub_programs)
        current_count = 0

        # create and store predictions and true results
        models = {}
        data_individual = {}
        pred_results = {}
        for i in sites:
            for j in job_families:
                for k in sub_programs:
                    temp_data = data_group[(data_group["SITE"]==i) & (data_group["JOB_FAMILY"]==j) & (data_group["SUB_PROGRAM"]==k)].reset_index()

                    # check threshold
                    threshold_data = temp_data[temp_data["ds"] >= threshold_start_date]
                    if threshold_data["y"].sum() >= 300.0:
                        # forecast numbers
                        temp_data = pd.merge(timeframe_past, temp_data, on="ds", how="outer")
                        temp_data["y"] = temp_data["y"].fillna(0)

                        data_individual[(i, j, k)] = temp_data
                        pred_results[(i, j, k)], models[(i, j, k)] = run_prophet(temp_data, timeframe_future)
                        print("Fitting -", i, j, k, ": Done")

                    # create progress bar
                    current_count += 1
                    sg.OneLineProgressMeter('Fitting models.', current_count, size, 'fit_model', 'Fitting models.', orientation="horizontal")

        # compile results
        current_count = 0
        weekly = {}
        for i in data_individual.keys():
            # create week column
            combined= pred_results[i][["ds", "yhat", "yhat_lower", "yhat_upper"]]
            combined["week"] = combined["ds"].dt.week
            combined["ds"] = combined["ds"]-pd.DateOffset(weekday=0, weeks=1)

            # store y, yhat, yhat_lower, yhat_upper
            weekly_yhat = combined.groupby("ds").yhat.sum().round(0).astype(int).reset_index()
            weekly_yhat_lower = combined.groupby("ds").yhat_lower.sum().round(0).astype(int).reset_index()
            weekly_yhat_upper = combined.groupby("ds").yhat_upper.sum().round(0).astype(int).reset_index()

            # merge weekly results
            weekly[i] = pd.concat([weekly_yhat["ds"], weekly_yhat["yhat"],
                                   weekly_yhat_lower["yhat_lower"],
                                   weekly_yhat_upper["yhat_upper"]], axis=1)


            # create columns "year", "site", "JOB_FAMILY"
            length = weekly[i].shape[0]
            weekly[i]["week"] = weekly[i]["ds"].dt.weekofyear
            weekly[i]["site"] = np.repeat(i[0], length)
            weekly[i]["job_family"] = np.repeat(i[1], length)
            weekly[i]["sub_program"] = np.repeat(i[2], length)

            # code for minimizing errors (model residuals)
            forecasted = models[i].predict(timeframe_future)
            actual = data_individual[i]

            # get residuals
            error = actual["y"] - forecasted["yhat"]
            obs = timeframe_past.copy()
            obs["error"] = error
            obs = obs.set_index("ds")

            # model residuals
            period = int((np.max(timeframe_future) - np.min(timeframe_future)).dt.days)+1
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

            # create progress bar
            current_count += 1
            sg.OneLineProgressMeter('Compiling Results.', current_count+1, size, 'compile_results','Compiling Results.', orientation="horizontal")

        # create data/predictions folder if it doesn't exist
        predictions_path = "../data/predictions/"
        if not os.path.exists(predictions_path):
            os.mkdir(predictions_path)

        # export to "data/predictions/" directory
        total_data = pd.DataFrame()
        for i in weekly:
            total_data = pd.concat([total_data, weekly[i]], axis=0)
        total_data.to_csv(predictions_path + "predictions.csv")
        break
window.Close()
