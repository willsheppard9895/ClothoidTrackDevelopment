### This script removes outliers and creates averages for student project collated steering data academic year 2019-2020
# import libraries
library("tidyverse")
#library(xlsx)
#library("brms")
#library(ggplot2)
#library(brmstools)
#library(cowplot)
#library(dplyr)
#library(tidyr)


# set working directory
#setwd("C:/VENLAb data/ClothoidTrackDevelopment/Analysis")
#setwd("C:/VENLAb data/ClothoidTrackDevelopment/Data")

setwd("C:/Users/pscmgo/OneDrive for Business/PhD/Project/Experiment_Code/ClothoidTrackDevelopment")

#read .csv
steerdata = read_csv("collated_steering.csv", col_names = TRUE)

#sTEErING HEADErs: 
#columns = ('ppid', 'block','world_x','world_z','world_yaw',
  #'timestamp_exp','timestamp_trial','maxyr','bend',
  #''dn','autoflag','yr_sec','yr_frames','distance_frames',
  #''dt','sw_value','wheelcorrection','sw_angle')

#add left bend
steerdata <- steerdata %>% 
  mutate(bend = ifelse(bend < 0, "left", "right"))

# label failure point to be used as a factor, allows onsettime to be used to calculate reaction times

# You seem to be creating some NA values when you compute the failure point. For example you have onset
# times that are equal to 15 but you do not label these. Do these have a condition type? That'll be way
# you create NA values in your final trial/condition average CSVs. Unsure if this is a problem, just
# thought I'd note it. 

steerdata <- steerdata %>% 
  mutate(failurepoint = case_when(onsettime == 1.5 ~ "Straight1",
                                  onsettime == 5 ~ "Cloth1",
                                  onsettime == 8 ~ "Apex",
                                  onsettime == 11 ~ "Cloth2",
                                  onsettime == 17 ~ "NoFailure" 
  ))

# Create a  trial id
steerdata <- steerdata %>%
  mutate(trialid = paste(ppid, block, maxyr, failurepoint, bend, dn, sep = "_"))

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
  group_by(ppid, block, maxyr, failurepoint) %>% 
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

#calculate grand means of the main measures for failure conditions
conditionavgs <- steerdata_trialavgs %>% 
  ungroup() %>% 
  filter(rt > 0 | is.na(rt)) %>% 
  group_by(maxyr, failurepoint) %>%
  summarise(onsettime = first(onsettime),
            mn_rt = mean(rt, na.rm= T),
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
            perc_takeover = sum(disengaged)/n()
            )



write.csv(steerdata_trialavgs,"C:/VENLAB data/ClothoidTrackDevelopment/4Students/trialavgs.csv", row.names = FALSE)
write.csv(conditionavgs,"C:/VENLAB data/ClothoidTrackDevelopment/4Students/conditionavgs.csv", row.names = FALSE)

