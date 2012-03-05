#!/usr/bin/python
import gtk
from org.umlfri.api.mainLoops import GtkMainLoop
from gtk.gdk import WindowTypeHint
import MySQLdb
from connect import *
from operations import *
from list import *
import math


class DRA:
    def __init__(self,interface):
        self.__interface=interface
        self.__menu=None
        self.__menuConnect=None
    def pluginMain(self):
        self.__menu = self.__interface.gui_manager.main_menu.add_menu_item('DRA', '', -1, 'DRA')
        self.__menu.add_submenu()
        self.__menu.visible=False
        submenu = self.__menu.submenu
        submenu.add_menu_item('Pripoj', lambda x:menuConnect(), -1, 'Pripoj k databaze')
        submenu.add_menu_item('Vykonaj',lambda z:execute(),-1,'Vykonaj')
        self.__interface.add_notification('project-opened', lambda y:self.showMenu())
        self.__interface.transaction.autocommit = True
        self.__interface.set_main_loop(GtkMainLoop())
    def showMenu(self):
        if self.__interface.project.metamodel.uri == "urn:umlfri.org:metamodel:DRAmodel":

            self.__menu.visible = True
        else:
            self.__menu.visible = False
    def menuConnect(self):
        b=gtk.Builder()
        b.add_from_file("share\\addons\\DRA\\plugin\\menu.glade")
        self.__menuConnect=b.get_object("dialog1")
        self.__menuConnect.set_keep_above(True)
        self.__menuConnect.show_all()
        self.__menuConnect.set_keep_above(False)
        self.__menuConnect.grab_focus()
        c=b.get_object("button1")
        c.connect("clicked",lambda x:connect())

    def connect(self):
        #db = MySQLdb.connect(host=b.get_object("entry1").get_text(),user=b.get_object("entry3").get_text(),
        #passwd=b.get_object("entry4").get_text(),db=b.get_object("entry2").get_text())
        #db = MySQLdb.connect(host="localhost",user="belas",passwd="824510802",db="skuska")
        self.__menuConnect.hide()
        a=Connection()
        a.pripoj(2)
        b=Connection()
    def execute(self):
        a = self.__interface.current_diagram.selected
        tem=list(a)
        if len(tem) == 1:
            select=tem.pop()
            object=self.create(select)
            o=object.execute()
            if o==None:
                print "empty result"
            else:
                for row in o:
                    for column in row:
                        print column,
                    print "\n",
            PyApp(o)
            gtk.main()


        else:
            print "musis oznacit nejaky element"
    def create(self,trunk,ob=None):
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
            object=Inner_Join(trunk.object.values["column1"],trunk.object.values["condition"],trunk.object.values["column2"])
        elif name=="Left outter join":
            pass
        elif name=="Right outter join":
            pass
        elif name=="Full outter join":
            pass
        if(ob!=None):
            ob.set(object)
        connections=trunk.connections
        list_connection=list(connections)
        source_position=trunk.position
        left_object=None
        right_object=None
        for i in range(0,len(list_connection)):
            conn=list_connection[i]
            object1=conn.source
            object1_position=object1.position
            corner=math.atan2(source_position[1]-object1_position[1],source_position[0]-object1_position[0])
            if(corner<0):
                print "wrong orientation of diagram"
                return None
            else:
                if(left_object==None):
                    left_object=object1
                    if(len(list_connection)!=1):
                        conn2=list_connection[i+1]
                        right_object=conn2.source
                else:
                    left_object_position=left_object.position
                    if(math.atan2(source_position[1]-left_object_position[1],source_position[0]-left_object_position[0])>corner):
                        right_object=left_object
                        left_object=object1
        if (left_object.object.name != trunk.object.name):
            self.create(left_object,object)
        if(right_object!=None):
            if(right_object.object.name != trunk.object.name):
                self.create(right_object,object)
        if(ob==None):
            return object