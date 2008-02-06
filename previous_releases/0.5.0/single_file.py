"""
single_file.py:

A script that runs a UHBD calculation on a single file.

"""

"""
Version notes:
0.4:    060113

0.4.1:  060403
    Hokiness fix.  Changed from some_path = x + os.sep + y to os.path.join(x,y)
"""

__author__ = "Michael J. Harms"
__date__ = "060403"
__version__ = "0.4.1"


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
    
    filename = os.path.join(initialize.invocation_path,filename)
    
    # Create output directory (if invoked from command line)
    if __name__ == "__main__":
        try:
            os.mkdir(os.path.join(initialize.invocation_path,output_path))
        except OSError, value:
            # Don't stop if we are only overwriting existing directory
            if value[0] != 17: 
                print 'File error.'
                print value[0], output_path, value[1]
                sys.exit()
                
    # Perform UHBD run
    uhbd.main(filename,pH_start,pH_stop,pH_interval,ionic_strength,dielectric)
    uhbd.copyFinalOutput(os.path.join(initialize.invocation_path,output_path))
    uhbd.runCleanup()
    
# If this is invoked from the command line, run the main function
if __name__ == "__main__":
    # Grab command line options
    required, optional = argParser.main(sys.argv,["pdb_file","output_dir"],
                                        ["inpfile","outdir"],
                                        ["dielectric","ionic_strength","pHtitr"])
    main(required["pdb_file"],required["output_dir"],optional.pHtitr[0],
         optional.pHtitr[1],optional.pHtitr[2],optional.ionic_strength,
         optional.dielectric)

