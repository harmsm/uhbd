"""
UhbdSingleFunctions.py

Functions for running single-site calculations using UHBD.  Replaces the
prepares and doinps binaries.
"""

import os

TITRATABLE = {"HISA":"NE2","HISB":"ND1","HISN":"ND1","HISC":"ND1",
              "LYS":"NZ","LYSN":"NZ","LYSC":"NZ",
              "ARG":"CZ","ARGN":"CZ","ARGC":"CZ",
              "ASP":"CG","ASPN":"CG","ASPC":"CG",
              "GLU":"CD","GLUN":"CD","GLUC":"CD",
              "TYR":"OH","TYRN":"OH","TYRC":"OH",
              "CYS":"SG","CYSN":"SG","CYSC":"SG"}


def writeOutput(output_file,data_list):
    """
    Mini function that writes output files.
    """

    g = open(output_file,'w')
    g.writelines(data_list)
    g.close()


def prepareSingle():
    """
    A python implementation of UHBD fortran "prepares.f"  It does not direclty
    write out uhbdini.inp.  See the makeUhbdini function for that.
    """

    # Open pdb file and read it
    f = open("proteinH.pdb","r")
    pdb = f.readlines()
    f.close()

    # Pull only titratable atoms from the pdb
    n_terminus = [l for l in pdb if l[0:4] == "ATOM" 
                  and l[20:21] == "N"]
    titr_groups = [l for l in pdb if l[0:4] == "ATOM"
                   and l[17:21].strip() in TITRATABLE.keys()]
    c_terminus = [l for l in pdb if l[0:4] == "ATOM" 
                  and l[20:21] == "C"]

    # Create list of all titratable groups in the pdb file
    titr_resid = []
    titr_resid.extend(n_terminus)
    titr_resid.extend(titr_groups)
    titr_resid.extend(c_terminus)
    titr_resid = ["%s\n" % l[:54] for l in titr_resid]
   
    # Grab list of all unique residues
    resid_list = [titr_resid[0][21:26]]
    for l in titr_resid:
        if resid_list[-1] != l[21:26]:
            resid_list.append(l[21:26])  

    # Create tempor output file, listing all atoms of all titratable residues
    # in the order of the original file
    tempor = [] 
    for residue in resid_list:
        residue_atoms = [l for l in titr_resid if l[21:26] == residue]
        residue_atoms = ["%6s%5i%s" % (a[0:6],i+1,a[11:]) 
                         for i, a in enumerate(residue_atoms)]
        tempor.extend(residue_atoms)

    # Create sitesinpr and titraa files, which list all titratable atoms and
    # all titratable residues with titratable atom in first position.
    sitesinpr = []
    titraa = []
    for residue in resid_list:
        residue_atoms = [l for l in titr_resid if l[21:26] == residue]
    
        # Figure out what the titratable atom is for this residue 
        try: 
            titr_atom = TITRATABLE[residue_atoms[0][17:21].strip()]
        except KeyError:
            if residue_atoms[0][20] == "N":
                titr_atom = "N"
            elif residue_atoms[0][20] == "C":
                titr_atom = "C"

        titr_line = [l for l in residue_atoms 
                     if l[12:16].strip() == titr_atom][0]
        sitesinpr.append(titr_line)

        residue_atoms = [l for l in residue_atoms if l != titr_line]
        residue_atoms.insert(0,titr_line)
        residue_atoms = ["%6s%5i%s" % (a[0:6],i+1,a[11:]) 
                         for i, a in enumerate(residue_atoms)]
       
        titraa.extend(residue_atoms) 

    # Close sitesinpr file
    sitesinpr.insert(0,"%-54s\n" % (pdb[0].strip()))
    sitesinpr.append("END")

    
    # Write output files         
    writeOutput("tempor.pdb",tempor)
    writeOutput("sitesinpr.pdb",sitesinpr)
    writeOutput("titraa.pdb",titraa)



def makeUhbdini(calc_param):
    """
    Write out uhbdini.inp.
    """

    short_param_file = os.path.split(calc_param.param_file)[-1]

    uhbdini = [\
    "read mol 1 file \"%s\"     pdb end\n" % "proteinH.pdb",
    "set charge radii file \"%s\"     para mine end\n" % short_param_file,
    "\n elec setup mol 1\ncenter\n",
    " spacing   %.2F dime    %i    %i    %i\n" % (calc_param.grid[0][0],
                                                  calc_param.grid[0][1],
                                                  calc_param.grid[0][2],
                                                  calc_param.grid[0][3]),
    " nmap      %.1F\n" % calc_param.map_sphere,
    " nsph     %i\n" % calc_param.map_sample,
    " sdie   %.2F\n" % calc_param.solvent_dielec,
    " pdie   %.2F\n" % calc_param.protein_dielec,
    "end\n\n",
    "write grid epsi binary file  \"coarse.epsi\" end\n",
    "write grid epsj binary file  \"coarse.epsj\" end\n",
    "write grid epsk binary file  \"coarse.epsk\" end\n\n"
    "stop\n"]

    writeOutput("pkaS-uhbdini.inp",uhbdini)

def runPrepares(calc_param):

    prepareSingle()
    makeUhbdini(calc_param)



