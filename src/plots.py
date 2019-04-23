import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def count_plot(data, column, figsize=None, filename=None):
    """
    Saves and returns a plot of the count of observations
    given a dataframe and a column.

    Key arguments:
    --------------
    data -- (DataFrame) data that we want to filter
    column -- (str) column name
    figsize -- (tuple) figure size
    filename -- (str) name of the saved file

    Returns: 
    --------------
    A barplot of the count for each unique observation

    """
    # count_dict = dict(Counter(data[column]))
    count_dict = dict(data[column].value_counts())
    keys = []
    values = []
    for key, val in count_dict.items():
        keys.append(key)
        values.append(val)
    df = pd.DataFrame({column: keys, "COUNT": values})
    plt.figure(figsize=figsize)
    plot = sns.barplot(data = df, x = column, y = "COUNT")
    if filename:
        plt.savefig(filename)
    return plot
    

def hour_plot(data, column, figsize=None, filename=None):
    """
    Saves and returns a plot of the total exception hours
    grouped by a column given a dataframe and a column.

    Key arguments:
    --------------
    data -- (DataFrame) data that we want to filter
    column -- (str) column name
    figsize -- (tuple) figure size
    filename -- (str) name of the saved file

    Returns: 
    --------------
    Returns a plot of the total exception hours
    grouped by a column given a dataframe and a column

    """
    hour_counter = {}
    for i, j in enumerate(data[column]):
        if j in hour_counter:
            hour_counter[j] += data.loc[i, "EXCEPTION_HOURS"]
        else:
            hour_counter[j] = data.loc[i, "EXCEPTION_HOURS"]
    keys = []
    values = []
    for key, val in hour_counter.items():
        keys.append(key)
        values.append(val)
    df = pd.DataFrame({column: keys, "HOURS": values})
    plt.figure(figsize=figsize)
    plot = sns.barplot(data = df, x = column, y = "HOURS")
    if filename:
        plt.savefig(filename)
    return plot


def filter_bygroup(data, column, min_obs=1):
    """
    Filters a DataFrame by keeping only groups 
    that reach the minimum number of observations.

    Key arguments:
    --------------
    data -- (DataFrame) data that we want to filter
    column -- (str) column name
    min_obs -- (int) minimum number of observations per group

    Returns: 
    --------------
    The filtered DataFrame

    """
    return data.groupby(column).filter(lambda x: len(x) > min_obs)