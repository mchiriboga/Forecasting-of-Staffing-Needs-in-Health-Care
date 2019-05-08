# Blueprint

## I. Prediction

#### Steps

1. Start from the training data.
2. Split by sites (`SITE`) and jobs (`LABOR_ARGEEMENT`).
3. Use `prophet` to make predictions.
4. Get number of exceptions for each group.

#### Sample Output

| Time | Year 2020, Week 2 |
| ---- | ---- |
| Site | St John's Hospital |
| Position| Nurse |
| Predicted Exceptions | 600 |


## II. Pattern Analysis

#### Steps

1. Start from the training data.
2. Find pattern for certain issues by EDA.
  - Relief Not Found
  - Relief Not Needed
  - Overtime
  - Short Notice
  - Exception Groups
3. Predict the percentage or other indicators
4. Adjust the result by site and jobs
  - Linear Regression
  - Classification

#### Sample Output

| Time | Year 2020, Week 2 |
| ---- | ---- |
| Site | St John's Hospital |
| Position| Nurse |
| Predicted Exceptions | 600 |
| Overtime | 25% |
| Short Notice | 10% |
