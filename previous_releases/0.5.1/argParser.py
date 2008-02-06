"""
argParser.py:
Parses arguments from a command line.
    Requires four arguments: argv,required_arg,required_arg_type,optional_arg
        argv is a direct pass of sys.argv
        required_arg    (list)  arguments required for calling script execution.
    FINISH ME!
"""

"""
Version noes:
0.1: 060113

0.1.1: 060310
Changed hybrid default pH values from 0,16 to -5,20 to assure convergence of pKa
values.

0.1.2: 060519
Made the output directory an optional rather than a required argument.
"""

#*****************************************************************************#
#                            INITALIZE MODULE                                 #
#*****************************************************************************#

__author__ = "Michael J. Harms"
__version__ = "0.1.2"
__date__ = "060519"

from optparse import OptionParser
import sys
import os
import copy

# SEE BOTTOM OF SCRIPT TO DEFINE OPTIONS THAT THE SCRIPT "KNOWS" HOW TO PARSE

#*****************************************************************************#
#                          FUNCTION DEFINITIONS                               #
#*****************************************************************************#

def addDielectric(default_dielectric=20):
    """Add dielectric constant to list of possible arguments."""
    
    parser.add_option("-D","--dielectric",action="store",type="float",
                  dest="dielectric",
                  help="Dielectric constant for UHBD calculations (default=20)",
                  default=default_dielectric)

def addIonicStrength(default_ionic_strength=0.1):
    """Add ionic strength to list of possible arguments."""
    
    parser.add_option("-I","--ionic-strength",action="store",type="float",
                  dest="ionic_strength",
                  help="Ionic strength for UHBD calculations (default=0.1 M)",
                  default=default_ionic_strength)

def addPHTitration(default_pH_titration=(-5,20,0.25)):
    """Add pH titration to list of possible arguments."""
    
    parser.add_option("-P","--pH-titration",action="store",type="float",
                      dest="pHtitr",nargs=3,
                      help="pH titration for UHBD calculations. PHTITR is a \
                      set of three values PH_START PH_STOP PH_INTERVAL. \
                      (Default -5 20 0.25)",
                      default=default_pH_titration)

def addOutDir(default_out_dir="uhbd_calcs"):
    """Add output dir to list of possible arguments."""
    
    parser.add_option("-d","--directory",action="store",type="str",
                      dest="out_dir",nargs=1,
                      help="Output directory for UHBD calculations. \
                      (Default uhbd_calcs)",
                      default=default_out_dir)

def grabRequiredArgs(passed_required_arg,required_arg,required_arg_type):
    """
    Checks validity of required arguments (i.e. inputfile and output_dir).
    Arguments:
        passed_required_args    (list)  set of arguments on the command line
                                        that are not a part of an "option"
        required_arg            (list)  list of string identifiers for required
                                        arguments.  
        required_arg_type       (list)  list of strings that identify argument
                                        types.  Types are'inpfile', 'outfile',
                                        or 'outdir', telling script whether to
                                        check for file existance, create new
                                        file, or create a new output directory.
    Returns:
        required_arg_values     (dict)  Dictionary of required_arg identifiers
                                        and command line values.
    """
    
    # Check for correct number of arguments
    if len(passed_required_arg) - 1 < len(required_arg):
        print "Missing arguments(s)"
        print "Try --help for options."
        sys.exit(1)
    
    # Pull command line values and place in dictionary with correct argument
    # identifier
    required_arg_values = {}
    for i in range(0,len(required_arg)):
        required_arg_values.update([(required_arg[i],passed_required_arg[i+1])])
        
    # Do a few sanity checks on required arguments (using required_arg_type)
    for index, arg in enumerate(required_arg):
        # Check for input file existance
        if required_arg_type[index] == 'inpfile':
            try:
                open(required_arg_values[arg],'r')
            except IOError:
                print "File '" + required_arg_values[arg] + "' not readable!"
                sys.exit(2)
        
        # Prompt before overwriting output files
        if required_arg_type[index] == 'outfile':
            try:
                open(required_arg_values[arg],'r')
            except IOError:
                continue
            decision = raw_input("Warning!  File '" + required_arg_values[arg] \
                                 + "' already exists! overwrite (y/n)? ")
            if decision[0] == 'Y' or decision[1] == 'y':
                os.remove(required_arg_values[arg])
            else:
                sys.exit()
            
        
    # If there are any more arguments on the command line, report them and
    # ignore them.
    if len(passed_required_arg) - 1 > len(required_arg):
        print "Trailing arguments (not evaluated):"
        for trailer in passed_required_arg[len(required_arg):]:
            print trailer
            
    return required_arg_values

def checkOptionalArgs(passed_optional_arg):

    
    # Check for directory existance
    dir = passed_optional_arg.out_dir
    try:
        os.listdir(dir)
    except OSError:
        if dir == "uhbd_calcs":
            os.mkdir(dir)
            return 0
        decision = raw_input("Directory %s does not exist. " % dir + \
                             "Create it (y/n)? ")
        if decision[0] == 'Y' or decision[0] == 'y':
            os.mkdir(dir)
        else:
            sys.exit()

    return 0
    

def main(argv,required_arg,required_arg_type,optional_arg):
    """Takes a command line (passed from other module) and parse options (also
    passed) and returns proper values (either specified by user or default.
    """
    
    # add optional_arguments to the parser
    for option in optional_arg:
        parse_option_dictionary[option]()
    
    # parse the command line
    passed_optional_arg, passed_required_arg = parser.parse_args(argv)
    
    required_arg_values = grabRequiredArgs(passed_required_arg,required_arg,
                                           required_arg_type)

    checkOptionalArgs(passed_optional_arg)

    return required_arg_values, passed_optional_arg


#*****************************************************************************#
#              DEFINE OPTIONS SCRIPT IS ABLE TO PARSE                         #
#*****************************************************************************#

global parser
parser = OptionParser()
parse_option_dictionary = {"ionic_strength":addIonicStrength,
                           "dielectric":addDielectric,
                           "pHtitr":addPHTitration,
                           "out_dir":addOutDir}


# REMOVE THIS, WON'T BE USED IN PRODUCTION!  WE DON'T WANT TO BE ABLE TO CALL
# THIS FROM COMMAND LINE
#if __name__ == "__main__":
#    print main(sys.argv,["file1","file2"],["inpfile","outdir"],["ionic_strength","dielectric","pHtitr"])





