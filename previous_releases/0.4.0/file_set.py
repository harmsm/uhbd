"""file_set.py (v 0.4).  A script that runs UHBD calculations on a set of 
   files in a directory without manual intervention."""

__author__ = "Michael J. Harms"
__date__ = "1/12/06"
__version__ = "0.4"

#*******************************
# USER INPUTS
input_path = 'SS_withH/'
output_path = 'uhbd_calcs/'

# Titration parameters
pH_start = 0
pH_stop = 16
pH_interval = 0.25
ionic_strength = 0.1
dielectric = 20

import initialize
import uhbd
import os
import sys

def main(input_path,output_path,pH_start,pH_stop,pH_interval,ionic_strength,dielectric):
    # FOR EVERY DIRECTORY IN DIR, LOOK FOR FILES
    dir_list = os.listdir(initialize.invocation_path + input_path)
    for dir in dir_list:
            
        # MAKE MAIN OUTPUT DIRECTORY
        print dir
        total_path = initialize.invocation_path + input_path + dir + os.sep
        try:
            os.mkdir(initialize.invocation_path + output_path + dir + os.sep)
        except OSError, value:
            # Don't stop if we are only overwriting existing directory
            if value[0] != 17: 
                print 'File error.'
                print initialize.invocation_path + output_path + dir + os.sep
                print value[0], dir, value[1]
                sys.exit()
            
        # FOR EVERY pdb FILE IN DIR, RUN CALCULATIONS
        file_list = os.listdir(total_path)
        file_list = [x for x in file_list if x[-4:] == '.pdb']
            
        for filename in file_list:
            print filename
            uhbd.fullRun(total_path + os.sep + filename,pH_start,pH_stop,
                         pH_interval,ionic_strength,dielectric)
                
            # Create individual output directory
            X = os.sep
            total_output = initialize.invocation_path + output_path + X + \
                           dir + X + filename[:-4] + X
            try:
                os.mkdir(total_output)
            except OSError, value:
                # Don't stop if we are only overwriting existing directory
                if value[0] != 17:
                    print 'File error.'
                    print value[0], dir, value[1]
                    sys.exit()
        
            # Copy files to directory
            uhbd.copyFinalOutput(total_output)
        
            # Wipe out temporary files
            uhbd.runCleanup()
            
# If the program is invoked from the command line, run the main function
if __name__ == "__main__":
    main(input_path,output_path,pH_start,pH_stop,pH_interval,ionic_strength,dielectric)