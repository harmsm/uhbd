"""
UhbdErrorCheck.py

A set of functions to check for errors in uhbd output.
"""


def checkOut(out,filename):
    """
    Check for errors in uhbdaa and uhbdpr.out.
    """
    
    lines = out.split("\n")

    # Check for fatal errors
    hash = [l[1:6] for l in lines]
    try:
        err_index = hash.index("FATAL")
    
        err = ["%s\n" % (80*"-")]
        err.append("Fatal Error in %s:\n" % filename)
        err.extend(["%s\n" % (80*"-")])
        err.append("tail -5 %s\n\n" % filename)
        err.extend(["%s\n" % l for l in lines[-5:]])
        
        return 1, "".join(err)
    
    except ValueError:
        return 0, ""



