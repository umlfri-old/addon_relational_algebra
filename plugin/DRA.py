#!/usr/bin/python
import gtk
from org.umlfri.api.mainLoops import GtkMainLoop
from gtk.gdk import WindowTypeHint
import MySQLdb
from connect import *
from operations import *
from list import *
from attention import *
import math


class DRA:
    def __init__(self,interface):
        self.__interface=interface
        self.__orientation=False
        self.__menu=None
        self.__menuConnect=None
        self.__connection_Select=False
    def pluginMain(self):
        self.__menu = self.__interface.gui_manager.main_menu.add_menu_item('DRA', '', -1, 'Relational algebra')
        self.__menu.add_submenu()
        self.__menu.visible=False
        self.__submenu = self.__menu.submenu
        self.__submenu.add_menu_item('disconnect',lambda z:self.disconnect(),-1,'Disconnect')
        self.__submenu.add_menu_item('connect', lambda x:self.menuConnect(), -1, 'Connect to database')
        self.__submenu.add_menu_item('execute',lambda z:self.execute(),-1,'Execute')
        menu=self.__submenu.items
        for m in menu:
            if(m.gui_id=="disconnect"):
                m.visible=False
        self.__interface.add_notification('project-opened', lambda y:self.showMenu())
        self.__interface.transaction.autocommit = True
        self.__interface.set_main_loop(GtkMainLoop())
    def showMenu(self):
        if self.__interface.project.metamodel.uri == "urn:umlfri.org:metamodel:DRAmodel":
            self.__menu.visible = True
        else:
            self.__menu.visible = False
    def menuConnect(self):
        self.__gtkBuilder=gtk.Builder()
        self.__gtkBuilder.add_from_file("share\\addons\\DRA\\plugin\\menu.glade")
        self.__menuConnect=self.__gtkBuilder.get_object("window1")
        store = gtk.ListStore(str)
        store.append (["MySQL"])
        store.append (["Oracle"])
        store.append (["PostgreSQL"])
        self.__combobox=self.__gtkBuilder.get_object("combobox1")
        self.__combobox.set_model(store)
        cell = gtk.CellRendererText()
        self.__combobox.pack_start(cell, True)
        self.__combobox.add_attribute(cell, 'text',0)
        self.__menuConnect.set_keep_above(True)
        self.__menuConnect.show_all()
        self.__menuConnect.set_keep_above(False)
        self.__menuConnect.grab_focus()
        connect_button=self.__gtkBuilder.get_object("button1")
        cancel_button=self.__gtkBuilder.get_object("button2")
        connect_button.connect("clicked",lambda x:self.connect())
        cancel_button.connect("clicked",lambda y:self.cancel())
    def cancel(self):
        self.__menuConnect.hide()
    def connect(self):
        self.__menuConnect.hide()
        host=self.__gtkBuilder.get_object("entry1").get_text()
        database=self.__gtkBuilder.get_object("entry2").get_text()
        user=self.__gtkBuilder.get_object("entry3").get_text()
        password=self.__gtkBuilder.get_object("entry4").get_text()
        type=self.__combobox.get_active()
        if(type==-1):
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must choose type of database","Warning")
        elif (host==""):
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must type host name","Warning")
        elif (database==""):
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must type name of database","Warning")
        elif (user==""):
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must type user name","Warning")
        elif(password==""):
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must type password","Warning")
        else:
            try:
                a=Connection()
                a.pripoj(type)
                menu=self.__submenu.items
                for m in menu:
                    if(m.gui_id=="connect"):
                        m.visible=False
                    if(m.gui_id=="disconnect"):
                        m.visible=True
            except:
                self.__menuConnect.show()
                attention=InfoBarDemo("Connection error","Connect to database failed","Warning")
    def disconnect(self):
        a=Connection()
        a.disconnect()
        menu=self.__submenu.items
        for m in menu:
            if(m.gui_id=="connect"):
                m.visible=True
            if(m.gui_id=="disconnect"):
                m.visible=False
    def execute(self):
        self.__orientation=False
        self.__connection_Select=False
        a = self.__interface.current_diagram.selected
        tem=list(a)
        c=Connection()
        if (c.getTyp()!= ""):
            if (len(tem) == 1):
                select=tem.pop()
                object=self.create(select)
                if object==-1:
                    attention=InfoBarDemo("Execute error","Wrong orientation of model","Warning")
                elif object==0:
                    attention=InfoBarDemo("Execute error","You cannot select connection","Warning")
                else:
                    o=object.execute()
                    if o==None:
                        attention=InfoBarDemo("Execute error","Empty result","Warning")
                    else:
                        PyApp(o)
                        gtk.main()
            else:
                attention=InfoBarDemo("Execute error","You must select one element","Warning")
        else:
            attention=InfoBarDemo("Connect error","You must first connect to database","Warning")
    def create(self,trunk,ob=None):
        name= trunk.object.type.name
        if name=="Table":
            a=Connection()
            object=Table(a,trunk.object.values["name"])
        elif name=="Union":
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
        else:
            self.__connection_Select=True
        if (self.__connection_Select==False):
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
                    self.__orientation=True
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
            if(ob==None) and (self.__orientation==False):
                return object
            elif(ob==None) and (self.__orientation==True):
                return -1
        return 0