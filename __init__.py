"""
__init__.py:

Initializes pyUHBD.  At this point the biggest function of this module is to 
record the calling directory (invocation_path).  Work can then be done in a 
temporary directory and then copied to calling directory. NOTE!  It is important
that the invocation_path is defined before uhbd is imported.  uhbd uses 
__init__.invocation_path!

Version information:

0.4:    060113

0.4.1:  060403
    Hokiness fix.  Changed from some_path = x + os.sep + y to os.path.join(x,y)
0.5.0:  060519
    Changed to __init__ per python convention.
"""

__author__ = "Michael J. Harms"
__date__ = "060519"
__version__ = "0.5.0"


import os, sys

invocation_path = os.getcwd()

import UhbdInterface
