#!/bin/env python
'''
Plot lines with points masked out.

This would typically be used with gappy data, to
break the line at the data gaps.
'''

import matplotlib.numerix.ma as M
from pylab import *

x = M.arange(0, 2*pi, 0.02)
y = M.sin(x)
y1 = sin(2*x)
y2 = sin(3*x)
ym1 = M.masked_where(y1 > 0.5, y1)
ym2 = M.masked_where(y2 < -0.5, y2)

lines = plot(x, y, 'r', x, ym1, 'g', x, ym2, 'bo')
set(lines[0], linewidth = 4)
set(lines[1], linewidth = 2)
set(lines[2], markersize = 10)

legend( ('No mask', 'Masked if > 0.5', 'Masked if < -0.5') ,
        loc = 'upper right')
title('Masked line demo')
savefig('test.svg')
#savefig('test.ps')
show()