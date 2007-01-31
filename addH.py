#!/usr/bin/env python
"""
addH.py

Adds hydrogens to a pdb file as first step in a UHBD finite difference
calculation.  Meant to be be executed from the command line.
"""

__author__ = "Michael J. Harms"

from copy import copy
import os
from charmm import ParseCharmm, GenerateCharmmInput, CharmmInterface
from common import ProcessInputFiles, SystemOps

bin_path = SystemOps.checkEnvironVariable("CHARMM")
charmm = os.path.join(bin_path,"charmm")
if not os.path.isfile(charmm):
    raise OSError("charmm binary not found in $CHARMM (%s)" % bin_path)

def createIndivParam(filename,calc_param):
    """
    Generate parameters specific to a pdb file.
    """

    indiv_calc_param = copy(calc_param)

    # ---------- Check for continuous pdb file -------------------- #
    # (*** At some point this will be replaced with sophisticated code that will
    # deal with non-continous pdb files.  A the moment however...)

    # Load in pdb file
    f = open(filename,'r')
    pdb = f.readlines()
    f.close()
    pdb = [l for l in pdb if l[0:4] == "ATOM"]

    # Verify that there are no gaps in the chain
    residues = [int(l[22:26]) for l in pdb if l[13:16] == "CA "]
    continuity = [(residues[j]+1) == residues[j+1]
                  for j in range(len(residues)-1)]
    if False in continuity:
        err = "%s is not a continuous pdb file!" % p
        err += " (gap at residue %i)" % residues[continuity.index(False)]
        raise IOError(err)

    indiv_calc_param.offset = -(int(pdb[0][22:26]) - 1)
    indiv_calc_param.chain = "A"
    indiv_calc_param.termini = [calc_param.n_terminus,calc_param.n_terminus]

    # Decide his tautomeric states, either using a file or the default settings
    his_dict = {0:"HIS ",1:"HSD ",2:"HIS "}
    his_list = ProcessInputFiles.processHis(pdb,calc_param.his_tautomers)
    indiv_calc_param.his_type = [his_dict[x] for x in his_list]
    indiv_calc_param.pdb_file = filename
    indiv_calc_param.charmm_tmp = "%s.tmp" % filename.lower()
    indiv_calc_param.final_pdb = "%sH.pdb" % filename[:-4]

    return indiv_calc_param


def indivRun(filename,calc_param):
    """
    Generates paramters specific to pdb file, creates a CHARMm input file, then
    adds hydrogens to that file.
    """

    # Set up parameters specific to this pdb file
    indiv_calc_param = createIndivParam(filename,calc_param)

    # Create a charmm input file
    GenerateCharmmInput.createCharmmFile(indiv_calc_param)

    # Run Charmm
    CharmmInterface.runCharmm(indiv_calc_param,charmm)

def main():
    """
    Parses the command line and adds hydrogens to all files specified.
    """

    ParseCharmm.main()
    calc_param = ParseCharmm.calc_param

    # Perform calculation on all files in file_list
    for filename in ParseCharmm.file_list:
        print "Adding hydrogens for %s" % filename
        indiv_calc_param = createIndivParam(filename,calc_param)
        indivRun(filename,indiv_calc_param)

if __name__ == "__main__":
    main()


