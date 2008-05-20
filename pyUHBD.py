#!/usr/bin/env python
"""
pyUHBD.py

Main module for performing finite-difference poission-boltzmann calculations
using uhbd.  Intended to be called from the command line.
"""

__author__ = "Michael J. Harms"

# The options in nonstandard_titr do not have the normal directory structure for
# a titration: they are already in their own directories in every calculation.
NONSTANDARD_TITR = ["protein_dielec","ionic_strength"]

import os, sys, shutil, copy
from uhbd import ParseUhbd, GenerateUhbdInput
from common import ProcessInputFiles, SystemOps, Error

invocation_path = os.getcwd()
pyUHBD_dir = os.path.realpath(os.path.split(__file__)[0])

def setupOverride(calc_param,filename):
    """
    Function that sets up override directory properly
    """

    # Create output directory
    output_dir = "%s_override" % filename[:-4]
    SystemOps.makeDir(output_dir)

    # Read in override file
    f = open(calc_param.override,'r')
    over_file = f.readlines()
    f.close()

    # Make sure that declared pdb file matches pdb file in input file
    index = over_file.index("          NAME of mol 1 file\n") + 1
    pdb_in_file = over_file[index].strip()
    if pdb_in_file != os.path.split(filename)[-1]:
        err = "pdb file on command line (%s) " % os.path.split(filename)[-1]
        err += " does not match pdb file in override file (%s)!" % pdb_in_file
        raise OSError(err)

    # Find parameter files specified in override file
    index = over_file.index("          NAME of charge and radius file\n") + 1
    param_in_file = over_file[index].strip()


    # Try to copy that file into the output directory
    if os.path.isfile(param_in_file):
        calc_param.param_file = calc_in_file
    else:
        # See if paramater file is in the pyUHBD/parameters directory
        default_file = os.path.join(pyUHBD_dir,"parameters",
                                    param_in_file)
        if os.path.isfile(default_file):
            calc_param.param_file = default_file
        else:
            # It cannot be found!
            err = "Unable to locate parameter file %s " % param_in_file
            err += "(specified in %s)." % calc_param.override
            raise OSError(err)

    return output_dir

def indivRun(filename,calc_param):
    """
    Performs a single UHBD run.  If a variable is titrating, the titration is
    run as well.
    """

    # Create fully specified path to filename
    filename = os.path.join(invocation_path,filename)

    if calc_param.titration == None:

        # Create output directory
        if calc_param.override != None:
            output_dir = setupOverride(calc_param,filename)
        else:
            output_dir = [filename[:-4],"D%.1F" % calc_param.protein_dielec,
                          "%.1F" % calc_param.ionic_strength]
            output_dir = os.path.join(*output_dir)
            SystemOps.makeDir(output_dir)

        # Run calculation
        runCore(filename,output_dir,calc_param)

    else:
        titr_var = calc_param.titration[0]
        for t in calc_param.titr_values:

            # Set the calc parameter that is titrating to the correct value
            calc_param.__dict__[titr_var] = t

            # Generate correct output directory name
            if calc_param.titration[0] not in NONSTANDARD_TITR:
                if type(t) == float:
                    titr_dir = "%s_%.2F" % (calc_param.titration[0],t)
                else:
                    titr_dir = "%s_%s" % (calc_param.titration[0],t)
            else:
                titr_dir = ""

            # Create output directory
            output_dir = [filename[:-4],"D%.1F" % calc_param.protein_dielec,
                          "%.1F" % calc_param.ionic_strength,
                          titr_dir]
            output_dir = os.path.join(*output_dir)
            SystemOps.makeDir(output_dir)

            # Run uhbd
            print "Titration %s: %s\n" % (titr_var,t),
            runCore(filename,output_dir,calc_param)


def runCore(filename,output_dir,calc_param):
    """
    The core operations that are done during a uhbd calculation.
    """

    # Copy pdb file to calculation directory and chdir
    shutil.copy(filename,os.path.join(output_dir,"proteinH.pdb"))
    os.chdir(output_dir)

    # Strip down to only ATOM entries, then add dummy remarks at the top and a
    # proper END statement at the end.
    f = open("proteinH.pdb","r")
    pdb = f.readlines()
    f.close()

    pdb = [l for l in pdb if l[0:4] == "ATOM"]
    pdb.insert(0,"%-79s\n%-79s\n" % ("REMARK","REMARK"))
    pdb.append("END")

    g = open("proteinH.pdb","w")
    g.writelines(pdb)
    g.close()

    # Set up input file (either copy manual override or generate automatically).
    if calc_param.override != None:
        shutil.copy(calc_param.override,calc_param.inp_name)
    else:
        GenerateUhbdInput.createDoinp(filename,calc_param)

    # Copy parameter file into calculation directory
    shutil.copy(calc_param.param_file,'.')

    # Run calculation
    calc_param.run_uhbd(calc_param)

    # Delete temporary files
    SystemOps.runCleanup(calc_param)

    # Return to starting directory
    os.chdir(invocation_path)


def createIndivParam(filename,calc_param):
    """
    Generates an instance of calc_param indivdually tailored for the pdb file
    passed in filename.  This instance is returned (and ultimately passed to
    GenerateInputFile by pyUHBD).
    """

    # Make a copy of the instance lest we overwrite global parameters!
    indiv_calc_param = copy.copy(calc_param)

    # Read in pdb file
    f = open(filename,'r')
    pdb = f.readlines()
    f.close()

    # Find the first and last residues in the pdb file
    residues = [int(line[22:26]) for line in pdb if line[0:4] == "ATOM"]
    indiv_calc_param.first_residues = residues[0] - 1
    indiv_calc_param.last_residues = residues[-1] + 1

    # Set up his, cys, and grids for this pdb file
    indiv_calc_param.his_tautomers = \
                    ProcessInputFiles.processHis(pdb,
                                                 indiv_calc_param.his_tautomers)
    indiv_calc_param.cys_titrate = \
                    ProcessInputFiles.processCys(pdb,
                                                 indiv_calc_param.cys_titrate)
    indiv_calc_param.grid = \
                    ProcessInputFiles.processGrid(pdb,
                                                  indiv_calc_param.grid)
    indiv_calc_param.pdb_file = os.path.split(filename)[-1]
    indiv_calc_param.keep_files.append(indiv_calc_param.pdb_file)

    return indiv_calc_param


def main():
    """
    Perform fdpb calculations on a set of pdb files.
    """

    calc_param, file_list = ParseUhbd.main()

    # Perform calculation on all files in file_list
    for file in file_list:
        print "Calculation on %s" % file
        indiv_calc_param = createIndivParam(file,calc_param)
        indivRun(file,indiv_calc_param)

# If pyUHBD is invoked from the command line, run main
if __name__ == "__main__":
    main()
