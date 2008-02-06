"""
pyUHBD.py

The main script that is executed by a pyUHBD user. 
"""

__author__ = "Michael J. Harms"
__date__ = "060519"
__version__ = "0.6.0"

__usage__ = \
"""
pyUHBD runs UHBD in three different modes.  One of these must be specified.

single: runs UHBD on a single file.
    pyUHBD.py single pdb_file [optional arguments]

salts: runs UHBD on a single file at a set of salts.
    pyUHBD.py salts pdb_file salts_file [optional arguments]

dielec: runs UHBD on a single file for a set of protein dielectric constants.
    pyUHBD.py dielec pdb_file dielectric_file [optional arguments]

pyUHBD.py mode --help shows all options for that mode.
"""


import os, sys
import __init__, ArgParser, UhbdInterface

def indivRun(filename,output_path,pH_start,pH_stop,pH_interval,ionic_strength,
    dielectric):
    """
    Performs a single UHBD run.
    """

    filename = os.path.join(__init__.invocation_path,filename)
    
    # Create output directory (if invoked from command line)
    if __name__ == "__main__":
        try:
            os.mkdir(os.path.join(__init__.invocation_path,output_path))
        except OSError, value:
            # Don't stop if we are only overwriting existing directory
            if value[0] != 17: 
                print 'File error.'
                print value[0], output_path, value[1]
                sys.exit()
                
    # Perform UHBD run
    UhbdInterface.main(filename,pH_start,pH_stop,pH_interval,ionic_strength,
        dielectric)
    UhbdInterface.copyFinalOutput(os.path.join(__init__.invocation_path,
        output_path))
    UhbdInterface.runCleanup()


def runSingle(arg):
    """
    Runs UHBD calculation on a single file.
    """
    
    single = ArgParser.modeClass("single",["pdb_file"],["inpfile"],
        ["dielectric", "ionic_strength","pHtitr","out_dir"])
    single.parseArg(arg)

    indivRun(single.required["pdb_file"],single.optional.out_dir,
        single.optional.pHtitr[0],single.optional.pHtitr[1],
        single.optional.pHtitr[2],single.optional.ionic_strength,
        single.optional.dielectric)


def runSalts(arg):
    """
    Runs UHBD calculation on set of salts in salts_file.
    """

    # Parse the command line arguments
    salts = ArgParser.modeClass("salts",["pdb_file","salt_file"],
        ["inpfile","inpfile"],["dielectric","pHtitr","out_dir"])
    salts.parseArg(arg)
    
    filename = salts.required["pdb_file"]
    salts_file = salts.required["salt_file"]
    output_path = salts.optional.out_dir
    pH_start = salts.optional.pHtitr[0]
    pH_stop = salts.optional.pHtitr[1]
    pH_interval = salts.optional.pHtitr[2]
    dielectric = salts.optional.dielectric 

    # Execute the indivRun function for every salt in salts_file
    f = open(salts_file)
    salts = [float(salt) for salt in f.readlines()]
    f.close()
    
    for salt in salts:
        print "Ionic strength: %4.2F" % salt
        salt_output = os.path.join(output_path,"%.1F" % salt)
        
        # Create output directory
        try:
            os.mkdir(os.path.join(__init__.invocation_path,salt_output))
        except OSError, value:
            # Don't stop if we are only overwriting existing directory
            if value[0] != 17: 
                print 'File error.'
                print value[0], os.path.join(__init__.invocation_path,
                                             salt_output), value[1]
                sys.exit()

        # Run UHBD at this specific salt concentration
        indivRun(filename,salt_output,pH_start,pH_stop,pH_interval,salt,
                 dielectric)

def runDielec(arg):
    """
    Runs UHBD calculation with a set of dielectric constants in dielc_file.
    """

    # Parse the command line arguments
    dielec = ArgParser.modeClass("dielec",["pdb_file","dielec_file"],
        ["inpfile","inpfile"],["ionic_strength","pHtitr","out_dir"])
    dielec.parseArg(arg)

    filename = dielec.required["pdb_file"]
    dielec_file = dielec.required["dielec_file"]
    output_path = dielec.optional.out_dir
    pH_start = dielec.optional.pHtitr[0]
    pH_stop = dielec.optional.pHtitr[1]
    pH_interval = dielec.optional.pHtitr[2]
    salt = dielec.optional.ionic_strength

    f = open(dielec_file)
    dielectric_constants = [float(d) for d in f.readlines()]
    f.close()
    
    for dielectric in dielectric_constants:
        print "dielectric constant: %4.2F" % dielectric 
        dielec_output = os.path.join(output_path,"%.1F" % dielectric)
        
        # Create output directory
        try:
            os.mkdir(os.path.join(__init__.invocation_path,dielec_output))
        except OSError, value:
            # Don't stop if we are only overwriting existing directory
            if value[0] != 17: 
                print 'File error.'
                print value[0], os.path.join(__init__.invocation_path,
                                             dielec_output), value[1]
                sys.exit()
    
        indivRun(filename,dielec_output,pH_start,pH_stop,pH_interval,salt,
                 dielectric)



# Dictionary of possible modes
possible_modes = {"single":runSingle,"salts":runSalts,"dielec":runDielec}

# Make sure a proper mode is specified.  If it is not, raise exception and exit.
try:
    mode_key = sys.argv.pop(1)
    if mode_key not in possible_modes.keys():
        raise KeyError
except IndexError:
    print "No mode specified!"
    print __usage__
    sys.exit()
except KeyError:
    print "Invalid mode '%s' specified!" % mode_key
    print __usage__
    sys.exit()

# Execute mode function
possible_modes[mode_key](sys.argv)




