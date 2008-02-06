"""
salts.py:

A script that runs a UHBD calculation on a single pdb file at multiple salt
concentrations.
"""

"""
Version notes:
0.4:    060113

0.4.1:  060403
    Hokiness fix.  Changed from some_path = x + os.sep + y to os.path.join(x,y)
"""

__author__ = "Michael J. Harms"
__date__ = "060403"
__version__ = "0.4"


#*****************************************************************************#
#                            INITALIZE MODULE                                 #
#*****************************************************************************#

import initialize
import single_file
import os
import sys
import argParser


#*****************************************************************************#
#                          FUNCTION DEFINITIONS                               #
#*****************************************************************************#

def main(filename,salts_file,output_path,pH_start,pH_stop,
         pH_interval,dielectric):

    f = open(salts_file)
    salts = [float(salt) for salt in f.readlines()]
    f.close()
    
    for salt in salts:
        print salt
        salt_output = os.path.join(output_path,"%.1F" % salt)
        
        # Create output directory
        try:
            os.mkdir(os.path.join(initialize.invocation_path,salt_output))
        except OSError, value:
            # Don't stop if we are only overwriting existing directory
            if value[0] != 17: 
                print 'File error.'
                print value[0], os.path.join(initialize.invocation_path,
                                             salt_output), value[1]
                sys.exit()
    
        single_file.main(filename,salt_output,pH_start,pH_stop,pH_interval,salt,
                         dielectric)


# If this is the script that is executed, then run the main function
if __name__ == "__main__":
    # Parse the command line arguments
    required, optional = argParser.main(sys.argv,
                                        ["pdb_file","salt_file","output_dir"],
                                        ["inpfile","inpfile","outdir"],
                                        ["dielectric","pHtitr"])
    # Execute the salts script
    main(required["pdb_file"],required["salt_file"],required["output_dir"],
         pH_start=optional.pHtitr[0],pH_stop=optional.pHtitr[1],
         pH_interval=optional.pHtitr[2],dielectric=optional.dielectric)

