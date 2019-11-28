## TO DO - FIGURE OUT WHERE EDGE MAKER NEEDS CALLING!!!

rootpath = 'C:\\VENLAB data\\shared_modules'
sys.path.append(rootpath)
rootpath = 'C:\\VENLAB data\\TrackMaker'
sys.path.append(rootpath)

import viz
import clothoid_curve as cc
import numpy as np
from vizTrackMaker import vizStraight

viz.go()

viz.MainView.setPosition([00,75,00])
viz.MainView.setEuler([0,90,0])

def setStage():
	
	"""Creates grass textured groundplane"""
	
	###should set this hope so it builds new tiles if you are reaching the boundary.
	#fName = 'C:/VENLAB data/shared_modules/textures/strong_edge.bmp'
	fName = 'C:/VENLAB data/shared_modules/textures/ground_moon.png'
	
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
	colour = viz.WHITE, primitive = viz.QUAD_STRIP, rw = 3.0, primitive_width = 1.5, texturefile = None,
	 midline_step_size = .005, edge_step_size = .5
	 ):
#""" returns a semi-transparent bend of given roadwidth and clothoid geometry. """
		
		print ("Creating a Clothoid Bend")
		
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
			
		self.MidlineStepSize = midline_step_size
		#print('MSS: ', self.MidlineStepSize)
		
		self.EdgeStepSize = edge_step_size
		#print('ESS: ', self.EdgeStepSize)
		
		self.xDirection = x_dir

		self.zDirection = z_dir

		self.Colour = colour
		self.Primitive = primitive
		self.PrimitiveWidth = primitive_width

		#if primitive_width is None:
			#if primitive == viz.QUAD_STRIP:
				#primitive_width = .05
				#self.PrimitiveWidth = primitive_width 

			#elif primitive == viz.LINE_STRIP:
				#self.PrimitiveWidth = 2
				#viz.linewidth(self.PrimitiveWidth)
				#primitive_width = 0 #so I can use the same code below for both primitive types.

		self.CurveLength = ((self.TotalTime)*(self.Speed))
		#print('CL: ', self.CurveLength)
		
		self.MidlinePts = round(self.CurveLength / self.MidlineStepSize) 
		#print('MPts: ', self.MidlinePts)
		
		self.EdgePts = round(self.CurveLength / self.EdgeStepSize)
		#print('EPts ', self.EdgePts)
		
		self.InsideEdge = self.EdgeMaker(t = self.TimeStep, yawrate = self.Yawrate, transition_duration = self.Transition, rw = self.RoadWidth, speed = self.Speed)

		self.OutsideEdge = self.EdgeMaker(t = self.TimeStep, yawrate = self.Yawrate, transition_duration = self.Transition, rw = self.RoadWidth, speed = self.Speed)
		
				
		self.Midline = self.MidlineMaker()
		self.Midline = np.add(self.Midline, self.StartPos)
		
		print(self.Midline)
		
		#ensure all bends start invisible.
		self.ToggleVisibility(viz.OFF)        
		
		self.Texturefile = texturefile
		if primitive == viz.QUAD_STRIP: 
			self.AddTexture()
		
		#add road end.
		self.RoadEnd = self.Midline[-1,:]
		
		

	def AddTexture(self):
		"""function to add texture to the viz.primitive"""

		pass        

	def EdgeMaker(self, t, yawrate, transition_duration, rw, speed):
		"""function returns a bend edge"""
				
		x, y, bearing = cc.clothoid_curve(t, speed, yawrate, transition_duration)

		outside = cc.add_edge(x, y, (rw/2))
		inside = cc.add_edge(x, y, -(rw/2))
	
		o_edge = np.array(outside).T
		i_edge = np.array(inside).T
		
		print(o_edge.shape)
		print(i_edge.shape)
		
		viz.startlayer(self.Primitive)  	
		
		i = 0
		while i < self.EdgePts:
			for ins, out in zip(i_edge, o_edge):

				viz.vertex(ins[0], ABOVEGROUND, ins[1])
				viz.vertexcolor(self.Colour)
				
				viz.vertex(out[0], ABOVEGROUND, out[1])
				viz.vertexcolor(self.Colour)
			i += 1

			

		Bend = viz.endlayer()
		
		return Bend

	def MidlineMaker(self):
		"""returns midline"""

		midline_x, midline_y, bearing = cc.clothoid_curve(ts = self.TimeStep, v = self.Speed, max_yr = self.Yawrate, transition_duration = self.Transition)
					
		midline = np.zeros((len(self.TimeStep), 2))
		midline[:, 0] = midline_x
		midline[:, 1] = midline_y # is this z?
		
		#print('x', midline[0:10, 0])
		#print('y', midline[0:10, 1])
		print(midline)
		return midline

	def ToggleVisibility(self, visible = viz.ON):
		"""switches bends off or on"""

		if self.RoadWidth == 0:
			self.MidlineEdge.visible(visible)
		else:
			self.InsideEdge.visible(visible)
			self.OutsideEdge.visible(visible)

	def setAlpha(self, alpha = 1):
		
		pass
		
	#	if self.RoadWidth == 0:
	#		self.MidlineEdge.alpha(alpha)
	#	else:
	#		self.InsideEdge.alpha(alpha)
	#		self.OutsideEdge.alpha(alpha)
			
setStage()

#### MAKE STRAIGHT OBJECT ####
"""L = 16#2sec.
Straight = vizStraight(
	startpos = [0,0], primitive_width=1.5, road_width = 0, length = L, colour = [.6, .6, .6]
	)#, texturefile='strong_edge_soft.bmp')
Straight.ToggleVisibility(viz.ON)
Straight.setAlpha(.5)"""

## make clothoid
sp = [0, 0]
v = 8
tr = 4 #seconds
cornering = 4 # seconds
total = 2*tr + cornering #12 s
time_step = np.linspace(0, total, 1000) # ~1 ms steps
#yawrates = np.radians(np.linspace(6, 20, 3)) # 3 conditions of constant curvature yawrates
yr = 6

clothoid = vizClothoid(
	start_pos = sp, t = time_step,  speed = v, yawrate = yr, transition = tr
	)
clothoid.ToggleVisibility(visible = viz.ON)

	#def __init__(
	#self, start_pos, t,  speed, yawrate, transition, x_dir = 1, z_dir = 1,
	#colour = viz.WHITE, primitive = viz.QUAD_STRIP, rw = 3.0, primitive_width = 1.5, texturefile = None#,
	 #midline_step_size = .005, edge_step_size = .5
	 #):

	
	