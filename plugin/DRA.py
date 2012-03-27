#!/usr/bin/python
from org.umlfri.api.mainLoops import GtkMainLoop
from connect import *
from operations import *
from list import *
from attention import *
import math
from error import *

class DRA:
    def __init__(self,interface):
        self.__interface=interface
        self.__menu=None
        self.__menuConnect=None
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
            if m.gui_id=="disconnect":
                m.visible=False
            if m.gui_id=="execute":
                m.enabled=False
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
        self.__hbox6=self.__gtkBuilder.get_object("hbox6")
        self.__hbox7=self.__gtkBuilder.get_object("hbox7")
        self.__hbox8=self.__gtkBuilder.get_object("hbox8")
        self.__database=self.__gtkBuilder.get_object("entry2")
        self.__check=self.__gtkBuilder.get_object("checkbutton1")
        store = gtk.ListStore(str)
        store.append (["MySQL"])
        store.append (["Oracle"])
        store.append (["PostgreSQL"])
        self.__combobox=self.__gtkBuilder.get_object("combobox1")
        self.__combobox.set_model(store)
        self.__check.connect("toggled",lambda z:self.check())
        self.__combobox.connect("changed",lambda z:self.oracle())
        cell = gtk.CellRendererText()
        self.__combobox.pack_start(cell, True)
        self.__combobox.add_attribute(cell, 'text',0)
        self.__menuConnect.set_keep_above(True)
        self.__menuConnect.show_all()
        connect_button=self.__gtkBuilder.get_object("button1")
        cancel_button=self.__gtkBuilder.get_object("button2")
        connect_button.connect("clicked",lambda x:self.connect())
        cancel_button.connect("clicked",lambda y:self.cancel())
    def check(self):
        if self.__check.get_active():
            entry=self.__gtkBuilder.get_object("entry5")
            entry.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
            entry.set_editable(False)
            entry=self.__gtkBuilder.get_object("entry6")
            entry.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
            entry.set_editable(False)
        else:
            entry=self.__gtkBuilder.get_object("entry5")
            entry.set_editable(True)
            entry.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            entry=self.__gtkBuilder.get_object("entry6")
            entry.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            entry.set_editable(True)

    def oracle(self):
        type=self.__combobox.get_active()
        if type is 1:
            self.__hbox6.show()
            self.__hbox7.show()
            self.__hbox8.show()
            self.__database.set_editable(False)
            self.__database.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
        else:
            self.__hbox6.hide()
            self.__hbox7.hide()
            self.__hbox8.hide()
            self.__menuConnect.resize(310,150)
            self.__database.set_editable(True)
            self.__database.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))


    def cancel(self):
        self.__menuConnect.hide()
    def connect(self):
        host=self.__gtkBuilder.get_object("entry1").get_text()
        database=self.__gtkBuilder.get_object("entry2").get_text()
        user=self.__gtkBuilder.get_object("entry3").get_text()
        password=self.__gtkBuilder.get_object("entry4").get_text()
        user1=self.__gtkBuilder.get_object("entry5").get_text()
        password1=self.__gtkBuilder.get_object("entry6").get_text()
        check=self.__check.get_active()
        type=self.__combobox.get_active()
        if type==-1:
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must choose type of database","Warning")
        elif host=="":
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must type host name","Warning")
        elif database=="" and type!=1:
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must type name of database","Warning")
        elif user=="":
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must type user name","Warning")
        elif password=="":
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must type password","Warning")
        elif check == False and type==1 and user1=="":
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must type user name for database or use check button for using same login info","Warning")
        elif check == False and type==1 and password1=="":
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error","You must type password for database or use check button for using same login info","Warning")
        else:
            try:
                a=Connection()
                if type==1 and check==False:
                    a.connect(host,database,user,password,type,user1,password1)
                else:
                    a.connect(host,database,user,password,type)
                self.__menuConnect.hide()
                menu=self.__submenu.items
                for m in menu:
                    if m.gui_id=="connect":
                        m.visible=False
                    if m.gui_id=="disconnect":
                        m.visible=True
                    if m.gui_id=="execute":
                        m.enabled=True
            except Exception:
                self.__menuConnect.show()
                attention=InfoBarDemo("Connection error","Connect to database failed","Warning")
    def disconnect(self):
        a=Connection()
        a.disconnect()
        menu=self.__submenu.items
        for m in menu:
            if m.gui_id=="connect":
                m.visible=True
            if m.gui_id=="disconnect":
                m.visible=False
            if m.gui_id=="execute":
                m.enabled=False
    def execute(self):
        a = self.__interface.current_diagram.selected
        tem=list(a)
        c=Connection()
        o=None
        if c.getTyp()!= "":
            if len(tem) == 1:
                select=tem.pop()
                try:
                    object=self.create(select)
                    o=object.execute()
                except CompileError as error:
                    attention=InfoBarDemo(error.getName(),error.getValue(),"Warning")
                if o is not None:
                    PyApp(o)
                    gtk.main()
            else:
                attention=InfoBarDemo("Execute error","You must select one element","Warning")
        else:
            attention=InfoBarDemo("Connect error","You must first connect to database","Warning")
    def create(self,trunk,ob=None):
        name= trunk.object.type.name
        connections=trunk.connections
        list_connection=list(connections)
        list_destination=[]
        list_source=[]
        for connect in list_connection:
            if connect.destination.object.name == trunk.object.name :
                list_destination.append(connect)
            else:
                list_source.append(connect)
        if len(list_source)>1:
            raise CompileError(name + " "+ trunk.object.name+" have to much output connections","Compile error")
        if name=="Table":
            a=Connection()
            if len(list_destination) > 1:
                raise CompileError("Table "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Table(a,trunk.object.values["name"])
        elif name=="Union":
            if len(list_destination) != 2:
                raise CompileError("Union "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Union(trunk.object.values["name"])
        elif name=="Intersection":
            if len(list_destination) != 2:
                raise CompileError("Intersection "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Intersection(trunk.object.values["name"])
        elif name=="Product":
            if len(list_destination) != 2:
                raise CompileError("Product "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Product(trunk.object.values["name"])
        elif name=="Difference":
            if len(list_destination) != 2:
                raise CompileError("Difference "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Difference(trunk.object.values["name"])
        elif name=="Division":
            if len(list_destination) != 2:
                raise CompileError("Intersection "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Division(trunk.object.values["name"])
        elif name=="Selection":
            if len(list_destination) != 1:
                raise CompileError("Intersection "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Selection(trunk.object.values["name"],trunk.object.values["column1"],trunk.object.values["condition"],trunk.object.values["column2"])
        elif name=="Projection":
            if len(list_destination) != 1:
                raise CompileError("Intersection "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Projection(trunk.object.values["name"],trunk.object.values["c"])
        elif name=="Inner join":
            if len(list_destination) != 2:
                raise CompileError("Intersection "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Join(trunk.object.values["name"],trunk.object.values["column1"],trunk.object.values["condition"],trunk.object.values["column2"])
        elif name=="Left outter join":
            if len(list_destination) != 2:
                raise CompileError("Intersection "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Join(trunk.object.values["name"],trunk.object.values["column1"],trunk.object.values["condition"],trunk.object.values["column2"],True)
        elif name=="Right outter join":
            if len(list_destination) != 2:
                raise CompileError("Intersection "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Join(trunk.object.values["name"],trunk.object.values["column1"],trunk.object.values["condition"],trunk.object.values["column2"],right=True)
        elif name=="Full outter join":
            if len(list_destination) != 2:
                raise CompileError("Intersection "+trunk.object.values["name"]+" have wrong number of connections","Compile error")
            else:
                object=Join(trunk.object.values["name"],trunk.object.values["column1"],trunk.object.values["condition"],trunk.object.values["column2"],True,True)
        else:
            raise CompileError("You cannot select connection","Compile error")
        if ob is not None:
            ob.set(object)

        source_position=trunk.position
        left_object=None
        right_object=None
        for i in range(0,len(list_connection)):
            conn=list_connection[i]
            object1=conn.source
            object1_position=object1.position
            corner=math.atan2(source_position[1]-object1_position[1],source_position[0]-object1_position[0])
            if corner<0:
                raise CompileError("Wrong orientation of diagram","Compile error")
            if left_object is None:
                left_object=object1
                if len(list_connection)!=1:
                    conn2=list_connection[i+1]
                    right_object=conn2.source
            else:
                left_object_position=left_object.position
                if math.atan2(source_position[1]-left_object_position[1],source_position[0]-left_object_position[0])>corner:
                    right_object=left_object
                    left_object=object1
        if left_object.object.name != trunk.object.name:
            self.create(left_object,object)
        if right_object is not None:
            if right_object.object.name != trunk.object.name:
                self.create(right_object,object)
        if ob is None:
            return object
