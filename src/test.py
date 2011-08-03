import gtkmozembed
import gtk

def on_new_window(mozembed, retval, chromemask):
    print retval

mozembed = gtkmozembed.MozEmbed()
mozembed.load_url("http://www.google.com/")
mozembed.connect("new-window", on_new_window)

win = gtk.Window()
win.add(mozembed)
win.show_all()
gtk.main()