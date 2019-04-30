#' Created by Iris
#' 
#' This script takes the raw data from your local repo
#' Splits the data by year of the shift date
#' Produces the splitted data sets

# import packages
suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(lubridate))

# read file
# file should be in data repo
# change the file name as you need
df <- read_csv("../data/raw.csv")

# split the data by year
years <- c("2012","2013","2014","2015","2016","2017","2018","2019","2020")
for (y in years) {
  # filter the group by year
  output <- df %>% 
    filter(year(SHIFT_DATE) == y) %>% 
    arrange(SHIFT_DATE)
  
  # write the splitted group to csv
  write.csv(output, file = paste("../data/raw_", y, ".csv", sep = ""))
}

# split the training set from 2012 to 2017
train <- df %>% 
  filter(year(SHIFT_DATE) < 2018) %>% 
  arrange(SHIFT_DATE)
# write training set to csv
write.csv(train, file = "../data/train.csv")
