"""

matlab (and matplotlib) allow you to use set and get to set and get
object properties, as well as to do introspection on the object

set
    To set the linestyle of a line to be dashed, you can do

      >>> line, = plot([1,2,3])
      >>> set(line, linestyle='--')

    If you want to know the valid types of arguments, you can provide the
    name of the property you want to set without a value

      >>> set(line, 'linestyle')
          linestyle: [ '-' | '--' | '-.' | ':' | 'steps' | 'None' ]

    If you want to see all the properties that can be set, and their
    possible values, you can do

        >>> set(line)

    set operates on a single instance or a list of instances.  If you are
    in quey mode introspecting the possible values, only the first
    instance in the sequnce is used.  When actually setting values, all
    the instances will be set.  Eg, suppose you have a list of two lines,
    the following will make both lines thicker and red

        >>> x = arange(0,1.0,0.01)
        >>> y1 = sin(2*pi*x)
        >>> y2 = sin(4*pi*x)
        >>> lines = plot(x, y1, x, y2)
        >>> set(lines, linewidth=2, color='r')


get:

    get returns the value of a given attribute.  You can use get to query
    the value of a single attribute

        >>> get(line, 'linewidth')
            0.5

    or all the attribute/value pairs

    >>> get(line)
        aa = True
        alpha = 1.0
        antialiased = True
        c = b
        clip_on = True
        color = b
        ... long listing skipped ...
  
Alisases:

  To reduce keystrokes in interactive mode, a number of properties
  have short aliases, eg 'lw' for 'linewidth' and 'mec' for
  'markeredgecolor'.  When calling set or get in introspection mode,
  these properties will be listed as 'fullname or aliasname', as in

  

  
"""

from matplotlib.matlab import *


x = arange(0,1.0,0.01)
y1 = sin(2*pi*x)
y2 = sin(4*pi*x)
lines = plot(x, y1, x, y2)
l1, l2 = lines
set(lines, linestyle='--')       # set both to dashed 
set(l1, linewidth=2, color='r')  # line1 is thick and red
set(l2, linewidth=1, color='g')  # line2 is thicker and green


print 'Line setters'
set(l1)
print 'Line getters'
get(l1)

print 'Rectangle setters'
set(gca().axesPatch)
print 'Rectangle getters'
get(gca().axesPatch)

t = title('Hi mom')
print 'Text setters'
set(t)
print 'Text getters'
get(t)

show()