#!/usr/bin/python
import math
import threading

from org.umlfri.api.mainLoops import GtkMainLoop
from connect import *
from composite_operations import *
from list import *
from attention import *
from sql_parser import Sql_parser
try:
    from igraph import *
except ImportError:
    pass


class DRA:
    def __init__(self,interface):
        self.__type = "ine"
        self.__windows = []
        self.__graph = Graph()
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
        self.__graph = Graph()
        buffer = self.__sqlCommand.get_buffer()
        command = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        try:
            composite = self.__parser.parse(command)
            with self.__interface.transaction:
                el, pos, level = composite.paint(self.__interface, self.__diagram, self.__graph, 0)
            try:
                layout = self.__graph.layout_reingold_tilford(root=composite.get_position())
                layout.rotate(angle=180)
                layout.mirror(0)
                layout.fit_into(bbox=BoundingBox(0, 0, 300, level * 80))
                with self.__interface.transaction:
                    composite.move(layout.coords)
            except Exception:
                pass
        except CompileError as e:
            attention = InfoBarDemo("Parse error", e.message, "Warning")
            self.__windows.append(attention)
            attention.show()
        #except Exception:
            #attention = InfoBarDemo("Parse error", "SQL syntax error", "Warning")
            #self.__windows.append(attention)
            #attention.show()

    def pluginMain(self):
        self.__interface.add_notification('project-opened', self.showMenu)
        self.__interface.set_main_loop(GtkMainLoop())

    def showMenu(self):
        if self.__interface.project.metamodel.uri == "urn:umlfri.org:metamodel:DRAmodel":
            self.__type = "DRA"
            menu = self.__submenu.items
            for m in menu:
                if m.gui_id == "disconnect":
                    m.visible = False
                if m.gui_id == "execute":
                    m.enabled = False
                if m.gui_id == "connect":
                    m.visible = True
                    m.enabled = True
            self.__menu.visible = True
        else:
            if self.__type is "DRA":
                a = Connection()
                a.disconnect()
                for window in self.__windows:
                    if window.get_title() == "Connect to database" or isinstance(window, WaitingBar):
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
            self.__gtkBuilder = gtk.Builder()
            self.__gtkBuilder.add_from_file("share\\addons\\DRA\\plugin\\menu.glade")
            self.__menuConnect = self.__gtkBuilder.get_object("window1")
            self.__password = self.__gtkBuilder.get_object("password")
            self.__database = self.__gtkBuilder.get_object("database")
            store = gtk.ListStore(str)
            connection = Connection()
            databases = connection.getAvailableDatabases()
            for data in databases:
                store.append([data])
            self.__combobox = self.__gtkBuilder.get_object("type")
            self.__combobox.set_model(store)
            self.__combobox.connect("changed", lambda x: self.oracle())
            cell = gtk.CellRendererText()
            self.__combobox.pack_start(cell, True)
            self.__combobox.add_attribute(cell, 'text', 0)
            connect_button = self.__gtkBuilder.get_object("button1")
            cancel_button = self.__gtkBuilder.get_object("button2")
            connect_button.connect("clicked", lambda x: self.connect())
            cancel_button.connect("clicked", lambda x: self.cancel())
            self.__sid = self.__gtkBuilder.get_object("sid")
            self.__sid.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
            self.__menuConnect.set_keep_above(True)
            self.__menuConnect.set_modal(True)
            self.__menuConnect.set_transient_for(None)
            self.__menuConnect.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
            self.__password.delete_text(0, len(self.__password.get_text())-1)
            self.__windows = [self.__menuConnect]
            self.__menuConnect.show_all()
        else:
            self.__password.delete_text(0,len(self.__password.get_text()))
            self.__menuConnect.show_all()

    def oracle(self):
        type = self.__combobox.get_active()
        if type is 1:
            self.__sid.set_editable(True)
            self.__sid.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            self.__database.set_editable(False)
            self.__database.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
        else:
            self.__sid.set_editable(False)
            self.__sid.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
            self.__database.set_editable(True)
            self.__database.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))

    def cancel(self):
        self.__menuConnect.hide()

    def connect(self):
        host = self.__gtkBuilder.get_object("host").get_text()
        database = self.__gtkBuilder.get_object("database").get_text()
        user = self.__gtkBuilder.get_object("login").get_text()
        password = self.__gtkBuilder.get_object("password").get_text()
        port = self.__gtkBuilder.get_object("port").get_text()
        sid = self.__gtkBuilder.get_object("sid").get_text()
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
        elif user == "":
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error", "You must type user name", "Warning")
            self.__windows.append(attention)
            attention.show()
        elif type == "1" and sid == "":
            self.__menuConnect.show()
            attention=InfoBarDemo("Connect error", "You must specific SID", "Warning")
            self.__windows.append(attention)
            attention.show()
        else:
            menu = self.__submenu.items
            a = Connection()
            threading._start_new_thread(a.connect, (host, database, user, password, sid, port,type,menu, self.__windows))
            self.__menuConnect.hide()
            for m in menu:
                if m.gui_id == "connect":
                    m.enabled=False

    def disconnect(self):
        a = Connection()
        a.disconnect()
        menu = self.__submenu.items
        for m in menu:
            if m.gui_id == "connect":
                m.visible = True
                m.enabled = True
            if m.gui_id == "disconnect":
                m.visible = False
            if m.gui_id == "execute":
                m.enabled = False
        self.__menuConnect = None

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
        if self.__elements.has_key(elementName):
            object = self.__elements[elementName]
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
                    object = Table(trunk.object.values["table_name"], a)
            elif name == "Rename":
                a = Connection()
                if len(list_destination) > 1:
                    raise CompileError("Rename "+trunk.object.values["table_name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Rename(trunk.object.values["alias_name"], trunk.object.values["attribute_name"])
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
                    object = Selection(trunk.object.values["column1"], trunk.object.values["condition"], trunk.object.values["column2"], False)
            elif name == "Projection":
                if len(list_destination) != 1:
                    raise CompileError("Projection "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Projection(trunk.object.values["c"])
            elif name == "Inner join":
                if len(list_destination) != 2:
                    raise CompileError("Inner join "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Join(left=False, right=False, condition=trunk.object.values["cond"])
            elif name == "Left outter join":
                if len(list_destination) != 2:
                    raise CompileError("Left outter join "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Join(left=True, right=False, condition=trunk.object.values["cond"])
            elif name == "Right outter join":
                if len(list_destination) != 2:
                    raise CompileError("Right outter join "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Join(left=False, right=True, condition=trunk.object.values["cond"])
            elif name == "Full outter join":
                if len(list_destination) != 2:
                    raise CompileError("Full outter join "+trunk.object.values["name"]+" have wrong number of connections", "Compile error")
                else:
                    object = Join(left=True, right=True, condition=trunk.object.values["cond"])
            else:
                raise CompileError("You cannot select connection", "Compile error")
            self.__elements[elementName] = object
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
