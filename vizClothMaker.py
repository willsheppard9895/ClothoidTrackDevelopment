""" Retrns a vizard object, with above ground features of a clothoid curve """

rootpath = 'C:\\VENLAB data\\shared_modules'
sys.path.append(rootpath)

import numpy as np
from scipy.special import fresnel
import viz
from clothoid_curve import clothoid_curve

ABOVEGROUND = .01 #distance above ground

class vizClothoid():
    
    def __init__(self, startpos, bearing, clothoid_midline, road_width = 3.0, colour = viz.WHITE, primitive = viz.QUAD_STRIP, primitive_width=None, midline_step_size = .005, edge_step_size = .5, x_dir = 1, z_dir = 1, texturefile = None):

    #make sign -1 if you want a left bend.
        #improve to have a flag if it's a quad, and the quad width.
        print ("Creating a Bend")        

        self.RoadStart = startpos #2 dim xz array 
       
        self.Bearing = bearing
        
        self.RoadWidth = road_width		
        if self.RoadWidth == 0:
            self.HalfRoadWidth = 0
        else:
            self.HalfRoadWidth = road_width/2.0	
        
        self.Colour = colour
        
        self.Primitive = primitive
       
        self.PrimitiveWidth = primitive_width
        if primitive_width is None:
            if primitive == viz.QUAD_STRIP:
                primitive_width = .05
                self.primitive_width = primitive_width 

            elif primitive == viz.LINE_STRIP:
                self.primitive_width = 2
                viz.linewidth(self.primitive_width)
                primitive_width = 0 #so I can use the same code below for both primitive types.	
        
        
        self.BendLength = clothoid_midline ### need help!!!
        #### TODO!!!!!!
        self.MidlineStepSize = midline_step_size
        self.Midline_Points = int(round(self.BendLength / self.MidlineStepSize))
        
        self.EdgeStepSize = edge_step_size
        self.EdgePoints = int(round(self.BendLength / self.EdgeStepSize))

        self.Xdirection = x_dir

        """
        This needs updating for clothoid curve!!!

        if self.Xdirection > 0:
            
            self.RoadArray = np.linspace(np.pi, (np.pi - self.arc_angle), self.Edge_Pts) 
            self.MidlineArray = np.linspace(np.pi, (np.pi - self.arc_angle), self.Midline_Pts)  #right bend
        else:
            self.RoadArray = np.linspace(0.0, self.arc_angle, self.Edge_Pts)  #left bend
            self.MidlineArray = np.linspace(0.0, self.arc_angle, self.Midline_Pts)  
        """
        self.Zdirection = z_dir #[1, -1] 

        if self.RoadWidth == 0:
            self.MidlineEdge = self.EdgeMaker([self.RoadStart[0], ABOVEGROUND, self.RoadStart[1]], self.Bearing, primitive_width)
            self.InsideEdge = None
            self.OutsideEdge = None
        else:
            self.InsideEdgeClothoid = self.ClothoidMidline - (self.HalfRoadWidth)
            self.InsideEdgeStart = [self.RoadStart[0] - self.HalfRoadWidth, ABOVEGROUND, self.RoadStart[1]] 

            self.OutsideEdgeClothoid = self.ClothoidMidline + (self.RoadWidth/2.0)
            self.OutsideEdgeStart = [self.RoadStart[0]  +self.HalfRoadWidth, ABOVEGROUND, self.RoadStart[1]]

            self.InsideEdge = self.EdgeMaker(self.InsideEdge_Start, self.InsideEdge_Rads, primitive_width)
            self.OutsideEdge = self.EdgeMaker(self.OutsideEdge_Start, self.OutsideEdge_Rads, primitive_width)

            #make it so both edges have the same center. The setCenter is in local coordinates
            self.InsideEdge.setCenter([-self.HalfRoadWidth, 0, 0])
            self.OutsideEdge.setCenter([+self.HalfRoadWidth, 0, 0])		

            self.MidlineEdge = None

        self.midline = self.MidlineMaker()
        self.midline = np.add(self.midline, self.RoadStart)

        #CurveOrigin always starts at zero. We need to make it so curve origin equals the following.
        translate = self.Bearing * self.Xdirection
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

    def EdgeMaker(self, startpos, bearing, primitive_width):
        """function returns a bend edge"""
        """function returns a bend edge"""
        
        viz.startlayer(self.primitive) 	
        
        for ins, out in zip(inside,outside):

            viz.vertex(ins[0], ABOVEGROUND, ins[1])
            viz.vertexcolor(self.colour)
            viz.vertex(out[0], ABOVEGROUND, out[1])
            viz.vertexcolor(self.colour)

        """
        while i < self.Edge_Pts:			
            x1 = ((bearing - primitive_width)*np.cos(self.RoadArray[i])) + startpos[0]
            z1 = self.Zdirection*((bearing - primitive_width)*np.sin(self.RoadArray[i])) + startpos[2]

            #print (z1[i])			
            viz.vertex(x1, ABOVEGROUND, z1)				
            viz.vertexcolor(self.colour)

            if self.primitive == viz.QUAD_STRIP:
                x2 = ((rads + primitive_width)*np.cos(self.RoadArray[i])) + startpos[0]
                z2 = self.Zdirection*((rads + primitive_width)*np.sin(self.RoadArray[i])) + startpos[2]
                viz.vertex(x2, ABOVEGROUND, z2)				
                viz.vertexcolor(self.colour)

            i += 1

        """

        Bend = viz.endlayer()

        return Bend

    def MidlineMaker(self):
        """returns midline"""

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

