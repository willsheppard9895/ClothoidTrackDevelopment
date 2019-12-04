###script to view and almagamate eye tracking files.

import os
import pandas as pd
from glob import glob


if __name__ == '__main__':
	#rootdir = sys.argv[1] 
    
    #rootdir = "/Data"
    os.chdir('C:/VENLAB data/ClothoidTrackDevelopment/Data')
    rootdir = os.getcwd()
    output_filename = 'collated_steering.csv'

    master_stitch = pd.DataFrame() #master data for gaze and steering          

    #print(rootdir + '/*.csv')
    print(rootdir)
    for fn in glob(rootdir + '/*.csv'):
        
        
        print(fn)

        trial_data = pd.read_csv(fn)
        #print(trial_data)

            
        master_stitch = pd.concat([master_stitch,trial_data])
        
    #now you've built the master data of all trials, save it.
    master_stitch.to_csv(output_filename)



