"""
initialize.py:

Initializes control scripts for UHBD. Every script that can be invoked by the
user imports this module.  This assures that the code knows where the original
working directory resides.
"""

"""
Version information:

0.4:    060113

0.4.1:  060403
    Hokiness fix.  Changed from some_path = x + os.sep + y to os.path.join(x,y)
"""

__author__ = "Michael J. Harms"
__date__ = "060403"
__version__ = "0.4.1"


import os
import sys

# invocation path is where the script was started. This allows the user to
# execute the script in an arbitrary directory.
invocation_path = os.getcwd()
#invocation_path += os.sep


import uhbd