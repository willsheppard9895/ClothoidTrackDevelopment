import sys

## TO DO - sort straight edge maker
rootpath = 'C:\\VENLAB data\\shared_modules'
sys.path.append(rootpath)
rootpath = 'C:\\VENLAB data\\shared_modules\\textures'
sys.path.append(rootpath)
rootpath = 'C:\\VENLAB data\\TrackMaker'
sys.path.append(rootpath)


import viz
import vizmat
import clothoid_curve as cc
import numpy as np
import matplotlib.pyplot as plt
from vizTrackMaker import vizStraight

viz.go()

viz.MainView.setPosition([0,300,0])
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


        #print ("Startpos: ", startpos)
        #print ("Endpos: ", endpos)
                
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
        
        pass
        

    
    def setAlpha(self, alpha = 1):
        
        self.Straight.alpha(alpha)

#setStage()

#### MAKE FIRST STRAIGHT OBJECT ####
#L = 16#2sec.
#Straight = vizStraightBearing(
#	bearing = 1, startpos = [0,0], primitive_width=1.5, road_width = 0, length = L, colour = viz.RED)
#Straight.ToggleVisibility(viz.ON)
#Straight.setAlpha(1)



