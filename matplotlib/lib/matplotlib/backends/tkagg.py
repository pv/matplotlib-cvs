import _tkagg
import Tkinter as Tk

def blit(photoimage, aggimage, colormode=1):
    tk = photoimage.tk
    try:
        tk.call("PyAggImagePhoto", photoimage, id(aggimage), colormode)
    except Tk.TclError, v:
        try:
            try:
                _tkagg.tkinit(tk.interpaddr(), 1)
            except AttributeError:
                _tkagg.tkinit(id(tk), 0)
            tk.call("PyAggImagePhoto", photoimage, id(aggimage), colormode)
        except (ImportError, AttributeError, Tk.TclError):
            raise

def test(aggimage):
    import time
    r = Tk.Tk()
    c = Tk.Canvas(r, width=aggimage.width, height=aggimage.height)
    c.pack()
    p = Tk.PhotoImage(width=aggimage.width, height=aggimage.height)
    blit(p, aggimage)
    c.create_image(aggimage.width,aggimage.height,image=p)
    blit(p, aggimage)
    while 1: r.update_idletasks()
