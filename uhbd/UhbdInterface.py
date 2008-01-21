"""
UhbdInterface.py

Module to interface with uhbd binaries.
"""

__author__ = "Michael J. Harms"

# ---------- Initialize module --------------------

import __init__, UhbdFullFunctions, UhbdSingleFunctions, UhbdErrorCheck
import os, shutil
from common import SystemOps, Error

# Set up uhbd binary
global uhbd
bin_path = SystemOps.checkEnvironVariable('UHBD')
uhbd = os.path.join(bin_path,'uhbd')
if not os.path.isfile(uhbd):
    raise OSError("uhbd binary not found in $UHBD (%s)" % bin_path)

# ---------- Function definitions --------------------

def runUHBD(inputfile,outputfile):
    """
    Runs UHBD from an inputfile, putting standard out to outputfile.
    """

    global uhbd

    print "uhbd < %s > %s" % (inputfile,outputfile)

    f = open(inputfile,'r')
    inp = f.read()
    f.close()

    try:
        cin, cout = os.popen2(uhbd)
        cin.write(inp)
        cin.close()
        out = cout.read()
        cout.close()
    except IOError:
        err = "uhbd binary (%s) not executable" % uhbd
        raise IOError(err)

    status = UhbdErrorCheck.checkOut(out,outputfile)

    g = open(outputfile,'w')
    g.write(out)
    g.close()

    if status[0] == 1:
        raise Error.UhbdError(status[1]) 

def runSingleCalculation(calc_param):
    """Peform pH titration on filename."""

    # Set up aliases for binaries
    getgrid = os.path.join(bin_path,'getgrids')
    doinp = os.path.join(bin_path,'doinps')
    getpot = os.path.join(bin_path,'getpots')
    hybrid = os.path.join(bin_path,'hybrids')

    # Make sure that all of the executables exist:
    to_check = [getgrid, doinp, getpot, hybrid]
    checksum = sum([os.path.isfile(f) for f in to_check])
    if checksum != len(to_check):
        raise OSError("Not all required binaries in $UHBD (%s)" % bin_path)

    print 'prepares'
    UhbdSingleFunctions.runPrepares(calc_param)

    runUHBD('pkaS-uhbdini.inp','pkaS-uhbdini.out')

    print 'getgrids'
    SystemOps.runBin(getgrid)

    print 'Running stopnow loop.'
    while os.path.isfile('stopnow') == False:
        SystemOps.runBin(doinp)
        runUHBD('uhbdpr.inp','uhbdpr.out')
        runUHBD('uhbdaa.inp','uhbdaa.out')
        SystemOps.runBin(getpot)

    shutil.copy('potentials','pkaS-potentials')
    shutil.copy('sitesinpr.pdb','pkaS-sitesinpr.pdb')

    # Run hybrid
    hybrid_run = os.popen(hybrid,'w')
    hybrid_run.write("%s\n%s\n%s\n" % calc_param.ph_param)
    hybrid_run.close()


def runFullCalculation(calc_param):
    """Peform pH titration on filename."""

    # Set up aliases for binaries
    prep = os.path.join(bin_path,'prepare')
    getgrid = os.path.join(bin_path,'getgrid')
    doinp = os.path.join(bin_path,'doinp')
    getpot = os.path.join(bin_path,'getpot')
    hybrid = os.path.join(bin_path,'hybrid')

    # Make sure that all of the executables exist:
    to_check = [prep, getgrid, doinp, getpot, hybrid]
    checksum = sum([os.path.isfile(f) for f in to_check])
    if checksum != 5:
        raise OSError("Not all required binaries in $UHBD (%s)" % bin_path)

    print 'Prepare'
    UhbdFullFunctions.runPrepare(calc_param)

    runUHBD('uhbdini.inp','uhbdini.out')

    print 'Getgrid'
    SystemOps.runBin(getgrid)

    print 'Running stopnow loop.'
    while os.path.isfile('stopnow') == False:
        SystemOps.runBin(doinp)
        runUHBD('uhbdpr.inp1','uhbdpr.out1')
        runUHBD('uhbdpr.inp2','uhbdpr.out2')
        runUHBD('uhbdaa.inp1','uhbdaa.out1')
        runUHBD('uhbdaa.inp2','uhbdaa.out2')
        SystemOps.runBin(getpot)

        shutil.move('tempallG.pdb','allgroups.pdb')
        shutil.move('tempallR.pdb','allresidues.pdb')
        shutil.move('tmp_for_pot.dat','for_pot.dat')

    shutil.copy('potentials','pkaF-potentials')

    # Run hybrid
    hybrid_run = os.popen(hybrid,'w')
    hybrid_run.write("%s\n%s\n%s\n" % calc_param.ph_param)
    hybrid_run.close()



