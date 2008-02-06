"""
FileOps.py
A set of functions that interact with the system.
"""

__author__ = "Michael J. Harms"
__date__ = "060817"
__version__ = "0.1"

# import modules
import os, shutil, time, sys, math, random

# Global variables
global tmp_dir, script_path, tmp_path

def checkEnvironVariable(variable_name):
    """
    Checks the definition of some environment variable specifying directory.
    Returns the path to that directory.
    """

    try:
        var_path = os.environ[variable_name]
        if os.path.isdir(var_path) != True:
            print "Invalid path specified in environment variable %s:" % \
                variable_name
            print "\t%s = %s" % (variable_name,var_path)
            sys.exit()
    except KeyError:
        print "Environment variable %s not defined!" % variable_name
        sys.exit()

    return var_path


def createTemporaryDirectory():
    """Create temporary directory and chdir into it."""
    
    global tmp_dir
    time_tuple = time.localtime(time.time())
    current_time = "%4i-%2i-%2i_%2i-%2i_" % (time_tuple[0],time_tuple[1],
                                             time_tuple[2],time_tuple[3],
                                             time_tuple[4])
    current_time = current_time.replace(" ","0")    

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    tmp_dir_root = os.path.join(tmp_path,current_time)
    
    letter_index = 0
    while os.path.isdir("%s%s" % (tmp_dir_root,letters[letter_index])):
        letter_index += 1 
    tmp_dir = "%s%s" % (tmp_dir_root,letters[letter_index])
    os.mkdir(tmp_dir)
    os.chdir(tmp_dir)

    
def runCleanup():
    """A function to clean out temporary directory after UHBD run."""
    
    os.chdir(script_path)
    for file in os.listdir(tmp_dir):
        os.remove(os.path.join(tmp_dir,file))
    os.rmdir(tmp_dir)


def copyFinalOutput(output_directory):
    """Copy output files from temporary directory to output_directory."""
    
    shutil.copy('pkaS-potentials',output_directory)
    shutil.copy('hybrid.out',output_directory)
    shutil.copy('pkaS-sitesinpr.pdb',output_directory)
    shutil.copy('pkaS-doinp.inp',output_directory)
    shutil.copy('titraa.pdb',output_directory)

def makeDir(dir):
    """
    Creates a directory, checking to make sure creation succeeds.  
    """

    try:
        os.mkdir(dir)
    except OSError, value:
        # Don't stop if error is "directory exists"
        if value[0] != 17: 
            print 'File error.'
            print value[0], dir, value[1]
            sys.exit()

def setupInp(pdb_name,ionic_strength,dielectric,css_cut=3.5):
    """
    Function to set up pkaS-doinp.inp for a UHBD run.  Finds the starting
    and stopping residues, histidines, titratable cysteines, and grid sizes.
    Arguments:
        pdb_name        (string)       name of pdb file to be processed
        ionic_strength  (float)        ionic_strength for calculation
        dielectric      (float)        protein dielectric constant
        css_cut         (float)        cutoff SG-SG distance for disulfide bond
                                       assignment (default = 3.5 angstroms).
    """

    # Copy required files into temporary directory
    createTemporaryDirectory()
    shutil.copy(pdb_name,'pkaSH.pdb')
    shutil.copy(os.path.join(script_path,'inputs','pkaS-doinp.inp.src'),
                'pkaS-doinp.inp')
    shutil.copy(os.path.join(script_path,'inputs','pkaS.dat'),
                'pkaS.dat')
    
    # *****pdb file info *****
    # grab first and last residue indicies from pdb file
    f = open('pkaSH.pdb','r')
    pdb = f.readlines()
    f.close()

    # Find the first and last atom in the pdb file
    for line in pdb:
        if line[0:4] == 'ATOM':
            start_index = int(line[22:26])
            break
    end_index = int(pdb[-2][22:26])

    # Grab HIS and CYS from pdb file
    hisnum = []
    cysnum = []
    cyscoord = []
    for line in pdb:
        if line[17:20] == 'HIS':
            resi = int(line[22:26])
            if (resi in hisnum) == 0: hisnum.append(resi)
        if line[17:20] == 'CSS' and line[12:14] == 'SG':
            cysnum.append(int(line[22:26]))
            cyscoord.append([float(line[31:38]),float(line[39:46]), \
                             float(line[47:54])])
    number_his = len(hisnum)
    hisstring = number_his*"2 "  

    # FIND DISULFIDE BONDS (look for SG - SG distances < css_cut)
    css_cut_squared = css_cut**2
    cys_rem = []
    for i in range(len(cysnum)):
        for j in range(i+1,len(cysnum)):
            sep = 0
            for k in range(3):
                sep += (cyscoord[i][k] - cyscoord[j][k])**2
            if sep < css_cut_squared:
                cys_rem.append(cysnum[i])
                cys_rem.append(cysnum[j])

    cysnum = [i for i in cysnum if (i in cys_rem) == 0]
    number_cys = len(cysnum)
    cysstring = ''
    for cys in cysnum:
        cysstring = 3*"%s" % (cysstring,cys,' ')

    # CALCULATE GRID SIZES
    # 1) Find maximum dimension
    CA = [line for line in pdb if line[0:4] == "ATOM" and line[12:15] == "CA "]
    coord = []
    for atom in CA:
        coord.append([float(atom[30+8*i:37+8*i]) for i in range(3)])
    size = len(coord)
    max_dim = 0.0
    for i in range(size):
        for j in range(i+1,size):
            dist = 0.0
            for k in range(3):
                dist += (coord[i][k] - coord[j][k])**2
            if dist > max_dim: max_dim = dist
    
    # 2) Find grid sizes proper
    globalmax = 2*math.sqrt(max_dim)
    interval = globalmax/65
    if interval < 1.5: interval = 1.5

    # OPEN pkaS-doinp FOR EDITING
    f = open('pkaS-doinp.inp','r')
    inp = f.readlines()
    f.close()

    inp[7] = "%s\n" % (start_index)
    inp[9] = "%i\n" % (end_index + 2)
    inp[11] = "%s\n" % number_his
    inp[12] = "%s\n" % hisstring
    inp[15] = "%3.1F%s\n" % (interval,' 65 65 65')
    inp[24] = "78.5 %.1F\n" % dielectric
    inp[26] = "%.1F 2.0\n" % ionic_strength
    inp[30] = "%s\n" % number_cys
    inp[31] = "%s\n" % cysstring


    if number_his == 0: inp[12] = ''
    if number_cys == 0: inp[31] = ''

    # write input file
    g = open('pkaS-doinp.inp','w')
    g.writelines(inp)
    g.close()


# define location of script (for temporary folder creation)
script_path = __file__
script_path = os.path.split(script_path)[0]

tmp_path = checkEnvironVariable("HOME")
tmp_path = os.path.join(tmp_path,".pyUHBD")
if not os.path.isdir(tmp_path):
    os.mkdir(tmp_path)
