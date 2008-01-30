"""
ProcessInputFiles.py

A module containing functions for processing pyUHBD input files.
"""

__author__ = "Michael J. Harms"

from math import sqrt
import os
import SystemOps


class MangledFileError(Exception):
    """
    Raise for input files that cannot be read.
    """

    pass

def processHis(pdb,his_tautomers,default_his=2,
               valid_his={"CD1":0,"ND1":1,"NE2":2}):
    """
    Take the calc_param.his_tautomers and generate proper input for the
    generation of an input file.  Either:
        1) An input file is specified; read the file but return an error if it
           is mangled.
        2) No input file is specified; assign every histidine a default
           tautomer.
    Either way, the function returns hist_out (a list of integers).
    """
    his_names = ["HIS","HSD","HSE"]

    # List of histidine residues
    his_resid = [l for l in pdb if l[0:4] == "ATOM" and l[17:20] in his_names] 
    his_resid = [l for l in his_resid
                 if l[12:17] == " CA  " or l[12:17] == "CA   "]
    his_resid = [int(l[22:26]) for l in his_resid]

    # If an input file is specified...
    if his_tautomers != None:

        # Read input file
        his_lines = SystemOps.readFile(his_tautomers)

        # Parse input file
        his_out = []
        for line in his_lines:
            his_out.extend(line.split())
            his_out = [int(v) for v in his_out]

        # Make sure that the input file is valid.
        his_check = [v in valid_his.values() for v in his_out]
        if False in his_check:
            his_keys = valid_his.keys()
            his_keys.sort()
            valid_entries = ["   %i: %s\n" % (valid_his[k],k) for k in his_keys]
            err = "%s: %s%s" % (his_tautomers,
                                "Specify his tautomers with ingeters:\n",
                                "".join(valid_entries))
            raise MangledFileError(err)

        # Make sure that the number of histidines in the input file match the
        # number in the pdb file.
        if len(his_out) != len(his_resid):
            err = "Number of his specified in %s (%i) does not match number in"
            err += "pdb file (%j)" 
            err = err % (his_tautomers,len(his_out),len(his_resid))
            
            raise MangledFileError(err)

    # If not input file is specified...
    else:
        his_out = [default_his for i in range(len(his_resid))]

    return his_out


def processCys(pdb,cys_titrate,disulfide_cutoff=3.5):
    """
    Take the calc_param.cys_titrate and generate proper input for the
    generation of an input file.  Either:
        1) An input file is specified; read the file but return an error if it
           is mangled.
        2) No input file is specified; decide whether each cysteine should
           titrate based on how close it is to another cysteine.  (If two CYS SG
           are within disulfide_cutoff, they do not titrate).
    Either way, the function returns cys_out (a list of residue numbers, int).
    """

    # List of cys residues
    cys_resid = [int(l[22:26]) for l in pdb if l[0:4] == "ATOM"
                 and l[12:15] == "SG " and l[17:20] == "CYS"]
    num_cys = len(cys_resid)

    # If an input file is specified...
    if cys_titrate != None:

        # read input file
        cys_lines = SystemOps.readFile(cys_titrate)

        # Parse input file
        cys_out = []
        for line in cys_lines:
            cys_out.extend(line.split())
            cys_out = [int(v) for v in cys_out]

        # Make sure that all specified cys are in pdb file
        cys_check = [v in cys_resid for v in cys_out]
        if False in cys_check:

            # Generate error message
            err_resid = [cys_out[i] for i in range(len(cys_check))
                         if not cys_check[i]]
            err = ["Some cys specified in input file that are not in pdb file:"]
            err.append(len(err_resid)*"   %i " % tuple(err_resid))
            err = "".join(err)
            raise MangledFileError(err)

    # If no input file is specified...
    else:

        # Read in CYS SG coordinates
        coord = [[float(l[31+8*i:38+8*i]) for i in range(3)] for l in pdb
                 if l[0:4] == "ATOM" and l[12:15] == "SG "]

        # Define all cys within disulfide_cutoff angstroms of each other as in
        # disulfide bonds
        cutoff_squared = disulfide_cutoff**2
        disulfide = []
        for i in range(num_cys):
            for j in range(i+1,num_cys):
                r = sum([(coord[i][k] - coord[j][k])**2 for k in range(3)])
                if r < cutoff_squared:
                    disulfide.append(cys_resid[i])
                    disulfide.append(cys_resid[j])

        # Residues not in disulfide bonds can titrate
        cys_out = [c for c in cys_resid if c not in disulfide]

    return cys_out


def processGrid(pdb,grid):
    """
    Take the calc_param.grid and generate proper input for the generation of an
    input file.  Either:
        1) A grid input file is specified; read the file but return an error
           if it is mangled.
        2) No grid input file is specified; generate a default grid based on the
           maximum dimension of the molecule.
    Either way, the function returns grid_out (a nested list of grid levels).
    """

    # If the grid file is specified...
    if grid != None:
        grid_file = SystemOps.readFile(grid)
        if len(grid_file) > 5:
            err = "%s: grid cannot have more than five levels!"
            raise MangledFileError(err)
        else:
            try:
                grid_out = []
                for g in grid_file:
                    c = g.split()
                    grid_out.append([float(c[0]),int(c[1]),int(c[2]),int(c[3])])
            except ValueError or IndexError:
                err = "%s: not a valid grid file!" % grid
                raise MangledFileError(err)

    # If the grid file is not specified...
    else:

        # Load in coordinates of all Ca atoms
        ca = [l for l in pdb if l[0:4] == "ATOM" and l[12:15] == "CA "]
        coord = []
        for atom in ca:
            coord.append([float(atom[30+8*i:37+8*i]) for i in range(3)])
        size = len(coord)

        # Find maximum dimension
        d = [0. for i in range(size**2)]
        for i in range(size):
            for j in range(i+1,size):
                d[i*size + j] = sum([(coord[i][k] - coord[j][k])**2
                    for k in range(3)])
        max_d = sqrt(max(d))

        # Find top-level grid interval (3 * maximum dimension)/65.  If the
        # interval is less than 1.5 A, make it 1.5 A.
        interval = (3*max_d)/65
        if interval < 1.5:
            interval = 1.5

        grid_out = [[interval, 65, 65, 65],
                    [1.2,      40, 40, 40],
                    [0.75,     40, 40, 40],
                    [0.25,     40, 40, 40]]

    return grid_out



