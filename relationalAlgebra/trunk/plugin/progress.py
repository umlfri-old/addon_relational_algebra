import gtk

class WaitingBar(gtk.Window):
    def __init__(self, connect,parent=None):
        gtk.Window.__init__(self)
        self.dialog = gtk.Dialog(None,
                   None,
                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        self.label=gtk.Label()
        self.dialog.connect("destroy",lambda x:self.cancel())
        icon = self.dialog.render_icon(gtk.STOCK_CONNECT, gtk.ICON_SIZE_BUTTON)
        self.dialog.set_icon(icon)
        image=gtk.Image()
        self.__connect=connect
        self.dialog.set_title("Connecting...")
        image.set_from_file("share\\addons\\DRA\\plugin\\progress_bar.gif")
        self.dialog.vbox.pack_start(image)
        image.show()
    def cancel(self):
        pass
    def hide_all(self, *args, **kwargs):
        self.dialog.hide_all()
    def show_all(self, *args, **kwargs):
        self.dialog.set_keep_above(True)
        self.dialog.show_all()