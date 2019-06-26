#!/usr/bin/env python
# 
# This script takes exception hours data from past year
# Use the same strategy in the user interface script of Exception_Classification.py
# Generates the test result of 2018
# That can be shown in Tableau to reproduce the graph in the report

# example usage
# python classification_test_result.py ../data/exception_hours.csv

# import packages
import pandas as pd
import numpy as np
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
import datetime
import os
import warnings
warnings.filterwarnings("ignore")
import argparse

# read in command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('raw')  # raw data
args = parser.parse_args()

# global variables
CAT_1 = ["Regular Relief Utilized",
         "Casual at Straight-Time",
         "PT Over FTE",
         "Miscellaneous Straight-Time",
         "PT Employee Moved - Straight-Time",
         "FT Employee Moved - Straight-Time"]
CAT_2 = ["Overtime",
         "Relief Not Found",
         "Agency",
         "Insufficient Notice",
         "On-Call"]

# main function
def main():
    '''
    Main function that generates the result.
    '''

    # read dataframe
    raw_data = pd.read_csv(args.raw,index_col=[0])
    training = raw_data[(raw_data["SHIFT_DATE"]>"2012-12-31") & (raw_data["SHIFT_DATE"]<"2018-01-01")]
    test = raw_data[(raw_data["SHIFT_DATE"]>"2017-12-31") & (raw_data["SHIFT_DATE"]<"2019-01-01")]

    # generate result
    train = training_wrangling(training) #df2
    pred = prediction_wrangling(test) #df3
    output = exception_prediction(train, pred) #df4

    # export output
    output = output.reset_index()
    output.to_csv("../data/predictions/classification_result.csv", header=True)


def training_wrangling(dataframe):
    '''
    Given a dataframe, wrangling to format using for training the model.
    
    Paramenters
    -----------
    dataframe: dataframe
        Raw data 
        
    Returns
    -------
    dataframe
        One for natural prediction, one for conservative prediction
    '''
    df = dataframe.copy()
    
    # filter target group: Nurse
    df = df[df["LABOR_AGREEMENT"]=="NURS"]

    # filter the 6 site the client suggested
    df = df[(df["SITE"]=="St Paul's Hospital") |
            (df["SITE"]=="Mt St Joseph") |
            (df["SITE"]=="Holy Family") |
            (df["SITE"]=="SVH Langara") |
            (df["SITE"]=="Brock Fahrni") |
            (df["SITE"]=="Youville Residence")]
    
    # filter NaN in MIN_CALL_TO_MAX_CALL_MINUTES and EXCEPTION_CREATION_TO_SHIFTSTART_MINUTES
    df = df[pd.notnull(df["MIN_CALL_TO_MAX_CALL_MINUTES"])]
    df = df[pd.notnull(df["EXCEPTION_CREATION_TO_SHIFTSTART_MINUTES"])]

    # filter MIN_CALL_TO_MAX_CALL_MINUTES > 0 which means the call time is after exception creation time
    df = df[(df["MIN_CALL_TO_MAX_CALL_MINUTES"] >= 0)]

    # filter EXCEPTION_CREATION_TO_SHIFTSTART_MINUTES < 0 which means the creation time is ahead of shift start
    df = df[(df["EXCEPTION_CREATION_TO_SHIFTSTART_MINUTES"] <= 0)]

    # create NOTICE = EXCEPTION_CREATION_TO_MAXCALL_MINUTES - MIN_CALL_TO_MAX_CALL_MINUTES 
    #               =EXCEPTION_CREATION_TO_MINCALL_MINUTES
    df["NOTICE_"] = df["EXCEPTION_CREATION_TO_MAXCALL_MINUTES"] + df["MIN_CALL_TO_MAX_CALL_MINUTES"]

    # create a column to indicate the month of the SHIFT_DATE
    df["MONTH_"] = pd.to_datetime(df['SHIFT_DATE']).dt.month

    # create a column to indicate the SHIFT of the exception
    df["START_TIME"] = pd.to_datetime(df["START_TIME"])
    df["SHIFT_"] = 3
    df["SHIFT_"][(df["START_TIME"] >= "06:00:00") & (df["START_TIME"] < "13:00:00")] = 1
    df["SHIFT_"][(df["START_TIME"] >= "13:00:00") & (df["START_TIME"] < "19:00:00")] = 2

    # convert "EXCEPTION_GROUP","PROGRAM","SITE","DEPARTMENT" value from str to numeric for randomforest model
    le = preprocessing.LabelEncoder()
    df["EXCEPTION_GROUP_"] = le.fit_transform(df["EXCEPTION_GROUP"])                     
    df["PROGRAM_"] = le.fit_transform(df["PROGRAM"])
    df["SITE_"] = le.fit_transform(df["SITE"])
    df["JOB_FAMILY_"] = le.fit_transform(df["JOB_FAMILY"])
    df["SUB_PROGRAM_"] = le.fit_transform(df["SUB_PROGRAM"])
    df["DEPARTMENT_"] = le.fit_transform(df["DEPARTMENT"])
    return df

def prediction_wrangling(dataframe):
    '''
    Given a dataframe using for prediction, wrangling to format using for training the model.
    
    Paramenters
    -----------
    dataframe: dataframe
        Raw data of prediction, which should not contains "EARNING_CATEGORY"
        
    Returns
    -------
    dataframe
        Dataframe that contains converted value
        
    '''
    df = dataframe.copy()
    
    # if the dataframe contains EARNING_CATEGORY, drop the column
    if 'EARNING_CATEGORY' in df.columns:
        df = df.drop('EARNING_CATEGORY', 1)
    
    # filter target group: Nurse
    df = df[df["LABOR_AGREEMENT"]=="NURS"]

    # filter the 6 site the client suggested
    df = df[(df["SITE"]=="St Paul's Hospital") |
            (df["SITE"]=="Mt St Joseph") |
            (df["SITE"]=="Holy Family") |
            (df["SITE"]=="SVH Langara") |
            (df["SITE"]=="Brock Fahrni") |
            (df["SITE"]=="Youville Residence")]
    
    # filter NaN in MIN_CALL_TO_MAX_CALL_MINUTES and EXCEPTION_CREATION_TO_SHIFTSTART_MINUTES
    # df["NOTICE_"] = pd.to_datetime(df["EXCEPTION_CREATION_DATE"]).map(lambda x:int((x - datetime.datetime.now()).total_seconds()/60))
    
    # filter NaN in MIN_CALL_TO_MAX_CALL_MINUTES and EXCEPTION_CREATION_TO_SHIFTSTART_MINUTES
    df = df[pd.notnull(df["MIN_CALL_TO_MAX_CALL_MINUTES"])]
    df = df[pd.notnull(df["EXCEPTION_CREATION_TO_SHIFTSTART_MINUTES"])]
    # filter MIN_CALL_TO_MAX_CALL_MINUTES > 0 which means the call time is after exception creation time
    df = df[(df["MIN_CALL_TO_MAX_CALL_MINUTES"] >= 0)]
    # filter EXCEPTION_CREATION_TO_SHIFTSTART_MINUTES < 0 which means the creation time is ahead of shift start
    df = df[(df["EXCEPTION_CREATION_TO_SHIFTSTART_MINUTES"] <= 0)]
    
    df["NOTICE_"] = df["EXCEPTION_CREATION_TO_MAXCALL_MINUTES"] + df["MIN_CALL_TO_MAX_CALL_MINUTES"]
    
    # create a column to indicate the month of the SHIFT_DATE
    df["MONTH_"] = pd.to_datetime(df['SHIFT_DATE']).dt.month

    # create a column to indicate the SHIFT of the exception
    df["START_TIME"] = pd.to_datetime(df["START_TIME"])
    df["SHIFT_"] = 3
    df["SHIFT_"][(df["START_TIME"] >= "06:00:00") & (df["START_TIME"] < "13:00:00")] = 1
    df["SHIFT_"][(df["START_TIME"] >= "13:00:00") & (df["START_TIME"] < "19:00:00")] = 2

    # convert "EXCEPTION_GROUP","PROGRAM","SITE","DEPARTMENT" value from str to numeric for randomforest model
    le = preprocessing.LabelEncoder()
    df["EXCEPTION_GROUP_"] = le.fit_transform(df["EXCEPTION_GROUP"])                     
    df["PROGRAM_"] = le.fit_transform(df["PROGRAM"])
    df["SITE_"] = le.fit_transform(df["SITE"])
    df["JOB_FAMILY_"] = le.fit_transform(df["JOB_FAMILY"])
    df["SUB_PROGRAM_"] = le.fit_transform(df["SUB_PROGRAM"])
    df["DEPARTMENT_"] = le.fit_transform(df["DEPARTMENT"])
    return df

def replace_str(string):
    '''
    Create function for grouping label
    '''
    if string in CAT_1:
        return string.replace(string, "Straight Time")
    elif string in CAT_2:
        return string.replace(string, "Overtime and Beyond")
    else:
        return string

def exception_prediction(dataframe1,dataframe2):
    '''
    Given training dataframe and prediction dataframe doing prediction.
    
    Paramenters
    -----------
    dataframe1: 
        dataframe wrangled by training_wrangling
    
    dataframe2: 
        dataframe wrangled by prediction_wrangling
        
    Returns
    -------
    dataframe
        Contains prediction result and Suggestion
    '''
    # create dataframe for Natural Prediction and Conservative Prediction
    df = dataframe1.copy()
    df["EARNING_CATEGORY"] = df["EARNING_CATEGORY"].apply(replace_str)

    # Prepare data for model fitting
    feature_cols = ["EXCEPTION_HOURS",
                    "EXCEPTION_CREATION_TO_SHIFTSTART_MINUTES",
                    "SITE_",
                    "EXCEPTION_GROUP_",
                    "PROGRAM_",
                    "MONTH_",
                    "SUB_PROGRAM_",
                    "DEPARTMENT_",
                    "NOTICE_",
                    "SHIFT_"]
    X = df.loc[:, feature_cols]
    y = df.EARNING_CATEGORY

    # build random forest model and test
    RF = RandomForestClassifier(n_estimators=25, 
                                max_depth=15,
                                min_samples_split=6,
                                min_samples_leaf = 7,
                                class_weight='balanced')
    RF.fit(X,y)
    print("Model Training Score:", round(RF.score(X,y),3))

    # create result dataframe
    pred_dict = dataframe2.copy()
    pred_dict['PREDICTION'] = RF.predict(dataframe2.loc[:,feature_cols])
    result = pred_dict.drop(["SITE_", "EXCEPTION_GROUP_", "PROGRAM_", "MONTH_", "SUB_PROGRAM_", "DEPARTMENT_", "NOTICE_","JOB_FAMILY_"], axis=1)
    return result

# call main function
if __name__ == "__main__":
    main()