import gtk

class WaitingBar(gtk.Window):
    def __init__(self, connect,parent=None):
        gtk.Window.__init__(self)
        self.dialog = gtk.Dialog(None,
                   None,
                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        self.label=gtk.Label()
        self.dialog.connect("destroy",lambda x:self.cancel())
        self.label.set_text("Trying to connect. Please wait")
        image=gtk.Image()
        self.__connect=connect
        image.set_from_file("C:\Users\michal\Desktop\progress_bar.gif")
        self.dialog.vbox.pack_start(self.label)
        self.dialog.vbox.pack_start(image)
        image.show()
    def cancel(self):
        pass
    def hide_all(self, *args, **kwargs):
        self.dialog.hide_all()
    def show_all(self, *args, **kwargs):
        self.label.show()
        self.dialog.set_keep_above(True)
        self.dialog.show_all()