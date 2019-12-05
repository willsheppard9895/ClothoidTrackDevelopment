### This script removes outliers and creates averages for student project collated steering data academic year 2019-2020
# import libraries
library("tidyverse")
library(xlsx)
#library("brms")
#library(ggplot2)
#library(brmstools)
#library(cowplot)
#library(dplyr)
#library(tidyr)


# set working directory
#setwd("C:/VENLAb data/ClothoidTrackDevelopment/Analysis")
setwd("C:/VENLAb data/ClothoidTrackDevelopment/Data")

#read .csv
steerdata = read_csv("collated_steering.csv")

#sTEErING HEADErs: 
#columns = ('ppid', 'block','world_x','world_z','world_yaw',
  #'timestamp_exp','timestamp_trial','maxyr','bend',
  #''dn','autoflag','yr_sec','yr_frames','distance_frames',
  #''dt','sw_value','wheelcorrection','sw_angle')

#add left bend
steerdata <- steerdata %>% 
  mutate(bend = ifelse(bend < 0, "left", "right"))

# Create a  trial id
steerdata <- steerdata %>%
  mutate(trialid = paste(ppid, block, maxyr, failurepoint, bend, dn, sep = "_"))

# label failure point tobe used as a factor, allows onsettime to be used to calculate reaction times
steerdata <- steerdata %>% 
  mutate(failurepoint = case_when(onsettime == 1.5 ~ "Straight1",
                                  onsettime == 5 ~ "Cloth1",
                                  onsettime == 8 ~ "Apex",
                                  onsettime == 11 ~ "Cloth2",
                                  onsettime %in% c(15, 17) ~ "Straight2" 
  ))

#create function retrieving rt.
disengage_rt <- function(onsettime, timestamp_trial, autoflag){
  
  #pick first frame where autoflag == false, then take the timestamp and minus the onset_time
  auto_false <- which(autoflag == 0)
  disengage_index <- first(auto_false)
  disengage_trialtime <- timestamp_trial[disengage_index]
  onset_time <- first(onsettime)
  rt <- disengage_trialtime - onset_time #can be negative
  return(rt)
}

#create factors
steerdata$ppid <- as.factor(steerdata$ppid)
steerdata$block <- as.factor(steerdata$block)
steerdata$maxyr <- as.factor(steerdata$maxyr)
steerdata$failurepoint <- as.factor(steerdata$failurepoint)


# create trial counts per condition and create trial averages
steerdata_trialavgs <- steerdata  %>% 
  group_by(ppid, block, maxyr, failurepoint, trialid) %>% 
  summarize(rt = disengage_rt(onsettime, timestamp_trial, autoflag),
            onsettime = first(onsettime),
            swa_var = sd(sw_angle),
            mean_swa_vel = mean(diff(sw_angle)),
            #sdlp = sd(steeringbias),
            #sb = mean(steeringbias),
            #rms = mean(sqrt(steeringbias^2)),
            yr_var = sd(yr_sec),
            disengaged = ifelse(is.na(rt), 0, 1)
  )

steerdata_trialavgs <- steerdata_trialavgs %>%
  mutate(trialn_cndt = 1:n())

print(trial_cndt)

#calculate grand means of the main measures for imputing.
grandmeans <- steerdata_trialavgs %>% 
  ungroup() %>% 
  filter(rt > 0) %>% 
  group_by(maxyr, failurepoint) %>%
  summarise(mn_rt = mean(rt, na.rm= T),
            sd_rt = sd(rt, na.rm = T),
            mn_swa_var = mean(swa_var),
            sd_swa_var = sd(swa_var),
            mn_swa_vel = mean(mean_swa_vel),
            sd_swa_vel = sd(mean_swa_vel),
            #mn_sdlp = mean(sdlp),
            #sd_sdlp = sd(sdlp),
            #mn_sb = mean(sb),
            #sd_sb = sd(sb),
            #mn_rms = mean(rms),
            #sd_rms = sd(rms),
            mn_disengaged = mean(disengaged),
            sd_disengaged = sd(disengaged),
            perc_takeover = sum(disengaged)/n())


write.xlsx(steerdata_trialavgs, "C:/VENLAB data/ClothoidTrackDevelopment/4Students/steerdata_trialavgs.xlsx")
