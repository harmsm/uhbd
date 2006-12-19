"""
FileOps.py
A set of functions that interact with the system.
"""

__author__ = "Michael J. Harms"
__date__ = "060817"
__version__ = "0.1"

# import modules
import os, shutil, time, sys, random

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



# define location of script (for temporary folder creation)
script_path = __file__
script_path = os.path.split(script_path)[0]

tmp_path = checkEnvironVariable("HOME")
tmp_path = os.path.join(tmp_path,".pyUHBD")
if not os.path.isdir(tmp_path):
    os.mkdir(tmp_path)
