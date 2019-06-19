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

### Exception Classification

The classification model is using random forests to predict the possible outcome for an exception. We are aiming to generate insights for exceptions which have been created but yet been fulfilled, so the HR may change their priority to handling some exceptions to avoid unnecessary cost. After applying logistic regression, random forests, and gradient boosting, random forests performs best. And the interoperability is better than the other two, hence we agreed to choose random forests as our model.

`EARNING_CATEGORY` is the label in our model.  it  has 12 values which is too detailed for our prediction and affect the model accuracy hugely. Per partner’s advice, as long as the relief type (like straight time) is the same, we can treat them as the same. Hence, we group the 12 labels into 3 labels, which are:

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

As you can see, the overall accuracy is not bad. But if we break it down to every category, the difference is obvious. Since the Overtime costs more than Straight time, we need to improve the accuracy of overtime. The reason caused the gap between categories is imbalanced data.  We found out that the number of straight time is way more than the other two. Which makes sense that the model is more likely to predict an exception as straight time instead of the other two. So we updated our model to make it more balanced.

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

This model’s output file is also a .csv file which adds two columns to the input data, one is the shift of exceptions per partner’s request. The other one is our prediction result.

#### Difficulties, Limitations, and Potential Improvements

Through the whole project, there are 2 main difficulties.

The first one is that the missing data. Due to technical reasons, some of our data (like “MIN_TO_MAX_MINUTES”) is missing. We had to remove some records in order to keep training data quality, which had affected the model accuracy

The second one is the feature selection. Though current features has proper performance, we still want to improved it to the next level. We would focus on discovering new features to improve the accuracy, if time allows.

During the presentation, we learned that the LightBGM might have a better performance than random forest, which is impressive. Due to time and resource limits, we didn’t try to implement this model.

## Data Product and results

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
