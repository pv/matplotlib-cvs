"""numerix  imports either Numeric or numarray based on various selectors.

0.  If the value "--numarray" or "--Numeric" is specified on the
command line, then numerix imports the specified array package.

1. The value of numerix in ~/.matplotlibrc: either Numeric or numarray

2. If none of the above is done, the default array package is Numeric.
Because the .matplotlibrc always provides *some* value for numerix (it
has it's own system of default values), this default is most likely
never used.

To summarize: the  commandline is examined first, the  rc file second,
and the default array package is Numeric.  
"""

import sys, os
from matplotlib import rcParams, verbose

which = None, None

# First, see if --numarray or --Numeric was specified on the command
# line:
if hasattr(sys, 'argv'):        #Once again, Apache mod_python has no argv
    for a in sys.argv:
        if a in ["--Numeric", "--numeric", "--NUMERIC",
                 "--Numarray", "--numarray", "--NUMARRAY"]:
            which = a[2:], "command line"
            break

if which[0] is None:     
    try:  # In theory, rcParams always has *some* value for numerix.
        which = rcParams['numerix'], "rc"
    except KeyError:
        pass

# If all the above fail, default to Numeric. Most likely not used.
if which[0] is None:
    which = "numeric", "defaulted"

which = which[0].strip().lower(), which[1]
if which[0] not in ["numeric", "numarray"]:
    verbose.report_error(__doc__)
    raise ValueError("numerix selector must be either 'Numeric' or 'numarray' but the value obtained from the %s was '%s'." % (which[1], which[0]))

if which[0] == "numarray":
    from na_imports import *
    import numarray
    version = 'numarray %s'%numarray.__version__

elif which[0] == "numeric":
    from nc_imports import *
    import Numeric
    version = 'Numeric %s'%Numeric.__version__
else:
    raise RuntimeError("invalid numerix selector")

verbose.report('numerix %s'%version)
# a bug fix for blas numeric suggested by Fernando Perez
matrixmultiply=dot