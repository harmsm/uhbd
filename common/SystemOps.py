"""
SystemOps.py

A set of functions for interacting with the native file system.
"""

__author__ = "Michael J. Harms"

# import modules
import os, shutil, sys

def checkEnvironVariable(variable_name):
    """
    Checks the definition of some environment variable specifying directory.
    Returns the path to that directory.
    """

    try:
        var = os.environ[variable_name]
    except KeyError:
        raise OSError("Environment variable %s not defined!" % variable_name)

    return var


def makeDir(dir):
    """
    Create directory dir, recursively filling in directories if need be.  This
    will wipe out the directory if it exists (i.e. checking before overwrite 
    should be done elsewhere).
    """

    try:
        os.mkdir(dir)
    except OSError, value:
        if value[0] == 17:
            # If the directory exists, delete its contents. (This is to prevent
            # fortran "file exists" type errors).
            dir_contents = [os.path.join(dir,f) for f in os.listdir(dir)]
            dir_contents = [f for f in dir_contents if os.path.isfile(f)]
            for f in dir_contents:
                os.remove(f)
        elif value[0] == 2:
            # The directory does not exist: begin recursion
            dir_list = os.path.split(dir)
            makeDir(dir_list[0])
            makeDir(dir)
        else:
            # Something else went wrong
            raise IOError("Could not create directory %s!" % dir)


def readFile(some_file):
    """
    Reads an ascii file if it exists, removes blank lines, whitespace, and
    comments (denoted by #), and spits out a list of lines.
    """

    # Make sure the file is truly a file
    if os.path.isfile(some_file):

        # Read in the file
        f = open(some_file)
        lines = f.readlines()
        f.close()

        # Strip out comments, extra whitespace, and blank lines
        lines = [l for l in lines if l[0] != "#"]
        lines = [l.strip() for l in lines if len(l.strip()) != 0]

        return lines
    else:
        raise IOError("%s does not exist" % some_file)


def runBin(some_bin):
    """
    Runs a binary file, checking for a variety of errors.
    """

    status = os.spawnl(os.P_WAIT,some_bin,'')
    if status == 127:
        err = "Problem with binary %s" % some_bin
        raise IOError(err)

def runCleanup(calc_param):
    """
    Delete temporary files from a uhbd calculation.
    """

    # Only if the user has not specified to keep temporary files
    if not calc_param.keep_temp:

        # Create list of files to delete, ignoring keep_files and directories
        file_list = os.listdir('./')
        file_list = [f for f in file_list if f not in calc_param.keep_files]
        file_list = [f for f in file_list if os.path.isfile(f)]

        # Delete files
        for f in file_list:
            os.remove(f)
