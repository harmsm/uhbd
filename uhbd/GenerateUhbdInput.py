"""
GenerateUhbdInput.py

Generates a standard UHBD finite-difference calculation input file given a
structure file name and a set of calculation parameters.
"""

import os

class DoinpEntry:
    """
    Parent class for entries into doinp.  Contains generic initialization
    function and output function.
    """

    def __init__(self,id_string,value):
        """
        Initialize class.
        """

        format_dict = {float:"%.1F ", str:"%s ", int:"%i "}

        # ID string output
        self.id_string = "          %s" % id_string

        # Create value output
        if type(value) != list:
            value = [value]
        value_type = [type(v) for v in value]
        self.value = [format_dict[value_type[i]] % v
                      for i, v in enumerate(value)]
        self.value = "".join(self.value)

    def writeOutput(self):
        """
        Write general output for DoinpEntry.
        """

        return "%s\n%s\n" % (self.id_string,self.value)


class GridEntry(DoinpEntry):
    """
    Subclass of DoinpEntry that spits out grid values in proper format.
    """

    def __init__(self,id_string,value):
        """
        Rewritten __init__ function that properly deals with grid formatting
        requirements.
        """

        self.id_string = "          %s" % id_string

        self.value = ["%i\n" % len(value)]
        for g in value:
            self.value.extend("%.2F %i %i %i\n" % tuple(g))
        self.value = "".join(self.value)
        self.value = self.value[:-1]


class ResidueEntry(DoinpEntry):
    """
    Subclass of DoinpEntry that spits out residue info in proper format.
    """

    def __init__(self,id_string,value):
        """
        Rewritten __init__ function that properly deals with residue formatting
        requirements.
        """
        self.id_string = "          %s" % id_string

        self.value = ["%i\n" % len(value)]
        self.value.extend(["%i " % v for v in value])
        self.value = "".join(self.value)
        self.value = self.value[:-1]


def createDoinp(filename,calc_param):
    """
    Generates a standard UHBD input file given a filename and set of calc
    paramters.  This is done by generating DoinpEntry instances for each option
    that are then written to a file using DoinpEntry.writeOutput.
    """

    # Some uber-long ID strings I place here for readability purposes
    his_str = "NO of histidins, sites: 1=ND1=HISB; 2=NE2=HISA; 0=CE1 in A or B"
    add_str = "NO ADD TITR SITES, SITES DATA:a4,1x,a4,1x,f5.1,1x,i2"
    cys_str = "CYS to be included, how many? and their res numbers"

    # Generate list of instances of DoinpEntry (and children)
    inp_file = [DoinpEntry("NAME of mol 1 file",calc_param.pdb_file),
                DoinpEntry("NAME of charge and radius file",
                           os.path.split(calc_param.param_file)[-1]),
                DoinpEntry("NUMBER of polypeptide chains of mol 1",
                           calc_param.num_chains),
                DoinpEntry("NUMBERS of first residues of each chain",
                           calc_param.first_residues),
                DoinpEntry("NUMBERS of last residues of each chain",
                           calc_param.last_residues),
                ResidueEntry(his_str,calc_param.his_tautomers),
                GridEntry("NO GRIDS; SPACING and dime (max 5 grids)",
                          calc_param.grid),
                DoinpEntry("MAXIMAL number of iterations for elec",
                           calc_param.iterations),
                DoinpEntry("TEMPERATURE in K",calc_param.temperature),
                DoinpEntry("DIELECTRIC constants of solvent and protein",
                      [calc_param.solvent_dielec,calc_param.protein_dielec]),
                DoinpEntry("IONIC strength and radius of ions",
                           [calc_param.ionic_strength,calc_param.ionic_radius]),
                DoinpEntry(add_str,calc_param.added_residues),
                ResidueEntry(cys_str,calc_param.cys_titrate),
                DoinpEntry("DATA for new diel. map: nmap and nsph. ",
                    [calc_param.map_sphere,calc_param.map_sample])]

    if calc_param.full:
        inp_file.append(DoinpEntry("CHANGES in ASP GLU residues?",
                                   calc_param.change_acid))

    # Write ouput for DoinpEntry classes
    inp_file = [entry.writeOutput() for entry in inp_file]
    inp_file = "".join(inp_file)

    # Write output to inp file name
    g = open(calc_param.inp_name,"w")
    g.write(inp_file)
    g.close()




