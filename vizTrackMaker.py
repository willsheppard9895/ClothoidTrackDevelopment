"""module returns vizard objects"""

import numpy as np
import viz
import clothoid_curve as cc

"""TODO: 

- Overall 'TrackSection' class with methods that all sub-sections will inherit. 

- Overall 'Track' class that has sections as sub-classes. The user can specify the Bends and Straights, in order, with radii and lengths.

- record end position within Bend Class.

- Keep usability in mind at all times 

- Programme in Bend length.

- Need to incorporate world-euler of end position of each section so the new section can seamlessly be added on, regardless of where the bend is pointed.



 - TODO: use simTrackMaker as the basic geometry creater. Then use the vizTracker to add the visuals.
"""
ABOVEGROUND = .01 #distance above ground

class vizBend():

    def __init__(self, startpos, rads, size = 500,  x_dir = 1, z_dir = 1, colour = viz.WHITE, primitive = viz.QUAD_STRIP, primitive_width=None, road_width = 3.0, texturefile = None, arc_angle = np.pi, midline_step_size = .005, edge_step_size = .5):
        """Returns a  bend of a specific road width, with functions to set the visibility, position, or Euler of both edges at once. Put road_width to 0 for single edge"""	

        """
        arc_angle is the length of the arc in radians. 
        step_size is the granulation of the midline road arrays, in metres
        size is the edge array size, doesn't need to be as granulated.
        """

        #make sign -1 if you want a left bend.
        #improve to have a flag if it's a quad, and the quad width.
        print ("Creating a Bend")        

        self.RoadStart = startpos #2 dim xz array 

        self.RoadWidth = road_width		
        if self.RoadWidth == 0:
            self.HalfRoadWidth = 0
        else:
            self.HalfRoadWidth = road_width/2.0		
        
        self.Rads = rads
        
        self.arc_angle = arc_angle
        
        circumference = 2 * np.pi * rads
        
        self.bend_length = (arc_angle / (2*np.pi)) * circumference
        print ("Bend_length:",self.bend_length)
        
        self.midline_step_size = midline_step_size
        
        self.edge_step_size = edge_step_size
        
        self.Edge_Pts = int(round(self.bend_length / self.edge_step_size))
        print ("Edge_Pts: ", self.Edge_Pts)
        
        self.Midline_Pts = int(round(self.bend_length / self.midline_step_size))
        print ("Midline_Pts: ", self.Midline_Pts)
        
        self.X_direction = x_dir

        if self.X_direction > 0:
            
            self.RoadArray = np.linspace(np.pi, (np.pi - self.arc_angle), self.Edge_Pts) 
            self.MidlineArray = np.linspace(np.pi, (np.pi - self.arc_angle), self.Midline_Pts)  #right bend
        else:
            self.RoadArray = np.linspace(0.0, self.arc_angle, self.Edge_Pts)  #left bend
            self.MidlineArray = np.linspace(0.0, self.arc_angle, self.Midline_Pts)  

        self.Z_direction = z_dir #[1, -1] 
        self.colour = colour
        self.primitive = primitive
        self.primitive_width = primitive_width
        
        if primitive_width is None:
            if primitive == viz.QUAD_STRIP:
                primitive_width = .05
                self.primitive_width = primitive_width 

            elif primitive == viz.LINE_STRIP:
                self.primitive_width = 2
                viz.linewidth(self.primitive_width)
                primitive_width = 0 #so I can use the same code below for both primitive types.		


        if self.RoadWidth == 0:
            self.MidlineEdge = self.EdgeMaker([self.RoadStart[0],ABOVEGROUND,self.RoadStart[1]], self.Rads, primitive_width)
            self.InsideEdge = None
            self.OutsideEdge = None
        else:
            self.InsideEdge_Rads = self.Rads-(self.HalfRoadWidth)
            self.InsideEdge_Start = [self.RoadStart[0]-self.HalfRoadWidth,ABOVEGROUND, self.RoadStart[1]] 

            self.OutsideEdge_Rads = self.Rads+(self.RoadWidth/2.0)
            self.OutsideEdge_Start = [self.RoadStart[0]+self.HalfRoadWidth,ABOVEGROUND, self.RoadStart[1]]

            self.InsideEdge = self.EdgeMaker(self.InsideEdge_Start, self.InsideEdge_Rads, primitive_width)
            self.OutsideEdge = self.EdgeMaker(self.OutsideEdge_Start, self.OutsideEdge_Rads, primitive_width)

            #make it so both edges have the same center. The setCenter is in local coordinates
            self.InsideEdge.setCenter([-self.HalfRoadWidth, 0, 0])
            self.OutsideEdge.setCenter([+self.HalfRoadWidth, 0, 0])		

            self.MidlineEdge = None
        
        self.midline = self.MidlineMaker()
        self.midline = np.add(self.midline, self.RoadStart)
        
        #CurveOrigin always starts at zero. We need to make it so curve origin equals the following.
        translate = self.Rads * self.X_direction
        self.CurveOrigin = np.add(self.RoadStart, [translate,0])
        print ("CurveOrigin: ", self.CurveOrigin)

        #this requires translating the bend position and the midline by the radius, in the opposite direction of X_direction.
        if self.RoadWidth == 0:
            self.MidlineEdge.setPosition([translate, 0, 0], mode = viz.REL_LOCAL)    
        else:
            self.InsideEdge.setPosition([translate, 0, 0], mode = viz.REL_LOCAL)
            self.OutsideEdge.setPosition([translate, 0, 0], mode = viz.REL_LOCAL)

        self.midline[:,0] = np.add(self.midline[:,0], translate)
        
        #ensure all bends start invisible.
        self.ToggleVisibility(viz.OFF)        
        
        self.Texturefile = texturefile
        if primitive == viz.QUAD_STRIP: 
            self.AddTexture()


        #add road end.
        self.RoadEnd = self.midline[-1,:]
        #put default widths if not given        

    def AddTexture(self):
        """function to add texture to the viz.primitive"""

        pass        


    def EdgeMaker(self, startpos, rads, primitive_width):
        """function returns a bend edge"""
        i = 0
        viz.startlayer(self.primitive) 	
        
        while i < self.Edge_Pts:			
            x1 = ((rads-primitive_width)*np.cos(self.RoadArray[i])) + startpos[0]
            z1 = self.Z_direction*((rads-primitive_width)*np.sin(self.RoadArray[i])) + startpos[2]

            #print (z1[i])			
            viz.vertex(x1, ABOVEGROUND, z1)				
            viz.vertexcolor(self.colour)

            if self.primitive == viz.QUAD_STRIP:
                x2 = ((rads+primitive_width)*np.cos(self.RoadArray[i])) + startpos[0]
                z2 = self.Z_direction*((rads+primitive_width)*np.sin(self.RoadArray[i])) + startpos[2]
                viz.vertex(x2, ABOVEGROUND, z2)				
                viz.vertexcolor(self.colour)

            i += 1

        Bend = viz.endlayer()

        return Bend

    def MidlineMaker(self):
        """returns midline"""
        #make midline        
        midline = np.zeros((int(self.Midline_Pts),2))
        midline[:,0] = self.Rads*np.cos(self.MidlineArray)
        midline[:,1] = self.Z_direction*self.Rads*np.sin(self.MidlineArray)
            
        return midline

    def ToggleVisibility(self, visible = viz.ON):
        """switches bends off or on"""

        if self.RoadWidth == 0:
            self.MidlineEdge.visible(visible)
        else:
            self.InsideEdge.visible(visible)
            self.OutsideEdge.visible(visible)

    def setAlpha(self, alpha = 1):
        
        if self.RoadWidth == 0:
            self.MidlineEdge.alpha(alpha)
        else:
            self.InsideEdge.alpha(alpha)
            self.OutsideEdge.alpha(alpha)
            
class vizClothoid():
	
	def __init__(
	self, start_pos, t,  speed, yawrate, transition, x_dir = 1, z_dir = 1,
	colour = viz.WHITE, primitive = viz.QUAD_STRIP, rw = 3.0, primitive_width = 1.5, texturefile = None,
	ABOVEGROUND = .01):
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
		self.Bend.visible(visible)
			
	def setAlpha(self, alpha = 1):
		""" set road opacy """
		self.Bend.alpha(alpha)

class vizStraight():


    def __init__(self, startpos, length = 50, size = 500, z_dir = 1, colour = viz.WHITE, primitive = viz.QUAD_STRIP, primitive_width=None, road_width = 3.0, texturefile = None, midline_step_size = .005):
        """ultimately this class should inherit a super class called road section. But for now let's just make a straight"""

        """returns a straight, given some starting coords and length"""
        
        print('Creating vizStraight')
        
        self.RoadLength = length                

        self.RoadStart = startpos #2 dimensional x, z array.
        self.RoadEnd = [startpos[0],startpos[1]+(length*z_dir)] #currently only if it's north or south orientation. #2dim xz array
        self.midline_step_size = midline_step_size        
        
        self.Midline_Pts = int(round(self.RoadLength / self.midline_step_size))
        
        #self.RoadSize_Pts = size
        self.RoadWidth = road_width		
        if self.RoadWidth == 0:
            self.HalfRoadWidth = 0
        else:
            self.HalfRoadWidth = road_width/2.0		

        self.Z_direction = z_dir #[1, -1] 
        self.colour = colour
        self.primitive = primitive
        self.primitive_width = primitive_width
    
        if primitive_width is None:
            if primitive == viz.QUAD_STRIP:
                primitive_width = .05
                self.primitive_width = primitive_width 

            elif primitive == viz.LINE_STRIP:
                self.primitive_width = 2
                viz.linewidth(self.primitive_width)
                primitive_width = 0 #so I can use the same code below for both primitive types.	
                
        if self.RoadWidth == 0:
            self.MidlineEdge = self.StraightEdgeMaker([self.RoadStart[0],ABOVEGROUND,self.RoadStart[1]], [self.RoadEnd[0],ABOVEGROUND,self.RoadEnd[1]], primitive_width)
            self.InsideEdge = None
            self.OutsideEdge = None
        else:
            self.InsideEdge_Start = [self.RoadStart[0]-self.HalfRoadWidth,ABOVEGROUND, self.RoadStart[1]] 
            self.InsideEdge_End = [self.RoadEnd[0]-self.HalfRoadWidth,ABOVEGROUND, self.RoadEnd[1]] 
            self.OutsideEdge_Start = [self.RoadStart[0]+self.HalfRoadWidth,ABOVEGROUND, self.RoadStart[1]]
            self.OutsideEdge_End = [self.RoadEnd[0]+self.HalfRoadWidth,ABOVEGROUND, self.RoadEnd[1]]

            self.InsideEdge = self.StraightEdgeMaker(self.InsideEdge_Start, self.InsideEdge_End, primitive_width)
            self.OutsideEdge = self.StraightEdgeMaker(self.OutsideEdge_Start, self.OutsideEdge_End, primitive_width)

              #make it so both edges have the same center. The setCenter is in local coordinates
            self.InsideEdge.setCenter([-self.HalfRoadWidth, 0, 0])
            self.OutsideEdge.setCenter([+self.HalfRoadWidth, 0, 0])	

            self.MidlineEdge = None	

        
        self.midline = self.StraightMidlineMaker()

                #ensure all bends start invisible.
        self.ToggleVisibility(viz.OFF)

        
        
        self.Texturefile = texturefile
        if primitive == viz.QUAD_STRIP: 
            self.AddTexture()

        #put default widths if not given        

    def AddTexture(self):
        """function to add texture to the viz.primitive"""

        pass 


    def StraightEdgeMaker(self, startpos, endpos, primitive_width):
        """function returns a bend edge"""
        i = 0
        viz.startlayer(self.primitive) 


        print ("Startpos: ", startpos)
        print ("Endpos: ", endpos)
                
        viz.vertex([startpos[0]-primitive_width, startpos[1], startpos[2]])        
        viz.vertexcolor(self.colour)
        viz.vertex([startpos[0]+primitive_width, startpos[1], startpos[2]])
        viz.vertexcolor(self.colour)
        viz.vertex([endpos[0]-primitive_width, endpos[1], endpos[2]])
        viz.vertexcolor(self.colour)
        viz.vertex([endpos[0]+primitive_width, endpos[1], endpos[2]])		
        viz.vertexcolor(self.colour)

        straightedge = viz.endlayer()

        return (straightedge)
    
    def StraightMidlineMaker(self):
        """returns midline"""
        #make midline        
            
        midline_x = np.linspace(self.RoadStart[0], self.RoadEnd[0], self.Midline_Pts)
        midline_z = np.linspace(self.RoadStart[1], self.RoadEnd[1], self.Midline_Pts)
        
        midline = np.column_stack((midline_x, midline_z))
            
        return midline

    def ToggleVisibility(self, visible = viz.ON):
        """switches straights off or on"""

        if self.RoadWidth == 0:
            self.MidlineEdge.visible(visible)
        else:
            self.InsideEdge.visible(visible)
            self.OutsideEdge.visible(visible)

    
    def setAlpha(self, alpha = 1):
        
        if self.RoadWidth == 0:
            self.MidlineEdge.alpha(alpha)
        else:
            self.InsideEdge.alpha(alpha)
            self.OutsideEdge.alpha(alpha)
            
class vizStraightBearing():
    
    def __init__(self, startpos, length, bearing = 0, road_width = 3, colour = viz.WHITE, primitive = viz.QUAD_STRIP, primitive_width = 1.5, x_dir = 1, z_dir = 1):
        """ Creates a straightt section of road given a start position, length, bearing, and road width"""
        print('Creating vizStraightBearing')
        
        self.StartPos = startpos
        
        self.Length = length
        
        self.Bearing = bearing
                
        self.RoadEnd = [(self.StartPos[0]+(self.Length * (np.sin(self.Bearing)))), (self.StartPos[1]+(self.Length*(np.cos(self.Bearing))))]#2dim xz array
        #print('road end', self.RoadEnd)
        
        self.RoadWidth = road_width
        
        self.Colour = colour
        
        self.Primitive = primitive
        
        self.PrimitiveWidth = primitive_width 
        
        self.xDirection = x_dir
        
        self.zDirection = z_dir
        
        straightlist = self.StraightMaker(startpos = self.StartPos, bearing = self.Bearing, length = self.Length, primitive_width = self.PrimitiveWidth)
        
        self.Straight, self.RoadEnd = straightlist
        
        self.Straight.visible(viz.ON)
        
        #print(self.RoadEnd)
        
        
    def StraightMaker(self, startpos, bearing, length, primitive_width):
        
        endpos = [(startpos[0] + (length * (np.sin(bearing)))),(startpos[1]+(length*(np.cos(bearing))))]
        
        viz.startlayer(self.Primitive) 


        #print ("Startpos: ", startpos)
       # print ("Endpos: ", endpos)
        
        start_left = ([
        (startpos[0] + (primitive_width * (np.sin(bearing - np.pi/2)))), ABOVEGROUND, (startpos[1] + (primitive_width * (np.cos(bearing - np.pi/2))))
        ])
        #print('1L', start_left)
        viz.vertex(start_left)       
        viz.vertexcolor(self.Colour)
        
        # start rightside
        start_right = ([
        (startpos[0] + (primitive_width * (np.sin(bearing + np.pi/2)))), ABOVEGROUND, (startpos[1] + (primitive_width * (np.cos(bearing + np.pi/2))))
        ])
        #print('1R', start_right)
        viz.vertex(start_right)
        viz.vertexcolor(self.Colour)
        
        # end leftside: 
        end_left = ([
        (endpos[0] + (primitive_width * (np.sin(bearing - np.pi/2)))), ABOVEGROUND, (endpos[1] + (primitive_width * (np.cos(bearing - np.pi/2))))
        ])
        #print('2L', end_left)
        viz.vertex(end_left)
        viz.vertexcolor(self.Colour)
        
        # end rightside: 
        end_right = ([
        (endpos[0] + (primitive_width * (np.sin(bearing + np.pi/2)))), ABOVEGROUND, (endpos[1] + (primitive_width * (np.cos(bearing + np.pi/2))))
        ])
        #print('2R', end_right)
        viz.vertex(end_right)
        viz.vertexcolor(self.Colour)

        straight = viz.endlayer()

        return (straight, endpos)
            
    
    def ToggleVisibility(self, visible = viz.ON):
        
        self.Straight.visible(visible)
        

    
    def setAlpha(self, alpha = 1):
        
        self.Straight.alpha(alpha)