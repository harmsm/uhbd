"""initialize.py (v 0.4).
Initializes control scripts for UHBD... Every script
that can be invoked by the user imports this module.  This assures that the
code knows where the original working directory resides.
"""

__author__ = "Michael J. Harms"
__date__ = "1/13/06"
__version__ = "0.4"

import os
import sys

# invocation path is where the script was started. This allows the user to
# execute the script in an arbitrary directory.
invocation_path = os.getcwd()
invocation_path += os.sep

import uhbd