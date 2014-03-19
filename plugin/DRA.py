#!/usr/bin/python
import math
import threading

from org.umlfri.api.mainLoops import GtkMainLoop
from connect import *
from composite_operations import *
from list import *
from attention import *
from sql_parser import Sql_parser


class DRA:
    def __init__(self,interface):
        self.__type = "ine"
        self.__windows = []
        self.__interface = interface
        self.__menuConnect = None
        self.__editorWindow = None
        self.__menu = self.__interface.gui_manager.main_menu.add_menu_item('DRA', '', -1, 'Relational algebra')
        self.__menu.add_submenu()
        self.__menu.visible=False
        self.__submenu = self.__menu.submenu
        self.__submenu.add_menu_item('disconnect',lambda x:self.disconnect(), -1, 'Disconnect')
        self.__submenu.add_menu_item('connect', lambda x:self.menuConnect(), -1, 'Connect to database')
        self.__submenu.add_menu_item('sqlcommand',lambda x:self.showSqlEditor(), -1, 'Sql command')
        self.__submenu.add_menu_item('execute',lambda x:self.execute(), -1, 'Execute')
        self.__parser = Sql_parser()
        self.__elements = {}

    def showSqlEditor(self):
        if self.__editorWindow is None:
            self.__gtkBuilder = gtk.Builder()
            self.__gtkBuilder.add_from_file("share\\addons\\DRA\\plugin\\editor.glade")
            self.__editorWindow = self.__gtkBuilder.get_object("window1")
            connect_button = self.__gtkBuilder.get_object("button1")
            cancel_button = self.__gtkBuilder.get_object("button2")
            self.__sqlCommand = self.__gtkBuilder.get_object("text_view")
            connect_button.connect("clicked",lambda x:self.parseSql())
            cancel_button.connect("clicked",lambda x:self.cancelEditor())
            self.__editorWindow.set_keep_above(True)
            self.__editorWindow.set_modal(True)
            self.__editorWindow.set_transient_for(None)
            self.__editorWindow.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
            self.__editorWindow.show_all()
            self.__windows.append(self.__editorWindow)
        else:
            self.__editorWindow.show_all()

    def cancelEditor(self):
        self.__editorWindow.hide()

    def parseSql(self):
        self.__diagram = list(self.__interface.project.root.diagrams)[0]
        self.__editorWindow.hide()
        buffer = self.__sqlCommand.get_buffer()
        command = buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
        composite = self.__parser.parse(command)
        composite.paint(self.__interface, self.__diagram)


    def pluginMain(self):
        self.__interface.add_notification('project-opened', self.showMenu)
        self.__interface.transaction.autocommit = True
        self.__interface.set_main_loop(GtkMainLoop())

    def showMenu(self):
        if self.__interface.project.metamodel.uri == "urn:umlfri.org:metamodel:DRAmodel":
            self.__type="DRA"
            menu=self.__submenu.items
            for m in menu:
                if m.gui_id=="disconnect":
                    m.visible=False
                if m.gui_id=="execute":
                    m.enabled=False
                if m.gui_id=="connect":
                    m.visible=True
                    m.enabled=True
            self.__menu.visible = True
        else:
            if self.__type is "DRA":
                a=Connection()
                a.disconnect()
                for window in self.__windows:
                    if window.get_title()=="Connect to database" or isinstance(window,WaitingBar):
                        try:
                            window.hide_all()
                        except Exception:
                            pass
                    else:
                        try:
                            window.destroy()
                        except Exception:
                            pass
                if self.__menuConnect is not None:
                    self.__menuConnect.hide()
                self.__windows=[]
                self.__menu.visible = False
            self.__type="ine"

    def menuConnect(self):
        if self.__menuConnect is None:
            self.__gtkBuilder=gtk.Builder()
            self.__gtkBuilder.add_from_file("share\\addons\\DRA\\plugin\\menu.glade")
            self.__menuConnect=self.__gtkBuilder.get_object("window1")
            self.__password=self.__gtkBuilder.get_object("entry4")
            self.__password2=self.__gtkBuilder.get_object("entry6")
            self.__database=self.__gtkBuilder.get_object("entry2")
            self.__check=self.__gtkBuilder.get_object("checkbutton1")
            store = gtk.ListStore(str)
            connection = Connection()
            databases = connection.getAvailableDatabases()
            for data in databases:
                store.append([data])
            #store.append (["MySQL"])
            #store.append (["Oracle"])
            #store.append (["PostgreSQL"])
            self.__combobox=self.__gtkBuilder.get_object("combobox1")
            self.__combobox.set_model(store)
            self.__check.connect("toggled",lambda x:self.check())
            self.__combobox.connect("changed",lambda x:self.oracle())
            cell = gtk.CellRendererText()
            self.__combobox.pack_start(cell, True)
            self.__combobox.add_attribute(cell, 'text',0)
            connect_button=self.__gtkBuilder.get_object("button1")
            cancel_button=self.__gtkBuilder.get_object("button2")
            connect_button.connect("clicked",lambda x:self.connect())
            cancel_button.connect("clicked",lambda x:self.cancel())
            self.__objectes=[]
            self.__objectes.append(self.__gtkBuilder.get_object("accellabel1"))
            self.__objectes.append(self.__gtkBuilder.get_object("checkbutton1"))
            self.__objectes.append(self.__gtkBuilder.get_object("accellabel2"))
            self.__objectes.append(self.__gtkBuilder.get_object("accellabel3"))
            self.__objectes.append(self.__gtkBuilder.get_object("entry5"))
            self.__objectes.append(self.__gtkBuilder.get_object("entry6"))
            entry=self.__gtkBuilder.get_object("entry5")
            entry.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
            entry.set_editable(False)
            entry=self.__gtkBuilder.get_object("entry6")
            entry.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
            entry.set_editable(False)
            self.__menuConnect.set_keep_above(True)
            self.__menuConnect.set_modal(True)
            self.__menuConnect.set_transient_for(None)
            self.__menuConnect.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
            self.__password.delete_text(0,len(self.__password.get_text())-1)
            self.__password2.delete_text(0,len(self.__password2.get_text())-1)
            self.__windows=[self.__menuConnect]
            self.__menuConnect.show_all()
            for object in self.__objectes:
                object.hide()
        else:
            self.__password.delete_text(0,len(self.__password.get_text()))
            self.__password2.delete_text(0,len(self.__password2.get_text()))
            self.__menuConnect.show_all()

    def check(self):
        if self.__check.get_active():
            entry = self.__gtkBuilder.get_object("entry5")
            entry.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
            entry.set_editable(False)
            entry = self.__gtkBuilder.get_object("entry6")
            entry.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
            entry.set_editable(False)
        else:
            entry = self.__gtkBuilder.get_object("entry5")
            entry.set_editable(True)
            entry.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            entry = self.__gtkBuilder.get_object("entry6")
            entry.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            entry.set_editable(True)

    def oracle(self):
        type=self.__combobox.get_active()
        if type is 1:
            for object in self.__objectes:
                object.show()
            self.__database.set_editable(False)
            self.__database.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
        else:
            for object in self.__objectes:
                object.hide()
            self.__database.set_editable(True)
            self.__database.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))


    def cancel(self):
        self.__menuConnect.hide()

    def connect(self):
        host = self.__gtkBuilder.get_object("entry1").get_text()
        database = self.__gtkBuilder.get_object("entry2").get_text()
        user = self.__gtkBuilder.get_object("entry3").get_text()
        password = self.__gtkBuilder.get_object("entry4").get_text()
        user1 = self.__gtkBuilder.get_object("entry5").get_text()
        password1 = self.__gtkBuilder.get_object("entry6").get_text()
        check = self.__check.get_active()
        type = self.__combobox.get_active()
        if type == -1:
            self.__menuConnect.show()
            attention = InfoBarDemo("Connect error", "You must choose type of database","Warning")
            self.__windows.append(attention)
            attention.show()
        elif host == "":
            self.__menuConnect.show()
            attention = InfoBarDemo("Connect error", "You must type host name", "Warning")
            self.__windows.append(attention)
            attention.show()
        elif database == "" and type != 1:
            self.__menuConnect.show()
            attention = InfoBarDemo("Connect error","You must type name of database", "Warning")
            self.__windows.append(attention)
            attention.show()
        elif user=="":
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error", "You must type user name", "Warning")
            self.__windows.append(attention)
            attention.show()
        elif not check and type == 1 and user1 == "":
            self.__menuConnect.show()
            attention = InfoBarDemo("Connect error", "You must type user name for server or use check button for using same login info", "Warning")
            self.__windows.append(attention)
            attention.show()
        elif not check and type == 1 and password1 == "":
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error", "You must type password for server or use check button for using same login info", "Warning")
            self.__windows.append(attention)
            attention.show()
        else:
            menu = self.__submenu.items
            a = Connection()
            if type == 1 and not check:
                threading._start_new_thread(a.connect, (host, database, user, password, type,menu, self.__windows, user1, password1))
            else:
                threading._start_new_thread(a.connect, (host, database, user, password, type,menu, self.__windows))
            self.__menuConnect.hide()
            for m in menu:
                if m.gui_id == "connect":
                    m.enabled=False

    def disconnect(self):
        a=Connection()
        a.disconnect()
        menu=self.__submenu.items
        for m in menu:
            if m.gui_id=="connect":
                m.visible=True
                m.enabled=True
            if m.gui_id=="disconnect":
                m.visible=False
            if m.gui_id=="execute":
                m.enabled=False
        self.__menuConnect=None

    def execute(self):
        self.__elements = {}
        a = self.__interface.current_diagram.selected
        tem = list(a)
        c = Connection()
        o = None
        if c.getTyp() != "":
            if len(tem) == 1:
                select = tem.pop()
                try:
                    object = self.create(select)
                    o = object.execute()
                except CompileError as error:
                    attention = InfoBarDemo(error.getName(), error.getValue(), "Warning")
                    self.__windows.append(attention)
                    attention.show()
                if o is not None:
                    if not o.getHeader():
                        attention = InfoBarDemo("Relation error", "Relation is empty", "Warning")
                        self.__windows.append(attention)
                        attention.show()
                    else:
                        self.__windows.append(PyApp(o))
                        gtk.main()
            else:
                attention = InfoBarDemo("Execute error", "You must select one element"," Warning")
                self.__windows.append(attention)
                attention.show()

        else:
            attention = InfoBarDemo("Connect error", "You must first connect to database", "Warning")
            self.__windows.append(attention)
            attention.show()

    def create(self, trunk, ob=None):
        name = trunk.object.type.name
        reused = False
        elementName = trunk.object.values["name"]
        if elementName in self.__elements:
            object = self.__elements[name]
            reused = True
        if not reused:
            connections = trunk.connections
            list_connection = list(connections)
            list_destination = []
            list_source = []
            for connect in list_connection:
                if connect.destination.object.name == trunk.object.name:
                    list_destination.append(connect)
                else:
                    list_source.append(connect)
            #if len(list_source) > 1:
            #    raise CompileError(name + " "+trunk.object.name + " have to much output connections", "Compile error")
            if name == "Table":
                a = Connection()
                if len(list_destination) > 1:
                    raise CompileError("Table "+trunk.object.values["table_name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Table(a, trunk.object.values["table_name"])
            elif name == "Union":
                if len(list_destination) != 2:
                    raise CompileError("Union "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Union()
            elif name == "Intersection":
                if len(list_destination) != 2:
                    raise CompileError("Intersection "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Intersection()
            elif name == "Product":
                if len(list_destination) != 2:
                    raise CompileError("Product "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Product()
            elif name == "Difference":
                if len(list_destination) != 2:
                    raise CompileError("Difference "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Difference()
            elif name == "Division":
                if len(list_destination) != 2:
                    raise CompileError("Division "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Division()
            elif name == "Selection":
                if len(list_destination) != 1:
                    raise CompileError("Selection "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Selection(trunk.object.values["column1"], trunk.object.values["condition"], trunk.object.values["column2"])
            elif name == "Projection":
                if len(list_destination) != 1:
                    raise CompileError("Projection "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Projection(trunk.object.values["c"])
            elif name == "Inner join":
                if len(list_destination) != 2:
                    raise CompileError("Inner join "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Join(trunk.object.values["cond"])
            elif name == "Left outter join":
                if len(list_destination) != 2:
                    raise CompileError("Left outter join "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Join(trunk.object.values["cond"], True)
            elif name == "Right outter join":
                if len(list_destination) != 2:
                    raise CompileError("Right outter join "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Join(trunk.object.values["cond"], right=True)
            elif name == "Full outter join":
                if len(list_destination) != 2:
                    raise CompileError("Full outter join "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Join(trunk.object.values["cond"], True, True)
            else:
                raise CompileError("You cannot select connection", "Compile error")
            if ob is not None:
                ob.set(object)
            if len(list_destination) is not 0:
                source_position = trunk.position
                left_object = None
                right_object = None
                for i in range(0, len(list_destination)):
                    conn = list_destination[i]
                    object1 = conn.source
                    object1_position = object1.position
                    corner = math.atan2(source_position[1]-object1_position[1], source_position[0]-object1_position[0])
                    if corner < 0:
                        raise CompileError("Wrong orientation of diagram", "Compile error")
                    if left_object is None:
                        left_object = object1
                        if len(list_destination) != 1:
                            conn2 = list_destination[i+1]
                            right_object = conn2.source
                    else:
                        left_object_position = left_object.position
                        if math.atan2(source_position[1]-left_object_position[1], source_position[0]-left_object_position[0]) > corner:
                            right_object = left_object
                            left_object = object1
                if left_object.object.name != trunk.object.name:
                    self.create(left_object, object)
                if right_object is not None:
                    if right_object.object.name != trunk.object.name:
                        self.create(right_object, object)
        else:
            if ob is not None:
                ob.set(object)
        if ob is None:
            return object
