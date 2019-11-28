import numpy as np

viz.go()

viz.MainView.setPosition([0,300,0])
viz.MainView.setEuler([0,90,0])

ABOVEGROUND = 0.01

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


class vizStraightBearing():
    
    def __init__(self, start_pos, length, bearing = 0, road_width = 3, colour = viz.WHITE, primitive = viz.QUAD_STRIP, primitive_width = 1.5, x_dir = 1, z_dir = 1):
        """ Creates a straightt section of road given a start position, length, bearing, and road width"""
        print('Creating vizStraightBearing')
        
        self.StartPos = start_pos
        
        self.Length = length
        
        self.Bearing = bearing
                
        self.RoadEnd = [(self.StartPos[0]+(self.Length * (np.sin(self.Bearing)))), (self.StartPos[1]+(self.Length*(np.cos(self.Bearing))))]#2dim xz array
        print('road end', self.RoadEnd)
        
        self.RoadWidth = road_width
        
        self.Colour = colour
        
        self.Primitive = primitive
        
        self.PrimitiveWidth = primitive_width 
        
        self.xDirection = x_dir
        
        self.zDirection = z_dir
        
        straightlist = self.StraightMaker(startpos = self.StartPos, bearing = self.Bearing, length = self.Length, primitive_width = self.PrimitiveWidth)
        
        self.Straight, self.RoadEnd = straightlist
        
        self.Straight.visible(viz.ON)
        
        print(self.RoadEnd)
        
        
    def StraightMaker(self, startpos, bearing, length, primitive_width):
        
        endpos = [(startpos[0] + (length * (np.sin(bearing)))),(startpos[1]+(length*(np.cos(bearing))))]
        
        viz.startlayer(self.Primitive) 


        print ("Startpos: ", startpos)
        print ("Endpos: ", endpos)
        
        start_left = ([
        (startpos[0] + (primitive_width * (np.sin(bearing - np.pi/2)))), ABOVEGROUND, (startpos[1] + (primitive_width * (np.cos(bearing - np.pi/2))))
        ])
        print('1L', start_left)
        viz.vertex(start_left)
        #viz.vertex([startpos[0]-primitive_width, startpos[1], startpos[2]])        
        viz.vertexcolor(self.Colour)
        
        # start rightside
        start_right = ([
        (startpos[0] + (primitive_width * (np.sin(bearing + np.pi/2)))), ABOVEGROUND, (startpos[1] + (primitive_width * (np.cos(bearing + np.pi/2))))
        ])
        #viz.vertex([startpos[0]+primitive_width, startpos[1], startpos[2]])
        print('1R', start_right)
        viz.vertex(start_right)
        viz.vertexcolor(self.Colour)
        
        # end leftside: 
        end_left = ([
        (endpos[0] + (primitive_width * (np.sin(bearing - np.pi/2)))), ABOVEGROUND, (endpos[1] + (primitive_width * (np.cos(bearing - np.pi/2))))
        ])
        #viz.vertex([endpos[0]-primitive_width, endpos[1], endpos[2]])
        print('2L', end_left)
        viz.vertex(end_left)
        viz.vertexcolor(self.Colour)
        
        # end rightside: 
        end_right = ([
        (endpos[0] + (primitive_width * (np.sin(bearing + np.pi/2)))), ABOVEGROUND, (endpos[1] + (primitive_width * (np.cos(bearing + np.pi/2))))
        ])
        #viz.vertex([endpos[0]+primitive_width, endpos[1], endpos[2]])		
        print('2R', end_right)
        viz.vertex(end_right)
        viz.vertexcolor(self.Colour)

        straight = viz.endlayer()

        return (straight, endpos)
            
    
    def ToggleVisibility(self, visible = viz.ON):
        
        pass
        

    
    def setAlpha(self, alpha = 1):
        
        pass
            
setStage()

#### MAKE FIRST STRAIGHT OBJECT ####
L = 16#2sec.
Straight = vizStraightBearing(
	start_pos = [0,0], length = L, bearing = -1
	)
Straight.ToggleVisibility(viz.ON)
Straight.setAlpha(1)