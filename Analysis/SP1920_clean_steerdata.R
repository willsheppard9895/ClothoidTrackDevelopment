### This script removes outliers and creates averages for student project collated steering data academic year 2019-2020
# import libraries
library("tidyverse")
#library("brms")
#library(ggplot2)
#library(brmstools)
#library(cowplot)
#library(dplyr)
#library(tidyr)


# set working directory
setwd("C:/VENLAB data/ClothoidTrackDevelopment/Analysis")

#read .csv
SP1920_steerdata = read_csv("collated_steering.csv")

#STEERING HEADERS: 
#columns = ('ppid', 'block','world_x','world_z','world_yaw',
  #'timestamp_exp','timestamp_trial','maxyr','bend',
  #''dn','autoflag','yr_sec','yr_frames','distance_frames',
  #''dt','sw_value','wheelcorrection','sw_angle')

# Create a unique trial id
SP1920_steerdata %>%
  mutate(trialid = paste(ppid, block, maxyr, bend, dn, sep = "_"))


###These steering data are averages per trial.

#remove pp1-4 as sparrow saving "-1".
steerdata <- steerdata %>% filter(pp %in% c(5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21)) # filter poor quality/pilot participants?

steerdata <- steerdata %>% mutate(Auto = ifelse(Fix=='Free_Fix' | Fix=='Free_Free','Free',
                                                ifelse(Fix=='Fix_Fix' | Fix=='Fix_Free', 'Fix', NA))) # relabel conditions
steerdata <- steerdata %>% mutate(Manual = ifelse(Fix=='Fix_Free' | Fix=='Free_Free','Free',
                                                  ifelse(Fix=='Free_Fix' | Fix=='Fix_Fix', 'Fix', NA)))

#filter extreme.
steerdata <- steerdata %>% filter(abs(SB) <5) # remove trials with particularly large or small steering bias

steerbycondition <- steerdata %>% group_by(pp, exp_id, Auto, Manual) %>% summarize(AvgYaw = mean(AvgYaw),
                                                                                   StdYaw = mean(StdYaw),
                                                                                   AvgSWA = mean(AvgSWA),
                                                                                   StdSWA = mean(StdSWA),
                                                                                   AvgSWVel = mean(AvgSWVel),
                                                                                   SB = mean(SB),
                                                                                   RMS = mean(RMS),
                                                                                   cndt = Fix[1]) # create averages by condition
write_csv(steerbycondition, path = "Data/EyetrackingData/SteeringByCondition_CrowSparrow.csv")


#plot data.
ggplot(steerbycondition, aes(x=cndt, y=RMS, colour=exp_id)) +# facet_wrap(~exp_id) +
  stat_summary(fun.data=mean_se,position = position_dodge(width=.5)) +
  #geom_point(position=position_jitterdodge(), size=1) +
  ylab("RMS (m)") + theme_classic() + expand_limits(y=1)