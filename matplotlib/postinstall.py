"""
See for example
http://www.geocrawler.com/archives/3/14884/2002/10/0/9979630/


"""

s = r"""#### MATPLOTLIBRC FORMAT 
# This is a sample matplotlib configuration file
# It should be placed in your home dir (Linux and friends) or
# in the matplotlib data path, is, where matplotlib installs it's
# data files (fonts, etc).  On windows, this would be, for example,
# C:\Python23\share\matplotlib
#
# This file is best viewed in a editor which supports python mode
# syntax highlighting
#
# Blank lines, or lines starting with a comment symbol, are ignored,
# as are trailing comments.  Other lines must have the format
#
#   key : val   # optional comment
#
# Colors: for the color values below, you can either use 
#  - a matplotlib color string, such as r, k, or b
#  - an rgb tuple, such as (1.0, 0.5, 0.0)
#  - a hex string, such as ff00ff  (no '#' symbol)
#  - a scalar grayscale intensity such as 0.75

#### CONFIGURATION BEGINS HERE
backend      : GTK       # the default backend
numerix      : numeric   # Numeric or numarray
interactive  : False     # see http://matplotlib.sourceforge.net/interactive.html

### LINES
# See http://matplotlib.sourceforge.net/matplotlib.lines.html for more
# information on line properties.  Note antialiased rendering looks
# better, but can be slower.  If you want fast antialiased rendering,
# use the agg backend (or TkAgg, or GTKAgg)
lines.linewidth   : 0.5     # line width in points
lines.linestyle   : -       # solid line
lines.color       : b       # blue; color format or hex string
lines.markersize  : 6       # markersize, in points
lines.antialiased : True    # render lines in antialised (no jaggies)
lines.data_clipping : False # Use data clipping in addition to viewport
                            # clipping.  Useful if you plot long data
                            # sets with only a fraction in the viewport

### TEXT
# text properties used by text.Text.  See
# http://matplotlib.sourceforge.net/matplotlib.Text.html for more
# information on text properties
text.fontname : Times   # default font name
text.fontsize : 10      # default size used by axes.text
text.color    : k       # black

### AXES
# default face and edge color, default tick sizes,
# default fontsizes for ticklabels, and so on
axes.facecolor     : w      # background color; white
axes.edgecolor     : k      # edge color; black
axes.linewidth     : 1.0    # edge linewidth
axes.grid          : False  # display grid or not
axes.titlesize     : 14     # fontsize of the axes title
axes.labelsize     : 12     # fontsize of the x any y labels
axes.labelcolor    : k      # black 

### TICKS
tick.size      : 4      # tick size in points
tick.color     : k      # color of the tick labels 
tick.labelsize : 10     # fontsize of the tick labels

### FIGURE
figure.figsize   : 8, 6    # figure size in inches
figure.dpi       : 80      # figure dots per inch
figure.facecolor : 0.75    # figure facecolor; 0.75 is scalar gray
figure.edgecolor : w       # figure edgecolor; w is white

### SAVING FIGURES
# the default savefig params can be different for the GUI backends.
# Eg, you may want a higher resolution, or to make the figure
# background white
savefig.dpi       : 100      # figure dots per inch
savefig.facecolor : w        # figure facecolor; 0.75 is scalar gray
savefig.edgecolor : w        # figure edgecolor; w is white

"""
import sys, os
import distutils.sysconfig

if sys.platform[:3] != 'win':
    sys.exit()

target = os.path.join(distutils.sysconfig.PREFIX,
                      'share', 'matplotlib', '.matplotlibrc')
if not os.path.exists(target):
    
    print 'Writing %s' % target
    file(target, 'w').write(s)
    file_created(target)
else:
    print 'matplotlibrc file %s already exists' % target
    