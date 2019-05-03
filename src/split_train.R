#' Created by Iris
#' 
#' This script takes the raw data from your local repo
#' Splits a training set from the data
#' Including data before 2018
#' 
#' Updated May 2 for the new data, file name changed

# import packages
suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(lubridate))

# read file
# file should be in data repo
# change the file name as you need
df <- read_csv("../data/exception_hours.csv")

# split the training set from 2012 to 2017
train <- df %>% 
  filter(year(SHIFT_DATE) < 2018) %>% 
  arrange(SHIFT_DATE)

# write training set to csv
write.csv(train, file = "../data/train.csv")

# 
df