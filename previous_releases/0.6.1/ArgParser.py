"""
argParser.py:
Parses arguments from a command line for pyUHBD.

Uses class modeClass to define how arguments should be parsed.  An instance of
modeClass is created for each possible mode defined in pyUHBD.py.  See modeClass
doc string for more information.

Version notes:
0.1: 060113

0.1.1: 060310
Changed hybrid default pH values from 0,16 to -5,20 to assure convergence of pKa
values.

0.2.0: 060519
Made the output directory an optional rather than a required argument.

Cleaned up help/usage strings.

Modified for pyUHBD 0.6.0 "mode" functionality.  This involved defining class
modeClass and making main (now parseArg) and sanity checking functions methods
of the class.

"""

__author__ = "Michael J. Harms"
__version__ = "0.2.0"
__date__ = "060519"


import os, sys, copy
from optparse import OptionParser

global parser, parse_option_dictionary

#*****************************************************************************#
#                            DEFINE MAIN CLASS                                #
#*****************************************************************************#

class modeClass:
    """
    Instance of modeClass parses command line in way particular to mode.  The
    parsed command line is then stored as two attributes: required and optional.

    "Input" Attributes (defined in pyUHBD.py):
        name                    (str)   string identifier for this mode (for
                                        help files, etc.)
        required_arg_name       (list)  list of string identifiers for required
                                        arguments.  
        required_arg_type       (list)  list of strings that identify argument
                                        types.  Types are 'inpfile' or 
                                        'outfile', telling script whether to
                                        check for file existance or to try to
                                        create a new file.
        optional_arg            (list)  list of keys to parse_option_dictionary
                                        that allows initialization of parser
                                        with options specific to this mode.

    "Output" Attributes (used by pyUHBD.py to run UHBD):
        required                (dict)  Dictionary of required arguments keyed
                                        to strings in required_arg_name.
        optional                (list)  Values instance containing values of
                                        optional arguments.

    """

    def __init__(self,name,required_arg_name,required_arg_type,optional_arg):
        """
        Initializes instace of modeClass, defining what arguments it should look
        to parse (both required and optional).
        """

        self.name = name
        self.required_arg_name = required_arg_name
        self.required_arg_type = required_arg_type
        self.optional_arg = optional_arg

    def parseArg(self,argv):
        """
        Parses the command line.  Defines attributes .required and .optional
        using checkRequiredArgs and checkOptionalArgs.
        """

        # Update parser usage string for this mode.
        req_arg_str = len(self.required_arg_name)*"%s " % \
            tuple(self.required_arg_name)
        parser.usage = parser.usage[0:5] + " %s %s[options]" %  \
            (self.name,req_arg_str)
    
        # add optional_arguments to the parser
        for option in self.optional_arg:
            parse_option_dictionary[option]()
    
        # parse the command line
        self.passed_optional_arg, self.passed_required_arg = \
            parser.parse_args(argv)
    
        # Process required arguments (define .required)
        self.checkRequiredArgs()

        # Check optional argument sanity (define.optional)
        self.checkOptionalArgs()



    def checkRequiredArgs(self):
        """
        Checks validity of required arguments, defining .required as it does so.
        """
    
        # Check for correct number of arguments
        if len(self.passed_required_arg) - 1 < len(self.required_arg_name):
            print "Missing arguments(s)"
            parser.print_help()
            sys.exit(1)
    
        # Pull command line values and place in dictionary keyed by argument 
        # name
        self.required = {}
        for i in range(0,len(self.required_arg_name)):
            self.required.update([(self.required_arg_name[i],
                                            self.passed_required_arg[i+1])])
        
        # Do a few sanity checks on required arguments (using required_arg_type)
        for index, arg in enumerate(self.required_arg_name):
            # Check for input file existance
            if self.required_arg_type[index] == 'inpfile':
                try:
                    open(self.required[arg],'r')
                except IOError:
                    print "File '%s' not readable!" %self.required[arg]
                    sys.exit(2)
        
            # Prompt before overwriting output files
            if self.required_arg_type[index] == 'outfile':
                try:
                    open(self.required[arg],'r')
                except IOError:
                    continue
                decision = raw_input("Warning!  File '%s' already exists! \
                                     Overwrite (y/n)? " %  \
                                     self.required[arg])
                if decision[0] == 'Y' or decision[1] == 'y':
                    os.remove(self.required[arg])
                else:
                    sys.exit()
            
        # If there are any more arguments on the command line, report them and
        # ignore them.
        if len(self.passed_required_arg) - 1 > len(self.required_arg_name):
            print "Trailing arguments (not evaluated):"
            for extra in self.passed_required_arg[len(self.required_arg_name):]:
                print extra
            
        return 0


    def checkOptionalArgs(self):
        """
        Does sanity checking on optional arguments, defining .optional.
        """
    
        # Check for output directory existance.  If it does not exist, ask the 
        # user if they want to create directory.
        dir = self.passed_optional_arg.out_dir
        try:
            os.listdir(dir)
        except OSError:
            if dir == "uhbd_calcs":
                os.mkdir(dir)
                self.optional = self.passed_optional_arg
                return 0
            decision = raw_input("Directory %s does not exist. Create it \
                                 (y/n)? " % dir)
            if decision[0] == 'Y' or decision[0] == 'y':
                os.mkdir(dir)
            else:
                sys.exit()

        self.optional = self.passed_optional_arg
        return 0


#*****************************************************************************#
#              DEFINE parser AND parse_option_dictionary                      #
#*****************************************************************************#

def addDielectric(default_dielectric=20):
    """
    Add dielectric constant to list of possible arguments.
    """
    
    parser.add_option("-D","--dielectric",action="store",type="float",
                  dest="dielectric",
                  help="Dielectric constant for UHBD calculations (default=20)",
                  default=default_dielectric)

def addIonicStrength(default_ionic_strength=100):
    """
    Add ionic strength to list of possible arguments.
    """
    
    parser.add_option("-I","--ionic-strength",action="store",type="float",
                  dest="ionic_strength",
                  help="Ionic strength for UHBD calculations (default=100 mM)",
                  default=default_ionic_strength)

def addPHTitration(default_pH_titration=(-5,20,0.25)):
    """
    Add pH titration to list of possible arguments.
    """
    
    parser.add_option("-P","--pH-titration",action="store",type="float",
                      dest="pHtitr",nargs=3,
                      help="pH titration for UHBD calculations. PHTITR is a \
                      set of three values PH_START PH_STOP PH_INTERVAL. \
                      (Default -5 20 0.25)",
                      default=default_pH_titration)

def addOutDir(default_out_dir="uhbd_calcs"):
    """
    Add output dir to list of possible arguments.
    """
    
    parser.add_option("-d","--directory",action="store",type="str",
                      dest="out_dir",nargs=1,
                      help="Output directory for UHBD calculations. \
                      (Default uhbd_calcs)",
                      default=default_out_dir)


parser = OptionParser()
parse_option_dictionary = {"ionic_strength":addIonicStrength,
                           "dielectric":addDielectric,
                           "pHtitr":addPHTitration,
                           "out_dir":addOutDir}

