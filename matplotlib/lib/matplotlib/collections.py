"""
Classes for the efficient drawing of large collections of objects that
share most properties, eg a large number of line segments or polygons

The classes are not meant to be as flexible as their single element
counterparts (eg you may not be able to select all line styles) but
they are meant to be fast for common use cases (eg a bunch of solid
line segemnts)
"""
import math
from matplotlib import rcParams

from artist import Artist
from cbook import True, False, is_string_like, iterable
from colors import colorConverter, looks_like_color
from cm import ScalarMappable
from numerix import arange, sin, cos, pi, asarray, sqrt
from transforms import identity_transform

class Collection(Artist):
    """
    All properties in a collection must be sequences.  The
    property of the ith element of the collection is the

      prop[i % len(props)].

    This implies that the properties cycle if the len of props is less
    than the number of elements of the collection.  A length 1
    property is shared by all the elements of the collection

    All color args to a collection are sequences of rgba tuples
    """

    def __init__(self):
        Artist.__init__(self)

    def _get_color(self, c, N=1):
        if looks_like_color(c):
	    return  [colorConverter.to_rgba(c)]*N
        elif iterable(c) and len(c) and iterable(c[0]) and len(c[0])==4:
	    # looks like a tuple of rgba
	    return c
        else:
	    raise TypeError('c must be a matplotlib color arg or nonzero length sequence of rgba tuples')

    def _get_value(self, val):
        try: return (float(val), )
        except TypeError:
	    if iterable(val) and len(val):
	        try: float(val[0])
	        except TypeError: pass # raise below
	        else: return val

        raise TypeError('val must be a float or nonzero sequence of floats')
    
    

class PatchCollection(Collection, ScalarMappable):
    """
    and transOffset are used to translate the patch after
    rendering (default no offsets)

    If any of edgecolors, facecolors, linewidths, antialiaseds are
    None, they default to their patch.* rc params setting, in sequence
    form

    The use of ScalarMappable is optional.  If the ScalarMappable
    matrix _A is not None (ie a call to set_array has been made), at
    draw time a call to scalar mappable will be made to set the face
    colors.
    """
    def __init__(self,
                 edgecolors=None,   
                 facecolors=None,
                 linewidths=None,
                 antialiaseds = None,
		 offsets = None,
		 transOffset = identity_transform(),
                 norm = None,  # optional for ScalarMappable
                 cmap = None,  # ditto
                 ):
        Collection.__init__(self)
        ScalarMappable.__init__(self, norm, cmap)
        
        if edgecolors is None: edgecolors =\
           self._get_color(rcParams['patch.edgecolor'])
        if facecolors is None: facecolors = \
           self._get_color(rcParams['patch.facecolor'])
        if linewidths is None: linewidths = ( rcParams['patch.linewidth'],)
        if antialiaseds is None: antialiaseds = ( rcParams['patch.antialiased'],)

        self._edgecolors = edgecolors
        self._facecolors  = facecolors
        self._linewidths  = linewidths
        self._antialiaseds = antialiaseds
        self._offsets = offsets
	self._transOffset = transOffset

    def set_linewidth(self, lw):
        """
        lw can be a scalar or a sequence; if it is a sequence the
        patches will cycle through the sequence        
        """
        self._linewidths = self._get_value(lw)

    def set_facecolor(self, c):
        """
        c can be a matplotlib color arg (all patches have same color),
        or a a sequence or rgba tuples; if it is a sequence the
        patches will cycle through the sequence
        """
        self._facecolors = self._get_color(c, len(self._facecolors))

    def set_edgecolor(self, c):
        """
        c can be a matplotlib color arg (all patches have same color),
        or a a sequence or rgba tuples; if it is a sequence the
        patches will cycle through the sequence
        """
        self._edgecolors = self._get_color(c, len(self._edgecolors))
        
    def set_alpha(self, alpha):
        try: float(alpha)
        except TypeError: raise TypeError('alpha must be a float')
        else:
            Artist.set_alpha(self, alpha)
            self._facecolors = [(r,g,b,alpha) for r,g,b,a in self._facecolors]
            if self._edgecolors != 'None':
                self._edgecolors = [(r,g,b,alpha) for r,g,b,a in self._edgecolors]

    def update_scalarmappable(self):
        """
        if the scalar mappable array is not none, update facecolors
        from scalar data
        """
        if self._A is None: return
        if len(self._A.shape)>1:
            raise ValueError('PatchCollections can only map rank 1 arrays')
        self._facecolors = [(r,g,b,a) for r,g,b,a in self.to_rgba(self._A, self._alpha)]
        
        
class PolyCollection(PatchCollection):
    def __init__(self, verts, **kwargs):
        """
	verts is a sequence of ( verts0, verts1, ...) where verts_i is
	a sequence of xy tuples of vertices.



	Optional kwargs from Patch collection include

          edgecolors 	= ( (0,0,0,1), ),
          facecolors 	= ( (1,1,1,0), ),
          linewidths 	= ( 1.0, ),
          antialiaseds 	= (1,),
	  offsets 	= None
	  transOffset 	= None
	"""
	PatchCollection.__init__(self,**kwargs)	
	self._verts = verts

    def draw(self, renderer):
        renderer.open_group('polycollection')
        self._transform.freeze()
	self._transOffset.freeze()
        self.update_scalarmappable()
        if self._edgecolors == 'None':
            self._edgecolors = self._facecolors
        renderer.draw_poly_collection(
            self._verts, self._transform, self.clipbox,  
            self._facecolors, self._edgecolors,
            self._linewidths, self._antialiaseds,
	    self._offsets,  self._transOffset)
        self._transform.thaw()
	self._transOffset.thaw()
	renderer.close_group('polycollection')
	
class RegularPolyCollection(PatchCollection):
    def __init__(self,
		 dpi,
                 numsides,
                 rotation = 0 ,
                 sizes = (1,),
                 **kwargs):
        """
        Draw a regular polygon with numsides.  sizes gives the area of
        the circle circumscribing the regular polygon and rotation is
        the rotation of the polygon in radians.  

        offsets are a sequence of x,y tuples that give the centers of
        the polygon in data coordinates, and transOffset is the
        Transformation instance used to transform the centers onto the
        canvas.
        
        dpi is the figure dpi instance, and is required to do the area
        scaling.

        """
        PatchCollection.__init__(self,**kwargs)
        self._sizes = asarray(sizes)
        self._dpi = dpi

        r = 1.0/math.sqrt(math.pi)  # unit area

        theta = (2*math.pi/numsides)*arange(numsides) + rotation

        self._verts = zip( r*sin(theta), r*cos(theta) )
        
        
            
    def draw(self, renderer):
        renderer.open_group('regpolycollection')
        self._transform.freeze()
	self._transOffset.freeze()
        self.update_scalarmappable()
        scales = sqrt(self._sizes*self._dpi.get()/72.0)

        if self._edgecolors == 'None':
            self._edgecolors = self._facecolors

        renderer.draw_regpoly_collection(
            self.clipbox, 
            self._offsets, self._transOffset,
            self._verts, scales, 
            self._facecolors, self._edgecolors,
            self._linewidths, self._antialiaseds)

        self._transform.thaw()
	self._transOffset.thaw()
	renderer.close_group('regpolycollection')

class LineCollection(Collection):
    """
    All parameters must be sequences.  The property of the ith line
    segment is the prop[i % len(props)], ie the properties cycle if
    the len of props is less than the number of sements

    """
    def __init__(self, segments,
                 linewidths    = None,
                 colors        = None,
                 antialiaseds  = None,
		 offsets = None,
		 transOffset = None,
                 ):
        """
        segments is a sequence of ( line0, line1, line2), where linen =
        (x0, y0), (x1, y1), ... (xm, ym).  Each line can be a
        different length

        

        colors must be a tuple of RGBA tuples (eg arbitrary color
        strings, etc, not allowed).
        
        antialiaseds must be a sequence of ones or zeros

        if linewidths, colors or antialiaseds is None, they default to
        their rc params setting, in sequence form
        """
        
        Collection.__init__(self)

        if linewidths is None   :
            linewidths   = (rcParams['lines.linewidth'], )
        if colors is None       :
            colors       = self._get_color(rcParams['lines.color'])
        if antialiaseds is None :
            antialiaseds = (rcParams['lines.antialiased'], )

        self._segments = segments
        self._colors = colors
        self._aa = antialiaseds
        self._lw = linewidths
	self._offsets = offsets
	self._transOffset = transOffset

    def draw(self, renderer):
        renderer.open_group('linecollection')
        self._transform.freeze()
        if self._transOffset is not None: self._transOffset.freeze()

        renderer.draw_line_collection(
            self._segments, self._transform, self.clipbox, 
            self._colors, self._lw, self._aa, self._offsets,
	    self._transOffset)
        self._transform.thaw()
	if self._transOffset is not None: self._transOffset.thaw()
	renderer.close_group('linecollection')

    def set_linewidth(self, lw):
        """
        lw can be a scalar or a sequence; if it is a sequence the
        patches will cycle through the sequence        
        """
        self._lw = self._get_value(lw)

    def color(self, c):
        """
        c can be a matplotlib color arg (all patches have same color),
        or a a sequence or rgba tuples; if it is a sequence the
        patches will cycle through the sequence
        """
        self._colors = self._get_color(c, len(self._colors))

    def set_alpha(self, alpha):

        try: float(alpha)
        except TypeError: raise TypeError('alpha must be a float')
        else:
            Artist.set_alpha(self, alpha)
            self._colors = [(r,g,b,alpha) for r,g,b,a in self._colors]
