"""
ArgParser.py

Defines classes and subclasses necessary to parse the command line.
"""

__author__ = "Michael J. Harms"


# Load builtin modules
import os, sys, copy
try:
    from optparse import OptionParser
    from optparse import Option, OptionValueError
except:
    error = """
    optparse module is missing (introduced in Python 2.3). Please verify that
    your Python version is up-to-date and that optparse is available. You are
    using Python %s """ % sys.version.split()[0]

# Load pyUHBD modules
import os
from common import SystemOps

default_location = os.path.split(__file__)[0]
default_location = os.path.split(default_location)[0]
default_location = os.path.realpath(os.path.join(default_location,"parameters"))

# ---------- Class/function definitions --------------------

def checkFile(option, opt, value):
    """
    Function that verifies a file exists in either calling directory or default
    directory.  Called by SuperOption istance if the type is "file."
    """

    # See if it's in the calling direcotry
    if os.path.isfile(os.path.join(os.getcwd(),os.path.split(value)[-1])):
        return os.path.join(os.getcwd(),os.path.split(value)[-1])
    else:
        default_file = os.path.join(default_location,value)
        if os.path.isfile(default_file):
            return default_file
        else:
            raise OptionValueError("option %s: file %r not found!" %(opt,value))


class SuperOption(Option):
    """
    Subclass of Option that has a "file" type.
    """

    TYPES = Option.TYPES + ("file",)
    TYPE_CHECKER = copy.copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["file"] = checkFile


class Parameters:
    """
    A simple class to store and edit calculation parameters as needed.  It is
    initialized from an instance of OptionParser.options.
    """

    def __init__(self,opt_options):
        """
        Load optparse options into self.__dict__.
        """
        self.__dict__ = dict([(k,opt_options.__dict__[k])
                              for k in opt_options.__dict__.keys()])
