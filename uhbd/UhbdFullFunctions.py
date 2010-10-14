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

import os

class AminoAcidParameters:
    """
    Class that stores and processes parameters from a uhbd full parameter file.
    """

    def __init__(self,entry,charge_state):
        """
        Initialize instance of AminoAcidParameters, taking an entry and the
        charge state of that entry as an argument.
        """

        # Create list of atoms and initialize parameter dictionary
        self.atom_list = [l.split()[1] for l in entry]
        self.param = {"charged":{},"neutral":{}}

        # Parse the first entry
        self.parseEntry(entry,charge_state)

    def parseEntry(self,entry,charge_state):
        """
        Parses a uhbd parameter file entry by amino acid.
        """

        for line in entry:
            columns = line.split()
            atom = columns[1]
            data = [float(d) for d in columns[2:5]]
            self.param[charge_state][atom] = data

    def findDifferences(self,residue_name):
        """
        Go through every atom in self.atom_list and determine if there are *any*
        differences in parameters.  A list of different atoms will then be
        returned.
        """
        self.different = []
        for atom in self.atom_list:
            if self.param['charged'][atom] != self.param['neutral'][atom]:
                self.different.append(atom)

        return self.different


def readParamFile(param_file):
    """
    Read a UHBD "full" parameter file and place individual amino acid data in
    AminoAcidParameters instances.  Use this class to determine which atoms are
    different between the charged and netural forms of each amino acid.  This is
    returned as a dictionary that can be read by prepareFull.
    """

    print "Reading parameter file %s" % param_file

    # Possible records in parameter file.  If there are any other records, they
    # will be subsumed into another record, probably causing an error.
    allowed_records = ["equi","neut","char"]

    # Read in file
    f = open(param_file)
    param = f.readlines()
    f.close()

    # strip comments and white space
    param = [l for l in param if l[0] != "!" and l.strip() != ""]

    record_table = []
    for index, line in enumerate(param):
        if line[0:4].lower() in allowed_records:
            record_table.append(index)

            # Record the location of neutral and charged entries in table of
            # records.
            if line[0:4].lower() == "neut":
                neutral = len(record_table) - 1
            elif line[0:4].lower() == "char":
                charged = len(record_table) - 1

    # Put on dummy last record to avoid IndexError
    record_table.append(-1)

    # Pull out data in neutral and charged database entries
    neutral_record = param[record_table[neutral]:record_table[neutral+1]]
    charged_record = param[record_table[charged]:record_table[charged+1]]

    # Strip out header
    neutral_record = neutral_record[2:]
    charged_record = charged_record[2:]

    # Dictionary that will hold instance of AminoAcidParameters keyed to
    # residue name.
    all_fields = {}

    # Go through netural record and find fields.  Create instance of
    # AminoAcidParameters class for each amino acid field.
    current_residue_field = []
    current_residue = neutral_record[0].split()[0]
    for line in neutral_record:
        if current_residue != line.split()[0]:
            all_fields.update([(current_residue,
                AminoAcidParameters(current_residue_field,"neutral"))])
            current_residue = line.split()[0]
            current_residue_field = [line]
        else:
            current_residue_field.append(line)

    # Go through charged record and find fields.  Update each instance of
    # AminoAcidParameters with charged information.
    current_residue_field = []
    current_residue = charged_record[0].split()[0]
    for line in charged_record:
        if current_residue != line.split()[0]:
            try:
                all_fields[current_residue].parseEntry(current_residue_field,
                                                       "charged")
            except KeyError:
                # If there was no neutral entry, there is no instance of
                # AminoAcidParameters, hence an error.
                err = "   %s has a charged entry " % current_residue
                err += "but no neutral entry!  Skipping..."
                print err
            current_residue = line.split()[0]
            current_residue_field = [line]
        else:
            current_residue_field.append(line)

    # Remove entries for which there is no charged data
    no_charged = [k for k in all_fields.keys()
                  if all_fields[k].param['charged'] == {}]
    err = ["   %s has neutral entry but no charged entry!  Skipping...\n" % x
           for x in no_charged]
    print "".join(err)

    all_fields = dict([(k,all_fields[k]) for k in all_fields.keys()
                       if  all_fields[k].param['charged'] != {}])

    # Create a dictionary keying amino acid to atoms that are different between
    # netural and charged forms of the amino acid.
    group_param = dict([(k,all_fields[k].findDifferences(k))
                        for k in all_fields.keys()])

    return group_param


def writeOutput(output_file,data_list):
    """
    Mini function that writes output files.
    """

    g = open(output_file,'w')
    g.writelines(data_list)
    g.close()


def prepareFull(pdb_file,group_param):
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
        if atom[12:15].strip() in group_param[current_name]:
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

    group_param = readParamFile(calc_param.param_file)
    prepareFull(calc_param.pdb_file,group_param)
    makeUhbdini(calc_param)



if __name__ == "__main__":

    __usage__ =\
    """
    UhbdFullFunctions.py parameter_file

    This module is not meant be invoked from the command line; however, it can
    be for diagnostic purposes.  If you run it with a parameter file as the
    argument, it will print out a list of a all atoms different between the
    charged and neutral forms of the amino acid.
    """

    import sys

    # Pare command line
    try:
        input_file = sys.argv[1]
        if os.path.isfile(input_file):
            group_param = readParamFile(input_file)
        else:
            err ="%s is not a file." % input_file
            raise IOError(err)
    except IndexError:
        print __usage__
        sys.exit()

    # Create list of amino acid keys
    keys = group_param.keys()
    keys.sort()

    # Go through every amino acid and spit out pretty-string list of outputs
    out = ["Differences between netural and charged atoms in %s\n" % input_file]
    for k in keys:
        out.append("%s:\n    " % k)
        out.extend(["%s " % g for g in group_param[k]])
        out.append("\n")

    print "".join(out)
