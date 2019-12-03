import vizcave
import viz
import viztracker
# import molefunc

class initCave(viz.EventClass):
	def __init__(self):
		viz.EventClass.__init__(self)
		
		self.EH = 1.2
		Proj_Dist = 1.0 #front projection distance to Eye
				
		Proj_V_F = 1.115#vertical extent of projection (m)
		Proj_H_F = 1.985#1.96#horizontal extent of projection (m)		
				
		Proj_HfG = .665 #Front projection height from ground.
			
		FB = Proj_HfG #FrontBottom
		FT = Proj_HfG + Proj_V_F #FrontTop

		FL = -Proj_H_F/2 #Front Left
		FR = Proj_H_F/2 #Front Right

		FC0 = FL,FB,Proj_Dist      # Front  Wall: FC0,FC1,FC2,FC3
		FC1 = FR,FB,Proj_Dist
		FC2 = FL,FT,Proj_Dist
		FC3 = FR,FT,Proj_Dist

		self.FrontWall = vizcave.Wall(   upperLeft=FC2,upperRight=FC3,lowerLeft=FC0,lowerRight=FC1,name='Front Wall' ) #Create front wall	
		
		viz.setMultiSample(8) #set anti-aliasing

		#Initialize graphics window		
		viz.go()
	#	viz.eyeheight(1.2)
		#for monitor in viz.window.getMonitorList():
		#    print monitor.name
		#    print '   ',monitor


		viz.window.setFullscreenMonitor(2)		
		viz.window.setFullscreen(viz.ON)

		
		self.cave = vizcave.Cave(stereo=0)		
		self.cave.addWall(self.FrontWall)#,window=self.frontWindow)

		# print ("1_N: ", self.cave.getNearPlane()) #default is [.1, -1.]
		# print ("1_F: ", self.cave.getFarPlane())

		#set near and far plane.
		self.cave.setNearPlane(1.0)
		self.cave.setFarPlane(100.0)

		view = viz.MainView

		self.track = viztracker.Keyboard6DOF() #tracker object
		self.track.setPosition(0,self.EH,0)
		viz.link(self.track,view) #linked to mainview
		self.cave.setTracker(pos=self.track)
		##Create CaveView object for manipulating the entire cave environment
		##The caveorigin is a node that can be adjusted to move the entire cave around the virtual environment, it needs a tracker object to initialise it.
		self.caveview = vizcave.CaveView(self.track)
		
		#To check that it's been set
		# print ("2_N: ", self.cave.getNearPlane())
		# print ("2_F: ", self.cave.getFarPlane())
		
	#	self.callback(viz.TIMER_EVENT,self.UpdateCave)
#		self.starttimer(0,0,viz.FOREVER)
	
	def getProjSpec(self):
		spec = []
		spec.append(self.proj1)
		spec.append(self.proj2)
		spec.append(self.size)
		spec.append(self.proj_nudge)
		return spec		
		
	def getCaveView(self):
		return self.caveview
	def getTracker(self):
		return self.track
		
	def getfrontWindow(self):
		return self.frontWindow
	
	def getleftWindow(self):
		return self.leftWindow
	
	def UpdateCave(self,num):	
	
		e_adj = 0
		p_adj = 0
		t_adj = 0
		if viz.key.isDown('i'):
	#		p_adj=.2*viz.elapsed()
			p_adj=.4
		if viz.key.isDown('k'):
	#		p_adj=-.2*viz.elapsed()
			p_adj=-.4
		if viz.key.isDown('j'):
	#		e_adj=-.1*viz.elapsed()
			e_adj=-.4
		elif viz.key.isDown('l'):
	#		e_adj=.1*viz.elapsed()	
			e_adj=.4
		elif viz.key.isDown('e'):		
			t_adj = (0,self.EH-.5,0)		
		elif viz.key.isDown('d'):
			t_adj = (0,-.2,0)
		elif viz.key.isDown('s'):
			t_adj = (-.2,0,0)
		elif viz.key.isDown('f'):
			t_adj = (.2,0,0)	
		

			
	#	pos = caveview.getPosition()
	#	if pos[2]>50 and VRU_flag==0:
	#		addVRU()		
			
		posnew = (0,0,p_adj)
		eulernew = (e_adj,0,0)
		self.caveview.setPosition(posnew, viz.REL_LOCAL)
		self.caveview.setEuler(eulernew, viz.REL_LOCAL)
#		
#		print 'position: ', self.caveview.getPosition()
	

