"""
This is an example that shows you how to work directly with the agg
figure canvas to create a figure using the pythonic API.

In this example, the contents of the agg canvas are extracted to a
string, which can in turn be passed off to PIL or put in a numeric
array


"""
#!/usr/bin/env python
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.axes import Subplot
from matplotlib.mlab import normpdf
from matplotlib.numerix import randn

fig = Figure(figsize=(5,4), dpi=100)
ax = fig.add_subplot(111)

canvas = FigureCanvasAgg(fig)

mu, sigma = 100, 15
x = mu + sigma*randn(10000)

# the histogram of the data
n, bins, patches = ax.hist(x, 50, normed=1)

# add a 'best fit' line
y = normpdf( bins, mu, sigma)
line, = ax.plot(bins, y, 'r--')
line.set_linewidth(1)

ax.set_xlabel('Smarts')
ax.set_ylabel('Probability')
ax.set_title(r'$\rm{Histogram of IQ: }\mu=100, \sigma=15$')

ax.set_xlim( (40, 160))
ax.set_ylim( (0, 0.03))

canvas.draw()

s = canvas.tostring_rgb()  # save this and convert to bitmap as needed

# get the figure dimensions for creating bitmaps or numeric arrays,
# etc.
l,b,w,h = fig.bbox.get_bounds()
w, h = int(w), int(h)

if 0:
    # convert to a Numeric array
    X = fromstring(s, UInt8)
    X.shape = h, w, 3

if 0:
    # pass off to PIL
    import Image
    im = Image.fromstring( "RGB", (w,h), s)
    im.show()


