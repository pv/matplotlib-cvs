"""
See pcolor_demo2 for a much faster way of generating pcolor plots
"""
from __future__ import division
from matplotlib.matlab import *

def func3(x,y):
    return (1- x/2 + x**5 + y**3)*exp(-x**2-y**2)


# make these smaller to increase the resolution
dx, dy = 0.05, 0.05

x = arange(-3.0, 3.0, dx)
y = arange(-3.0, 3.0, dy)
X,Y = meshgrid(x, y)

Z = func3(X, Y)
cmap = ColormapJet(500)

ax = subplot(111)
imshow(Z, cmap)
ax.set_image_extent(-3, 3, -3, 3)
#savefig('pcolor_demo2')
show()

    