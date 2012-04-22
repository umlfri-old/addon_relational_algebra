import gtk
class InfoBarDemo(gtk.Window):
    def __init__(self,message,text,title,menu=None,parent=None):
        gtk.Window.__init__(self)
        self.__dialog = gtk.MessageDialog(
                        self,
                        gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_WARNING,
                        gtk.BUTTONS_OK,
                        message)
        self.__dialog.format_secondary_text(text)
        self.__menu=menu
        self.__dialog.set_title(title)
        self.__dialog.set_keep_above(True)
    def show(self, *args, **kwargs):
        self.__dialog.run()
        self.__dialog.destroy()
        if self.__menu is not None:
            for m in self.__menu:
                if m.gui_id=="connect":
                    m.enabled=True
        return False