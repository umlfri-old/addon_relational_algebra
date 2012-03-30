# -*- coding: utf-8 -*-
import gtk

class PyApp(gtk.Window):
    def __init__(self,data):
        super(PyApp, self).__init__()
        self.__data=data
        height=self.__data.getLen()
        self.__header=self.__data.getColumnsName()
        width=180
        length=0
        z=0
        for i in self.__header:
            length += len(i)
        if length>30:
            z=length-30
        width=width+(z*15)
        self.set_size_request(width, 50+(height*25))
        self.destroy_with_parent
        self.set_position(gtk.WIN_POS_CENTER)
        
        self.connect("destroy", gtk.main_quit)
        self.set_title("Result of "+self.__data.getName())

        vbox = gtk.VBox(False, 8)
        
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        vbox.pack_start(sw, True, True, 0)

        store = self.create_model()

        treeView = gtk.TreeView(store)
        treeView.set_rules_hint(True)
        sw.add(treeView)
        self.create_columns(treeView)
        self.add(vbox)
        self.show_all()
    def create_model(self):
        
        
        store = gtk.ListStore(*([str] * len(self.__header)))

        for i in self.__data:
            new=[]
            for column in i:
                if column=="`":
                    column=" "
                new.append(column)
            store.append(new)
        return store


    def create_columns(self, treeView):
        for i in range(0,len(self.__header)):
            rendererText = gtk.CellRendererText()
            new=self.__header[i].replace('_','_ ')
            column = gtk.TreeViewColumn(new, rendererText, text=i)
            column.set_sort_column_id(i)
            treeView.append_column(column)
