﻿#add path for wheel automation libs
rootpath = 'C:\\VENLAB data\\shared_modules\\Logitech_force_feedback'
import sys
sys.path.append(rootpath)
import viz
import viztask
import numpy as np
import matplotlib.pyplot as plt
import vizTrackMaker as tm
from ConditionListGenerator import ConditionList
import myCave
import vizdriver_Tuna19 as vizdriver
import io, csv, os
import pandas as pd

#viz.setMultiSample(64)

def setStage(fName = 'strong_edge.bmp'):
	
	"""Creates grass textured groundplane"""
	
	###should set this hope so it builds new tiles if you are reaching the boundary.
	#fName = 'C:/VENLAB data/shared_modules/textures/strong_edge.bmp'	
	
	# add groundplane (wrap mode)
	groundtexture = viz.addTexture(fName)
	groundtexture.wrap(viz.WRAP_T, viz.REPEAT)	
	groundtexture.wrap(viz.WRAP_S, viz.REPEAT)	
	groundtexture.anisotropy(16)
	
	groundplane = viz.addTexQuad() ##ground for right bends (tight)
	tilesize = 500
	#planesize = tilesize/5
	planesize = 40
	groundplane.setScale(tilesize, tilesize, tilesize)
	
	groundplane.setEuler((0, 90, 0),viz.REL_LOCAL)
	#groundplane.setPosition((0,0,1000),viz.REL_LOCAL) #move forward 1km so don't need to render as much.
	matrix = vizmat.Transform()
	matrix.setScale( planesize, planesize, planesize )
	groundplane.texmat( matrix )
	groundplane.texture(groundtexture)
	groundplane.visible(0)	
			
	return groundplane


class Track():
	
	def __init__(self, maxYR = 25, x_dir = -1, alpha = 1):
				
		#set parameters
		v = 8		
		tr = 4 #seconds
		straights = 2 #seconds
		L = (straights*v) #ms
		cornering = 4 # seconds
		total = 2*tr + cornering #12 s
		time_step = np.linspace(0, total, 1000) # ~1 ms steps
		width = 1.5
		yr = np.radians(maxYR) #26.232
		
		#build track
		straight1 = tm.vizStraight(startpos = [0,0], primitive_width=width, road_width = 0, length = L, colour = viz.WHITE)		
		clothoid = tm.vizClothoid(start_pos = straight1.RoadEnd, t = time_step,  speed = v, yawrate = yr, transition = tr, x_dir = x_dir, rw=width*2)
		straight2 = tm.vizStraightBearing(bearing = clothoid.Bearing[-1], startpos = clothoid.RoadEnd, primitive_width=width, road_width = 3, length = L*60, colour = viz.WHITE)
		
		self.components = [straight1, clothoid, straight2]
		self.trialtime = total + (straights*2)
		
		self.setAlpha(alpha)
		self.ToggleVisibility(viz.OFF)
		
	def ToggleVisibility(self, visible = viz.ON):		
		for c in self.components: c.ToggleVisibility(visible)
		
	def setAlpha(self, alpha= 1):		
		for c in self.components: c.setAlpha(alpha)
		
def SaveData(data = None, filename = None):

	data.seek(0)
	df = pd.read_csv(data) #grab bytesIO object.		
	
	fileext = '.csv'
	file_path = 'Data//' + filename 
	complete_path = file_path + fileext
	exists = True
	i = 0
	while exists:		
		print("here")
		if os.path.exists(complete_path):
			i += 1			
			complete_path = file_path + '_copy_' + str(i) + fileext			
		else:
			exists = False

	df.to_csv(complete_path) #save to file.
	

def CloseConnections(wheel):
	
	wheel.thread_kill()
	wheel.shutdown()
	viz.quit()

def run(CL, tracks, grounds, backgrounds, cave, driver, wheel):
	
	trialtime = tracks[list(tracks.keys())[0]].trialtime
	wait_texture = setStage('dusk.png')	
	wait_col = list(np.mean(np.array([viz.BLACK,viz.SKYBLUE]).T, axis = 1))	
		
	"""
	datacolumns = ('autofile_i','bend','maxyr',
	'onsettime','ppid','trialn','block','timestamp_exp','timestamp_trial',
	'world_x','world_z','world_yaw','swa', 
	'yawrate_seconds','turnangle_frames',
	'distance_frames','dt','wheelcorrection', 
	'steeringbias', 'autoflag', 'autofile')
	"""
	
	columns = ('world_x','world_z','world_yaw','swa','timestamp_exp','timestamp_trial','maxyr','bend','dn')	
	
	def update(num):
		
		if UPDATE:
			#update position
			updatevals = driver.UpdateView() 
			#return the values used in position update			
			
			#retrieve position and orientation
			pos = cave.getPosition()							
			yaw = vizmat.NormAngle(cave.getEuler()[0])			
						
			#record data			
			output = (pos[0], pos[2], yaw, updatevals[4], viz.tick(), viz.tick() - trialstart, yr, bend, dn) #output array
			
			#print(output)
		
			#self.OutputWriter.loc[self.Current_RowIndex,:] = output #this dataframe is actually just one line. 		
			OutputWriter.writerow(output)  #output to csv. any quicker?
			
	
	#call update every frame
	UPDATE = False
	viz.callback(viz.TIMER_EVENT, update)
	viz.starttimer(0,1.0/60.0,viz.FOREVER)
		
	print(CL)	
	
	
	for idx, trial in CL.iterrows():
		
		trialstart = viz.tick()
		
		#set up dataframe and csv writer
		OutputFile = io.BytesIO()
		OutputWriter = csv.writer(OutputFile)
		OutputWriter.writerow(columns) #write headers.
		
		
		#get unique key
		bend = int(trial['Bend'])
		yr = trial['maxYR']
		dn = trial['Day/Night']
		key = str(bend)+'_'+str(yr)+'_' + dn
		
		#only switch on update loop after retrieving parameters
		
		
		#pick track and make visible
		track = tracks[key]
		track.ToggleVisibility(1)
		
		ground = grounds[dn]
		ground.visible(viz.ON)
		
		viz.clearcolor(backgrounds[dn])
		yield viztask.waitTime(.5)
		UPDATE = True
		
		#run trial
		yield viztask.waitTime(trialtime)
		
		#reset trial
		track.ToggleVisibility(0)
		ground.visible(viz.OFF)
		driver.reset()
		wait_texture.visible(1)
		viz.clearcolor(wait_col)
		UPDATE = False
		
		yield viztask.waitTime(.5)
		wait_texture.visible(0)
		UPDATE = True
		
		fn = str(bend)+'_'+str(yr)
		SaveData(OutputFile, fn)
	
	
	CloseConnections(wheel)
	#viz.MainScene.visible(viz.ON,viz.WORLD)

def LoadCave():
	"""loads myCave and returns Caveview"""

	#set EH in myCave
	cave = myCave.initCave()
	caveview = cave.getCaveView()
	return (caveview)


def LoadAutomationModules():

	#Loads automation modules and initialises automation thread

	import logitech_wheel_threaded
	
	handle = viz.window.getHandle()
	mywheel = logitech_wheel_threaded.steeringWheelThreaded(handle)	
	mywheel.init() #Initialise the wheel
	mywheel.start() #Start the wheels thread

	#centre the wheel at start of experiment
	mywheel.set_position(0) #Set the pd control target
	mywheel.control_on()

	return(mywheel)


	
if __name__ == '__main__':
	
		
	#initialise display
	cave = LoadCave()

	#initialise driver
	driver = vizdriver.Driver(cave)		
	

	#set up condition list
	yawrates = np.linspace(6, 20, 3)
	onsets_list = [1.5, 5, 8, 11, 15, 17]
			
	CL = ConditionList(yawrates, onsets_list, repetitions = 1)

	CONDITIONLIST = CL.GenerateConditionList()
	print(CONDITIONLIST)
	
	tracks = {}	
	al = {'D':.25,'N':.025}
	#al = {'D':1,'N':1}
	for bend in [1, -1]:
		for yr in yawrates:		
			for dn in ['D','N']:
				track = Track(yr, bend, al[dn])			
				key = str(bend)+'_'+str(yr)+'_' + dn
				tracks[key] = track
				print(tracks)
		
	
	#create textures
	grounds = {}
	for dn, f in zip(['D','N'],['day.png','night.png']):
		 g = setStage(f)
		 grounds[dn] = g
	
	backgrounds = {'D':viz.SKYBLUE, 'N':viz.BLACK}	
	
	
	wheel = LoadAutomationModules()
	wheel.FF_on(.2) # set to zero to turn off force feedback
	
	#viz.callback(viz.EXIT_EVENT,CloseConnections(wheel))
		
	viztask.schedule( run( CONDITIONLIST, tracks, grounds, backgrounds, cave, driver, wheel ))
		



	