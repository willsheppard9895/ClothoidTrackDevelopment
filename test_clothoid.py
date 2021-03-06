﻿#add path for wheel automation libs
rootpath = 'C:\\VENLAB data\\shared_modules\\Logitech_force_feedback'
import sys
sys.path.append(rootpath)
import viz
import viztask, vizact
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

def OpenTrial(filename):
	"""opens csv file"""

	filename = filename + '.csv'
	print ("Loading file: " + filename)
	playbackdata = pd.read_csv("Data/autofiles/"+filename)
	return (playbackdata)

def run(CL, tracks, grounds, backgrounds, cave, driver, autofiles, wheel, save_prefix):
	
	DEBUG = False
	
	trialtime = tracks[list(tracks.keys())[0]].trialtime	
	if DEBUG: trialtime = 6
		
	wait_texture = setStage('dusk.png')	
	wait_col = list(np.mean(np.array([viz.BLACK,viz.SKYBLUE]).T, axis = 1))	
	
		
	#add audio files
	manual_audio = 'C:\\VENLAB data\\shared_modules\\textures\\490_200ms.wav'
	viz.playSound(manual_audio, viz.SOUND_PRELOAD)	
	def SingleBeep():
		"""play single beep"""
		viz.playSound(manual_audio)
	"""
	datacolumns = ('autofile_i','bend','maxyr',
	'onsettime','ppid','trialn','block','timestamp_exp','timestamp_trial',
	'world_x','world_z','world_yaw','swa', 
	'yawrate_seconds','turnangle_frames',
	'distance_frames','dt','wheelcorrection', 
	'steeringbias', 'autoflag', 'autofile')
	"""
	"""
			UpdateValues = []
		UpdateValues.append(yawrate)
		UpdateValues.append(turnangle)
		UpdateValues.append(distance)
		UpdateValues.append(dt)
		UpdateValues.append(SteeringWheelValue)
		UpdateValues.append(self.__Wheel_yawrate_adjustment)
	"""
	
	expid, ppid, block = save_prefix.split('_')
	columns = ('ppid','block','world_x','world_z','world_yaw','timestamp_exp','timestamp_trial','maxyr', 'onsettime', 'bend','dn','autoflag','yr_sec','yr_frames','distance_frames','dt','sw_value','wheelcorrection','sw_angle')	
	
	def update(num):		
		
		
		if UPDATE:
			
			trialtimer = viz.tick() - trialstart	
			if DEBUG: txtmode.message(str(onset) +'\n' + str(yr) + '\n' + str(round(trialtimer,2)))
			
			if AUTOFLAG:
				
				#read the corresponding entry on the playback_data
				if trialtimer <= onset:
					i, auto_row = next(playback_iter)
					#print(i, auto_row)
					dir = auto_row.bend							
					new_swa = auto_row.swa * dir * bend #these columns are named slightly differently to the final experiment data
					new_yr = auto_row.yr * dir * bend
					
					#move the wheel.									
					wheel.set_position(new_swa)	#set steering wheel to 							
				else:
					#driver.setAutomation(False)
					new_yr = 0 #off-tangent failure
			
			else:
				new_yr = None					
			
			#update position
			updatevals = driver.UpdateView(new_yr) 
			#return the values used in position update			
				
				
				#retrieve position and orientation
			pos = cave.getPosition()							
			yaw = vizmat.NormAngle(cave.getEuler()[0])			
						
			#record data	
			#columns = ('ppid', 'block','world_x','world_z','world_yaw','timestamp_exp','timestamp_trial','maxyr', 'onsettime', 'bend','dn','autoflag','yr_sec','yr_frames','distance_frames','dt','sw_value','wheelcorrection','sw_angle')	
			output = (ppid, block, pos[0], pos[2], yaw, viz.tick(), trialtimer, yr, onset, bend, dn, int(AUTOFLAG), updatevals[0], updatevals[1],updatevals[2], updatevals[3],updatevals[4],updatevals[5], updatevals[4]*90) #output array			
				
			#print(output)
		
			#self.OutputWriter.loc[self.Current_RowIndex,:] = output #this dataframe is actually just one line. 		
			OutputWriter.writerow(output)  #output to csv. any quicker?
			
	
	#call update every frame
	UPDATE = False
	
	viz.callback(viz.TIMER_EVENT, update)
	viz.starttimer(0,1.0/60.0,viz.FOREVER)
	
		
	txtmode = viz.addText("Mode",parent=viz.SCREEN)	
	#set above skyline so I can easily filter glances to the letter out of the data
	txtmode.setPosition(.05,.52)
	txtmode.fontSize(36)
	txtmode.color(viz.WHITE)	

	if not DEBUG: txtmode.message('A')
		
	print(CL)	
		
	for trial_i, (idx, trial) in enumerate(CL.iterrows()):
		
		#reset key trial variables 
		trialstart = viz.tick()
		AUTOFLAG = True
		driver.setAutomation(AUTOFLAG)
		
		#set up dataframe and csv writer
		OutputFile = io.BytesIO()
		OutputWriter = csv.writer(OutputFile)
		OutputWriter.writerow(columns) #write headers.
		
		bend = int(trial['Bend'])
		yr = trial['maxYR']
		dn = trial['Day/Night']
		onset = trial['OnsetTime']		
		key = str(bend)+'_'+str(yr)+'_' + dn
		#retrieve playback
		playback = autofiles[str(yr)]
		playback_iter = playback.iterrows()
		
		
		
		#only switch on update loop after retrieving parameters
		
		
		#pick track and make visible
		track = tracks[key]
		track.ToggleVisibility(1)
		
		ground = grounds[dn]
		ground.visible(viz.ON)
		
		viz.clearcolor(backgrounds[dn])
		if trial_i == 0:
			yield viztask.waitTime(2)
		else:
			yield viztask.waitTime(.5)
		
		
		#start the trial proper
		UPDATE = True
		
		#run trial
		def PlaybackReached():
			"""checks for playback limit or whether automation has been disengaged"""
			end = False
			#print(viz.tick() - trialstart)
			if (viz.tick() - trialstart) > trialtime: end = True
			return(end)
		
		def CheckDisengage():
			"""checks automation status of driver class """
			end = False
			auto = driver.getAutomation()
			if auto == False:end = True				
			return (end)

		#create viztask functions.
		waitPlayback = viztask.waitTrue( PlaybackReached )
		waitDisengage = viztask.waitTrue( CheckDisengage )
		
		d = yield viztask.waitAny( [ waitPlayback, waitDisengage ] )		

		if d.condition is waitPlayback:
			print ('end of trial reached')
			
		elif d.condition is waitDisengage:
			print ('Automation Disengaged')
			if not DEBUG: txtmode.message('M')
			
			AUTOFLAG = False				
			wheel.FF_on(.2)				
			SingleBeep()
			yield viztask.waitTime(trialtime - (viz.tick()-trialstart))
			
		#END OF STEERING TASK
		
		#reset trial
		track.ToggleVisibility(0)
		ground.visible(viz.OFF)
		driver.reset()
		wait_texture.visible(1)
		viz.clearcolor(wait_col)
		UPDATE = False
		if not DEBUG: txtmode.message('A')
		
		yield viztask.waitTime(.5)
		wait_texture.visible(0)
		UPDATE = True
		
		savename = save_prefix +'_'+str(trial_i)
		SaveData(OutputFile, savename)
	
	
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

def raiseandquit(warn):
	
	print(warn.upper())
	viz.quit()

	
if __name__ == '__main__':
	
		
	#initialise display
	cave = LoadCave()

	#initialise driver
	driver = vizdriver.Driver(cave)		
	

	#set up condition list
	yawrates = np.linspace(6, 20, 3)
	#onsets_list = [1.5, 3, 4, 5]
	onsets_list = [1.5, 5, 8, 11, 17, 17]
			
	CL = ConditionList(yawrates, onsets_list, repetitions = 2)

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
	
	#load playback
	autofiles = {}
	for yr in yawrates: 
		auto_fn = str(yr)
		playback = OpenTrial(auto_fn)	
		autofiles[auto_fn] = playback
	
	wheel = LoadAutomationModules()
	wheel.FF_on(1) # set to zero to turn off force feedback
	vizact.onexit(CloseConnections, wheel)
	
	## add participant interaction
	pp_id = viz.input('Participant code: ') #add participant code
	try:
		pp_id = int(pp_id)
	except: 
		raiseandquit("invalid pp code")		
		
	block = viz.input('Block: ') #add block number
	try: 
		block = int(block)
		if block not in [1,2,3,4]: raiseandquit("invalid block number")			
	except:
		raiseandquit("invalid block number")
		
	save_prefix = '_'.join(['Tuna19',str(pp_id),str(block)])
	print(save_prefix)
	
	if block == 1:
		consent_check = viz.input('Has consent been given (Y/N)?: ')
		try:
			str(consent_check)
			if not consent_check == 'Y': raiseandquit("Consent must be gained before proceeding")	
		except: 
			raiseandquit("Consent must be gained before proceeding")	
	
	#TODO: check instructions
	#put instructions here#
	viz.message("""
	\t\tYou will now begin the experiment \n\n The automated vehicle will attempt to navigate a series of bends. 
	\nYour task as the supervisory driver is to make sure the vehicle stays within the road edges. 
	\nDuring automation please keep your hands loosely on the wheel. 
	\nYou may take control by pressing the gear pads. 
	\nOnce pressed, you will immediately be in control of the vehicle
	""")
	viz.mouse.setVisible(viz.OFF) #switch mouse off
		
	viztask.schedule( run( CONDITIONLIST, tracks, grounds, backgrounds, cave, driver, autofiles, wheel, save_prefix ))
		



	