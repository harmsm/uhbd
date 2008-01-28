"""
ParseUhbd.py

Interfaces with common ArgParser and pyUHBD to parse command line.
"""

__author__ = "Michael J. Harms"
__usage__ = "[options] arg (arg is pdb file OR directory with pdb files)"
__version__ ="1.00"
description = \
"""
A GNU/Posix-style interface to UHBD that allows the user to perform
Finite-Difference Poisson-Boltzmann calculations.  Most calculation parameters
can be specified from the command line.  See the README file in the pyUHBD
directory for further help.
"""

# Locked settings are those for which I have no code to process input/output.
# They are defined but cannot be changed. I anticipate having to add them to the
# option parser in the future.
LOCKED_SETTINGS = {"iterations":300,"added_residues":0,"change_acid":"n",
                   "num_chains":1}

# Files to keep for clean up
SINGLE_KEEPFILES = ['hybrid.out','pkaS-doinp.inp','pkaS-potentials',
                    'pkaS-sitesinpr.pdb','titraa.pdb']
FULL_KEEPFILES =   ['hybrid.out','doinp.inp','pkaF-potentials']

# In a perfect world, the following global options would be attributes of each
# option in parser. This would involve some large, non-intuitive modifications
# to a OptionParser subclass. For now, at least, I have opted for the simpler
# solution of setting some global variables.

# Options that the user cannot titrate
NOT_TITRATABLE = ["full","keep_temp","titration","ph_param","override"]

# Options compatible with the --override setting; everything else is
# incompatible
OVERRIDE_COMPATIBLE = ["keep","ph_param","full","override"]


# ---------- Initialize module --------------------


# Load pyUHBD modules
import os
from common import SystemOps, ArgParser
from uhbd import UhbdInterface

default_location = os.path.split(__file__)[0]
default_location = os.path.split(default_location)[0]
default_location = os.path.realpath(os.path.join(default_location,"parameters"))

def main():
    """
    Populate parser, parse command line, and generate an instance of Parameters
    to hold calculation parameters.
    """

    # ---------- Populate the parser --------------------

    # Initialize parser
    usage = "%prog " + __usage__
    version = "%prog " + "%s" % __version__
    parser = ArgParser.OptionParser(option_class=ArgParser.SuperOption,
                                    usage=usage,version=version,
                                    description=description)

    # Boolean options (not available for titration)
    parser.add_option("-f","--full",action="store_true",default=False,
                      help="Full-site calculation [default single-site]")
    parser.add_option("-k","--keep-temp",action="store_true",default=False,
                      help="Delete temporary files [default %default]")

    # Calculation options (value typed on command line)
    parser.add_option("-T","--temperature",action="store",type="float",
                      default=298.0,
                      help="Temperature of calculation [default %default]")
    parser.add_option("-p","--protein-dielec",action="store",type="float",
                      default=20.,
                      help="Protein dielectric constant [default %default]")
    parser.add_option("-w","--solvent-dielec",action="store",type="float",
                      default=78.5,
                      help="Solvent dielectric constant [default %default]")
    parser.add_option("-i","--ionic-strength",action="store",type="float",
                      default=100.0,
                      help="Ionic strength [default %default]")
    parser.add_option("-r","--ionic-radius",action="store",type="float",
                      default=2.0,
                      help="Radius of ions [default %default]")
    parser.add_option("-m","--map-sphere",action="store",type="float",
                      default=1.4,
                      help="Radius of sphere used for map [default %default]")
    parser.add_option("-s","--map-sample",action="store",type="int",
                      default=500,
                      help="Number of samples used for map [default %default]")
    pH_help = "pH titration parameters (3 values) [default %default]"
    parser.add_option("-q","--ph-param",action="store",type="float",nargs=3,
                      default=(-5.0,20.0,0.25),
                      help=pH_help)

    # Options requiring input files
    parser.add_option("-a","--param-file",action="store",type="file",
                      default=os.path.join(default_location,"pkaS.dat"),
                      help="Parameter file [default %default]")
    parser.add_option("-e","--cys-titrate",action="store",type="file",
                      help="File containing list of titrating cysteines " +
                      "[default automatic]")
    parser.add_option("-H","--his-tautomers",action="store",type="file",
                      help="File containing list of his tautomers " +
                      "[default automatic]")
    parser.add_option("-g","--grid",action="store",type="file",
                      help="File containing list grids to use " +
                      "[default automatic]")
    parser.add_option("-o","--override",action="store",type="file",
                      help="Use user-specified doinp file [default None]")

    # Titration!
    titr_help = "Perform titration of arbitrary option (i.e. protein_dielec, "
    titr_help += "temperature, map_sphere, etc.) using values in a file. "
    titr_help += "TITRATION must be two arguments: the titrating option and a "
    titr_help += "file containing values for that option.  Thus, TITRATION "
    titr_help += "would be protein_dielec dielectrics.txt to titrate along "
    titr_help += "protein dielectric constant."
    parser.add_option("-t","--titration",action="store",type="string",nargs=2,
                      help=titr_help)


    # ---------- Parse arguments --------------------

    options, args = parser.parse_args()

    # Generate list of pdb files on which to perform calculations, doing some
    # error checking along the way
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    else:
        if os.path.isfile(args[0]):
            file_list = [args[0]]
        elif os.path.isdir(args[0]):
            dir = args[0]
            file_list = os.listdir(dir)
            file_list = [f for f in file_list if f[-4:] == ".pdb"]
            file_list = [os.path.join(dir,f) for f in file_list]
            if len(file_list) == 0:
                parser.error("%s does not contain any pdb files!" % dir)
            file_list.sort()
        else:
            parser.error("%s is not a pdb file or directory!" % args[0])

    # ---------- Check for incompatible options --------------------

    # Verify that the user specifies a proper parameter file if they are doing
    # full calculations.
    if options.full and parser.defaults['param_file'] == options.param_file:
        if not options.override:
            err = "--full is specified with the default parameter file!  The "
            err += "default file is for single-site calculations only. "
            err += "Specify a different parameter file using --param_file."
            parser.error(err)

    # Make sure that override is not placed with incompatible options
    if options.override != None:
        option_keys = options.__dict__.keys()
        option_keys = [k for k in option_keys if k not in OVERRIDE_COMPATIBLE]
        option_check = [options.__dict__[k] == parser.defaults[k]
                        for k in option_keys]

        if False in option_check:
            err = ["Some options incompatible with --override:\n"]
            err.extend(["  --%s\n" % option_keys[i].replace("_","-")
                       for i in range(len(option_keys)) if not option_check[i]])
            err = "".join(err)
            parser.error(err)



    # ---------- Set up global options --------------------

    # load optparse options into parameters class
    calc_param = ArgParser.Parameters(options)

    # Define some globalsettings depending on full/single calculation
    calc_param.__dict__.update([("inp_name",""),("keep_files",[]),
                                ("run_uhbd","")])
    if calc_param.full:
        calc_param.inp_name = "doinp.inp"
        calc_param.keep_files = FULL_KEEPFILES
        calc_param.run_uhbd = UhbdInterface.runFullCalculation
        calc_param.calc_type = "full"
    else:
        calc_param.inp_name = "pkaS-doinp.inp"
        calc_param.keep_files = SINGLE_KEEPFILES
        calc_param.run_uhbd = UhbdInterface.runSingleCalculation
        calc_param.calc_type = "single"

    # append the parameter file to the list to keep
    calc_param.keep_files.append(os.path.split(calc_param.param_file)[-1])

    # Set settings in LOCKED_SETTINGS to their locked values
    for d in LOCKED_SETTINGS.keys():
        calc_param.__dict__.update([(d,LOCKED_SETTINGS[d])])


    # ---------- Deal specifically with titration --------------------

    # If the user decides to titrate an option:
    if options.titration != None:

        # Make list of available titration
        available_titrations = options.__dict__.keys()
        available_titrations = [t for t in available_titrations
                                if t not in NOT_TITRATABLE]

        # Make sure that the option is titratable
        if options.titration[0] not in available_titrations:
            msg = "%s cannot be titrated. " % options.titration[0]
            msg = msg + "Available options are:\n"
            msg = msg + "".join(["   %s\n" % t for t in available_titrations])

            parser.error(msg)

        # Read in titration file
        titr_lines = SystemOps.readFile(options.titration[1])
        if len(titr_lines) <= 0:
            parser.error("%s is an empty file!" % options.titration[1])

        # Determine type of titrating value
        option_type = type(options.__dict__[options.titration[0]])

        # Create list of titration values of proper type
        titr_values = []
        for line in titr_lines:
            titr_values.extend(line.split())
        titr_values = [option_type(v) for v in titr_values]
        calc_param.__dict__.update([('titr_values',titr_values)])

    return calc_param, file_list
