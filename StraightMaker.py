
## TO DO - sort straight edge maker
rootpath = 'C:\\VENLAB data\\shared_modules'
sys.path.append(rootpath)
rootpath = 'C:\\VENLAB data\\shared_modules\\textures'
sys.path.append(rootpath)
rootpath = 'C:\\VENLAB data\\TrackMaker'
sys.path.append(rootpath)


import viz
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

class vizStraightBearing():


    def __init__(self, bearing, startpos, length = 50, size = 500, z_dir = 1, colour = viz.WHITE, primitive = viz.QUAD_STRIP, primitive_width=None, road_width = 3.0, texturefile = None, midline_step_size = .005):
        """ultimately this class should inherit a super class called road section. But for now let's just make a straight"""

        """returns a straight, given some starting coords and length"""

        self.RoadLength = length   
        
        self.Bearing = bearing

        self.RoadStart = startpos #2 dimensional x, z array.
        self.RoadEnd = [(startpos[0]+(self.RoadLength * (np.sin(self.Bearing)))), (startpos[1]+(self.RoadLength*(np.cos(self.Bearing))))]#2dim xz array
        print(self.RoadEnd)
        
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
            self.MidlineEdge = self.StraightEdgeMaker([self.RoadStart[0],ABOVEGROUND,self.RoadStart[1]], [self.RoadEnd[0],ABOVEGROUND,self.RoadEnd[1]], primitive_width, bearing = self.Bearing)
            self.InsideEdge = None
            self.OutsideEdge = None
        else:
            self.InsideEdge_Start = [self.RoadStart[0]-self.HalfRoadWidth,ABOVEGROUND, self.RoadStart[1]] 
            self.InsideEdge_End = [self.RoadEnd[0]-self.HalfRoadWidth,ABOVEGROUND, self.RoadEnd[1]] 
            self.OutsideEdge_Start = [self.RoadStart[0]+self.HalfRoadWidth,ABOVEGROUND, self.RoadStart[1]]
            self.OutsideEdge_End = [self.RoadEnd[0]+self.HalfRoadWidth,ABOVEGROUND, self.RoadEnd[1]]

            self.InsideEdge = self.StraightEdgeMaker(self.InsideEdge_Start, self.InsideEdge_End, primitive_width, bearing = self.Bearing)
            self.OutsideEdge = self.StraightEdgeMaker(self.OutsideEdge_Start, self.OutsideEdge_End, primitive_width, bearing = self.Bearing)

              #make it so both edges have the same center. The setCenter is in local coordinates
            self.InsideEdge.setCenter([-self.HalfRoadWidth, 0, 0])
            self.OutsideEdge.setCenter([+self.HalfRoadWidth, 0, 0])	

            self.MidlineEdge = None	

        
        self.midline = self.StraightMidlineMaker(rw = 3, start_pos = [0, 0])

                #ensure all bends start invisible.
        self.ToggleVisibility(viz.OFF)

        
        
        self.Texturefile = texturefile
        if primitive == viz.QUAD_STRIP: 
            self.AddTexture()

        #put default widths if not given        

    def AddTexture(self):
        """function to add texture to the viz.primitive"""

        pass 


    def StraightEdgeMaker(self, startpos, endpos, primitive_width, bearing):
        """function returns a bend edge"""
        i = 0
        viz.startlayer(self.primitive) 


        print ("Startpos: ", startpos)
        print ("Endpos: ", endpos)
         
                
        # start leftside: 
        start_left = ([
        (startpos[0] + (primitive_width * (np.sin(bearing - np.pi/2)))), startpos[1], (startpos[2] + (primitive_width * (np.cos(bearing - np.pi/2))))
        ])
        print('1L', start_left)
        viz.vertex(start_left)
        #viz.vertex([startpos[0]-primitive_width, startpos[1], startpos[2]])        
        viz.vertexcolor(self.colour)
        
        # start rightside
        start_right = ([
        (startpos[0] + (primitive_width * (np.sin(bearing + np.pi/2)))), startpos[1], (startpos[2] + (primitive_width * (np.cos(bearing + np.pi/2))))
        ])
        #viz.vertex([startpos[0]+primitive_width, startpos[1], startpos[2]])
        print('1R', start_right)
        viz.vertex(start_right)
        viz.vertexcolor(self.colour)
        
        # end leftside: 
        end_left = ([
        (endpos[0] + (primitive_width * (np.sin(bearing - np.pi/2)))), endpos[1], (endpos[2] + (primitive_width * (np.cos(bearing - np.pi/2))))
        ])
        #viz.vertex([endpos[0]-primitive_width, endpos[1], endpos[2]])
        print('2L', end_left)
        viz.vertex(end_left)
        viz.vertexcolor(self.colour)
        
        # end rightside: 
        end_right = ([
        (endpos[0] + (primitive_width * (np.sin(bearing + np.pi/2)))), endpos[1], (endpos[2] + (primitive_width * (np.cos(bearing + np.pi/2))))
        ])
        #viz.vertex([endpos[0]+primitive_width, endpos[1], endpos[2]])		
        print('2R', end_right)
        viz.vertex(end_right)
        viz.vertexcolor(self.colour)

        straightedge = viz.endlayer()

        return (straightedge)
    
    """def add_edge(x, z, rw, sp = [0, 0]):
         creates a s column array for x, y coords of the edges. sp = start position of the road
        
        g = np.gradient([x,z], axis = 1)
        angles = np.arctan2(g[1], g[0])
        #print(angles.shape)

        #rotate point of on x,z graph using angles.
        
        angles = angles + np.pi/2.0 #perpendicular normal. rotate counterclockwise
        
        unit_normals = np.array([np.cos(angles), np.sin(angles)]) #on unit circle
        unit_normals *= rw
        
        xl, zl = ((x + unit_normals[0]) + sp[0]), ((z  + unit_normals[1]) + sp[1])

        return([xl, zl])"""
    
    def StraightMidlineMaker(self, rw, start_pos):
        """returns midline"""
        #make midline        
            
        midline_x = np.linspace(self.RoadStart[0], self.RoadEnd[0], self.Midline_Pts)
        midline_z = np.linspace(self.RoadStart[1], self.RoadEnd[1], self.Midline_Pts)
     
        midline = np.column_stack((midline_x, midline_z))
        x = midline[:, 0]
        z = midline[:, 1]        
        
        outside = np.array(cc.add_edge(x, z, (rw/2), start_pos))
        inside = np.array(cc.add_edge(x, z, -(rw/2), start_pos))
            
        return midline, inside, outside

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

setStage()

#### MAKE FIRST STRAIGHT OBJECT ####
L = 16#2sec.
Straight = vizStraightBearing(
	bearing = 1, startpos = [0,0], primitive_width=1.5, road_width = 0, length = L, colour = viz.RED)
Straight.ToggleVisibility(viz.ON)
Straight.setAlpha(1)



class vizStraight():


    def __init__(self, bearing, startpos, length = 50, size = 500, z_dir = 1, colour = viz.WHITE, primitive = viz.QUAD_STRIP, primitive_width=None, road_width = 3.0, texturefile = None, midline_step_size = .005):
        """ultimately this class should inherit a super class called road section. But for now let's just make a straight"""

        """returns a straight, given some starting coords and length"""

        self.RoadLength = length   
        
        self.Bearing = bearing

        self.RoadStart = startpos #2 dimensional x, z array.
        self.RoadEnd = [(startpos[0]+(self.RoadLength * (np.sin(self.Bearing)))), (startpos[1]+(self.RoadLength*(np.cos(self.Bearing))))]#2dim xz array
        
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