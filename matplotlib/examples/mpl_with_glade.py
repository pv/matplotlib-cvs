import matplotlib
matplotlib.use('GTK')

from matplotlib.backends import Figure
from matplotlib.axes import Subplot
from matplotlib.backends.backend_gtk import NavigationToolbar

from Numeric import arange, sin, pi
import gtk
import gtk.glade


def simple_msg(msg, parent=None, title=None):
    dialog = gtk.MessageDialog(
        parent         = None,
        type           = gtk.MESSAGE_INFO,
        buttons        = gtk.BUTTONS_OK,
        message_format = msg)
    if parent is not None:
        dialog.set_transient_for(parent)
    if title is not None:
        dialog.set_title(title)
    dialog.show()
    dialog.run()
    dialog.destroy()
    return None



class GladeHandlers:
    def on_buttonClickMe_clicked(event):
        simple_msg('Nothing to say, really',
                   parent=widgets['windowMain'],
                   title='Thanks!')

class WidgetsWrapper:
    def __init__(self):
        self.widgets = gtk.glade.XML('mpl_with_glade.glade')
        self.widgets.signal_autoconnect(GladeHandlers.__dict__)

        self.figure = Figure(figsize=(5,4), dpi=100)
        self.figure.show()
        self.axis = Subplot(111)
        self.figure.add_axis(self.axis)
        t = arange(0.0,3.0,0.01)
        s = sin(2*pi*t)
        self.axis.plot(t,s)
        self.axis.set_xlabel('time (s)')
        self.axis.set_ylabel('voltage')
        
        self['vboxMain'].pack_start(self.figure, gtk.TRUE, gtk.TRUE)

        # below is optional if you want the navigation toolbar
        self.navToolbar = NavigationToolbar(self.figure, self['windowMain'])
        self.navToolbar.lastDir = '/var/tmp/'
        self['vboxMain'].pack_start(self.navToolbar)
        self.navToolbar.show()

        sep = gtk.HSeparator()
        sep.show()
        self['vboxMain'].pack_start(sep, gtk.TRUE, gtk.TRUE)


        self['vboxMain'].reorder_child(self['buttonClickMe'],-1)

    def __getitem__(self, key):
        return self.widgets.get_widget(key)

widgets = WidgetsWrapper()
gtk.mainloop ()