#' Created by Iris
#' Plot graphs for the proposal presentation/report

# import packages
suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(lubridate))

# read file
df <- read_csv("../data/raw.csv")
df18 <- read_csv("../data/raw_2018.csv")

# plot for each day of the year 2018
ts_1_day18 <- df18 %>% 
  group_by(SHIFT_DATE) %>% 
  summarise(count = n()) %>%
  ggplot() +
  geom_point(aes(x = SHIFT_DATE, y = count)) +
  labs(x = "Day of Year", y = "Number of Exceptions",
       title = "Exception Records by Day, 2018") +
  theme(plot.title = element_text(hjust = 0.5))
# save
ggsave("../doc/img/proposal/ts_1_day18.jpg", ts_1_day18, width = 9, height = 6)


# color by week, year 2018
ts_2_day18 <- df18 %>% 
  group_by(SHIFT_DATE) %>% 
  summarise(count = n()) %>% 
  mutate(week = factor(wday(SHIFT_DATE))) %>% 
  ggplot() +
  geom_point(aes(x = SHIFT_DATE, y = count, color = week)) +
  scale_color_discrete(name = "Week", 
                       labels = c("Mon","Tue","Wed","Thu","Fri","Sat","Sun")) +
  labs(x = "Day of Year", y = "Number of Exceptions",
       title = "Exception Records by Day, 2018") +
  theme(plot.title = element_text(hjust = 0.5))
# save
ggsave("../doc/img/ts_2_day18.jpg", ts_2_day18, width = 9, height = 6)


# plot for each day of the year, all years
by_day <- df %>% 
  group_by(SHIFT_DATE) %>% 
  summarise(count = n()) %>%
  mutate(weekend = factor(wday(SHIFT_DATE)),
         day = yday(SHIFT_DATE),
         year = factor(year(SHIFT_DATE))) %>% 
  ggplot() +
  geom_point(aes(x = day, y = count, color = weekend),
            size = 0.5) +
  scale_color_discrete(name = "Week", 
                       labels = c("Mon","Tue","Wed","Thu","Fri","Sat","Sun")) +
  scale_x_continuous(breaks = seq(0,365,20)) +
  labs(x = "Day of Year", y = "Number of Exceptions",
       title = "Exception Records by Day, 2012 to 2020") +
  theme(plot.title = element_text(hjust = 0.5))

# plot for each week, all years
ts_3_week <- df %>% 
  mutate(week = week(SHIFT_DATE),
         year = factor(year(SHIFT_DATE))) %>% 
  group_by(year, week) %>% 
  summarise(count = n()) %>%
  filter(week < 53) %>%  # remove the last week to avoid misleading
  ggplot() +
  geom_line(aes(x = week, y = count, color = year),
             size = 0.5) +
  scale_color_discrete(name = "Year") +
  labs(x = "Week of Year", y = "Number of Exceptions",
       title = "Exception Records by Week for each Year") +
  theme(plot.title = element_text(hjust = 0.5))
# save
ggsave("../doc/img/ts_3_week.jpg", ts_3_week, width = 9, height = 6)

# year 2018: exception group
lr_1_exp18 <- df18 %>% 
  mutate(week = week(SHIFT_DATE)) %>%
  filter(week < 53) %>% 
  ggplot() +
  geom_bar(aes(x = week, fill = factor(EXCEPTION_GROUP)),
           position = 'stack') + 
  scale_fill_discrete(name = "Exception Groups") +
  labs(x = "Week of Year", y = "Number of Exceptions",
       title = "Exception Records, group by Exception Groups") +
  theme(plot.title = element_text(hjust = 0.5))
# save
ggsave("../doc/img/lr_3_exp18.jpg", lr_1_exp18, width = 9, height = 6)

# year 2018: advance or not
lr_1_adv <- df %>% 
  mutate(week = week(SHIFT_DATE),
         advance = as.integer(SHIFT_DATE - EXCEPTION_CREATION_DATE) > 0) %>%
  ggplot() +
  geom_bar(aes(x = week, fill = factor(advance)),
           position = 'stack') + 
  scale_fill_discrete(name = "Exception Filed Ahead") +
  labs(x = "Week of Year", y = "Number of Exceptions",
       title = "Exception Records, Filed Ahead or Not") +
  theme(plot.title = element_text(hjust = 0.5))
# save
ggsave("../doc/img/lr_1_adv.jpg", lr_1_adv, width = 9, height = 6)

# year 2018: advance or not, vacation
lr_2_adv30 <- df %>% 
  mutate(week = week(SHIFT_DATE),
         advance = as.integer(SHIFT_DATE - EXCEPTION_CREATION_DATE) > 365) %>%
  ggplot() +
  geom_bar(aes(x = week, fill = factor(advance)),
           position = 'stack') + 
  scale_fill_discrete(name = "Filed Ahead for \nmore than 1 month") +
  labs(x = "Week of Year", y = "Number of Exceptions",
       title = "Exception Records, group by Exception Groups") +
  theme(plot.title = element_text(hjust = 0.5))
# save
ggsave("../doc/img/lr_2_adv30.jpg", lr_2_adv30, width = 9, height = 6)