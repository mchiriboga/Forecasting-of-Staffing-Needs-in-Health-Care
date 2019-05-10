#' Created by Iris
#' 
#' This script takes training data and the dates to predict
#' Generates an estimation of the overtime percentage for nurses by week
#' Also provides an prediction interval
#' And save the prediction as CSV file

#' Import packages:
suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(lubridate))
suppressPackageStartupMessages(library(prophet))

#' Input Data:
#' Training data should include column `SHIFT_DATE` and `LABOR_ARGREEMENT`
#' Prediction period should include column `ds` for dates
#' Dates are by day
#' 
#' For an example, the training data uses `train.csv`
#' And prediction data uses the dates in 2017

# training data
df <- read_csv("../data/train.csv")
training <- df %>%
  filter(year(SHIFT_DATE) < 2017)

# prediction period: 2017
future <- as.tibble(seq(ymd('2017-01-01'),ymd('2017-12-31'), by = "days")) %>% 
  select(ds = value)

#' Make prediction for group `NURS`:
#' Use Facebook's Prophet for predicting

# data for nurse
nurse_training <- training %>% 
  filter(LABOR_AGREEMENT == "NURS") %>% 
  mutate(overtime = EARNING_CATEGORY == "Overtime") %>% 
  group_by(SHIFT_DATE) %>% 
  summarise(over = sum(overtime), total = n()) %>% 
  mutate(y = over/total) %>% 
  select(ds = SHIFT_DATE, y)

# generate model by Prophet
m_nurse <- prophet(nurse_training, 
                   yearly.seasonality = TRUE, 
                   daily.seasonality = FALSE)

# make prediction
prediction <- predict(m_nurse, future)

# aggregate the results by week
prediction_weekly <- prediction %>% 
  mutate(ds = floor_date(ds, unit = "week")) %>% 
  group_by(ds) %>% 
  summarise(yhat = mean(yhat))

# add intervals by loess
loess <- loess(yhat ~ week(ds), data = prediction_weekly, span = 0.3)
smoothed <- predict(loess)
prediction_weekly <- prediction_weekly %>% 
  mutate(upper = smoothed + 0.03,
         lower = smoothed - 0.02)

# save file
write.csv(prediction_weekly, file = "../data/overtime_nurse.csv")