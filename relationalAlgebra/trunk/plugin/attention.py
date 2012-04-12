import gtk
class InfoBarDemo(gtk.Window):
    def __init__(self,message,text,title, parent=None):
        gtk.Window.__init__(self)
        self.__dialog = gtk.MessageDialog(
                        self,
                        gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_WARNING,
                        gtk.BUTTONS_OK,
                        message)
        self.__dialog.format_secondary_text(text)
        self.__dialog.set_title(title)
        self.__dialog.set_keep_above(True)
        self.__dialog.set_transient_for(parent)
        self.__dialog.set_modal(True)
        self.__dialog.show()
        self.__dialog.run()
        self.__dialog.destroy()