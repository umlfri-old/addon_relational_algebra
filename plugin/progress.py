import gtk
import gobject
class WaitingBar(gtk.Window):
    def __init__(self, connect,parent=None):
        gtk.Window.__init__(self)
        self.dialog = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.dialog.set_destroy_with_parent(True)
        self.dialog.set_resizable(False)
        self.dialog.connect("destroy",lambda x:self.cancel())
        icon = self.dialog.render_icon(gtk.STOCK_CONNECT, gtk.ICON_SIZE_BUTTON)
        self.dialog.set_icon(icon)
        self.label=gtk.Label(str="Please wait...")
        vbox = gtk.VBox(False, 5)
        vbox.set_border_width(10)
        self.dialog.add(vbox)
        vbox.show()
        self.timer = gobject.timeout_add (100, progress_timeout, self)
        self.dialog.set_title("Connecting...")
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        align2=gtk.Alignment(0.5,0.5,0,0)
        vbox.pack_start(align, False, False, 5)
        vbox.pack_start(align2, False, False, 5)
        align.show()
        align2.show()
        self.bar = gtk.ProgressBar()
        align.add(self.label)
        align2.add(self.bar)
        self.bar.pulse()
        self.bar.show()
        self.label.show()
    def cancel(self):
        pass
    def hide_all(self, *args, **kwargs):
        self.dialog.hide_all()
    def show_all(self, *args, **kwargs):
        self.dialog.set_keep_above(True)
        self.dialog.show_all()
def progress_timeout(obj):
    obj.bar.pulse()
    return True