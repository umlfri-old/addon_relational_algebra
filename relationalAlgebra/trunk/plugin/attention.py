import pygtk
import gtk

class InfoBarDemo(gtk.Window):
    def __init__(self,message,text,title, parent=None):
        gtk.Window.__init__(self)
        
        dialog = gtk.MessageDialog(
                        self,
                        gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_WARNING,
                        gtk.BUTTONS_OK,
                        message)
        dialog.format_secondary_text(text)
        dialog.set_title(title)
        dialog.set_keep_above(True)
        dialog.run()
        dialog.destroy()