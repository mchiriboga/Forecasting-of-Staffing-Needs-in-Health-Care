#!/usr/bin/env python
# 
# This script takes exception and productive hours data
# From past year as training data
# Takes the productive hours data of the period to predict
# Produces the number of urgent exceptions
# On a daily basis in the period you want to predict
# Generate the output in a csv file

# example usage
# Python urgent_prediction.py exception_train 2018-01-01 productive_train productive_pred result

# import packages
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
import argparse

# read in command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('excep_train')  # exception training data
parser.add_argument('valid_until')  # YYYY-MM-DD, date that the training data is valid until
parser.add_argument('prod_train')  # productive hours training data
parser.add_argument('prod_pred')  # productive hours prediction data
parser.add_argument('result')  # path of file to save the result
args = parser.parse_args()

# main function
def main():
    '''
    Main function that generates the result.
    '''

    # load data
    excep_train = pd.read_csv(args.excep_train)
    prod_train = pd.read_csv(args.prod_train)
    prod_pred = pd.read_csv(args.prod_pred)

    # data wrangling
    # exclude data of 2014 from the training data to generate better results
    excep_train_full = excep_train[(excep_train["SHIFT_DATE"] < "2014-01-01") |
                           ((excep_train["SHIFT_DATE"] > "2014-12-31") & (excep_train['SHIFT_DATE'] < args.valid_until))]
    prod_train_full = prod_train[(prod_train["SHIFT_DATE"] < "2014-01-01") |
                      ((prod_train["SHIFT_DATE"] > "2014-12-31") & (prod_train['SHIFT_DATE'] < args.valid_until))]

    # prediction for DC1000
    excep_train_dc1 = excep_train_full[excep_train_full["JOB_FAMILY"] == "DC1000"]
    prod_train_dc1 = prod_train_full[prod_train_full["JOB_FAMILY_DESCRIPTION"] == "Registered Nurse-DC1"]
    prod_pred_dc1 = prod_pred[prod_pred["JOB_FAMILY_DESCRIPTION"] == "Registered Nurse-DC1"]

    result_dc1 = fit_predict(excep_train_dc1, prod_train_dc1, prod_pred_dc1)
    result_dc1['job_family'] = "DC1000"

    # prediction for DC2A00
    excep_train_dc2a = excep_train_full[excep_train_full["JOB_FAMILY"] == "DC2A00"]
    prod_train_dc2a = prod_train_full[prod_train_full["JOB_FAMILY_DESCRIPTION"] == "Registered Nurse-DC2A Sup"]
    prod_pred_dc2a = prod_pred[prod_pred["JOB_FAMILY_DESCRIPTION"] == "Registered Nurse-DC2A Sup"]

    result_dc2a = fit_predict(excep_train_dc2a, prod_train_dc2a, prod_pred_dc2a)
    result_dc2a['job_family'] = "DC2A00"

    # prediction for DC2B00
    excep_train_dc2b = excep_train_full[excep_train_full["JOB_FAMILY"] == "DC2B00"]
    prod_train_dc2b = prod_train_full[prod_train_full["JOB_FAMILY_DESCRIPTION"] == "Registered Nurse-DC2B"]
    prod_pred_dc2b = prod_pred[prod_pred["JOB_FAMILY_DESCRIPTION"] == "Registered Nurse-DC2B"]

    result_dc2b = fit_predict(excep_train_dc2b, prod_train_dc2b, prod_pred_dc2b)
    result_dc2b['job_family'] = "DC2B00"

    # generate result
    output = pd.concat([result_dc1, result_dc2a, result_dc2b])
    output_num = output._get_numeric_data()
    output_num[output_num < 0] = 0  # convert negative values to zero
    
    # save result file
    output.to_csv(args.result)


def day_X(df, productive, enc = OneHotEncoder(handle_unknown='ignore', sparse = False), method = "train"):
    '''
    Generate the predictors to be used in the linear regression model.

    Args:
        df (pandas dataframe): exception hours data
        productive (pandas dataframe): productive hours data
        enc (OneHotEncoder object): generate a new encoder by default, use specific encoder while given
        method (str): "train" for generate training data and "pred" for generating predicting data
    
    Returns:
        dates (pandas dataframe): predictors data
        enc (OneHotEncoder object): the encoder used in this method

    '''

    # decide whether the output is for training data or predicting data
    if method == "train":
        dates = df
    else:
        dates = productive
    
    # extract information from dates
    dates = dates.groupby(['SHIFT_DATE']).size().reset_index()
    # week of the year
    dates["week"] = dates["SHIFT_DATE"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").isocalendar()[1])
    # day of the week
    dates["weekday"] = dates["SHIFT_DATE"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").isocalendar()[2])
    # month of the year
    dates['month'] = dates['SHIFT_DATE'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").month)
    # day of the month
    dates['monthday'] = dates['SHIFT_DATE'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").day)

    # in the training method, fit a new one hot encoder
    # in the predicting method, use the encoder from the training data
    if method == "train":
        enc.fit(dates[['week','weekday','month','monthday']])
    # encode date information into one hot format
    onehot = enc.transform(dates[['week','weekday','month','monthday']])

    # add date information to dataset
    for i in range(0,53):
        col_name = "week_" + str(i)
        dates[col_name] = onehot[:,i]

    for i in range(53,60):
        col_name = "day_" + str(i-52)
        dates[col_name] = onehot[:,i]

    for i in range(60,72):
        col_name = "month_" + str(i-59)
        dates[col_name] = onehot[:,i]

    for i in range(72,102):
        col_name = "monthday_" + str(i-71)
        dates[col_name] = onehot[:,i]

    # drop columns
    dates = dates.drop([0, 'week', 'weekday','month','monthday'], axis=1)
    dates = dates.set_index('SHIFT_DATE')
    
    # add productive hours information
    prod = productive.groupby(['SHIFT_DATE']).sum()
    dates = dates.join(prod)
    
    return dates, enc

def day_y(df, X):
    '''
    Generate the labels to be used in the linear regression model.

    Args:
        df (pandas dataframe): exception hours data
        X (pandas dataframe): predictors that is already generated
    
    Returns:
        combined.y (list): labels data

    '''
    
    # keep only the urgent groups we care about
    result = df[(df["EARNING_CATEGORY"] == "Overtime") | (df["EARNING_CATEGORY"] == "Relief Not Found")]
    # count the urgent exception on daily basis
    result = result.groupby(['SHIFT_DATE']).size()
    result = pd.DataFrame(result)
    result = result.rename({0:"y"}, axis=1)
    result = result.fillna(0)
    # keep the entries that are in the predictors set
    combined = X.join(result)
    
    return combined.y

def fit_predict(excep_train, prod_train, prod_pred):
    '''
    Fit a linear regression model and make predictons.

    Args:
        excep_train (pandas dataframe): exception hours data
        prod_train (pandas dataframe): productive data for training
        prod_pred (pandas dataframe): productive data for predicting
    
    Returns:
        prediction (pandas dataframe): urgent prediction

    '''
    
    # generate training data
    X_train, enc = day_X(excep_train, prod_train)
    y_train = day_y(excep_train, X_train)
    
    # generate predicting predictors
    X_val, temp = day_X(excep_train, prod_pred, enc, "pred")
    
    # clear possible nan and infinities
    X_train_clean = np.nan_to_num(X_train)
    y_train_clean = np.nan_to_num(y_train)
    X_val_clean = np.nan_to_num(X_val)

    # fit linear regression model
    reg = LinearRegression().fit(X_train_clean, y_train_clean)

    # result
    prediction = pd.DataFrame({"yhat": list(reg.predict(X_val_clean)), "ds": list(X_val.index)})
    
    return prediction

# call main function
if __name__ == "__main__":
    main()