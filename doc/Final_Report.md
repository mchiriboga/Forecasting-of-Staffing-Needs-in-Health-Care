## Data science methods
### Exception Classification

The classification model is using random forests to predict the possible outcome for an exception. We are aiming to generate insights for exceptions which have been created but yet been fulfilled, so the HR may change their priority to handling some exceptions to avoid unnecessary cost. After applying logistic regression, random forests, and gradient boosting, random forests performs best. And the interoperability is better than the other two, hence we agreed to choose random forests as our model.

`EARNING_CATEGORY` is the label in our model.  it  has 12 values which is too detailed for our prediction and affect the model accuracy hugely. Per partner’s advice, as long as the relief type (like straight time) is the same, we can treat them as the same. Hence, we group the 12 labels into 3 labels, which are:

- Straight time: which contains all kinds of straight time relief, the pay rate is the same as the normal rate which is positive

- Overtime and Beyond: which contains `Relief Not Found` and all kinds of relief which needs to be paid more than normal rate. 

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

| Exceptions | Amount |
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

### Difficulties, limitations, and potential improvement

Through the whole project, there are 2 main difficulties.

The first one is that the missing data. Due to technical reasons, some of our data (like “MIN_TO_MAX_MINUTES”) is missing. We had to remove some records in order to keep training data quality, which had affected the model accuracy

The second one is the feature selection. Though current features has proper performance, we still want to improved it to the next level. We would focus on discovering new features to improve the accuracy, if time allows.

During the prestation, we learned that the LightBGM might have a better performance than random forest, which is impressive. Due to time and resource limits, we didn’t try to implement this model. 
