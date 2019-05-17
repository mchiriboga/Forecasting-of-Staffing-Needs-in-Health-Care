#! /usr/bin/env

#' Created by Iris
#' Modified May 14
#' 
#' This script takes training data and the dates to predict
#' Generates an estimation of the overtime percentage for nurses by week
#' Also provides an prediction interval
#' And save the prediction as CSV file

#' Import packages:
suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(lubridate))
suppressPackageStartupMessages(library(prophet))


#' ---------------------------------------
#' Data Preparation
#' Include training data and prediction period
#' ---------------------------------------

#' Training data should include column `SHIFT_DATE` and `LABOR_ARGREEMENT`
#' Prediction period should include column `ds` for dates
#' 
#' For an example, the training data uses `train.csv`
#' And prediction data uses the dates in 2017

# training data
df <- read_csv("../data/train.csv")
training <- df %>%
  filter(year(SHIFT_DATE) < 2017)

# prediction period: 2017
future <- read_csv("../data/future.csv")


#' -------------------------------------
#' Prediction for group `NURS` in `LABOR_AGREEMENT`:
#' Use Facebook's Prophet for predicting
#' -------------------------------------

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
pred_nurse <- predict(m_nurse, future)

# aggregate the results by week
result <- pred_nurse %>% 
  mutate(ds = floor_date(ds, unit = "week")) %>% 
  group_by(ds) %>% 
  summarise(nurse_per = mean(yhat))

# add intervals by loess
loess_nurs <- loess(nurse_per ~ week(ds), data = result, span = 0.3)
smoothed_nurs <- predict(loess_nurs)
result <- result %>% 
  mutate(nurs_per_up = smoothed_nurs + 0.03,
         nurs_per_lo = smoothed_nurs - 0.014)


#' -------------------------------------
#' Prediction for group `DC1000` in `JOB_FAMILY`:
#' Use Facebook's Prophet for predicting
#' -------------------------------------

# data for DC1000
dc1_training <- training %>% 
  filter(JOB_FAMILY == "DC1000",
         year(SHIFT_DATE) %in% c(2013, 2015, 2016)) %>% 
  mutate(overtime = EARNING_CATEGORY == "Overtime") %>% 
  group_by(SHIFT_DATE) %>% 
  summarise(over = sum(overtime), total = n()) %>% 
  mutate(y = over/total) %>% 
  select(ds = SHIFT_DATE, y)

# generate model by Prophet
m_dc1 <- prophet(dc1_training,
                 yearly.seasonality = TRUE,
                 daily.seasonality = FALSE)

# make prediction
pred_dc1 <- predict(m_dc1, future)

# aggregate the results by week
pred_dc1 <- pred_dc1 %>% 
  mutate(ds = floor_date(ds, unit = "week")) %>% 
  group_by(ds) %>% 
  summarise(yhat = mean(yhat))

# add intervals by loess
loess_dc1 <- loess(yhat ~ week(ds), data = pred_dc1, span = 0.3)
smoothed_dc1 <- predict(loess_dc1)
result <- result %>% 
  mutate(dc1_per = pred_dc1$yhat,
         dc1_per_up = smoothed_dc1 + 0.026,
         dc1_per_lo = smoothed_dc1 - 0.02)


#' ------------------------------------
#' Result Checking
#' Will be deleted in the final version
#' ------------------------------------

# display results
#result

# graph for nurse
#result %>% 
#  ggplot(aes(x = ds)) +
#  geom_line(aes(y = nurse, color = "nurse")) +
#  geom_line(aes(y = nurs_up, color = "CI")) +
#  geom_line(aes(y = nurs_lo, color = "CI"))

# graph for DC1000
#result %>% 
#  ggplot(aes(x = ds)) +
#  geom_line(aes(y = dc1, color = "DC1000")) +
#  geom_line(aes(y = dc1_up, color = "CI")) +
#  geom_line(aes(y = dc1_lo, color = "CI"))


#' ------------------------
#' File Saving
#' File name to be changed
#' ------------------------

write.csv(result, file = "../data/overtime.csv")