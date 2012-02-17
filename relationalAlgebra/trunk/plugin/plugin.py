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
    a = interface.current_diagram.selected
    tem=list(a)
    if len(tem) == 1:
        select=tem.pop()
        object=create(None,select)
        print object.execute()
    else:
        print "musis oznacit nejaky element"
    #for element in a:
     #   if element.object.type.name=="Selection":
      #

def create(self,trunk,ob=None):
    name=trunk.object.type.name
    print trunk.object.name + "-nova funkcia"
    if name=="Table":
        object=Table(None,trunk.object.values["name"])
    elif name=="Union" :
        object=Union()
    elif name=="Intersection":
        pass
    elif name=="Product":
        pass
    elif name=="Difference":
        pass
    elif name=="Division":
        pass
    elif name=="Selection":
        object=Selection(trunk.object.values["column1"],trunk.object.values["condition"],trunk.object.values["column2"])
    elif name=="Projection":
        object=Projection(trunk.object.values["c"])
    elif name=="Inner join":
        pass
    elif name=="Left outter join":
        pass
    elif name=="Right outter join":
        pass
    elif name=="Full outter join":
        pass
    if(ob!=None):
        ob.set(object)
    conn=trunk.connections
    tem1=list(conn)
    tem1.reverse()
    con1=tem1.pop()
    object1=con1.source
    object2=None
    if (object1.object.name != trunk.object.name):
        create(None,object1,object)
        print ("skoncil lavy koren")
        if len(tem1)>=1:
            con2=tem1.pop()
            object2=con2.source
    else:
        if len(tem1)>=1:
            con2=tem1.pop()
            object1=con2.source
            create(None,object1,object)
    if(object2!=None):
        if(object2.object.name != trunk.object.name):
            create(None,object2,object)
            print ("skoncil pravy koren")
    if(ob==None):
        return object