"""
pyUHBD.py

The main script that is executed by a pyUHBD user. 
"""

__author__ = "Michael J. Harms"
__date__ = "060519"
__version__ = "0.6.1"

__usage__ = \
"""
pyUHBD runs UHBD in three different modes.  One of these must be specified.

single: runs UHBD on a single file.
    pyUHBD.py single pdb_file [optional arguments]

multiple: runs UHBD on a directory
    pyUHBD.py multiple directory [optional arguments]

salts: runs UHBD on a single file at a set of salts.
    pyUHBD.py salts pdb_file salts_file [optional arguments]

dielec: runs UHBD on a single file for a set of protein dielectric constants.
    pyUHBD.py dielec pdb_file dielectric_file [optional arguments]

pyUHBD.py mode --help shows all options for that mode.
"""


import os, sys
import __init__, ArgParser, FileOps, UhbdInterface

def indivRun(filename,output_path,pH_start,pH_stop,pH_interval,ionic_strength,
    dielectric):
    """
    Performs a single UHBD run.
    """

    filename = os.path.join(__init__.invocation_path,filename)
    
    # Create output directory 
    indiv_out_dir = os.path.join(__init__.invocation_path,output_path)
    FileOps.makeDir(indiv_out_dir)
                
    # Perform UHBD run
    UhbdInterface.setupInp(filename,ionic_strength,dielectric)
    UhbdInterface.main(filename,pH_start,pH_stop,pH_interval,ionic_strength,
        dielectric)
    FileOps.copyFinalOutput(indiv_out_dir)
    FileOps.runCleanup()


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

def runMultiple(arg):
    """
    Runs UHBD calculation on set of pdb files.
    """

    # Parse the command line arguments
    multiple = ArgParser.modeClass("multiple",["pdb_dir"],["inpdir"],
        ["dielectric", "ionic_strength","pHtitr","out_dir"])
    multiple.parseArg(arg)   
 
    input_dir = multiple.required["pdb_dir"]
    output_path = multiple.optional.out_dir
    pH_start = multiple.optional.pHtitr[0]
    pH_stop = multiple.optional.pHtitr[1]
    pH_interval = multiple.optional.pHtitr[2]
    ionic_strength = multiple.optional.ionic_strength
    dielectric = multiple.optional.dielectric 

    # Grab pdb files from specified directory.
    pdb_list = os.listdir(input_dir) 
    pdb_list = [f for f in pdb_list if f[-4:] == ".pdb"]
    pdb_list.sort()

    base_path = os.path.join(__init__.invocation_path,input_dir,output_path)    
    indiv_file_paths = [os.path.join(base_path,d[:-4]) for d in pdb_list]

    FileOps.makeDir(base_path)
    dielec_paths = []
    for path in indiv_file_paths:
        FileOps.makeDir(path)
        dielec_paths.append(os.path.join(path,"D%.1F" % dielectric))
        FileOps.makeDir(dielec_paths[-1])

    for pdb_index, pdb in enumerate(pdb_list):
        print "PDB FILE: %s" % pdb
        output = os.path.join(dielec_paths[pdb_index],
                                   "%.1F" % ionic_strength)
        
        # Create output directory
        FileOps.makeDir(output)

        # Run UHBD at this specific salt concentration
        indivRun(pdb,output,pH_start,pH_stop,pH_interval,ionic_strength,
                 dielectric)

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

    base_path = os.path.join(__init__.invocation_path,output_path)    
    dielec_path = os.path.join(base_path,"D%.1F" % dielectric)
    FileOps.makeDir(dielec_path)
    
    for salt in salts:
        print "Ionic strength: %4.2F" % salt
        salt_output = os.path.join(dielec_path,"%.1F" % salt)
        
        # Create output directory
        FileOps.makeDir(salt_output)

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

    base_path = os.path.join(__init__.invocation_path,output_path)

    for dielectric in dielectric_constants:
        print "dielectric constant: %4.2F" % dielectric 
        
        dielec_path = os.path.join(base_path,"D%.1F" % dielectric)
        FileOps.makeDir(dielec_path)

        dielec_output = os.path.join(dielec_path,"%.1F" % salt)
        FileOps.makeDir(dielec_output)
        
        indivRun(filename,dielec_output,pH_start,pH_stop,pH_interval,salt,
                 dielectric)


# Dictionary of possible modes
possible_modes = {"single":runSingle,"multiple":runMultiple,"salts":runSalts,
                  "dielec":runDielec}

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




