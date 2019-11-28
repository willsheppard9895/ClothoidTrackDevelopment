### NEED TO ADD TOGGLE VISIBILITY

import viz
import numpy as np
import matplotlib.pyplot as plt
import vizTrackMaker as tm
from ConditionListGenerator import ConditionList

#viz.setMultiSample(64)

viz.go()

viz.MainView.setPosition([-20,150,15])
viz.MainView.setEuler([0,90,0])

def setStage():
	
	"""Creates grass textured groundplane"""
	
	###should set this hope so it builds new tiles if you are reaching the boundary.
	#fName = 'C:/VENLAB data/shared_modules/textures/strong_edge.bmp'
	fName = 'strong_edge.bmp'
	
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

yawrates = np.linspace(6, 20, 3)
onsets_list = [1.5, 5, 8, 11]
		
CL = ConditionList(yawrates, onsets_list)

CONDITIONLIST = CL.GenerateConditionList()

print(CL.GenerateConditionList())

ABOVEGROUND = .01 #distance above ground

setStage()

def MyCurves(self):
    
    def __init__(self):
        
            viz.EventClass.__init__(self)
        
            #### MAKE FIRST STRAIGHT OBJECT ####
            L = 16#2sec.
            Straight = tm.vizStraight(
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
            
            clothoid = tm.vizClothoid(start_pos = sp, t = time_step,  speed = v, yawrate = yr, transition = tr, x_dir = -1)
            clothoid.setAlpha(alpha = .5)

            #### MAKE SECOND STRAIGHT OBJECT ####
            ## must match direction to clothoid.bearing[-1]
            SB = tm.vizStraightBearing(bearing = clothoid.Bearing[-1], startpos = clothoid.RoadEnd, primitive_width=1.5, road_width = 3, length = L, colour = viz.RED)
            SB.setAlpha(.5)

    def run(self):
        i = 0
        for i, trial in CONDITIONLIST.iterrows():
            yr = np.radians(trial['maxYR'])
        i += 0


        
Curves = MyCurves()

viztask.schedule(Curves.run())