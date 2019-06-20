# Forecasting of Staffing Needs in Health Care


June, 2019                               


Contributors: [Luo (Iris) Yang](https://github.com/lyiris22), [Marcelle Chiriboga](https://github.com/mchiriboga), [Patrick Tung](https://github.com/tungpatrick), [Weifeng (Davy) Guo](https://github.com/DavyGuo)

Mentor: [Rodolfo Lourenzutti](https://github.com/Lourenzutti)


## Executive Summary

For most positions in the healthcare business, any staff absences must always be filled in by another staff and the costs of substituting absences with short notice are usually significantly higher than regular staffing. Hence, preparing for potential shortages by predicting the short-term staffing needs can significantly improve the operational efficiency of healthcare institutions.

The purpose of the project was to help the People Analytics and Innovation Team from Providence Health Care (PHC) to predict the short-term staff needs in order to prepare for unexpected potential costs and staff shortages. The predictions are made based on the historical records of scheduled exceptions, i.e. staff absences due to unexpected or previously arranged reasons such as sick time, vacation, maternity leave, etc.

## Introduction

An increase in patients' waiting time at hospitals or the postponement of important procedures, such as surgeries, are known to be critical, which is why medical institutions try to make sure that their clinical positions have backups whenever possible. On the other hand, more than 70% of the operational costs in health care are tied to staffing and, overstaffing can result in a significant increase in these costs.

PHC is a government agency that operates more than 16 healthcare facilities in British Columbia, with almost 7,000 staff, including 1,000 medical staff. At their scale, under or over staffing can have significant impacts both in terms of cost to the organization and in quality of care provided to patients, and for this reason, accurately forecasting staffing needs can have a very positive impact.

In this project, we partnered with PHC to predict staff needs based in their historical exception records, focusing our predictions on the *operational level*, i.e. short term needs, specifically on a time horizon of less than a month. The goal was to answer the question “how many backup staff does PHC need on a weekly basis to have a full staff?”, giving them more time to handle the exceptions. More specifically we focused on building models for:

- Forecasting staffing needs on a weekly basis, allowing PHC to estimate how many back up staff are needed per site, subprogram, and job family;
- Forecasting how many exceptions will fall under the urgent exception groups (i.e. overtime and relief not found), allowing PHC to prioritize which exceptions to pay extra attention to in finding relief for;
- Classifying each exception logged on PHC's internal system in one of three possible categories.

## Data Science Methods

### Exception Count Predictions

To begin with the predictions of exception count, because we had to make sure that we did not overfit our model when training, we first split our data into three separate portions: training, validation, and testing. The training dataset consisted of data from 2013 to 2016. 2017 and 2018 were the datasets for validation and testing respectively. After further discussing about how to tackle this problem, we discovered that this was a problem in regards to time series data. Therefore, we concluded that there were several ways to solve this problem, for example, using regression, time series, or even neural networks. We attempted all of these methods on our validation set, and it turns out that fitting a time series model worked best for this problem. We then tried to fit different time series models using techniques and tools such as seasonal decomposition and Facebook’s open source tool called Prophet. Ultimately, we chose to move forward with the Prophet Facebook. Not only did the model provide the best results when comparing it with our validation set, it was also one of the easier models to implement on a large scale.

We want our forecast to be meaningful to PHC, which means that we wanted to provide accurate forecasts not just for the whole of PHC, but for the sub-categories belonging to PHC. Therefore, to do this, we split our data by SITE, JOB_FAMILY, and SUB_PROGRAM. As per our discussion with PHC, we chose to only focus our forecasts specifically on a subset of sites and job families. For SITE, we chose to focus only on the largest six health care facilities, which are: St Paul’s Hospital, Mt St Joseph, Holy Family, SVH Langara, Brock Fahrni, and Youville Residence. For JOB_FAMILY, we chose to focus only on nurses, but specifically the top three nurses: DC1000, DC2A00, DC2B00. 

To tune our models, we took a look at the Mean Absolute Error. The MAE provides a clear image for us to see how many exceptions we have predicted incorrectly averaged on a weekly basis. Overall, our MAE for our validation set and testing set were 118.42 and 131.57 respectively. This error is quite small in a sense that there are thousands of exceptions occurring each week. In terms of the errors for each facility, for the year 2018, we had the following MAEs:

<center>

| SITE | MAEs |
| --- | --- |
| St Paul's Hospital | 120.48 |
| Mt St Joseph | 40.69 |
| Holy Family | 17.54 |
| Brock Fahrni | 8.98 |
| Youville Residence | 6.23 |
| SVH Langara | 12.42 |

</center>

### Exception Classification

The classification model uses random forest classifiers to predict the possible outcome for an exception. We are aiming to generate insights for exceptions which have been created but yet been fulfilled, so the HR may change their priority to handling some exceptions to avoid unnecessary cost. After applying logistic regression, random forests, and gradient boosting, random forests performs best. And the interoperability is better than the other two, hence we agreed to choose random forest classifiers as our model.

`EARNING_CATEGORY` is the label in our model, but it has 12 values which is too detailed for our prediction and hugely affects the model accuracy. Per partner’s advice, as long as the relief type (like straight time) is the same, we can treat them as the same. Hence, we group the 12 labels into 3 labels, which are:

- Straight Time: which contains all kinds of straight time relief, the pay rate is the same as the normal rate which is positive

- Overtime and Beyond: which contains `Relief Not Found` and all kinds of relief which needs to be paid more than normal rate, which is negative to the company.

- Relief Not Needed, which is neutral to the company.

We applied the forward selection method to implement feature selection. We used `EXCEPTION_HOURS`, `EXCEPTION_CREATION_TO_SHIFTSTART_MINUTES`, `NOTCIE`(which is staff response time) to setup accuracy baseline, then added other features to see if it could increase model accuracy. After several tests, the following features are the rest of the features in our model: `SITE`, `PROGRAM`,  `SUB_PROGRAM`,  `EXCEPTION_GROUP`, `MONTH`, `DEPARTMENT`,  `SHIFT`.


We used validation set to test our model, the best result we have is listed below.

<center>

| |Accuracy|
|--------------------|:-------:|
| Validation | 0.841 |
| Straight Time | 0.936 |
| Overtime and Beyond| 0.638 |
| Relief Not Needed| 0.308 |

</center>

As you can see, the overall accuracy is not bad. But if we break it down to every category, the difference is obvious. Since Overtime costs more than Straight time, we need to improve the accuracy of Overtime. The reason caused the gap between categories is imbalanced data. We found out that the number of straight time is way more than the other two. Which makes sense that the model is more likely to predict an exception as straight time instead of the other two. So we updated our model to make it more balanced.

<center>

|  | Amount |
|--------------------|:-------:|
| Straight Time | 262,608 |
| Overtime and Beyond| 76,863 |
| Relief Not Needed| 11,806 |

</center>

The comparison of our model accuracy. We can see that the accuracy of overtime and relief not needed has increased while losing some accuracy of Straight time. Since the Overtime is more critical to PHC, the sacrifice of straight time is acceptable, and our final test accuracy is listed in the right column.

<center>

| | Original Validation | Adjusted Validation | Adjusted Test |
|--------------------|:-------:|:-------:|:-------:|
| Overall | 0.841 | 0.794 | 0.800 |
| Straight Time | 0.936 | 0.823 | 0.830 |
| Overtime and Beyond| 0.638 | 0.735 | 0.756 |
| Relief Not Needed| 0.308 | 0.625 | 0.633 |

</center>

This model’s output file is also a `.csv` file which adds two columns to the input data, one is the shift of exceptions per partner’s request. The other one is our prediction result.

#### Difficulties, Limitations, and Potential Improvements

Throughout the whole project, there were 2 main difficulties.

The first one is that we had missing data. Due to technical reasons, some of our data (e.g. `MIN_TO_MAX_MINUTES`) was missing. We had to remove some records in order to maintain the quality of our training data, which affected the model accuracy.

The second difficulty is feature selection. Though the current features performs quite well, if time allows, we will still want to improve it to the next level. We would focus on discovering new features to improve the accuracy. Perhaps we could even create our own features for better performance.

During the presentation, we learned that using a LightBGM model might perform better than random forests, which is impressive. However, due to the time and resource limits, we were not able to attempt this model.

## Data Product and Results

### Exception Count Predictions

The Exception Count Prediction Tool is delivered through a script that generates a user interface that is easy to use. The interface can be run on both Windows computers and Mac computers, and it uses the same code to run. The interface has two parts, the top asks for the user to input the training data, which is the raw `exception_hours.csv` file that PHC has provided us. After including the correct type of data, the user will need to input a prediction timeframe. After clicking "Submit", our time series models will run and generate a `.csv` file that would provide all the relevant predictions regarding the number of exceptions Providence Health Care would have within the prediction timeframe.


### Dashboard

We implemented the dashboard using Tableau, where we consolidated the three models. It has three different tabs:

- Predictions

This tab displays two charts stacked vertically.

The top chart shows how many exceptions are being predicted in a weekly basis by different sites, job families, and sub-program. The orange series corresponds to the predicted numbers of exceptions, while the grey ones represent the 95% confidence interval.

The bottom chart displays how many urgent exceptions, which includes overtime and relief not found, are being predicted. The different bar colors correspond to different job families.

<div align="center"><img src="img/dashboard_predictions.png"></div>

- Exceptions Classification

This tab displays a summary table, where the user can easily see how many exceptions of each label is already on PHC's system. The user can filter by date and site.

<div align="center"><img src="img/dashboard_classification.png"></div>

- Productive vs. Exception Hours

This tab displays a comparison between the productive and exception hours based on historical data. The user can filter by date, site, and job family.

<div align="center"><img src="img/dashboard_history.png"></div>

## Conclusions and Recommendations

Using the three data products we have developed, we are able to provide Providence Health Care with the potential to better plan for their staffing needs. Not only will the data products be able to provide accurate and classifications and forecasts of PHC's exceptions, it can also help plan for the short-term and long-term staffing needs. However, it should be noted that we recommend using each of the tools separately.

Firstly, in regards to the Exception Count Prediction Tool, because our forecasts will stay relevant for quite a while, it is not necessary for PHC to re-train the models every day or even every week. In fact, we recommend that PHC re-train the models once every month with updated data, which will definitely increase the efficiency for PHC.

* Include more here *
