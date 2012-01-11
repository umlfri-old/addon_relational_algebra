#!/usr/bin/python
import gtk
from org.umlfri.api.mainLoops import GtkMainLoop
from gtk.gdk import WindowTypeHint

def pluginMain(interface):
    menu = interface.gui_manager.main_menu.add_menu_item('DRA', '', -1, 'DRA')
    menu.add_submenu()
    submenu = menu.submenu
    submenu.add_menu_item('Pripoj', lambda x:pripoj(), -1, 'Pripoj k databaze')
    interface.transaction.autocommit = True
    interface.set_main_loop(GtkMainLoop())
def pripoj():
    b=gtk.Builder()
    b.add_from_file("c:\\Users\\Michal\\menu2.glade")
    w=b.get_object("window1")
    w.set_keep_above(True)
    w.show_all()




