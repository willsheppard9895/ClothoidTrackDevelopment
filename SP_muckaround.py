""" 
Script to run silent failure paradigm:
The steering scenario will occur across 3 geometricalaly related but different curves. 

These will have the structure: striaght(2s)-clothoid-constant-clothoid(12s)-straight(2s). Each trial will last 16s.
failures will be introduced at 4 matched time points across the three curves, thus producing different failures (by yaw rate) where the participants have had the same amount of timr to gather perceptual inupt.

These will include:
	straight 1 (1.5s)
	cloth 1 (5s)
	Mid point (8s)
	cloth 2 (11s)
		NOTE: cloth 1 & cloth 2 failure will have the same yaw rate due to symetrical nature of curve, 
		thus failure will only differ based on amount of time particiapnt has had to gather perceptual input.

These 12 failure conditions will be balanced across both day and night, as well as left and right bends.

The Class myExperiment handles execution of the experiment.

For perspective correct rendering - myCave.py

For motion through the virtual world - vizdriver.py

"""

import sys,os
#doc strings needed
rootpath = 'C:\\VENLAB data\\shared_modules\\Logitech_force_feedback'
sys.path.append(rootpath)
rootpath = 'C:\\VENLAB data\\shared_modules'
sys.path.append(rootpath)
rootpath = 'C:\\VENLAB data\\shared_modules\\pupil\\capture_settings\\plugins\\drivinglab_pupil\\'
sys.path.append(rootpath)
rootpath = 'C:\\VENLAB data\\TrackMaker\\'
sys.path.append(rootpath)

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

#vizard libraries
import viz # vizard library
import viztask # vizard library
import vizshape
import vizact
import vizmat
import vizmatplot

#personal libraries
import vizdriver_Orca18 as vizdriver
import myCave
import Count_Adjustable #distractor task
from vizTrackMaker import vizBend, vizStraight
from Scene_Creator import Scene, create_scenes
from SP_ConditionList import ConditionList

def LoadCave():
	"""loads myCave and returns Caveview"""

	#set EH in myCave
	cave = myCave.initCave()
	caveview = cave.getCaveView()
	return (caveview)

def LoadAutomationModules():

	"""Loads automation modules and initialises automation thread"""

	import logitech_wheel_threaded
	
	handle = viz.window.getHandle()
	mywheel = logitech_wheel_threaded.steeringWheelThreaded(handle)	
	mywheel.init() #Initialise the wheel
	mywheel.start() #Start the wheels thread

	#centre the wheel at start of experiment
	mywheel.set_position(0) #Set the pd control target
	mywheel.control_on()

	return(mywheel)


class myExperiment(viz.EventClass):
	
	def __init__(self):
	#practice, exp_id, autowheel, debug, ppid = 1, block = 1

		viz.EventClass.__init__(self)

		#self.PRACTICE = practice		
		#self.EXP_ID = exp_id
		#self.AUTOWHEEL = autowheel
		#self.DEBUG = debug
		#self.PP_id = ppid
		#self.BLOCK = block
		
		self.TrialLength = 15 #length of time that road is visible. Constant throughout experiment. Needs to match pre-recorded midline trajectories.
		
		#### PERSPECTIVE CORRECT ######
		self.caveview = LoadCave() #this module includes viz.go()

			
		#if self.AUTOWHEEL:
		#	self.Wheel = LoadAutomationModules()
		#else:
		#	self.Wheel = None
			

		## define max yawrates and onset times
		yawrates = np.linspace(6, 20, 3)
		onsets_list = [1.5, 5, 8, 11]

		### Generate Condition List		
		CL = ConditionList(yawrates, onsets_list)
		self.CONDITIONLIST = CL.GenerateConditionList()

		### Generate scenes day index = 0, night index = 1
		self.scenes = create_scenes()

		## Make straight objects
		L = 16#2sec.
		self.Straight = vizStraight(
			startpos = [0,0], primitive_width=1.5, road_width = 0, length = L, colour = [.6, .6, .6]
			)#, texturefile='strong_edge_soft.bmp')
		self.Straight.ToggleVisibility(viz.ON)
		## add to for loop when per trial - self.Straight.setAlpha(alpha)

		## Make bend object

		#viz.go()

	def run(self):
		"""Loops through the trial sequence"""
		viz.MainScene.visible(viz.ON,viz.WORLD)		

		#start with all turned off
		for scene in self.scenes: scene.turn_off()
	### why is the ground plane not changing????!!!! ###
		for lab, trial in self.CONDITIONLIST.iterrows():
			if trial['Day/Night'] > 0:
				trial_scene = self.scenes[0]
				#print(trial_scene)
				self.Straight.setAlpha(0.25)
			else: 
				trial_scene = self.scenes[1]
				#print(trial_scene)
				self.Straight.setAlpha(0.025)
			
			#switch the particular scene on
			print(trial_scene.name)
			trial_scene.turn_on()
			yield viz.waitTime(1)

			#switch that particular scene off
			trial_scene.turn_off()

myExp = myExperiment()
	
viztask.schedule(myExp.run())