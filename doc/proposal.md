# Short-term staff demand forecast for Providence Healthcare


April, 2019                               

[Marcelle A. Chiriboga Carvalho](https://github.com/mchiriboga), [Luo Yang](https://github.com/lyiris22), [Patrick Tung](https://github.com/tungpatrick) and [Weifeng (Davy) Guo](https://github.com/DavyGuo) 

Mentored by [Rodolfo Lourenzutti](https://github.com/Lourenzutti)


### Project Summary

The purpose of the project was to help the People Analytics and Innovation Team from Providence Health Care to predict the short-term staff needs in order to prepare for potential cost rising and staff shortage.


### Introduction

Providence Health Care (PHC) is a government agency that operates 16 healthcare facilities in BC. For most positions in the healthcare business, any staffing leaves must always be filled in by another person. More than 70% of the operation costs in health care is for staffing, and the substitute caused by short notice leave usually cost more than regular staff. Hence, predicting the short-term staff needs could help PHC prepare for potential leave with short notice. Suggested by our partner, we will focus our target on the “operation level”, which has the time horizon that less than a month. "Operational" means that we must answer the question "how many back up staff do we need on a daily basis to maintain 100% staffing"

Based on the data provided by Providence, our identified problem of this project is “How many exception will happen for the next 30 days and what are the types of exceptions”. We plan to study the data first to identify potential features and labels. Then using the sample data, we plan to build and train the model to predict and test for accuracy. Once we have a model prototype, we will bring new details and update the data and model until we have reached a certain level.

The final product will contain three component:

- A data wrangling script in R or Python to help the partner clean the data

- A script that handles modeling process and generate final

- A dashboard to visualize the result using Shiny App (for now; will adjust to Tableau based on partner's preference)


### Data Science Techniques

Since we are having more than 2 millions records of exceptions through 9 years, we intend to split the raw data based on year. In this way, not only we could have smaller dataset to generate some insight, but also telling the difference causing by time (facility opening, system develop, etc).  

We will start from simple question with simple data and move forward once we achieve certain goal. The milestone for questions are:

Step 1: How many exceptions will happen next month?

Step 2: For those exception predicted, how many of them will find relief or not find one.

Step 3: For those exception predicted, what kind of position they are.

We intend to try 3 approaches to solve the problem, and will apply some/all of them based on further study and process. The following approaches are:

- Time Series: We assume for every nature year, there is a pattern for the exception occurrence. Like mentioned earlier, we will predict a full year’s exception based on historical data, so that the partner could check any month or month period during the year to have the general idea

- Linear Regression: We assume that the partner would like to know the exception situation for next month based on a certain period of data (like one week from today using 1 year’s data before today). In this case, we will generate a linear regression to see the relationship among certain predictors. 

- Neural Network: Because our problem is to forecast time series data, neural networks may potentially be very helpful. We have seen that neural networks can be used in many applications in the world for problems ranging from driverless cars, to image recognition, and even for forecasting. The applications of neural networks as machine learning models has been dramatically increasing. Especially with LSTM models, we will be able to use a history of a sequence of data to “effectively” predict the future sequence. 


### Timeline and Evaluation

We have following time schedule base on group discussion, and the actual process may update due to the reality situation:

| Time Period | Milestone |
|-----------------|-------------|
| Week 1 | Finalize the proposal report to send to our mentor and partner |
| Week 2 | Data wrangling and feature selection (and more EDA) |
| Week 3 - 4 | Explore different approaches to fit the models |
| Week 5 | Build algorithms, testing, adjusting |
| Week 6 | Improve the dashboard, wrapping up |
| Week 7 | Presentations and reports |


### Feedback and discussion

