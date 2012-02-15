#!/usr/bin/python
import gtk
from org.umlfri.api.mainLoops import GtkMainLoop
from gtk.gdk import WindowTypeHint
import MySQLdb
from connect import Connection
from operations import *


def pluginMain(interface):
    menu = interface.gui_manager.main_menu.add_menu_item('DRA', '', -1, 'DRA')
    menu.add_submenu()
    submenu = menu.submenu
    submenu.add_menu_item('Pripoj', lambda x:menuConnect(), -1, 'Pripoj k databaze')
    submenu.add_menu_item('Vykonaj',lambda z:execute(interface),-1,'Vykonaj')
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
    w.grab_focus()
    c=b.get_object("button1")
    c.connect("clicked",lambda x:connect())

def connect():
    #db = MySQLdb.connect(host=b.get_object("entry1").get_text(),user=b.get_object("entry3").get_text(),
    #passwd=b.get_object("entry4").get_text(),db=b.get_object("entry2").get_text())
    #db = MySQLdb.connect(host="localhost",user="belas",passwd="824510802",db="skuska")
    global w
    w.hide()
    global a
    a=Connection()
    a.pripoj(1)
    #cursor=db.cursor()
    #cursor.execute('SELECT * FROM tabulka')
    #for row in cursor:
    #   print row
def execute(interface):
    array=[]
    a = interface.current_diagram.selected
    tem=list(a)
    if len(tem) == 1:
        select=a.next()
        create(select)

            

    else:
        print "musis oznacit nejaky element"
    #for element in a:
     #   if element.object.type.name=="Selection":
      #

def create(self,trunk):
    name=trunk.object.type.name
    if name=="Union" :
        pass
    elif name=="Intersection":
        pass
    elif name=="Product":
        pass
    elif name=="Difference":
        pass
    elif name=="Division":
        pass
    elif name=="Selection":
        object=Selection(select.object.values["column1"],select.object.values["condition"],select.object.values["column2"])
        array.append(object)
    elif name=="Projection":
        pass
    elif name=="Inner join":
        pass
    elif name=="Left outter join":
        pass
    elif name=="Right outter join":
        pass
    elif name=="Full outter join":
        pass
    cons=trunk.connections
    tem1=list(cons)
    i=0
    while(i<len(tem1)):
        con=cons.next()
        object1=con.source()
        object.set(object1)

    create(object1)
        





