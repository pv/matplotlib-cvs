"""
Abstract base classes definine the primitives that renderers and
graphics contexts must implement to serve as a matplotlib backend
"""

from __future__ import division
import sys
from numerix import array, sqrt, pi, log

from cbook import True, False

from cbook import is_string_like, enumerate, True, False
from colors import colorConverter
from numerix import asarray, ones, Float
from patches import Rectangle
from transforms import lbwh_to_bbox

class RendererBase:

    def open_group(self, s):
        'open a grouping element with label s'
        pass

    def close_group(self, s):
        'close a grouping element with label s'
        pass
    
    def get_canvas_width_height(self):
        'return the canvas width and height in display coords'
        return 1, 1

    def get_text_width_height(self, s, fontsize, ismath=False):
        """
        get the width and height in display coords of the string s
        with fontsize in points
        """
        return 1,1

                              
    def flipy(self):
        'return true if y small numbers are top for renderer'
        return True
    
    def points_to_pixels(self, points):
        """
        convert points to display units; unless your backend doesn't
        have dpi, eg, postscript, you need to overrride this function
        """
        return points  

    def get_text_extent(self, text):
        """
        Get the text extent in window coords
        """
        return lbwh_to_bbox(0,0,1,1)  # your values here


    def draw_arc(self, gcEdge, gcFace, x, y, width, height, angle1, angle2):
        """
        Draw an arc centered at x,y with width and height and angles
        from 0.0 to 360.0

        If gcFace is not None, fill the rectangle with it.  gcEdge
        is a GraphicsContext instance
        """
        pass  # derived must override

    def draw_image(self, x, y, im, origin, bbox):
        """
        Draw the Image instance into the current axes; x is the
        distance in pixels from the left hand side of the canvas. y is
        the distance from the origin.  That is, if origin is upper, y
        is the distance from top.  If origin is lower, y is the
        distance from bottom

        origin is 'upper' or 'lower'

        bbox is a matplotlib.transforms.BBox instance for clipping, or
        None
        """
        print >>sys.stderr, 'This backend does not yet support images'

    def draw_line(self, gc, x1, y1, x2, y2):
        """
        Draw a single line from x1,y1 to x2,y2
        """
        pass  # derived must override

    def draw_poly_collection(
        self, verts, transform, clipbox, facecolors, edgecolors,
        linewidths, antialiaseds, offsets, transOffset):
        """
        Draw a polygon collection

        verts are a sequence of polygon vectors, where each polygon
        vector is a sequence of x,y tuples of vertices

        facecolors and edgecolors are a sequence of RGBA tuples
        linewidths are a sequence of linewidths
        antialiaseds are a sequence of 0,1 integers whether to use aa
        """

        Nface = len(facecolors)
        Nedge = len(edgecolors)
        Nlw = len(linewidths)
        Naa = len(antialiaseds)

        usingOffsets = offsets is not None
        Noffsets = 0
        Nverts = len(verts)
        if usingOffsets:
            Noffsets = len(offsets)

        N = max(Noffsets, Nverts)

        gc = self.new_gc()
        if clipbox is not None: gc.set_clip_rectangle(clipbox.get_bounds())

        for i in xrange(N):

            
            rf,gf,bf,af = facecolors[i % Nface]
            re,ge,be,ae = edgecolors[i % Nedge]
            if af==0: rgbFace = None
            else: rgbFace = rf,gf,bf
            # the draw_poly interface can't handle separate alphas for
            # edge and face so we'll just use the maximum
            alpha = max(af,ae)
            
            gc.set_foreground( (re,ge,be), isRGB=True)
            gc.set_alpha( alpha )
            gc.set_linewidth( linewidths[i % Nlw] )
            gc.set_antialiased( antialiaseds[i % Naa] )
            #print 'verts', zip(thisxverts, thisyverts)

            tverts = transform.seq_xy_tups(verts[i % Nverts])
            if usingOffsets:
                xo,yo = transOffset.xy_tup(offsets[i % Noffsets])
                tverts = [(x+xo,y+yo) for x,y in tverts]

            self.draw_polygon(gc, rgbFace, tverts)

    def draw_regpoly_collection(
        self, clipbox, offsets, transOffset, verts, sizes,
        facecolors, edgecolors, linewidths, antialiaseds):
        """
        Draw a regular poly collection

        offsets is a sequence is x,y tuples and transOffset maps this
        to display coords

        verts are the vertices of the regular polygon at the origin

        sizes are the area of the circle that circumscribes the
        polygon in points^2

        facecolors and edgecolors are a sequence of RGBA tuples
        linewidths are a sequence of linewidths
        antialiaseds are a sequence of 0,1 integers whether to use aa
        """
        xverts, yverts = zip(*verts)
        xverts = asarray(xverts)
        yverts = asarray(yverts)
                   
        Nface = len(facecolors)
        Nedge = len(edgecolors)
        Nlw = len(linewidths)
        Naa = len(antialiaseds)
        Nsizes = len(sizes)


        gc = self.new_gc()
        if clipbox is not None: gc.set_clip_rectangle(clipbox.get_bounds())

        for i, loc in enumerate(offsets):
            xo,yo = transOffset.xy_tup(loc)
            #print 'xo, yo', loc, (xo, yo)
            scale = sizes[i % Nsizes]

            thisxverts = scale*xverts + xo
            thisyverts = scale*yverts + yo
            #print 'xverts', xverts
            rf,gf,bf,af = facecolors[i % Nface]
            re,ge,be,ae = edgecolors[i % Nedge]
            if af==0:
                rgbFace = None
            else:
                rgbFace = rf,gf,bf
            # the draw_poly interface can't handle separate alphas for
            # edge and face so we'll just use 
            alpha = max(af,ae)
            
            gc.set_foreground( (re,ge,be), isRGB=True)
            gc.set_alpha( alpha )
            gc.set_linewidth( linewidths[i % Nlw] )
            gc.set_antialiased( antialiaseds[i % Naa] )
            #print 'verts', zip(thisxverts, thisyverts)
            self.draw_polygon(gc, rgbFace, zip(thisxverts, thisyverts))

        
        

    def draw_line_collection(self, segments, transform, clipbox,
                             colors, linewidths, antialiaseds,
                             offsets, transOffset):
        """
        This is a function for optimized line drawing.  If you need to
        draw many line segments with similar properties, it is faster
        to avoid the overhead of all the object creation etc.  The
        lack of total configurability is compensated for with
        efficiency.  Hence we don't use a GC and many of the line
        props it supports.  See matplotlib.collections for more
        details

        sements is a sequence of ( line0, line1, line2), where linen =
        (x0, y0), (x1, y1), ... (xm, ym).  Each line can be a
        different length

        transform is used to Transform the lines

        clipbox is a  xmin, ymin, width, height clip rect
        
        colors is a tuple of RGBA tuples

        linewidths is a tuple of linewidths

        antialiseds is a tuple of ones or zeros indicating whether the
        segment should be aa or not

        offsets, if not None, is a list of x,y offsets to translate
        the lines by after transoff is used to transform the offset
        coords

        This function is intended to be overridden by the backend
        level in extension code for backends that want fast line
        collection drawing.  Here is is implemented using native
        backend calls and may be slow
        """

        gc = self.new_gc()

        i = 0
        Nc = len(colors)
        Nlw = len(linewidths)
        Naa = len(antialiaseds)

        usingOffsets = offsets is not None
        Noffsets = 0
        Nsegments = len(segments)
        if usingOffsets:
            Noffsets = len(offsets)

        N = max(Noffsets, Nsegments)
            
        gc.set_clip_rectangle(clipbox.get_bounds())


        for i in xrange(N):
            x, y = zip(*segments[i % Nsegments])
            x, y = transform.numerix_x_y(array(x), array(y))

            color = colors[i % Nc]
            rgb = color[0], color[1], color[2]
            alpha = color[-1]
            
            gc.set_foreground( rgb, isRGB=True)
            gc.set_alpha( alpha )
            gc.set_linewidth( linewidths[i % Nlw] )
            gc.set_antialiased( antialiaseds[i % Naa] )
            if usingOffsets:
                xo, yo = transOffset.xy_tup(offsets[i % Noffsets])
                x += xo
                y += yo
            self.draw_lines(gc, x, y)
            i += 1
            
    def draw_lines(self, gc, x, y):
        """
        x and y are equal length arrays, draw lines connecting each
        point in x, y
        """
        pass  # derived must override

    def draw_point(self, gc, x, y):
        """
        Draw a single point at x,y
        """
        pass  # derived must override

    def draw_polygon(self, gc, rgbFace, points):
        """
        Draw a polygon.  points is a len vertices tuple, each element
        giving the x,y coords a vertex

        If rgbFace is not None, fill the poly with it.  gc
        is a GraphicsContext instance

        """  
        pass # derived must override

    def draw_rectangle(self, gcEdge, gcFace, x, y, width, height):
        """
        Draw a rectangle with lower left at x,y with width and height.

        If gcFace is not None, fill the rectangle with it.  gcEdge
        is a GraphicsContext instance
        """
        pass # derived must override

    def strip_math(self, s):
        remove = (r'\rm', '\cal', '\tt', '\it', '\\', '{', '}')
        s = s[1:-1]
        for r in remove:  s = s.replace(r,'')
        return s
    
    def draw_text(self, gc, x, y, s, prop, angle, ismath=False):
        """
        Draw string s at x,y (display coords) with font properties
        instance prop at angle in degrees
        """
        pass

    
    def new_gc(self):
        """
        Return an instance of a GraphicsContextBase
        """
        return GraphicsContextBase()



class GraphicsContextBase:    

    # a mapping from dash styles to suggested offset, dash pairs
    _dashd = {
        'solid'   : (None, None),
        'dashed'  : (0, array([6.0, 6.0])),
        'dashdot' : (0, array([3.0, 5.0, 1.0, 5.0])),
        'dotted'  : (0, array([1.0, 3.0]))
              }

    def __init__(self):
        self._rgb = (0.0, 0.0, 0.0)
        self._linewidth = 1
        self._capstyle = 'butt'
        self._joinstyle = 'miter'
        self._dashes = None, None
        self._cliprect = None
        self._linestyle = 'solid'
        self._antialiased = 1  # use 0,1 not True, False for extension code
        self._alpha = 1.0
    
    def get_antialiased(self):
        "Return true if the object shuold try to do antialiased rendering"
        return self._antialiased

    def get_clip_rectangle(self):
        """
        Return the clip rectangle as (left, bottom, width, height)
        """
        return self._cliprect

    def get_dashes(self):
        """
        Return the dash information as an offset dashlist tuple The
        dash list is a even size list that gives the ink on, ink off
        in pixels.  See p107 of to postscript BLUEBOOK for more info

        Default value is None
        """
        return self._dashes

    def get_alpha(self):
        """
        Return the alpha value used for blending - not supported on
        all backends
        """
        return self._alpha

    def get_capstyle(self):
        """
        Return the capstyle as a string in ('butt', 'round', 'projecting')
        """
        return self._capstyle

    def get_joinstyle(self):
        """
        Return the line join style as one of ('miter', 'round', 'bevel')
        """
        return self._joinstyle

    def get_linestyle(self, style):
        """
        Return the linestyle: one of ('solid', 'dashed', 'dashdot',
        'dotted').  
        """
        return self._linestyle

    def get_rgb(self):
        """
        returns a tuple of three floats from 0-1.  color can be a
        matlab format string, a html hex color string, or a rgb tuple
        """
        return self._rgb

    def set_antialiased(self, b):
        """
        True if object should be drawn with antialiased rendering
        """

        # use 0, 1 to make life easier on extension code trying to read the gc
        if b: self._antialiased = 1
        else: self._antialiased = 0

    def set_clip_rectangle(self, rectangle):
        """
        Set the clip rectangle with sequence (left, bottom, width, height)
        """
        self._cliprect = rectangle



    def set_alpha(self, alpha):
        """
        Set the alpha value used for blending - not supported on
        all backends
        """
        self._alpha = alpha

    def set_linestyle(self, style):
        """
        Set the linestyle to be one of ('solid', 'dashed', 'dashdot',
        'dotted').  
        """
        if style not in ('solid', 'dashed', 'dashdot', 'dotted'):
            error_msg('Unrecognized linestyle.  Found %s' % js)
            return
        self._linestyle = style
        offset, dashes = self._dashd[style]
        self.set_dashes(offset, dashes)

    def set_dashes(self, dash_offset, dash_list):
        """
        Set the dash style for the gc.  dash offset is the offset
        (usually 0).  Dash list specifies the on-off sequence as
        points
        """
        self._dashes = dash_offset, dash_list
    
    def set_foreground(self, fg, isRGB=None):
        """
        Set the foreground color.  fg can be a matlab format string, a
        html hex color string, an rgb unit tuple, or a float between 0
        and 1.  In the latter case, grayscale is used.

        The GraphicsContext converts colors to rgb internally.  If you
        know the color is rgb already, you can set isRGB to True to
        avoid the performace hit of the conversion
        """
        if isRGB:
            self._rgb = fg
        else:
            self._rgb = colorConverter.to_rgb(fg)

    def set_graylevel(self, frac):
        """
        Set the foreground color to be a gray level with frac frac
        """
        self._rgb = (frac, frac, frac)
        

    def set_linewidth(self, w):
        """
        Set the linewidth in points
        """
        self._linewidth = w

    def set_capstyle(self, cs):
        """
        Set the capstyle as a string in ('butt', 'round', 'projecting')
        """
        if cs not in ('butt', 'round', 'projecting'):
            error_msg('Unrecognized cap style.  Found %s' % cs)
        self._capstyle = cs

    def set_joinstyle(self, js):
        """
        Set the join style to be one of ('miter', 'round', 'bevel')
        """
        
        if js not in ('miter', 'round', 'bevel'):
            error_msg('Unrecognized join style.  Found %s' % js)
        self._joinstyle = js


    def get_linewidth(self):
        """
        Return the line width in points as a scalar
        """
        return self._linewidth

    def copy_properties(self, gc):
        'Copy properties from gc to self'
        self._rgb = gc._rgb
        self._linewidth = gc._linewidth
        self._capstyle = gc._capstyle
        self._joinstyle = gc._joinstyle
        self._linestyle = gc._linestyle
        self._dashes = gc._dashes
        self._cliprect = gc._cliprect
        self._antialiased = gc._antialiased
        self._alpha = gc._alpha
        

class MplEvent:
    """
    A matplotlib event.  Attach additional attributes as defined in
    FigureCanvas.connect.  The following attributes are defined and
    shown with their default values
    name                # the event name
    canvas              # the FigureCanvas instance generating the event
    x      = None       # x position - pixels from left of canvas
    y      = None       # y position - pixels from bottom of canvas
    button = None       # button pressed None, 1, 2, 3
    key    = None       # the key pressed: None, chr(range(255), shift, win, or control
    inaxes = None       # the Axes instance if mouse us over axes
    xdata  = None       # x coord of mouse in data coords
    ydata  = None       # y coord of mouse in data coords
    
    """
    x      = None       # x position - pixels from left of canvas
    y      = None       # y position - pixels from right of canvas
    button = None       # button pressed None, 1, 2, 3
    inaxes = None       # the Axes instance if mouse us over axes
    xdata  = None       # x coord of mouse in data coords
    ydata  = None       # y coord of mouse in data coords
    
    def __init__(self, name, canvas):
        self.name = name
        self.canvas = canvas

class FigureCanvasBase:
    """
    The canvas the figure renders into.

    Public attribute

      figure - A Figure instance
    """
    events = ('button_press_event',
              'button_release_event',
              'motion_notify_event',
              )

    def __init__(self, figure):
        self.figure = figure
        
    def draw(self):
        """
        Render the figure
        """
        pass

    def print_figure(self, filename, dpi=300, facecolor='w', edgecolor='w'):
        """
        Render the figure to hardcopy.  Set the figure patch face and
        edge colors.  This is useful because some of the GUIs have a
        gray figure face color background and you'll probably want to
        override this on hardcopy
        """
        pass

    def switch_backends(self, FigureCanvasClass):
        """
        instantiate an instance of FigureCanvasClass

        This is used for backend switching, eg, to instantiate a
        FigureCanvasPS from a FigureCanvasGTK.  Note, deep copying is
        not done, so any changes to one of the instances (eg, setting
        figure size or line props), will be reflected in the other
        """
        newCanvas = FigureCanvasClass(self.figure)
        return newCanvas

    def mpl_connect(self, s, func):
        """\
        Connect event with string s to func.  The signature of func is

          def func(event)

        where event is a MplEvent.  The following events are recognized

         'button_press_event' 
         'button_release_event' 
         'motion_notify_event' 

         For the three events above, if the mouse is over the axes,
         the variable event.inaxes will be set to the axes it is over,
         and additionally, the variables event.xdata and event.ydata
         will be defined.  This is the mouse location in data coords.
         See backend_bases.MplEvent.

        return value is a connection id that can be used with
        mpl_disconnect """
        pass
        
    def mpl_disconnect(self, cid):
        """
        Connect s to func. return an id that can be used with disconnect
        Method should return None
        """
        return None

class FigureManagerBase:
    """
    Helper class for matlab mode, wraps everything up into a neat bundle

    Public attibutes
    canvas - A FigureCanvas instance
    num    - The figure number
    """
    def __init__(self, canvas, num):
        self.canvas = canvas
        self.num = num
        self.clf()
        
    def clf(self):
        'clear the figure'
        self.axes = {}
        self.currentAxis = None
        self.canvas.figure.clf()
        
    def add_subplot(self, *args, **kwargs):
        """
        Add a subplot to the current figure
        """
        key = (args, tuple(kwargs.items()))
        if self.axes.has_key(key):
            self.currentAxis = self.axes[key]
        else:
            a = self.canvas.figure.add_subplot(*args, **kwargs)
            self.axes[key] = a
            self.currentAxis = a
            return a
        
    def add_axes(self, rect, **kwargs):
        """
        Add an axes to the current figure
        """
        rect = tuple(rect)
        key = (rect, tuple(kwargs.items()))
        if self.axes.has_key(key):
            self.currentAxis = self.axes[key]
            return self.currentAxis
        else:
            a = self.canvas.figure.add_axes(rect, **kwargs)
            self.axes[key] = a
            self.currentAxis = a
            return a

    def get_current_axis(self):
        """
        Return the current axes
        """
        if self.currentAxis is not None:
            return self.currentAxis
        else:
            self.add_subplot(111)
            return self.currentAxis


    def set_current_axes(self, a):
        """
        Set the current axes to be a
        """
        if a is None:
            self.currentAxis = None
            return
        if a not in self.axes.values():
            error_msg('Axes is not in current figure')
        self.currentAxis = a

    def destroy(self):
        pass


# cursors
class Cursors:  #namespace
    HAND, POINTER, SELECT_REGION, MOVE = range(4)
cursors = Cursors()


class Stack:
    """
    Implement a stack where elements can be pushed on and you can move
    back and forth.  But no pop.  Should mimib home / back / forward
    in a browser
    """

    def __init__(self):
        self.clear()
        
    def __call__(self):
        'return the current element, or None'
        if not len(self._elements): return None
        else: return self._elements[self._pos]

    def forward(self):
        'move the position forward and return the current element'
        N = len(self._elements)
        if self._pos<N-1: self._pos += 1
        return self()

    def back(self):
        'move the position back and return the current element'
        if self._pos>0: self._pos -= 1
        return self()

    def push(self, o):
        """
        push object onto stack at current position - all elements
        occurring later than the current position are discarded
        """
        self._elements = self._elements[:self._pos+1]
        self._elements.append(o)
        self._pos = len(self._elements)-1
        return self()
    
    def home(self):
        'push the first element onto the top of the stack'
        if not len(self._elements): return
        self.push(self._elements[0])
        return self()

    def empty(self):
        return len(self._elements)==0

    def clear(self):
        'empty the stack'
        self._pos = -1
        self._elements = []

class NavigationToolbar2:
    """
    Base class for the navigation cursor, version 2

    backends must implement a canvas that handles connections for
    'button_press_event' and 'button_release_event'.  See
    FigureCanvas.connect for more information


    They must also define

     * save_figure - save the current figure

     * set_cursor - if you want the pointer icon to change

     * _init_toolbar - create your toolbar widget

     * draw_rubberband (optional) : draw the zoom to rect
       "rubberband" rectangle

    * press : (optional) whenever a mouse button is pressed, you'll be
       notified with the event
    
    * release : (optional) whenever a mouse button is released,
       you'll be notified with the event

    * dynamic_update (optional) dynamically update the window while
      navigating

    * set_message (optional) - display message
    
    That's it, we'll do the rest!
    """

    def __init__(self, canvas):
        self.canvas = canvas
        
        # a dict from axes index to a list of view limits
        self._views = Stack()
        self._xypress = None  # the  location and axis info at the time of the press 
        self._idPress = None
        self._idRelease = None
        self._active = None
        self._lastCursor = None
        self._init_toolbar()
        self._idDrag=self.canvas.mpl_connect('motion_notify_event', self.mouse_move)  
        self._button_pressed = None # determined by the button pressed at start

        self.mode = ''  # a mode string for the status bar

    def set_message(self, s):
        'display a message on toolbar or in status bar'
        pass
    
    def back(self, *args):
        'move back up the view lim stack'
        self._views.back()
        self._update_view()

    def dynamic_update(self):
        pass
    
    def draw_rubberband(self, event, x0, y0, x1, y1):
        'draw a rectangle rubberband to indicate zoom limits'
        pass

    def forward(self, *args):
        'move forward in the view lim stack'
        self._views.forward()
        self._update_view()

    def home(self, *args):
        'restore the original view'
        self._views.home()
        self._update_view()
        self.draw()

    def _init_toolbar(self):
        """
        This is where you actually build the GUI widgets (called by
        __init__).  The icons home.xpm, back.xpm, forward.xpm,
        hand.xpm, zoom_to_rect.xpm and filesave.xpm are standard
        across backends (there are ppm versions in CVS also).

        You just need to set the callbacks

        home         : self.home
        back         : self.back
        forward      : self.forward
        hand         : self.pan
        zoom_to_rect : self.zoom
        filesave     : self.save_figure

        You only need to define the last one - the others are in the base
        class implementation.
        
        """
        raise NotImplementedError

    def mouse_move(self, event):
        #print 'mouse_move', event.button

        if not event.inaxes or not self._active:
            if self._lastCursor != cursors.POINTER:
                self.set_cursor(cursors.POINTER)
                self._lastCursor = cursors.POINTER
        else:
            if self._active=='ZOOM':
                if self._lastCursor != cursors.SELECT_REGION:
                    self.set_cursor(cursors.SELECT_REGION)
                    self._lastCursor = cursors.SELECT_REGION
                if self._xypress is not None:
                    x, y = event.x, event.y
                    lastx, lasty, a, ind, lim, trans= self._xypress
                    self.draw_rubberband(event, x, y, lastx, lasty)
            elif (self._active=='PAN' and
                  self._lastCursor != cursors.MOVE):
                self.set_cursor(cursors.MOVE)

                self._lastCursor = cursors.MOVE

        if event.inaxes:

            xs = event.inaxes.format_xdata(event.xdata)
            ys = event.inaxes.format_ydata(event.ydata)            
            
            loc = 'x=%s, y=%s'%(xs,ys)
            if len(self.mode):
                self.set_message('%s : %s' % (self.mode, loc))
            else:
                self.set_message(loc)
        else: self.set_message(self.mode)            
            
    def pan(self,*args):
        'Activate the pan/zoom tool. pan with left button, zoom with right'
        # set the pointer icon and button press funcs to the
        # appropriate callbacks

        if self._active == 'PAN':
            self._active = None
        else:
            self._active = 'PAN'

        if self._idPress is not None:
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease = self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''

        if self._active:    
            self._idPress = self.canvas.mpl_connect(
                'button_press_event', self.press_pan)
            self._idRelease = self.canvas.mpl_connect(
                'button_release_event', self.release_pan)
            self.mode = 'pan/zoom mode'

        self.set_message(self.mode)

    def press(self, event):
        'this will be called whenver a mouse button is pressed'
        pass

    def press_pan(self, event):
        'the press mouse button in pan/zoom mode callback'

        if event.button == 1:
            self._button_pressed=1
        elif  event.button == 3: 
            self._button_pressed=3
        else: 
            self._button_pressed=None
            return

        x, y = event.x, event.y

        # push the current view to define home if stack is empty
        if self._views.empty(): self.push_current()
        
            
        for i, a in enumerate(self.canvas.figure.get_axes()):
            if event.inaxes == a:
                xmin, xmax = a.get_xlim()
                ymin, ymax = a.get_ylim()
                lim = xmin, xmax, ymin, ymax
                self._xypress = x, y, a, i, lim,a.transData.deepcopy()
                self.canvas.mpl_disconnect(self._idDrag)   
                self._idDrag=self.canvas.mpl_connect('motion_notify_event', self.drag_pan) 
                break

        self.press(event)

    def press_zoom(self, event):
        'the press mouse button in zoom to rect mode callback'
        if event.button == 1:
            self._button_pressed=1
        elif  event.button == 3: 
            self._button_pressed=3
        else: 
            self._button_pressed=None
            return
            
        x, y = event.x, event.y

        # push the current view to define home if stack is empty
        if self._views.empty(): self.push_current()

        for i, a in enumerate(self.canvas.figure.get_axes()):
            if event.inaxes==a:
                xmin, xmax = a.get_xlim()
                ymin, ymax = a.get_ylim()
                lim = xmin, xmax, ymin, ymax
                self._xypress = x, y, a, i, lim, a.transData.deepcopy()

                break
        self.press(event)

    def push_current(self):
        'push the current view limits onto the stack'
        lims = []
        for a in self.canvas.figure.get_axes():
            xmin, xmax = a.get_xlim()
            ymin, ymax = a.get_ylim()
            lims.append( (xmin, xmax, ymin, ymax) )
        self._views.push(lims)
        
        

    def release(self, event):
        'this will be called whenever mouse button is released'
        pass

    def release_pan(self, event):
        'the release mouse button callback in pan/zoom mode'
        self.canvas.mpl_disconnect(self._idDrag)   
        self._idDrag=self.canvas.mpl_connect('motion_notify_event', self.mouse_move)   
        if self._xypress is None: return
        self._xypress = None
        self._button_pressed=None
        self.push_current()
        self.release(event)
        self.draw()
        
    def drag_pan(self, event):
        'the drag callback in pan/zoom mode'

        def format_deltas(event,dx,dy):
            if event.key=='control':
                if(abs(dx)>abs(dy)):
                    dy = dx
                else:
                    dx = dy
            elif event.key=='x':
                dy = 0
            elif event.key=='y':
                dx = 0
            elif event.key=='shift':
                if 2*abs(dx) < abs(dy):
                    dx=0
                elif 2*abs(dy) < abs(dx):
                    dy=0
                elif(abs(dx)>abs(dy)):
                    dy=dy/abs(dy)*abs(dx)
                else:    
                    dx=dx/abs(dx)*abs(dy)
            return (dx,dy)                
                    
        if self._xypress is None: return
        x, y = event.x, event.y

        lastx, lasty, a, ind, lim, trans = self._xypress
        xmin, xmax, ymin, ymax = lim
        #safer to use the recorded buttin at the press than current button: 
        #multiple button can get pressed during motion...   
        if self._button_pressed==1: 
            lastx, lasty = trans.inverse_xy_tup( (lastx, lasty) )
            x, y = trans.inverse_xy_tup( (x, y) )
            if a.get_xscale()=='log':
                dx=1-lastx/x
            else:    
                dx=x-lastx
            if a.get_yscale()=='log':
                dy=1-lasty/y
            else:    
                dy=y-lasty
            dx,dy=format_deltas(event,dx,dy)
            if a.get_xscale()=='log':
                xmin *= 1-dx
                xmax *= 1-dx
            else: 
                xmin -= dx
                xmax -= dx   
            if a.get_yscale()=='log':
                ymin *= 1-dy
                ymax *= 1-dy
            else:
                ymin -= dy
                ymax -= dy   
        elif self._button_pressed==3: 
            dx=(lastx-x)/float(a.bbox.width())
            dy=(lasty-y)/float(a.bbox.height())
            dx,dy=format_deltas(event,dx,dy)
            alphax = pow(10.0,dx)
            alphay = pow(10.0,dy)#use logscaling, avoid singularities and smother scaling...
            lastx, lasty = trans.inverse_xy_tup( (lastx, lasty) )
            if a.get_xscale()=='log':
                xmin = lastx*(xmin/lastx)**alphax
                xmax = lastx*(xmax/lastx)**alphax
            else:
                xmin = lastx+alphax*(xmin-lastx)
                xmax = lastx+alphax*(xmax-lastx)
            if a.get_yscale()=='log':
                ymin = lasty*(ymin/lasty)**alphay
                ymax = lasty*(ymax/lasty)**alphay
            else:
                ymin = lasty+alphay*(ymin-lasty)
                ymax = lasty+alphay*(ymax-lasty)

        a.set_xlim((xmin, xmax))
        a.set_ylim((ymin, ymax))

        self.dynamic_update()

          
            
    def release_zoom(self, event):
        'the release mouse button callback in zoom to rect mode'        
        if self._xypress is None: return
        x, y = event.x, event.y

        
        lastx, lasty, a, ind, lim, trans = self._xypress
        # ignore singular clicks - 5 pixels is a threshold
        if abs(x-lastx)<5 or abs(y-lasty)<5 or not a.in_axes(x,y):
            self._xypress = None
            self.release(event)
            self.draw()
            return

        xmin, ymin, xmax, ymax = lim

        # zoom to rect
        lastx, lasty = a.transData.inverse_xy_tup( (lastx, lasty) )
        x, y = a.transData.inverse_xy_tup( (x, y) )            

        if x<lastx:  xmin, xmax = x, lastx
        else: xmin, xmax = lastx, x

        if y<lasty:  ymin, ymax = y, lasty
        else: ymin, ymax = lasty, y

        if self._button_pressed == 1:  
            a.set_xlim((xmin, xmax))
            a.set_ylim((ymin, ymax))
        elif self._button_pressed == 3: 
            Xmin,Xmax=a.get_xlim()
            Ymin,Ymax=a.get_ylim()
            if a.get_xscale()=='log':
                alpha=log(Xmax/Xmin)/log(xmax/xmin)
                x1=pow(Xmin/xmin,alpha)*Xmin
                x2=pow(Xmax/xmin,alpha)*Xmin
            else:    
                alpha=(Xmax-Xmin)/(xmax-xmin)
                x1=alpha*(Xmin-xmin)+Xmin
                x2=alpha*(Xmax-xmin)+Xmin
            if a.get_yscale()=='log':
                alpha=log(Ymax/Ymin)/log(ymax/ymin)
                y1=pow(Ymin/ymin,alpha)*Ymin
                y2=pow(Ymax/ymin,alpha)*Ymin
            else:    
                alpha=(Ymax-Ymin)/(ymax-ymin)
                y1=alpha*(Ymin-ymin)+Ymin
                y2=alpha*(Ymax-ymin)+Ymin
            a.set_xlim((x1, x2))
            a.set_ylim((y1, y2))    

        self.draw()
        self._xypress = None
        self._button_pressed == None

        self.push_current()
        self.release(event)

    def draw(self):
        'redraw the canvases, update the locators'
        for a in self.canvas.figure.get_axes():
            for loc in (a.xaxis.get_major_locator(),
                        a.xaxis.get_minor_locator(),
                        a.yaxis.get_major_locator(),
                        a.yaxis.get_minor_locator()):
                loc.refresh()
        self.canvas.draw()
                       
            
                                
    def _update_view(self):
        'update the viewlim from the view stack for each axes'

        lims = self._views()
        if lims is None:  return
        for i, a in enumerate(self.canvas.figure.get_axes()):
            xmin, xmax, ymin, ymax = lims[i]
            a.set_xlim((xmin, xmax))
            a.set_ylim((ymin, ymax))

        self.draw()


    def save_figure(self, *args):
        'save the current figure'
        raise NotImplementedError
        
    def set_cursor(self, cursor):
        """
        Set the current cursor to one of the backend_bases.Cursors
        enums values
        """
        pass

    def update(self):
        'reset the axes stack'
        self._views.clear()

    def zoom(self, *args):
        'activate zoom to rect mode'
        if self._active == 'ZOOM':
            self._active = None
        else:
            self._active = 'ZOOM'

        if self._idPress is not None:
            self._idPress=self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease=self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''
            
        if  self._active: 
            self._idPress = self.canvas.mpl_connect('button_press_event', self.press_zoom)
            self._idRelease = self.canvas.mpl_connect('button_release_event', self.release_zoom)
            self.mode = 'Zoom to rect mode'

        self.set_message(self.mode)
        
def error_msg(msg, *args, **kwargs):
    """
    Alert an error condition with message
    """
    print >>sys.stderr, msg
    sys.exit()


