#!/usr/bin/python
import gtk
from org.umlfri.api.mainLoops import GtkMainLoop
from gtk.gdk import WindowTypeHint
import MySQLdb
from connect import Connection



def pluginMain(interface):
    menu = interface.gui_manager.main_menu.add_menu_item('DRA', '', -1, 'DRA')
    menu.add_submenu()
    submenu = menu.submenu
    submenu.add_menu_item('Pripoj', lambda x:menuConnect(), -1, 'Pripoj k databaze')
    interface.transaction.autocommit = True
    interface.set_main_loop(GtkMainLoop())
def menuConnect():
    b=gtk.Builder()
    b.add_from_file("c:\\Users\\Michal\\menu.glade")
    global w
    w=b.get_object("dialog1")
    w.set_keep_above(True)
    w.show_all()
    w.set_keep_above(False)
    c=b.get_object("button1")
    c.connect("clicked",lambda x:connect())

def connect():
    #db = MySQLdb.connect(host=b.get_object("entry1").get_text(),user=b.get_object("entry3").get_text(),
    #passwd=b.get_object("entry4").get_text(),db=b.get_object("entry2").get_text())
    #db = MySQLdb.connect(host="localhost",user="belas",passwd="824510802",db="skuska")
    global w
    w.hide()
    a=Connection(1)
    print a.typ
    b=Connection(2)
    print a.typ
    #cursor=db.cursor()
    #cursor.execute('SELECT * FROM tabulka')
    #for row in cursor:
    #   print row







