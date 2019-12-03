import viz
import vizact
import vizmat
import vizjoy
import viztask
import math as mt # python library
JOY_FIRE_BUTTONS = [100, 101, 102]
JOY_DIR_SWITCH_BUTTON = [5, 6]
KEY_FIRE_BUTTONS = [' ']
KEY_DIR_SWITCH_BUTTON = viz.KEY_DELETE

class Driver(viz.EventClass):
	def __init__(self, Cave, Distractor = None):
		viz.EventClass.__init__(self)
				
		#self.__speed = 0.223 #metres per frame. equates to 13.4 m/s therefore 30mph.
		#8ms = 8/60 = .1333
		self.__speed = 8 #m./s =30mph
		self.__heading = 0.0
		self.__pause = 0#pauses for 50 frames at the start of each trial
		self.gearPressed = False #a second way to measure gearpaddown, for distractor end of trial.

		self.__Wheel_yawrate_adjustment = 0 #difference between real steering angle and virtual yaw-rate.
		
		self.__Distractor = Distractor #distractor class for callbacks.

		self.__view = Cave
		# self.__view = viz.MainView.setPosition(0,1.20,0) #Grabs the main graphics window
		# self.__view = viz.MainView
		# self.__view.moverelative(viz.BODY_ORI)
		
		self.__automation = False

		self.__dir = 1.0 # direction of the vehicle (+: )
			
		#self.callback(viz.TIMER_EVENT,self.__ontimer)
		self.callback(viz.KEYDOWN_EVENT,self.keyDown) #enables control with the keyboard
		self.callback(vizjoy.BUTTONDOWN_EVENT,self.joyDown) 
		self.callback(vizjoy.MOVE_EVENT,self.joymove)
		#self.starttimer(0,0,viz.FOREVER)

		global joy
		joy = vizjoy.add()

		
	def toggleDir(self):
		if self.__dir > 0:
			self.__dir = -1.0
		else:
			self.__dir = 1.0
		
	def reset(self, position = None):
		
		self.__heading = 0.0
		self.__dir = 1.0
		turnrate = 0.0
		#self.__view.reset(viz.BODY_ORI) 

		if position is None:
			self.__view.setPosition([0,0,0])
			self.__view.setEuler([0,0,0])			
		else:
			self.__view.setPosition([position[0],0,position[1]])
			self.__view.setEuler([0,0,0])

		self.__pause = 0#-50
		
		self.__Wheel_yawrate_adjustment = 0

		#self.__view = viz.MainView.setPosition(0,1.20,0) ##CHANGE EYE-HEIGHT FROM HERE
		# self.__view = viz.MainView.setPosition(0,1.20,0) ##CHANGE EYE-HEIGHT FROM HERE
		# self.__view = viz.MainView
		# self.__view.moverelative(viz.BODY_ORI)
		data = joy.getPosition()
		data[0] = 0
		
		gas = data[1]

	def UpdateView(self, YR_input = None):
		#elapsedTime = viz.elapsed()

		elapsedTime = viz.getFrameElapsed()

		if elapsedTime > .02:
			print ("viz.tick: ", viz.tick())
			print ("frame number: ", viz.getFrameNumber())
			print ("elapsedTime:", elapsedTime)

		yawrate = 0.0
		turnangle = 0.0
		distance = 0.0

		dt = elapsedTime
		#dt = 1.0/60.0 #not sure why but it's perceptually smoother with a constant. This shouldn't be the case.

		#Get steering wheel and gas position
		data = joy.getPosition()
		SteeringWheelValue = data[0] # on scale from -1 to 1.
		gas = data[1]

		
		#keep heading up to date.
		ori = self.__view.getEuler()
		self.__heading = ori[0]

		if viz.key.isDown(viz.KEY_UP):
			gas = -5
		elif viz.key.isDown(viz.KEY_DOWN):
			gas = 5
		if viz.key.isDown(viz.KEY_LEFT): #rudimentary control with the left/right arrows. 
			data[0] = -1
		elif viz.key.isDown(viz.KEY_RIGHT):
			data[0] = 1
	
#		#Compute drag
#		drag = self.__speed / 300.0
		self.__dir = 1
		if (YR_input is not None) and (self.__automation == True): #provides the opportunity to pass a yaw rate to the driver.
			yawrate = YR_input

			Wheel_yawrate = self.__dir * SteeringWheelValue  * 35.0 #max wheel lock is 35degrees per s yawrate

			self.__Wheel_yawrate_adjustment = yawrate - Wheel_yawrate #correction for any offset between virtual yawrate and yawrate as specified by the steering wheel angle.
		else:
			yawrate = self.__dir * SteeringWheelValue  * 35.0 #max wheel lock is 35degrees per s yawrate

			#add adjustment for smooth take-over.
			yawrate += self.__Wheel_yawrate_adjustment
			
		turnangle = yawrate * dt
		self.__heading += turnangle
	
		self.__pause = self.__pause+1
		#Update the viewpoint
		if self.__pause > 0:
							
			distance = self.__speed * dt

			#posnew = (0,0,self.__speed)
			posnew = (0,0,distance)
			eulernew = (self.__heading,0,0)
			
			self.__view.setPosition(posnew, viz.REL_LOCAL)
			self.__view.setEuler(eulernew) 
			
		else:
			self.__heading = 0.0
			self.__dir = 1.0
			turnangle = 0.0

		#return the values used in position update
		UpdateValues = []
		UpdateValues.append(yawrate)
		UpdateValues.append(turnangle)
		UpdateValues.append(distance)
		UpdateValues.append(dt)
		UpdateValues.append(SteeringWheelValue)
		UpdateValues.append(self.__Wheel_yawrate_adjustment)

		return (UpdateValues)

	def keyDown(self,button):
		if button == KEY_DIR_SWITCH_BUTTON:
			self.toggleDir()		
		
	def joyDown(self,e):
		if e.button == JOY_DIR_SWITCH_BUTTON:
			return e.button			
		if e.button in JOY_FIRE_BUTTONS:
			button = e.button # do nothing

		print ("Pressed: ", e.button)

				#left red buttons are 8,21,23. right red buttons are 7,20,22:
			#if buttons are left or right, call distractor task.
		if self.__Distractor is not None:
			if e.button in [8,7,21,23,20,22]:
				print ("responded to distractor task")
				self.__Distractor.keydown(e.button)

		if e.button in (5,6):
			
			if self.__Distractor is not None:
				EoTFlag = self.__Distractor.getFlag()
			else:
				EoTFlag = False

			if EoTFlag:
				self.gearPressed = True
			else:
				self.__automation = False
				print ("disengaged from automation")


	def resetHeading(self):
		self.__heading = 0.0

	def setAutomation(self,Auto):

		"""flag to disconnect wheel and visuals"""
		self.__automation = Auto

	
	def getAutomation(self):
		
		return self.__automation

		
	def getGearPressed(self):
		
		return self.gearPressed

	def setGearPressed(self, press = False):
		
		self.gearPressed = press

	def getSpeed(self):
		return self.__speed

	def getPos(self):
		xPos = joy.getPosition()
		return xPos[0]#*90.0 ##degrees of steering wheel rotation 
		
	def getPause(self): ###added for flow manipulations
		return self.__pause
		
	def joymove(self,e):
		
		if self.__Distractor is not None:
			end_of_trial_flag = self.__Distractor.getFlag()
			
			#if end of trial screen on.
			if end_of_trial_flag:
				self.__Distractor.joymove(e.pos)
		else:
			pass

	def getJoy(self):
		return joy