from matplotlib.numerix import which

if which[0] == "numarray":
    from numarray.linear_algebra import *
elif which[0] == "numeric":
    from LinearAlgebra import *
elif which[0] == "numpy":
    from numpy.linalg import *
else:
    raise RuntimeError("invalid numerix selector")
