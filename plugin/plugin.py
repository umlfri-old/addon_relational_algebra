#!/usr/bin/python
import gtk
from org.umlfri.api.mainLoops import GtkMainLoop
from gtk.gdk import WindowTypeHint
import MySQLdb
from connect import *
from operations import *


def pluginMain(interface):
    menu = interface.gui_manager.main_menu.add_menu_item('DRA', '', -1, 'DRA')
    menu.add_submenu()
    submenu = menu.submenu
    submenu.add_menu_item('Pripoj', lambda x:menuConnect(), -1, 'Pripoj k databaze')
    submenu.add_menu_item('Vykonaj',lambda z:execute(interface),-1,'Vykonaj')
    submenu.add_menu_item('Test',lambda y:test(),-1,'Test')
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
    a=Connection()
    a.pripoj(1)
    b=Connection()
def test():
    table=Table(a,"model")
    b=table.execute()
    print b
def execute(interface):
    a = interface.current_diagram.selected
    tem=list(a)
    if len(tem) == 1:
        select=tem.pop()
        object=create(select)
        o=object.execute()
        if o==None:
            print "empty result"
        else:
            for row in o:
                for column in row:
                    print column,
                print "\n",
    else:
        print "musis oznacit nejaky element"
def create(trunk,ob=None):
    name= trunk.object.type.name
    if name=="Table":
        a=Connection()
        object=Table(a,trunk.object.values["name"])
    elif name=="Union" :
        object=Union()
    elif name=="Intersection":
        object=Intersection()
    elif name=="Product":
        object=Product()
    elif name=="Difference":
        object=Difference()
    elif name=="Division":
        object=Division()
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
        create(object1,object)
        if len(tem1)>=1:
            con2=tem1.pop()
            object2=con2.source
    else:
        if len(tem1)>=1:
            con2=tem1.pop()
            object1=con2.source
            create(object1,object)
    if(object2!=None):
        if(object2.object.name != trunk.object.name):
            create(object2,object)
    if(ob==None):
        return object