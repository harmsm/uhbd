"""
    uhbd.py:
    Functions/data necessary to perform a UHBD calculation on a single pdb file.
    Core of the batch run suite.
    
    Required files:
        pkaS-doinp.inp (in ./inputs/)
        pkaS.dat       (in ./inputs/)
"""

"""
Version Notes:

0.4.1:  Fixed bug: if multiple jobs running, sometimes two jobs would try to use
        same temporary directory, causing crash.  Fixed by appending a random
        integer (1-1000) to temporary directory name.

0.4.2:  Changed temporary directory structure.  Temporary folders now created
        within 'scratch' directory inside the script directory.
        
0.4.3:  060310
    Changed default grid sizes.  Used to have program define first two grids,
    not have it define only the first grid.  The last three grids are fixed.
    
    Added error checking for bin_path variable
    
    Fixed bug: if / not specified at end of bin_path, script crashed.  (i.e. if
    bin_path were /home/harms/bin, the script would try to run:
    /home/harms/binmybin instead of /home/harms/bin/mybin

0.4.4:  060313
    Fixed bug.  For very small proteins, grid size would be too small, resulting
    in zero potentials.  Set cutoff so that minimum final grid is 1.5 A * 65.

0.5.0:  060404
    COMPATABILITY NOTE!  THIS VERSION SHOULD ***ONLY*** BE USED WITH THE
    LAB-CERTIFIED UHBD COMPILES!  THE LATEST COMPILE (060404) CREATES SLIGHTLY
    DIFFERENT OUTPUTS THAN THE COMPILE THIS SCRIPT WAS CREATED TO INTERACT WITH.
    runPrepares WILL DEAL CORRECTLY ONLY WITH THE NEW COMPILE!
    
    Altered runPrepares function.  The new uhbd compile does not add N-terminal
    groups incorrectly as the old one did.  Commented out portion of function
    that removes N-terminus.
    
    Hokiness fix.  Changed from some_path = x + os.sep + y to os.path.join(x,y)
    
    Moved specification of binary path from a variable in uhbd.py to a system
    environment variable (UHBD).
    
    
"""

__author__ = "Michael J. Harms"
__version__ = "0.5.0"
__date__ = "060404"


#*****************************************************************************#
#                            INITALIZE MODULE                                 #
#*****************************************************************************#

# import modules
import os, shutil, time, sys, math, random

# Global variables
global tmp_dir

# Take bin_path from environment variable UHBD and make it points to a valid
# directory.
try:
    bin_path = os.environ['UHBD']
    try:
        os.listdir(bin_path)
    except OSError:
        print "Invalid binary path specified in UHBD environment variable:"
        print "\tbin_path = %s" % bin_path
        sys.exit()
except KeyError:
    print "Environment variable UHBD not defined!"
    sys.exit()

# set up sundry strings to make code easier to read
prep = os.path.join(bin_path,'prepares')
uhbd = os.path.join(bin_path,'uhbd')
getgrids = os.path.join(bin_path,'getgrids')
doinps = os.path.join(bin_path,'doinps')
getpots = os.path.join(bin_path,'getpots')
hybrid = os.path.join(bin_path,'hybrid')


# define location of script (for temporary folder creation)
script_path = __file__
script_path = os.path.split(script_path)[0]


#*****************************************************************************#
#                        HOUSEKEEPING FUNCTIONS                               #
#*****************************************************************************#

def createTemporaryDirectory():
    """Create temporary directory and chdir into it."""
    
    global tmp_dir
    
    tmp_dir = os.path.join(script_path,'scratch',"tmp%i_%i" % \
                           (time.time(),random.choice(range(1000))))
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
    
    
#*****************************************************************************#
#                       UHBD INTERFACE FUNCTIONS                              #
#*****************************************************************************#

def runPrepares():
    """
    Run prepares in UHBD package, fixing problems with input files it 
    generates.
    """

    # RUN PREPARES
    os.spawnl(os.P_WAIT,prep,'')

    # FIX SITESINPR (remove second line (i.e. N terminus))
    f = open('sitesinpr.pdb','r')
    sitesinpr = f.readlines()
    f.close()
    
    """
    See **** below.
    sitesinpr.pop(1)
    """
    
    g = open('sitesinpr.pdb','w')
    g.writelines(sitesinpr)
    g.close()


    # FIX TITRAA (removes N and C-terminal groups)
    f = open('titraa.pdb','r')
    titraa = f.readlines()
    f.close()

    # remove last line (C-terminal oxygen)
    titraa.pop(-1)
   
    """"
    **** CHANGE! ****
    New compile of UHBD does not have bug at N-terminus where it keeps all
    N-terminal groups.  This was my attempt to fix the N-terminal problem for
    previous compiles.  Since this is no longer a problem, I'lve commented
    my fix out.
    
    #Removes titrating N-terminus
    j = 0
    for line in titraa:
        i = line.split()
        i = int(i[1])
        if i < j:
            for k in range(j):
                titraa.pop(0)
            break
        j += 1
    """

    g = open('titraa.pdb','w')
    g.writelines(titraa)
    g.close()


def runUHBD(inputfile,outputfile):
    """Runs UHBD from an inputfile, putting standard out to outputfile."""
    f = open(inputfile,'r')
    inp = f.read()
    f.close()

    cin, cout = os.popen2(uhbd)
    cin.write(inp)
    cin.close()
    out = cout.read()
    cout.close()

    g = open(outputfile,'w')
    g.write(out)
    g.close()


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
    shutil.copy(os.path.join(script_path,'inputs','pkaS-doinp.inp'),
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

    inp[7] = "%s\n" % start_index
    inp[9] = "%i\n" % (end_index + 2)
    inp[11] = "%s\n" % number_his
    inp[12] = "%s\n" % hisstring
    inp[15] = "%3.1F%s\n" % (interval,' 65 65 65')
    inp[24] = "78.5 %.1F\n" % dielectric
    inp[30] = "%s\n" % number_cys
    inp[31] = "%s\n" % cysstring

    if ionic_strength >= 0:
        inp[26] = "%.1F 2.0\n" % ionic_strength

    if number_his == 0: inp[12] = ''
    if number_cys == 0: inp[31] = ''

    # write input file
    g = open('pkaS-doinp.inp','w')
    g.writelines(inp)
    g.close()
    
    
#*****************************************************************************#
#                                   MAIN                                      #
#*****************************************************************************#
    
def main(filename,pH_start,pH_stop,pH_interval,ionic_strength,dielectric):
    """Peform full UHBD calculation (pH titration) on filename."""
    
    # SETUP UHBD CALCULATIONS
    setupInp(filename,ionic_strength,dielectric)

    print 'Prepares'
    runPrepares()

    print 'uhbdini'
    runUHBD('pkaS-uhbdini.inp','pkaS-uhbdini.out')

    print 'Getgrids'
    os.spawnl(os.P_WAIT,getgrids,'')

    # RUN STOPNOW LOOP
    print 'Running stopnow loop.'
    while os.path.isfile('stopnow') == False:
        os.spawnl(os.P_WAIT,doinps,'')
        runUHBD('uhbdpr.inp','uhbdpr.out')
        runUHBD('uhbdaa.inp','uhbdaa.out')
        os.spawnl(os.P_WAIT,getpots,'')

    # RUN HYBRID
    shutil.copy('potentials','pkaS-potentials')
    shutil.copy('sitesinpr.pdb','pkaS-sitesinpr.pdb')

    hybrid_run = os.popen(hybrid,'w')
    hybrid_run.write("%s\n%s\n%s\n" % (pH_start,pH_stop,pH_interval))
    hybrid_run.close()
