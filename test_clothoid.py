### NEED TO ADD TOGGLE VISIBILITY

import viz
import viztask
import numpy as np
import matplotlib.pyplot as plt
import vizTrackMaker as tm
from ConditionListGenerator import ConditionList
import myCave
import vizdriver_Tuna19 as vizdriver

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
		L = (2*v) #2sec.
		tr = 4 #seconds
		cornering = 4 # seconds
		total = 2*tr + cornering #12 s
		time_step = np.linspace(0, total, 1000) # ~1 ms steps
		yr = np.radians(maxYR) #26.232
		
		#build track
		straight1 = tm.vizStraight(startpos = [0,0], primitive_width=1.5, road_width = 0, length = L, colour = viz.RED)		
		clothoid = tm.vizClothoid(start_pos = straight1.RoadEnd, t = time_step,  speed = v, yawrate = yr, transition = tr, x_dir = x_dir)
		straight2 = tm.vizStraightBearing(bearing = clothoid.Bearing[-1], startpos = clothoid.RoadEnd, primitive_width=1.5, road_width = 3, length = L, colour = viz.RED)
		
		self.components = [straight1, clothoid, straight2]
		
		self.setAlpha(alpha)
		self.ToggleVisibility(viz.OFF)
		
	def ToggleVisibility(self, visible = viz.ON):		
		for c in self.components: c.ToggleVisibility(visible)
		
	def setAlpha(self, alpha= 1):		
		for c in self.components: c.setAlpha(alpha)
		

def run(CL, tracks, grounds, backgrounds):
		
	print(CL)	
	
	for idx, trial in CL.iterrows():
		
		#get unique key
		bend = int(trial['Bend'])
		yr = trial['maxYR']
		dn = trial['Day/Night']
		key = str(bend)+'_'+str(yr)+'_' + dn
		
		#pick track and make visible
		track = tracks[key]
		track.ToggleVisibility(1)
		
		ground = grounds[dn]
		ground.visible(viz.ON)
		
		viz.clearcolor(backgrounds[dn])
		
		
		#run trial
		yield viztask.waitTime(1)
		
		#switch track off again
		track.ToggleVisibility(0)
		ground.visible(viz.OFF)
		
	
	viz.quit()
	#viz.MainScene.visible(viz.ON,viz.WORLD)

def LoadCave():
	"""loads myCave and returns Caveview"""

	#set EH in myCave
	cave = myCave.initCave()
	caveview = cave.getCaveView()
	return (caveview)

"""
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
"""

	
if __name__ == '__main__':
	
		
	#initialise display
	cave = LoadCave()

	#initialise driver
	driver = vizdriver.Driver(cave)		
	

	#set up condition list
	yawrates = np.linspace(6, 20, 3)
	onsets_list = [1.5, 5, 8, 11]
			
	CL = ConditionList(yawrates, onsets_list)

	CONDITIONLIST = CL.GenerateConditionList()

	tracks = {}	
	al = {'D':.25,'N':.025}
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
	
	viztask.schedule( run( CONDITIONLIST, tracks, grounds, backgrounds ))
		



	