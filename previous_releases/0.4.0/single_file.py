"""single_file.py (v 0.4).  A script that runs a UHBD calculation on a single
file."""

__author__ = "Michael J. Harms"
__date__ = "1/13/06"
__version__ = "0.4"

# USER INPUTS
pH_start = 0
pH_stop = 16
pH_interval = 0.25
ionic_strength = 0.1
dielectric = 20

import initialize
import uhbd
import os
import sys
import argParser


def main(filename,output_path,pH_start,pH_stop,pH_interval,ionic_strength,dielectric):
    
    filename = initialize.invocation_path + filename
    
    # Create output directory (if invoked from command line)
    if __name__ == "__main__":
        try:
            os.mkdir(initialize.invocation_path + output_path)
        except OSError, value:
            # Don't stop if we are only overwriting existing directory
            if value[0] != 17: 
                print 'File error.'
                print value[0], output_path, value[1]
                sys.exit()
                
    # Perform UHBD run
    uhbd.fullRun(filename,pH_start,pH_stop,pH_interval,ionic_strength,dielectric)
    uhbd.copyFinalOutput(initialize.invocation_path + output_path + os.sep)
    uhbd.runCleanup()
    
# If this is invoked from the command line, run the main function
if __name__ == "__main__":
    # Grab command line options
    required, optional = argParser.main(sys.argv,["pdb_file","output_dir"],
                                        ["inpfile","outdir"],
                                        ["dielectric","ionic_strength"])
    main(required["pdb_file"],required["output_dir"],pH_start,pH_stop,pH_interval,
         optional.ionic_strength,optional.dielectric)

