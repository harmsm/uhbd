"""
    uhbd_interface.py:
    Functions/data necessary to perform a UHBD calculation on a single pdb file.
    Core of the batch run suite.
    
    Required files:
        pkaS-doinp.inp (in ./inputs/)
        pkaS.dat       (in ./inputs/)

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

0.6.0:  060519
    Restructured call structure.  New main file to look at for interface changes
    is pyUHBD.py.  Changed name of this file to UhbdInterface.py
    

0.6.1: 060522
    Put checkEnvironVariable in function.
"""

__author__ = "Michael J. Harms"
__version__ = "0.6.0"
__date__ = "060519"


#*****************************************************************************#
#                            INITALIZE MODULE                                 #
#*****************************************************************************#

# import modules
import FileOps
import os, shutil

# Take bin_path from environment variable UHBD and make it points to a valid
# directory.
bin_path = FileOps.checkEnvironVariable('UHBD')

# set up sundry strings to make code easier to read
prep = os.path.join(bin_path,'prepares')
uhbd = os.path.join(bin_path,'uhbd')
getgrids = os.path.join(bin_path,'getgrids')
doinps = os.path.join(bin_path,'doinps')
getpots = os.path.join(bin_path,'getpots')
hybrid = os.path.join(bin_path,'hybrid')

# Function definitions

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


    
    
#*****************************************************************************#
#                                   MAIN                                      #
#*****************************************************************************#
    
def main(filename,pH_start,pH_stop,pH_interval,ionic_strength,dielectric):
    """Peform full UHBD calculation (pH titration) on filename."""
    
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
