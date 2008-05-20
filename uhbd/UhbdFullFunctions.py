"""
UhbdFullFunctions.py

A set of functions that specifically deal with full calculations.  At the moment
this simply replaces the prepares binary.  (I think this could evolve and
subsume all binaries except the main uhbd binary).
"""

# Globally-defined residue information
GROUP_PKAS = {"HISA": 6.3,"HISB": 6.3,"LYS" :10.4,"ARG" :12.0,"ASP" : 4.0,
              "GLU" : 4.4,"TYR" : 9.6,"CYS" : 8.3,"TERN": 7.5,"NTEP": 7.5,
              "TERC": 3.8}
GROUP_CHARGES = {"HISA": 1,"HISB": 1,"LYS" : 1,"ARG" : 1,"ASP" :-1,
                 "GLU" :-1,"TYR" :-1,"CYS" : 1,"TERN": 1,"NTEP": 1,
                 "TERC":-1}
GROUP_ATOMS = {"ARG" :["CD  ","NE  ","HE  ","CZ  ","NH1 ","HH11","HH12","NH2 ",
                      "HH21","HH22"],
               "LYS" :["CE  ","NE  ","HZ1 ","HZ2 ","HZ3 "],
               "HISA":["CB  ","CG  ","CD2 ","ND1 ","ND1 ","NE2 ","HD1 ","HD2 ",
                       "HE1 ","HE2 "],
               "HISB":["CB  ","CG  ","CD2 ","ND1 ","ND1 ","NE2 ","HD1 ","HD2 ",
                       "HE1 ","HE2 "],
               "ASP" :["CB  ","CG  ","OD1 ","OD2 ","HD  "],
               "GLU" :["CG  ","CD  ","OE1 ","OE2 ","HE  "],
               "TYR" :["CB  ","CD1 ","HD1 ","CE1 ","HE1 ","CD2 ","HD2 ","CE2 ",
                       "HE2 ","CZ  ","OH  ","HH  "],
               "CYS" :["SG  ","HG  ","CB  "],
               "NTEP":["N   ","HT1 ","HT2 ","HT3 "],
               "TERN":["N   ","HT1 ","HT2 ","HT3 "],
               "TERC":["C   ","CA  ","O   ","OXT ","HXT "]}

import os

def writeOutput(output_file,data_list):
    """
    Mini function that writes output files.
    """

    g = open(output_file,'w')
    g.writelines(data_list)
    g.close()


def prepareFull(pdb_file):  #,group_param):
    """
    A python implementation of UHBD fortran "prepare.f"  It does not direclty
    write out uhbdini.inp.  See the makeUhbdini function for that.
    """

    # Open pdb file and read it
    f = open("proteinH.pdb","r")
    pdb = f.readlines()
    f.close()

    # Pull only titratable atoms from the pdb
    titr_atoms = [l for l in pdb if l[0:4] == "ATOM"
                  and l[17:21].strip() in GROUP_PKAS.keys()]

    # Initialize lists to hold output files
    all_groups = [pdb[0]]
    all_residues = [pdb[0]]
    for_pot, sites_dat = [], []

    # Initialize residue names/number and counter for going through pdb file
    current_name = titr_atoms[0][17:21].strip()
    current_numb = titr_atoms[0][23:26].strip()
    counter = 1
    for atom in titr_atoms:

        # If we are on a new residue, update output files.  Reset counters.
        if atom[23:26].strip() != current_numb:

            # Update output files
            for_pot.append("%4.1F%6i%13.6E%6i\n" % (GROUP_PKAS[current_name],
                                                    GROUP_CHARGES[current_name],
                                                    0.,counter))
            sites_dat.append("%4i %-4s %4i\n" % (counter,current_name,
                                               int(current_numb)))
            all_residues.append("%-76s\n" % ("NEXT"))
            all_groups.append("%-76s\n" % ("NEXT"))

            # Update counters
            current_name = atom[17:21].strip()
            current_numb = atom[23:26].strip()
            counter += 1

        # Update all_residues and all_groups
        all_residues.append(atom)
        if atom[12:16] in GROUP_ATOMS[current_name]:
            all_groups.append(atom)

    # Close out output files
    for_pot.append("%4.1F%6i%13.6E%6i\n" % (GROUP_PKAS[current_name],
                                            GROUP_CHARGES[current_name],
                                            0.,counter))
    sites_dat.append("%4i %-4s %4i\n" % (counter,current_name,
                                       int(current_numb)))
    all_residues.append("%-76s\nEND\n" % ("NEXT"))
    all_groups.append("%-76s\nEND\n" % ("NEXT"))

    # Write out files exactly like old fortran did
    writeOutput("allgroups.pdb",all_groups)
    writeOutput("allresidues.pdb",all_residues)
    writeOutput("allresidues.pdb.orig",all_residues)
    writeOutput("for_pot.dat",for_pot)
    writeOutput("sites.dat",sites_dat)
    writeOutput("potentials",["%i\n" % counter])


def makeUhbdini(calc_param):
    """
    Write out uhbdini.inp.
    """

    short_param_file = os.path.split(calc_param.param_file)[-1]

    uhbdini = [\
    "read mol 1 file \"%s\"     pdb end\n" % "proteinH.pdb",
    "set charge radii file \"%s\"     para neut end\n" % short_param_file,
    "\n elec setup mol 1\ncenter\n",
    " spacing   %.2F dime    %i    %i    %i\n" % (calc_param.grid[0][0],
                                                  calc_param.grid[0][1],
                                                  calc_param.grid[0][2],
                                                  calc_param.grid[0][3]),
    " nmap      %.1F\n" % calc_param.map_sphere,
    " nsph     %i\n" % calc_param.map_sample,
    " sdie   %.2F\n" % calc_param.solvent_dielec,
    " pdie   %.2F\n" % calc_param.protein_dielec,
    "end\n\nstop\n"]

    writeOutput("uhbdini.inp",uhbdini)

def runPrepare(calc_param):

    prepareFull(calc_param.pdb_file) 
    makeUhbdini(calc_param)


