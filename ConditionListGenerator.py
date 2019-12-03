import sys,os

#standard libraries
from timeit import default_timer as timer
import csv
import io #for efficient data saving
import numpy as np # numpy library - such as matrix calculation
import random # python library
import math as mt # python library
import pandas as pd
import matplotlib.pyplot as plt
import gzip
import itertools 

class ConditionList:
	
	def __init__(self, max_YR, FACTOR_onset, repetitions = 2):
		self.max_YR = max_YR # converts yawrates to radians
		self.FACTOR_onset = FACTOR_onset
		self.repetitions = repetitions

	def GenerateConditionList(self):
		"""
		Create a data frame with equal repetitions for onset point (1.5s, 5s, 8s, 11s).
		Onsettime (Factor_onset) and max yaw rate (max_YR) are the two factors
		"""
		## create the condition list by number of reps per onset time.
		
		ConditionList_Onset = np.tile(self.FACTOR_onset, self.repetitions)
		## tile this by the 3 tracks
		print('Condition list Onset', ConditionList_Onset)
		
		max_yr_list = np.repeat(self.max_YR, len(ConditionList_Onset)) # track
		#print('len max_yrlist', len(max_yr_list))
		#print(max_yr_list)
		ConditionList_Onset_full = np.tile(ConditionList_Onset, len(self.max_YR))
		
		
		#### sort order of the day/night conditions 
		DN = [1,2]
		dn_per_onset = np.repeat(DN, len(self.FACTOR_onset))
		n = int(len(self.FACTOR_onset)/2)		
		lr = np.concatenate([np.tile([-1,1], n),np.tile([1,-1], n)]) 
		dn_per_onset = dn_per_onset * lr		
		DN_list = np.tile(dn_per_onset, len(max_yr_list)/len(dn_per_onset))
			
		data = np.transpose([ConditionList_Onset_full, max_yr_list, DN_list])
		yaw_list = pd.DataFrame(data, columns = ['OnsetTime','maxYR', 'Day/Night'])
		
		#print('yaw list')
		#print(yaw_list)
		
		## define number of trials in the condition list
		#trials = len(yaw_list)
		#print('no. trials =', trials)
		#print(yaw_list)
			
		## make half day and half night trials either left or right
		for i, row in yaw_list.iterrows():
			if row['Day/Night'] % 2 > 0:
				yaw_list.loc[i, 'Bend'] = 1
			else:
				yaw_list.loc[i, 'Bend'] = -1
		
		## relabel day/night and direction columns
		# Day/Night - +ve values are day
		# Bend: 1 = Right

		yaw_list['Day/Night'] = yaw_list['Day/Night'].map({2 : 'D', 1 : 'D', -1 : 'N', -2 : 'N'})
		
		#print(yaw_list)
			
		## randomly order condition_list and drop index
		condition_list = yaw_list.sample(frac=1).reset_index(drop=True)
		#print(condition_list)
		trialn = np.linspace(1, len(condition_list), num = len(condition_list))
		#print(trialn)
		
		condition_list['TrialN'] = trialn
		
		return(condition_list)


if __name__ == '__main__':

	yawrates = np.linspace(6, 20, 3)
	onsets_list = [1.5, 5, 8, 11, 15, 17]#
			
	CL = ConditionList(yawrates, onsets_list)

	CONDITIONLIST = CL.GenerateConditionList()

	print(CONDITIONLIST)

