import numpy as np
from scipy.special import fresnel
import matplotlib.pyplot as plt
import viz

def rotate(x, y, a):
	s, c = np.sin(a), np.cos(a)
	return (
			c*x - s*y,
			s*x + c*y
			)

def clothoid_segment(t, s, v, x0=0, y0=0, bearing0=0):
	x, y = np.sqrt(np.pi)*v*np.array(fresnel(np.sqrt(s)*t/np.sqrt(np.pi)))/np.sqrt(s)
	bearing = s*t**2/2 + bearing0

	x, y = rotate(x, y, bearing0)

	x += x0
	y += y0

	return np.array((x, y, bearing))

def constant_curvature_segment(t, v, yr, x0=0, y0=0, bearing0=0):
	bearing = bearing0 + t*yr
	
	x = (v*np.cos(bearing0) - v*np.cos(bearing) + x0*yr)/yr
	y = (-v*np.sin(bearing0) + v*np.sin(bearing) + y0*yr)/yr

	return np.array((x, y, bearing))

"""
def clothoid_curve(ts, v, max_yr, total_yaw):
	duration = ts[-1]
	transition_duration = duration - total_yaw/max_yr
	cornering_duration = duration - transition_duration*2

	print(cornering_duration + transition_duration*2, duration)

	assert(transition_duration > 0)
	assert(cornering_duration > 0)
"""

def clothoid_curve(ts, v, max_yr, transition_duration):
	duration = ts[-1] #last values of t (=total duration)
	cornering_duration = duration - 2*transition_duration
	
	assert(transition_duration > 0)
	assert(cornering_duration > 0)
	
	s = max_yr/transition_duration #yawrate step of transition

	t = ts.copy() #timesteps
	e = t.searchsorted(transition_duration) #index at which timestep array exceeds transition duration
	#transition_timesteps = t[:e+1] 
	entry = clothoid_segment(t[:e+1], s, v) #

	t0, t = t[e], t[e:]
	t -= t0
	e = t.searchsorted(cornering_duration)
	cornering = constant_curvature_segment(
			t[:e+1],
			v, max_yr,
			*entry[:,-1])

	t0, t = t[e], t[e:]
	t -= t0
	outro = clothoid_segment(t[::-1], s, v)
	outro[1, :] *= -1
	outro[1, :] -= outro[1,0]
	outro[0, :] -= outro[0,0]
	outro[:2] = rotate(outro[0], outro[1], -outro[-1,0])
	
	outro[2] *= -1
	outro[2] -= outro[-1,0]
	outro[:2] = rotate(outro[0], outro[1], -cornering[-1,-1])
	
	outro[2] += cornering[-1,-1]
	
	outro[:2] += cornering[:2, -1].reshape(2, -1)
	
	out = np.concatenate((entry[:,:-1], cornering[:,:-1], outro), axis=1)
	
	#print(out)
	
	return out


def add_edge(x, y, rw, sp = [0, 0]):
	""" creates a s column array for x, y coords of the edges. sp = start position of the road"""
	
	g = np.gradient([x,y], axis = 1)
	angles = np.arctan2(g[1], g[0])
	#print(angles.shape)

	#rotate point of on x,y graph using angles.
	#xs = norms
	#ys = np.zeros(len(norms))
	angles = angles + np.pi/2.0 #perpendicular normal. rotate counterclockwise
	#unit_normals = [np.cos(angles) - np.sin(angles), np.sin(angles) + np.cos(angles)] #on unit circle
	unit_normals = np.array([np.cos(angles), np.sin(angles)]) #on unit circle
	unit_normals *= rw
	xl, yl = ((x + unit_normals[0]) + sp[0]), ((y  + unit_normals[1]) + sp[1])

	return([xl, yl])

ABOVEGROUND = 0.1

def build_curve_viz(t, yawrate, transition, rw = 3, speed = 8):


	x, y, bearing = clothoid_curve(t, speed, yawrate, transition)

	midline	= add_edge(x, y, rw = 0)
	outside = add_edge(x,y, rw)
	inside = add_edge(x,y, -rw)
	
	viz.startlayer(viz.POINTS)
	
	for mid, ins, out in zip(midline, inside, outside):

		viz.vertex(mid[0], ABOVEGROUND, mid[1])
		viz.vertexcolor(viz.RED)
		viz.vertex(ins[0], ABOVEGROUND, ins[1])
		viz.vertexcolor(viz.BLUE)
		viz.vertex(out[0], ABOVEGROUND, out[1])
		viz.vertexcolor(viz.GREEN)


	
	return( np.array( (x, y, bearing)))
	

def test():
	
	
	speed = 8
	transition = 4 #seconds
	cornering = 4
	total = 2*transition + cornering #12 s
	t = np.linspace(0, total, 1000) # ~1 ms steps
	yawrates = np.radians(np.linspace(6, 20, 3)) # 4 conditions of constant curvature yawrates
	
	for yawrate in yawrates:
		build_curve_viz(t, yawrate, transition)
	"""
	x = [:, 0]
	y = [:, 1]
	"""
		
	"""x, y, bearing = clothoid_curve(t, speed, yawrate, transition)
	plt.figure("coords")
	label = "Cornering yaw rate {np.degrees(yawrate):.1f}"
	plt.plot(x, y, label=label)
	plt.xlabel("X position (meters)")
	plt.ylabel("Y position (meters)")
	plt.figure("orientations")
	plt.plot(t, np.degrees(np.unwrap(bearing)), label=label)
	plt.xlabel("Time (seconds)")
	plt.ylabel("Bearing (degrees)")
	plt.figure("coords")
	plt.legend()
	plt.axis('equal')
	plt.figure("orientations")
	plt.legend()
	plt.show()"""

		

if __name__ == '__main__':
	test()


