#import sys

#rootpath = 'C:\\VENLAB data\\ClothoidTrackDevelopment'
#sys.path.append(rootpath)

import viz
import vizmat
import clothoid_curve as cc
import numpy as np
import matplotlib.pyplot as plt
import StraightMaker as sm

#viz.setMultiSample(64)

viz.go()

viz.MainView.setPosition([-20,150,15])
viz.MainView.setEuler([0,90,0])

def setStage():
	
	"""Creates grass textured groundplane"""
	
	###should set this hope so it builds new tiles if you are reaching the boundary.
	fName = 'C:/VENLAB data/shared_modules/textures/strong_edge.bmp'
	#fName = 'strong_edge.bmp'
	
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
	groundplane.visible(1)	
	
	viz.clearcolor(viz.SKYBLUE)
	
	return groundplane

ABOVEGROUND = .01 #distance above ground

class vizClothoid():
	
	def __init__(
	self, start_pos, t,  speed, yawrate, transition, x_dir = 1, z_dir = 1,
	colour = viz.WHITE, primitive = viz.QUAD_STRIP, rw = 3.0, primitive_width = 1.5, texturefile = None
	):
		""" returns a semi-transparent bend of given roadwidth and clothoid geometry. """
		
		print ("Creating a Clothoid Bend")
		
		# def clothoid_curve(ts, v, max_yr, transition_duration):
		
		self.StartPos = start_pos

		self.TimeStep = t
		
		self.TotalTime = t[-1]
		
		self.Speed = speed
		
		self.Yawrate = yawrate 
		
		self.Transition = transition
		
		self.RoadWidth = rw
		if self.RoadWidth == 0:
			self.HalfRoadWidth = 0
		else:
			self.HalfRoadWidth = rw/2.0	
					
		self.xDirection = x_dir

		self.zDirection = z_dir

		self.Colour = colour
		self.Primitive = primitive
		self.PrimitiveWidth = primitive_width
		
		#here it returns a list of the relevant items. You could just return the bend for testing.
		bendlist = self.BendMaker(t = self.TimeStep, yawrate = self.Yawrate, transition_duration = self.Transition, rw = self.RoadWidth, speed = self.Speed, sp = self.StartPos, x_dir = self.xDirection)
		
		self.Bend, self.Midline, self.InsideEdge, self.OutsideEdge, self.Bearing = bendlist
		
		#print('X = ', self.xDirection)
		#print('Midline', self.Midline[10:13])
		#print('InsideEdge', self.InsideEdge[10:13])
		#print('OutsideEdge', self.OutsideEdge[10:13])
		#print('bearing', self.Bearing[-1])
		#print('Bend', self.Bend[10:13])
		
		
		self.Bend.visible(viz.ON)
		
		#add road end.
		self.RoadEnd = self.Midline[-1,:]
		
	def AddTexture(self):
		"""function to add texture to the viz.primitive"""
		
		pass
		
		
	def BendMaker(self, t, yawrate, transition_duration, rw, speed, sp, x_dir):
		"""function returns a bend edge"""
		"""function returns a bend edge"""
				
		x, y, bearing = cc.clothoid_curve(t, speed, yawrate, transition_duration)
		
		if x_dir < 0:
			bearing[:] = [(2*(np.pi) - b) for b in bearing[:]]
				
		midline = np.array([((x*x_dir) + sp[0]),(y + sp[1])]).T
		

		outside = np.array(cc.add_edge((x*x_dir), y, (rw/2), sp)).T
		inside = np.array(cc.add_edge((x*x_dir), y, -(rw/2), sp)).T
		
		#print(outside.shape)
		#print(inside.shape)
	
		viz.startlayer(self.Primitive)  	
		
		for ins, out in zip(inside, outside):
			
			#print(ins)
			#print(ins.shape)
			viz.vertex(ins[0], ABOVEGROUND, ins[1])
			viz.vertexcolor(self.Colour)
			#print(ins[0], ins[1])
			viz.vertex(out[0], ABOVEGROUND, out[1])
			viz.vertexcolor(self.Colour)
			#print(out[0], out[1])
			

		Bend = viz.endlayer()

		return ([Bend, midline, inside, outside, bearing])
		
	def AddTexture(self):
		"""function to add texture to the viz.primitive"""

        pass

	def ToggleVisibility(self, visible = viz.ON):
		"""switches bends off or on"""
		if self.RoadWidth == 0:
			self.MidlineEdge.visible(visible)
		else:
			self.InsideEdge.visible(visible)
			self.OutsideEdge.visible(visible)
			
	def setAlpha(self, alpha = 1):
		""" set road opacy """
		self.Bend.alpha(alpha)
		

			
setStage()

#### MAKE FIRST STRAIGHT OBJECT ####
L = 16#2sec.
Straight = sm.vizStraight(
	startpos = [0,0], primitive_width=1.5, road_width = 0, length = L, colour = viz.RED
	)
Straight.ToggleVisibility(viz.ON)
Straight.setAlpha(.5)

## make clothoid
sp = Straight.RoadEnd
v = 8
tr = 4 #seconds
cornering = 4 # seconds
total = 2*tr + cornering #12 s
time_step = np.linspace(0, total, 1000) # ~1 ms steps
#yawrates = np.radians(np.linspace(6, 20, 3)) # 3 conditions of constant curvature yawrates
yr = np.radians(20)

clothoid = vizClothoid(start_pos = sp, t = time_step,  speed = v, yawrate = yr, transition = tr, x_dir = -1
	)
clothoid.setAlpha(alpha = .5)

#print('bearing', clothoid.Bearing[-1])
#print('road end x', clothoid.RoadEnd[0])
#print('road end z', clothoid.RoadEnd[1])


#### MAKE SECOND STRAIGHT OBJECT ####
## must match direction to clothoid.bearing[-1]


SB = sm.vizStraightBearing(bearing = clothoid.Bearing[-1], startpos = clothoid.RoadEnd, primitive_width=1.5, road_width = 3, length = L, colour = viz.RED)
SB.ToggleVisibility(viz.ON)
SB.setAlpha(.5)